"""統合モンテカルロ：ホルダー行動（構造モデル）× 外生ショック（EWMA・残差ブートストラップ）× 平方根インパクト × 値幅制限."""
from __future__ import annotations

import numpy as np

from .config import P, price_limit_vec
from .flows import sample_toshiba
from .structural import MarginModel
from .vol import ReturnEngine


def volume_coef(px):
    d = px.dropna(subset=["ret", "adv20"])
    y = (d.volume / d.adv20).values
    X = np.c_[np.ones(len(d)), d.ret.abs().values]
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b


def joint_mc(model_hist: MarginModel, w: np.ndarray, eng: ReturnEngine, rng, n_paths: int, h: int, p_last: float,
             adv: float, vol_b, gap_shift0: float = 0.0, gap_sd_scale0: float = 1.0, toshiba: str = "normal",
             impact_on: bool = True, mech_base: float = 0.0, tosh_base: float = 0.0, z_prev0: float = 0.0,
             conditional: bool = True) -> dict:
    """toshiba: 'none' | 'normal'（平常: 確率0.5で出来高の0.5〜6%） | 'burst'（毎日 6〜15%）.
    インパクトは『機械的フロー（強制＋一部売却）と東芝売りの、平常水準 (mech_base, tosh_base) からの超過分』にのみ適用.
    conditional=True: 前日リターン→窓、窓→日中 の条件付きブートストラップ（マルコフ）."""
    idx = rng.choice(len(w), size=n_paths, p=w)
    model = model_hist.select(idx)
    zg_u, zi_u = eng.sample_pairs(rng, n_paths, h)
    vg, vi = np.full(n_paths, eng.var_g_next), np.full(n_paths, eng.var_i_next)
    Y = rng.uniform(0.3, 0.9, n_paths) if impact_on else np.zeros(n_paths)   # 平方根インパクト係数はパス毎に不確実
    prev = np.full(n_paths, p_last, float)
    zprev = np.full(n_paths, z_prev0, float)
    tosh_kw = dict(none=dict(p_active=0.0), normal=dict(p_active=0.5, lo=0.005, hi=0.06), burst=dict(p_active=1.0, lo=0.06, hi=0.15))[toshiba]
    O = np.zeros((n_paths, h)); C = np.zeros((n_paths, h)); LK = np.zeros((n_paths, h), bool)
    keys = ("forced", "cure", "volc", "new", "trig", "sell", "S", "A", "D", "queued_f", "queued_c")
    F = {k: np.zeros((n_paths, h)) for k in keys}
    TOSH = np.zeros((n_paths, h)); IMP = np.zeros((n_paths, h))
    for t in range(h):
        lim = price_limit_vec(prev)
        sig = np.sqrt(vg + vi)
        # --- 寄付：予定売り（強制・一部売却）の MOO インパクト
        qf, qc = model.due_tomorrow()
        q_open = np.maximum(qf + qc - mech_base, 0.0)
        imp_open = -Y * sig * np.sqrt(q_open / adv)
        zg_t = eng.sample_gap_given_prev(rng, zprev) if conditional else zg_u[:, t]
        g = np.sqrt(vg) * zg_t * (gap_sd_scale0 if t == 0 else 1.0) + (gap_shift0 if t == 0 else 0.0) + imp_open
        o = np.clip(prev * np.exp(g), prev - lim, prev + lim)
        # --- 日中：窓（実現値）に条件付けた日中残差、東芝売りの超過分のインパクト、不動点反復
        zg_real = np.log(o / prev) / np.sqrt(vg)
        zi_t = eng.sample_intra_given_gap(rng, zg_real) if conditional else zi_u[:, t]
        z_in = np.sqrt(vi) * zi_t
        c = np.clip(o * np.exp(z_in), prev - lim, prev + lim)
        imp_intra = np.zeros(n_paths)
        tosh = np.zeros(n_paths)
        for _ in range(2):
            r = np.log(c / prev)
            V = adv * np.clip(vol_b[0] + vol_b[1] * np.abs(r), 0.3, 6.0)
            locked = c <= prev - lim + 0.5
            V = np.where(locked, V * 0.35, V)
            volc, N = model.preview_flows(prev, c, V)
            tosh = sample_toshiba(rng, n_paths, V, **tosh_kw) if toshiba != "none" else np.zeros(n_paths)
            Q = -np.maximum(tosh - tosh_base, 0.0)
            imp_intra = np.sign(Q) * Y * sig * np.sqrt(np.abs(Q) / adv)
            c = np.clip(o * np.exp(z_in + imp_intra), prev - lim, prev + lim)
        locked = c <= prev - lim + 0.5
        f = model.step(prev, o, c, V, locked)
        for k in keys:
            F[k][:, t] = f[k]
        O[:, t], C[:, t], LK[:, t], TOSH[:, t], IMP[:, t] = o, c, locked, tosh, imp_open + imp_intra
        rg, ri = np.log(o / prev), np.log(c / o)
        zprev = np.log(c / prev) / np.sqrt(vg + vi)
        vg = eng.lam_g * vg + (1 - eng.lam_g) * rg ** 2
        vi = eng.lam_i * vi + (1 - eng.lam_i) * ri ** 2
        prev = c
    return dict(O=O, C=C, LK=LK, F=F, TOSH=TOSH, IMP=IMP, model=model, idx=idx)


def entry_curve(O, C, exit_day=None):
    """エントリー時期（day1寄付, day1大引け, day2寄付, …）別に、最終日の大引けまで持った損益（対数）."""
    h = C.shape[1]
    exit_day = exit_day or h
    px_exit = C[:, exit_day - 1]
    rows = []
    for t in range(exit_day):
        for lab, entry in ((f"day{t + 1} 寄付", O[:, t]), (f"day{t + 1} 大引け", C[:, t])):
            if t == exit_day - 1 and lab.endswith("大引け"):
                continue
            x = np.log(px_exit / entry)
            pos = x > 0
            rows.append(dict(entry=lab, mean=float(x.mean()), med=float(np.median(x)), p_win=float(pos.mean()),
                             p10=float(np.percentile(x, 10)), p90=float(np.percentile(x, 90)),
                             entry_med=float(np.median(entry))))
    return rows


def hit_probs(C: np.ndarray, O: np.ndarray, ups, dns, horizons=(1, 3, 5)):
    rows = []
    for hz in horizons:
        mx = np.maximum(C[:, :hz].max(1), O[:, :hz].max(1))
        mn = np.minimum(C[:, :hz].min(1), O[:, :hz].min(1))
        rows.append(dict(h=hz, **{f"up{u}": float((mx >= u).mean()) for u in ups}, **{f"dn{d}": float((mn <= d).mean()) for d in dns}))
    return rows


def tactics(O, C, LK, F, S_last, p_last):
    """短期戦術ごとの損益分布（対数リターン）. 行動は終値/始値ベース、ロスカットは終値判定（近似）.
    約定の現実性: ストップ安張り付きの大引けでは『売り』は比例配分で約定しないとみなし、翌日寄付まで持ち越す。
    張り付いた寄付では新規の『売り』（ショート）は建てられないとみなし、その経路は取引なし（0）."""
    out = {}
    lock_open1 = O[:, 0] <= np.minimum.reduce([O[:, 0], C[:, 0]]) + 0.5   # 近似: 寄付が当日安値=張り付き
    exit1 = np.where(LK[:, 0], O[:, 1], C[:, 0])                            # 初日大引けの売りは張り付きなら翌日寄付へ

    def stats(x, mask=None, label=""):
        x = x[mask] if mask is not None else x
        if len(x) < 50:
            return dict(n=len(x))
        pos = x > 0
        gain = x[pos].mean() if pos.any() else 0.0
        lossv = -x[~pos].mean() if (~pos).any() else 1e-9
        return dict(n=len(x), mean=float(x.mean()), med=float(np.median(x)), p_win=float(pos.mean()),
                    p5=float(np.percentile(x, 5)), p95=float(np.percentile(x, 95)),
                    rr=float((gain * pos.mean()) / (lossv * (1 - pos.mean()) + 1e-12)), ev_per_risk=float(x.mean() / (lossv + 1e-12)))

    out["寄付で買い→当日大引けで売り（日中ロング; 張り付き時は翌日寄付で売り）"] = stats(np.log(exit1 / O[:, 0]))
    out["大引けで買い→翌日寄付で売り（オーバーナイト）"] = stats(np.log(O[:, 1] / C[:, 0]))
    out["寄付で買い→3日目大引け（終値-8%で損切り）"] = stats(_hold_with_stop(O[:, 0], C, 3, -0.08))
    short = np.where(LK[:, 0] & lock_open1, 0.0, -np.log(C[:, 0] / O[:, 0]))
    out["寄付で売り→当日大引けで買い戻し（日中ショート; 寄付張り付きなら建てられず0）"] = stats(short)
    gap_up = O[:, 1] > C[:, 0]
    out["翌日が窓上げで寄ったら寄付で買い→その日の大引け"] = stats(np.log(C[:, 1] / O[:, 1]), gap_up)
    out["翌日が窓上げで寄ったら寄付で買い→3営業日後大引け（-8%損切り）"] = stats(_hold_with_stop(O[:, 1], C[:, 1:], 3, -0.08), gap_up)
    fell = F["S"][:, 0] < S_last
    out["初日に信用買い残が減っていたら大引けで買い→3日目大引け"] = stats(np.log(C[:, 3] / C[:, 0]) if C.shape[1] > 3 else np.zeros(0), fell)
    no_lock = ~LK[:, 0]
    out["初日が張り付かなかったら大引けで買い→翌日大引け"] = stats(np.log(C[:, 1] / C[:, 0]), no_lock)
    return out


def _hold_with_stop(entry, C, days, stop):
    n = len(entry)
    pnl = np.zeros(n)
    done = np.zeros(n, bool)
    for t in range(min(days, C.shape[1])):
        r = np.log(C[:, t] / entry)
        hit = (r <= stop) & ~done
        pnl[hit] = r[hit]
        done |= hit
        if t == min(days, C.shape[1]) - 1:
            pnl[~done] = r[~done]
    return pnl
