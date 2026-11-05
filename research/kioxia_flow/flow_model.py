#!/usr/bin/env python3
"""Kioxia (285A) holder-pain & forced-flow model.

信用買い方・株主全体の「苦しさ」を定量化し、そこから生じる行動
（追証による強制決済、投げ、ナンピン、やれやれ売り、イベント需給）を予測する。

Usage (repo root):
    python3 research/kioxia_flow/flow_model.py                # 最新データで実行
    python3 research/kioxia_flow/flow_model.py --now 8100     # 気配/PTS/先物等の参考値を指定
    python3 research/kioxia_flow/flow_model.py --now 8100 --log   # 予測をpredictions_log.csvに記録

データ更新は data/*.csv に行を追記するだけ（README.md 参照）。
依存: numpy, pandas のみ。
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
REPORTS = BASE / "reports"

# ---------------------------------------------------------------- parameters
P = dict(
    shares_total=1_644_045_264,     # 分割後発行済株式数
    treasury=48_400_000,            # 自己株（8月取得 16.13M株×3）
    toshiba_shares=172_007_400,     # 東芝 10.46%（10/27時点）
    skhynix_pct=0.14,               # SKハイニックス（ベイン系ビークル経由、概算）
    maint=0.20,                     # 追証ライン（最低維持率、証券会社により20-30%）
    cure_buffer=0.05,               # 追証解消時に維持率+αまで入金すると仮定
    lag=2,                          # 追証発生→強制決済までの営業日（多くの証券会社で2営業日後）
    classes=(0.30, 0.50, 1.00),     # 新規建て時の保証金率クラス（フルレバ/2倍/ほぼ現金担保）
    legacy_split=((0.79, 0.30), (0.94, 0.40), (1.29, 0.30)),  # 初期建玉の建値分散(平均比, 比率)
    impact_Y=0.7,                   # 平方根インパクト則の係数
    turnover_alpha=(0.4, 0.6, 0.8), # 出来高のうち実質的な保有者入れ替わりの比率
    be_band=0.03,                   # 建値±3%を「やれやれ売り」ゾーンとみなす
    be_sell_margin=0.35,            # 建値回復時に信用買いが手仕舞う確率（仮定）
    be_sell_cash=0.10,              # 同、現物保有者（仮定）
    topix_ffw_step=0.175,           # TOPIX浮動株比率 0.325→0.5
    passive_share=(0.15, 0.20, 0.25),
    n_samples=12000, seed=7, top_k=100,
)
JP_HOLIDAYS = {dt.date(2026, 11, 23), dt.date(2026, 12, 31), dt.date(2027, 1, 1),
               dt.date(2027, 1, 11), dt.date(2027, 2, 11), dt.date(2027, 2, 23), dt.date(2027, 3, 22)}


def next_bdays(d: dt.date, n: int) -> list[dt.date]:
    out, cur = [], d
    while len(out) < n:
        cur += dt.timedelta(days=1)
        if cur.weekday() < 5 and cur not in JP_HOLIDAYS:
            out.append(cur)
    return out


def bdays_between(a: dt.date, b: dt.date) -> int:
    n, cur = 0, a
    while cur < b:
        cur += dt.timedelta(days=1)
        if cur.weekday() < 5 and cur not in JP_HOLIDAYS:
            n += 1
    return n


def price_limit(base: float) -> float:
    table = [(100, 30), (200, 50), (500, 80), (700, 100), (1000, 150), (1500, 300), (2000, 400),
             (3000, 500), (5000, 700), (7000, 1000), (10000, 1500), (15000, 3000), (20000, 4000),
             (30000, 5000), (50000, 7000), (70000, 10000), (100000, 15000)]
    for hi, lim in table:
        if base < hi:
            return lim
    return 30000


# ---------------------------------------------------------------- data
def load():
    px = pd.read_csv(DATA / "prices.csv", parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    mg = pd.read_csv(DATA / "margin_daily.csv", parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    jsf = pd.read_csv(DATA / "jsf_daily.csv", parse_dates=["trade_date"]).sort_values("trade_date")
    hold = pd.read_csv(DATA / "holders.csv", parse_dates=["calc_date"])
    ev = pd.read_csv(DATA / "events.csv", parse_dates=["date"])
    px["tp"] = (px.high + px.low + px.close) / 3
    px["ret"] = np.log(px.close).diff()
    px["adv20"] = px.volume.rolling(20, min_periods=5).mean().shift(1)
    return px, mg, jsf, hold, ev


def float_shares() -> float:
    return P["shares_total"] - P["treasury"] - P["toshiba_shares"] - P["shares_total"] * P["skhynix_pct"]


# ---------------------------------------------------------------- A. volatility / gaps
def vol_stats(px, n=20):
    r = px.ret.dropna().values[-n:]
    o, h, l, c = (px[k].values for k in ("open", "high", "low", "close"))
    on = np.log(o[1:] / c[:-1])[-n:]
    intra = np.log(c[1:] / o[1:])[-n:]
    park = math.sqrt(np.mean(np.log(h[-n:] / l[-n:]) ** 2) / (4 * math.log(2)))
    return dict(sd=r.std(ddof=1), mean=r.mean(), park=park, on_sum=on.sum(), on_sd=on.std(ddof=1),
                on_neg=int((on < 0).sum()), in_sum=intra.sum(), in_sd=intra.std(ddof=1),
                in_pos=int((intra > 0).sum()), n=n)


def volume_model(px):
    d = px.dropna(subset=["ret", "adv20"])
    y = (d.volume / d.adv20).values
    X = np.c_[np.ones(len(d)), d.ret.abs().values]
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b  # volume = adv20 * (b0 + b1*|ret|)


# ---------------------------------------------------------------- B. all-holder cost basis (turnover decay) & CGO
def cohort_model(px, alpha):
    F = float_shares()
    pre, costs, w, rp = 1.0, [], [], []
    for row in px.itertuples():
        f = min(alpha * row.volume / F, 0.95)
        pre *= 1 - f
        w = [x * (1 - f) for x in w]
        costs.append(row.tp)
        w.append(f)
        tot = sum(w)
        rp.append(sum(c * x for c, x in zip(costs, w)) / tot)
    return np.array(costs), np.array(w), pre, np.array(rp)


# ---------------------------------------------------------------- C. proportional-closure decomposition (diagnostic)
def decompose(px, mg):
    m = mg.merge(px[["date", "tp", "close", "ret", "volume"]], on="date", how="left")
    rows = []
    for i in range(1, len(m)):
        S0, A0, S1, A1, p = m.buy_shares[i - 1], m.buy_amount[i - 1], m.buy_shares[i], m.buy_amount[i], m.tp[i]
        den = A0 - p * S0
        keep = (A1 - p * S1) / den if den > 0 else S1 / S0
        keep = min(max(keep, 0.0), 1.0)
        N = S1 - S0 * keep
        if N < 0:
            N, keep = 0.0, min(S1 / S0, 1.0)
        rows.append(dict(date=m.date[i], close=m.close[i], ret=m.ret[i], closed_rate=1 - keep, new=N,
                         closed=S0 * (1 - keep), net=S1 - S0, vol=m.volume[i]))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- D. structural margin-call model
BOUNDS = dict(w30=(0, 0.6), w50=(0, 0.6), q=(0, 0.95), b0=(0, 0.03), b1=(0, 0.8), b2=(0, 0.6),
              n0=(0, 0.06), n1=(0, 0.6), n2=(0, 0.3), lD0=(10.0, 12.6))  # lD0 = log10(買い方の追加資金余力, 円)


def sample_theta(rng, n, center=None, scale=0.0):
    th = {}
    for k, (lo, hi) in BOUNDS.items():
        if center is None:
            th[k] = rng.uniform(lo, hi, n)
        else:
            th[k] = np.clip(rng.choice(center[k], n) + rng.normal(0, (hi - lo) * scale, n), lo, hi)
    s = th["w30"] + th["w50"]
    over = s > 0.95
    th["w30"][over] *= 0.95 / s[over]
    th["w50"][over] *= 0.95 / s[over]
    return th


def take(th, idx):
    return {k: v[idx] for k, v in th.items()}


def simulate(theta, closes, tps, rets, vols, S0, A0, P0, endo_from=None, sigma=None, adv=None, q_cap=None):
    """Vectorised over parameter samples.

    状態: 建玉ビンテージ(建値) × 保証金率クラス。各日:
      1) 2営業日前の追証のうち未解消分を強制決済
      2) 自主的手仕舞い  b0 + b1*下落率 + b2*上昇率
      3) 新規信用買い（ナンピン/逆張り） 出来高*(n0 + n1*下落率 + n2*上昇率)
      4) 大引けで維持率判定 → 確率qで入金（維持率+bufferへ）、1-qで強制決済キューへ
    endo_from 以降の日は、価格を強制決済の平方根インパクトだけで内生的に決める（他は横ばいの純カスケード）。
    """
    m = np.array(P["classes"])
    K, maint, buf, L = len(m), P["maint"], P["cure_buffer"], P["lag"]
    Ps, T = theta["q"].shape[0], len(closes)
    legacy = P["legacy_split"]
    NL = len(legacy)
    NV = NL + T
    avg0 = A0 / S0
    cost = np.zeros(NV)
    for j, (mult, _) in enumerate(legacy):
        cost[j] = avg0 * mult
    cost[NL:] = tps
    wk = np.stack([theta["w30"], theta["w50"], 1 - theta["w30"] - theta["w50"]], axis=1)
    sh = np.zeros((Ps, NV, K))
    me = np.tile(m, (Ps, NV, 1)).astype(float)
    for j, (mult, wl) in enumerate(legacy):
        sh[:, j, :] = S0 * wl * wk
        me[:, j, :] = np.maximum(m[None, :], maint + (1 - P0 / cost[j]) + buf)
    pend = np.zeros((L, Ps, NV, K))
    use_D = P.get("dry_powder", True) and "lD0" in theta
    D0 = 10 ** theta["lD0"] if use_D else np.ones(Ps)
    D = D0.copy()
    keys = ("S", "A", "forced", "trig", "new", "volc", "price", "D")
    out = {k: np.zeros((Ps, T)) for k in keys}
    prev = np.full(Ps, P0, dtype=float)
    for t in range(T):
        if use_D and q_cap is not None and q_cap[1] == 0 and t >= q_cap[0]:
            D = np.zeros(Ps)  # ストレス: 余力ゼロ（入金もナンピンも止まる）
        ex = pend[0].copy()
        pend = np.roll(pend, -1, axis=0)
        pend[-1] = 0
        F = ex.sum(axis=(1, 2))
        out["forced"][:, t] = F
        if endo_from is not None and t >= endo_from:
            Pt = prev * np.exp(-P["impact_Y"] * sigma * np.sqrt(F / adv))
            cost[NL + t] = 0.0  # placeholder, set below per-sample average
            tp_t = Pt
        else:
            Pt = np.full(Ps, closes[t], dtype=float)
            tp_t = None
        rt = np.log(Pt / prev)
        dn, up = np.maximum(-rt, 0), np.maximum(rt, 0)
        v = np.clip(theta["b0"] + theta["b1"] * dn + theta["b2"] * up, 0, 0.6)
        out["volc"][:, t] = sh.sum(axis=(1, 2)) * v
        sh *= (1 - v)[:, None, None]
        vol_t = vols[t] if np.isscalar(vols[t]) else vols[t]
        frac = np.clip(D / D0, 0, 1) if use_D else np.ones(Ps)
        N = vol_t * np.clip(theta["n0"] + theta["n1"] * dn * frac + theta["n2"] * up, 0, 1.0)
        out["new"][:, t] = N
        if tp_t is not None:  # endogenous day: vintage cost = sample mean price (approximation)
            cost[NL + t] = float(np.mean(tp_t))
        sh[:, NL + t, :] += N[:, None] * wk
        me[:, NL + t, :] = m[None, :]
        if use_D:  # 新規建ての保証金で余力を消費
            D = D - N * cost[NL + t] * (wk * m[None, :]).sum(1)
        loss = 1 - Pt[:, None] / cost[None, :]
        loss[:, cost == 0] = 0
        ratio = me - loss[:, :, None]
        trig = (ratio < maint) & (sh > 0)
        tsh = np.where(trig, sh, 0.0)
        q_t = theta["q"] if (q_cap is None or t < q_cap[0]) else np.minimum(theta["q"], q_cap[1])
        if use_D:  # 余力が減るほど追証を解消できない
            q_t = q_t * np.clip(D / D0, 0, 1)
        forced_new = tsh * (1 - q_t)[:, None, None]
        if use_D:  # 追証解消の入金額 = 建玉代金 × (維持率+buffer − 現在の維持率)
            need = np.clip(maint + buf - ratio, 0, None) * cost[None, :, None]
            D = D - (tsh * q_t[:, None, None] * need).sum(axis=(1, 2))
        out["trig"][:, t] = tsh.sum(axis=(1, 2))
        sh -= forced_new
        pend[L - 1] += forced_new
        me = np.where(trig, maint + loss[:, :, None] + buf, me)
        tot = sh + pend.sum(axis=0)
        out["S"][:, t] = tot.sum(axis=(1, 2))
        out["A"][:, t] = (tot * cost[None, :, None]).sum(axis=(1, 2))
        out["price"][:, t] = Pt
        out["D"][:, t] = np.clip(D / D0, 0, None)
        prev = Pt
    out["state"] = dict(sh=sh, me=me, pend=pend, cost=cost.copy())
    return out


def calibrate(px, mg, rng):
    m = mg.merge(px[["date", "tp", "close", "ret", "volume"]], on="date", how="left")
    S_obs, A_obs = m.buy_shares.values[1:], m.buy_amount.values[1:]
    args = (m.close.values[1:], m.tp.values[1:], m.ret.values[1:], m.volume.values[1:],
            m.buy_shares[0], m.buy_amount[0], m.close[0])

    def loss(out):
        S = out["S"]
        avg = out["A"] / np.maximum(S, 1)
        return (((S - S_obs) / S_obs) ** 2).sum(1) + (((avg - A_obs / S_obs) / (A_obs / S_obs)) ** 2).sum(1)

    n = P["n_samples"]
    th = sample_theta(rng, n)
    for scale in (None, 0.08, 0.03, 0.01):
        if scale is not None:
            th = sample_theta(rng, n, center=best, scale=scale)
        lo = loss(simulate(th, *args))
        idx = np.argsort(lo)[:300]
        best = take(th, idx)
        best_loss = lo[idx]
    k = P["top_k"]
    ens = take(best, np.arange(k))
    fit = simulate(ens, *args)
    rmse_S = np.sqrt(np.mean(((fit["S"][0] - S_obs) / S_obs) ** 2))
    avg_mod = fit["A"][0] / fit["S"][0]
    rmse_avg = np.sqrt(np.mean(((avg_mod - A_obs / S_obs) / (A_obs / S_obs)) ** 2))
    return ens, best_loss[:k], dict(rmse_S=rmse_S, rmse_avg=rmse_avg, m=m)


def forward_paths(px, mg, ens, scenario_closes, vol_b, adv, sigma, endo_days=0, q_stress=None):
    """Re-run ensemble from calibration start through known prices, then scenario/endogenous days."""
    m = mg.merge(px[["date", "tp", "close", "ret", "volume"]], on="date", how="left")
    last_mg = mg.date.max()
    known = px[px.date > last_mg]
    closes = list(m.close.values[1:]) + list(known.close.values)
    tps = list(m.tp.values[1:]) + list(known.tp.values)
    vols = list(m.volume.values[1:]) + list(known.volume.values)
    prev = closes[-1]
    for c in scenario_closes:
        r = abs(math.log(c / prev))
        closes.append(c)
        tps.append((prev + 2 * c) / 3)
        vols.append(adv * (vol_b[0] + vol_b[1] * r))
        prev = c
    endo_from = None
    if endo_days:
        endo_from = len(closes)
        for _ in range(endo_days):
            closes.append(prev)
            tps.append(prev)
            vols.append(adv)
    closes, tps, vols = map(np.array, (closes, tps, vols))
    rets = np.diff(np.log(np.r_[m.close[0], closes]))
    q_cap = None if q_stress is None else (len(m) - 1 + len(known), q_stress)
    out = simulate(ens, closes, tps, rets, vols, m.buy_shares[0], m.buy_amount[0], m.close[0],
                   endo_from=endo_from, sigma=sigma, adv=adv, q_cap=q_cap)
    out["n_known"] = len(m) - 1 + len(known)
    out["known_dates"] = list(m.date[1:]) + list(known.date)
    return out


def walk_forward(px, mg, n_test=6, seed=11):
    """1-step-ahead out-of-sample test: calibrate on margin data up to d-1, predict d (anchored)."""
    rows = []
    for k in range(n_test, 0, -1):
        mg_tr = mg.iloc[:-k].reset_index(drop=True)
        target = mg.iloc[-k]
        px_tr = px[px.date <= target.date].reset_index(drop=True)
        rng = np.random.default_rng(seed)
        ens, _, _ = calibrate(px_tr[px_tr.date <= mg_tr.date.max()].reset_index(drop=True), mg_tr, rng)
        o = forward_paths(px_tr, mg_tr, ens, [], None, 0, 0)
        i_last = len(mg_tr) - 2
        S = o["S"][:, i_last + 1] + (mg_tr.buy_shares.iloc[-1] - o["S"][:, i_last])
        naive = mg_tr.buy_shares.iloc[-1]
        rows.append(dict(date=target.date, actual=target.buy_shares, pred=np.median(S), lo=q(S, 10), hi=q(S, 90),
                         naive=naive, ret=float(np.log(px_tr.close.iloc[-1] / px_tr.close.iloc[-2]))))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- report helpers
def q(a, p):
    return float(np.percentile(a, p))


def fmt_m(x):
    return f"{x / 1e6:,.2f}M"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", type=float, default=None, help="参考現在値（気配/PTS/海外デリバ等）")
    ap.add_argument("--log", action="store_true", help="予測を predictions_log.csv に追記")
    ap.add_argument("--backtest", type=int, default=0, help="直近N日のウォークフォワード検証を実行")
    a = ap.parse_args()

    px, mg, jsf, hold, ev = load()
    rng = np.random.default_rng(P["seed"])
    asof = px.date.max().date()
    last = px.iloc[-1]
    now = a.now or float(last.close)
    vs = vol_stats(px)
    sigma = vs["sd"]
    adv = float(px.volume.iloc[-21:].mean())
    vol_b = volume_model(px)
    L = []
    w = L.append

    w(f"# キオクシア(285A) 需給・ホルダー行動モデル レポート\n")
    w(f"- 基準日: {asof}（終値 {last.close:,.0f}円） / 参考現在値: {now:,.0f}円（終値比 {now / last.close - 1:+.1%}）")
    w(f"- 生成: {dt.datetime.now():%Y-%m-%d %H:%M}  / 翌営業日の制限値幅 ±{price_limit(last.close):,.0f}円"
      f"（ストップ安 {last.close - price_limit(last.close):,.0f}円）\n")

    upcoming = ev[(ev.date.dt.date > asof) & (ev.date.dt.date <= next_bdays(asof, 5)[-1])]
    if len(upcoming):
        w("**直近5営業日のイベント**: " + " / ".join(f"{r.date:%m/%d} {r.event}" for r in upcoming.itertuples()) + "\n")

    # A
    w("## A. ボラティリティと窓（直近20営業日）")
    w(f"- 日次σ {vs['sd']:.2%}（年率 {vs['sd'] * math.sqrt(252):.0%}）、Parkinson σ {vs['park']:.2%}、平均日次 {vs['mean']:+.2%}")
    w(f"- 窓（夜間）: 合計 {vs['on_sum']:+.1%}・σ {vs['on_sd']:.2%}・下落 {vs['on_neg']}/{vs['n']}日")
    w(f"- 日中: 合計 {vs['in_sum']:+.1%}・σ {vs['in_sd']:.2%}・上昇 {vs['in_pos']}/{vs['n']}日")
    w(f"- 出来高モデル: 出来高/ADV20 = {vol_b[0]:.2f} + {vol_b[1]:.1f}×|日次リターン|  (ADV21 {fmt_m(adv)}株)\n")

    # B
    w("## B. 株主全体の取得コスト分布（回転率減衰モデル）とCGO")
    F = float_shares()
    w(f"- 推定浮動株 {F / 1e9:.3f}bn株、期間出来高 {px.volume.sum() / 1e9:.2f}bn株（浮動株の {px.volume.sum() / F:.2f}倍）")
    coh_mid = None
    for alpha in P["turnover_alpha"]:
        costs, wts, pre, rp = cohort_model(px, alpha)
        tot = wts.sum()
        avg = (costs * wts).sum() / tot
        under = wts[costs > now].sum() / tot
        cgo = now / avg - 1
        w(f"- α={alpha}: 期間前からの保有者 {pre:.0%} / 期間内取得者 {tot:.0%}（平均コスト {avg:,.0f}円、"
          f"現在値で {cgo:+.0%}、含み損 {under:.0%}）")
        if alpha == 0.6:
            coh_mid = (costs, wts, rp)
    costs, wts, rp = coh_mid
    cgo_series = px.close.values / rp - 1
    w(f"- 期間内取得者ベースのCGO（Grinblatt-Han型, α=0.6）: 5日前 {cgo_series[-6]:+.0%} → 直近 {cgo_series[-1]:+.0%}"
      f" → 現在値 {now / rp[-1] - 1:+.0%}")
    w("- 出来高価格帯（典型価格ベース）:")
    for lo in range(int(px.tp.min() // 1000 * 1000), int(px.tp.max() // 1000 * 1000) + 1000, 1000):
        mask = (px.tp >= lo) & (px.tp < lo + 1000)
        v = px.volume[mask].sum()
        if v > 0:
            w(f"  - {lo:,}–{lo + 999:,}円: {fmt_m(v)}株 {'█' * int(v / 2.5e7)}")
    w("")

    # C
    dec = decompose(px, mg)
    w("## C. 信用買い：日次の決済率・新規買い（比例決済分解）")
    w("| 日付 | 終値 | 決済率/日 | 新規(株) | 決済(株) | 純増減 |")
    w("|---|---|---|---|---|---|")
    for r in dec.tail(8).itertuples():
        w(f"| {r.date:%m/%d} | {r.close:,.0f} | {r.closed_rate:.1%} | {fmt_m(r.new)} | {fmt_m(r.closed)} | {r.net / 1e6:+.2f}M |")
    w("")

    # D calibration
    ens, lossv, cal = calibrate(px, mg, rng)
    w("## D. 構造モデル（保証金率クラス × 建値ビンテージ × 追証→強制決済）のキャリブレーション")
    w(f"- 観測 {len(cal['m']) - 1}営業日の信用買い残（株数・平均建値）に適合。上位{P['top_k']}パラメータをアンサンブルに使用")
    w(f"- 最良フィット誤差: 株数 RMSE {cal['rmse_S']:.1%}、平均建値 RMSE {cal['rmse_avg']:.1%}")
    names = dict(w30="保証金30%(フルレバ)比率", w50="保証金50%比率", q="追証時の入金確率", b0="平常の自主決済/日",
                 b1="下落率あたり投げ", b2="上昇率あたり手仕舞い", n0="平常の新規買い/出来高", n1="下落率あたりナンピン",
                 n2="上昇率あたり追随買い", lD0="log10(買い方の追加資金余力・円)")
    w("| パラメータ | 中央値 | 25–75% |")
    w("|---|---|---|")
    for k, nm in names.items():
        w(f"| {nm} | {np.median(ens[k]):.3f} | {q(ens[k], 25):.3f}–{q(ens[k], 75):.3f} |")
    w("")

    D0 = 10 ** ens["lD0"]
    w(f"- 推定『買い方の追加資金余力』（ナンピン＋追証入金に使える資金、{mg.date.iloc[0]:%m/%d}時点）: "
      f"{np.median(D0) / 1e8:,.0f}億円 [25–75%: {q(D0, 25) / 1e8:,.0f}–{q(D0, 75) / 1e8:,.0f}億円]\n")

    # D2 forecast of next published margin balance + scenarios
    last_mg = mg.date.max()
    known = px[px.date > last_mg]
    S_last, A_last = float(mg.buy_shares.iloc[-1]), float(mg.buy_amount.iloc[-1])
    w("## E. 予測（アンサンブル中央値 [10–90%]、最終観測値にアンカー補正）")
    base_out = forward_paths(px, mg, ens, [], vol_b, adv, sigma)
    nk = base_out["n_known"]
    i_last = nk - len(known) - 1          # column of last observed margin date
    offS = S_last - base_out["S"][:, i_last]
    ratA = (A_last / S_last) / (base_out["A"][:, i_last] / base_out["S"][:, i_last])
    w(f"- 最終観測日 {last_mg:%m/%d} のモデル残高 {fmt_m(np.median(base_out['S'][:, i_last]))}株 vs 実績 {fmt_m(S_last)}株 → 差分を補正")
    Dl = base_out["D"][:, i_last]
    Dk = base_out["D"][:, nk - 1]
    w(f"- **買い方の余力の残り**: {last_mg:%m/%d}時点 {np.median(Dl):.0%} [{q(Dl, 10):.0%}–{q(Dl, 90):.0%}] → "
      f"{px.date.iloc[-1]:%m/%d}終値反映後 {np.median(Dk):.0%}（0%に近づくほどナンピン停止・追証の未解消＝投げが増える）")
    preds = []
    for j, d in enumerate(known.date):
        col = nk - len(known) + j
        S = base_out["S"][:, col] + offS
        avg = base_out["A"][:, col] / base_out["S"][:, col] * ratA
        w(f"- **{d:%m/%d}分の信用買い残（未公表→検証可能な予測）**: {fmt_m(np.median(S))}株 "
          f"[{fmt_m(q(S, 10))}–{fmt_m(q(S, 90))}]（前日比 {np.median(S) / S_last - 1:+.1%}）、平均建値 {np.median(avg):,.0f}円 / "
          f"内訳: 強制決済 {fmt_m(np.median(base_out['forced'][:, col]))}・自主決済 {fmt_m(np.median(base_out['volc'][:, col]))}"
          f"・新規 {fmt_m(np.median(base_out['new'][:, col]))}")
        preds.append((d.date(), "buy_shares", np.median(S), q(S, 10), q(S, 90)))
        preds.append((d.date(), "avg_cost", np.median(avg), q(avg, 10), q(avg, 90)))
    jj = jsf.dropna(subset=["net_loan_minus_lend"])
    if len(jj) >= 2 and known.shape[0]:
        jchg = jj.net_loan_minus_lend.iloc[-1] / jj.net_loan_minus_lend.iloc[-2] - 1
        w(f"- 参考: 日証金差引残は同日 {jchg:+.1%}（日証金は全体の1割弱。11/4は日証金-1.8%に対し東証+2.3%と乖離した実績あり）")
    nd = next_bdays(asof, 4)
    scen = sorted({round(last.close - price_limit(last.close)), round(now), 8800, round(last.close), 10000})
    for label, qs in (("ベース（推定パラメータ）", None), ("ストレス（翌営業日から余力ゼロ＝入金もナンピンも停止）", 0.0)):
        w(f"\n**{label}** — 翌営業日（{nd[0]:%m/%d}）終値シナリオ別（その後横ばい）:")
        w(f"| {nd[0]:%m/%d}終値 | 追証発生 | 強制 {nd[0]:%m/%d} | 強制 {nd[1]:%m/%d} | 強制 {nd[2]:%m/%d} | 強制3日計 [10–90%] (ADV比) | 自主決済 {nd[0]:%m/%d} | 新規 {nd[0]:%m/%d} | {nd[0]:%m/%d}末残高 | 余力残({nd[2]:%m/%d}) |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for c in scen:
            o = forward_paths(px, mg, ens, [c, c, c], vol_b, adv, sigma, q_stress=qs)
            k0 = o["n_known"]
            fs = o["forced"][:, k0:k0 + 3]
            tot3 = fs.sum(1)
            S = o["S"][:, k0] + (S_last - o["S"][:, i_last])
            w(f"| {c:,.0f} | {fmt_m(np.median(o['trig'][:, k0]))} | {fmt_m(np.median(fs[:, 0]))} | {fmt_m(np.median(fs[:, 1]))} | "
              f"{fmt_m(np.median(fs[:, 2]))} | {fmt_m(np.median(tot3))} [{fmt_m(q(tot3, 10))}–{fmt_m(q(tot3, 90))}] ({np.median(tot3) / adv:.2f}日) | "
              f"{fmt_m(np.median(o['volc'][:, k0]))} | {fmt_m(np.median(o['new'][:, k0]))} | {fmt_m(np.median(S))} | "
              f"{np.median(o['D'][:, k0 + 2]):.0%} |")
    w("")

    # E3 short-term (5 trading days) path scenarios
    H5 = 5
    d5 = next_bdays(asof, H5)
    w(f"### E3. 5営業日（〜{d5[-1]:%m/%d}）の経路シナリオ（初日={now:,.0f}円から幾何補間）")
    w("| 経路 | 5日後残高 | 強制決済 累計 | 自主決済(投げ・戻り売り) 累計 | 新規(ナンピン) 累計 | 余力残 |")
    w("|---|---|---|---|---|---|")
    for lab, tgt in (("続落→7,000", 7000), ("横ばい", now), ("窓埋め→9,300", 9300), ("反発→10,000", 10000)):
        path = [now] + [now * (tgt / now) ** ((i + 1) / (H5 - 1)) for i in range(H5 - 1)]
        o = forward_paths(px, mg, ens, path, vol_b, adv, sigma)
        k0 = o["n_known"]
        S = o["S"][:, -1] + (S_last - o["S"][:, i_last])
        w(f"| {lab} | {fmt_m(np.median(S))} | {fmt_m(np.median(o['forced'][:, k0:].sum(1)))} | "
          f"{fmt_m(np.median(o['volc'][:, k0:].sum(1)))} | {fmt_m(np.median(o['new'][:, k0:].sum(1)))} | "
          f"{np.median(o['D'][:, -1]):.0%} |")
    w("")

    if a.backtest:
        bt = walk_forward(px, mg, a.backtest)
        w(f"### E2. ウォークフォワード検証（1日先、直近{a.backtest}日、アウトオブサンプル）")
        w("| 日付 | 当日リターン | 実績 | 予測 [10–90%] | 誤差 | 前日横ばい予測の誤差 |")
        w("|---|---|---|---|---|---|")
        for r in bt.itertuples():
            w(f"| {r.date:%m/%d} | {r.ret:+.1%} | {fmt_m(r.actual)} | {fmt_m(r.pred)} [{fmt_m(r.lo)}–{fmt_m(r.hi)}] | "
              f"{r.pred / r.actual - 1:+.1%} | {r.naive / r.actual - 1:+.1%} |")
        mae = np.mean(np.abs(bt.pred / bt.actual - 1))
        mae_n = np.mean(np.abs(bt.naive / bt.actual - 1))
        hit = np.mean(np.sign(bt.pred - bt.naive) == np.sign(bt.actual - bt.naive))
        w(f"- MAE: モデル {mae:.1%} / 横ばい {mae_n:.1%}、増減方向の的中率 {hit:.0%}\n")

    # F cascade
    w("## F. 追証カスケード（翌営業日終値→強制決済の平方根インパクトのみで内生的に価格決定、他フロー中立）")
    w("| 翌営業日終値 | ベース着地(3営業日後) | 追加下落 | 余力ゼロ時の着地 | 追加下落 |")
    w("|---|---|---|---|---|")
    for c in [7000, 7500, 7824, 8100, 8500, 9000]:
        res = []
        for qs in (None, 0.0):
            o = forward_paths(px, mg, ens, [c], vol_b, adv, sigma, endo_days=3, q_stress=qs)
            res.append(np.median(o["price"][:, -1]))
        w(f"| {c:,} | {res[0]:,.0f} | {res[0] / c - 1:+.1%} | {res[1]:,.0f} | {res[1] / c - 1:+.1%} |")
    w("")

    # G overhead supply ladder
    st = base_out["state"]
    shv = np.median(st["sh"].sum(axis=2) + st["pend"].sum(axis=(0, 3)), axis=0)
    cv = st["cost"]
    w("## G. 戻り売り（やれやれ売り）ラダー：価格帯ごとの想定売り供給")
    w(f"- 信用：建値±{P['be_band']:.0%}到達で{P['be_sell_margin']:.0%}が手仕舞い / 現物（期間内取得者, α=0.6）：同{P['be_sell_cash']:.0%}と仮定")
    w("| 価格帯 | 信用(株) | 現物(株) | 合計 | ADV比 | 1日で吸収時の価格インパクト |")
    w("|---|---|---|---|---|---|")
    cum = 0.0
    for lo in range(int(now // 500 * 500), 16001, 500):
        hi = lo + 500
        mar = shv[(cv >= lo) & (cv < hi)].sum() * P["be_sell_margin"]
        cash = wts[(costs >= lo) & (costs < hi)].sum() * F * P["be_sell_cash"]
        tot = mar + cash
        cum += tot
        if tot <= 0:
            continue
        imp = P["impact_Y"] * sigma * math.sqrt(tot / adv)
        w(f"| {lo:,}–{hi - 1:,} | {fmt_m(mar)} | {fmt_m(cash)} | {fmt_m(tot)} | {tot / adv:.2f}日 | -{imp:.1%} |")
    w("")

    # H flows: Toshiba, JPM, TOPIX
    w("## H. 大口フロー")
    ts = hold[(hold.entity == "Toshiba") & (hold.kind == "market_sale")].merge(
        px[["date", "volume"]], left_on="calc_date", right_on="date", how="left")
    if len(ts):
        part = (ts.shares / ts.volume)
        w("- 東芝の市場売却の出来高参加率: " + ", ".join(f"{d:%m/%d} {p:.1%}" for d, p in zip(ts.calc_date, part)))
        pm = float(part.mean())
        thr = P["shares_total"] * 0.01
        w(f"- 次の変更報告（1%減=約{fmt_m(thr)}株）までの所要: 参加率{pm:.1%}×ADVで約{thr / (pm * adv):.1f}営業日"
          f"（報告は5営業日以内にEDINET提出）/ 同ペースなら1日あたり約{fmt_m(pm * adv)}株の売り")
    jp = hold[(hold.kind == "short_report")].sort_values("calc_date").tail(1)
    if len(jp):
        r = jp.iloc[0]
        w(f"- 最新の大量空売り報告: {r.entity} {r.pct:.2f}%（{fmt_m(r.shares)}株, {r.calc_date:%m/%d}計算）= ADVの{r.shares / adv:.2f}日分")
    add = P["shares_total"] * P["topix_ffw_step"]
    topix_date = ev[ev.event.str.contains("TOPIX")].date.min()
    for s in P["passive_share"]:
        d = add * s
        imp = P["impact_Y"] * sigma * math.sqrt(d / adv)
        w(f"- TOPIX第2段階（{topix_date:%m/%d}大引け）パッシブ保有率{s:.0%}仮定: {fmt_m(d)}株 = ADV{d / adv:.2f}日・"
          f"信用買い残の{d / mg.buy_shares.iloc[-1]:.2f}倍・{d * now / 1e12:.2f}兆円・インパクト +{imp:.1%}")
    w("")

    # I capitulation detector
    w("## I. セリングクライマックス判定（直近6日）")
    w("| 日付 | 出来高/ADV20 | 終値位置 | 下ヒゲ | 翌日安値維持 | 信用純増減 |")
    w("|---|---|---|---|---|---|")
    netmap = dict(zip(dec.date, dec.net))
    tail = px.tail(7).reset_index(drop=True)
    for i in range(1, len(tail)):
        r = tail.iloc[i]
        rng_ = r.high - r.low
        pos = (r.close - r.low) / rng_
        lw = (min(r.open, r.close) - r.low) / rng_
        hold_next = "—" if i == len(tail) - 1 else ("○" if tail.low[i + 1] > r.low else "×")
        net = netmap.get(r.date)
        w(f"| {r.date:%m/%d} | {r.volume / r.adv20:.2f} | {pos:.0%} | {lw:.0%} | {hold_next} | "
          f"{'' if net is None else f'{net / 1e6:+.2f}M'} |")
    w("- 条件: 出来高≥1.5×ADV20 かつ 終値位置≥60% かつ 翌日安値維持 かつ 信用買い残が2-3日連続純減\n")

    # J Monte Carlo
    w("## J. 到達確率（20日リターンのブートストラップ、ドリフト除去、1・3・5営業日）")
    hist = px.ret.dropna().values[-20:]
    hist = hist - hist.mean()
    horizon = 5
    sims = rng.choice(hist, size=(50000, horizon))
    paths = now * np.exp(np.cumsum(sims, axis=1))
    mx, mn = paths.max(1), paths.min(1)
    levels_up = [9300, 10000, 10700]
    levels_dn = [7500, 7000, 6324]
    for hz in (1, 3, 5):
        pm_, pn_ = paths[:, :hz].max(1), paths[:, :hz].min(1)
        w(f"- {hz}営業日: " + ", ".join(f"↑{x:,} {np.mean(pm_ >= x):.0%}" for x in levels_up) + " / " +
          ", ".join(f"↓{x:,} {np.mean(pn_ <= x):.0%}" for x in levels_dn))
    w("")

    # JSF
    j = jsf.dropna(subset=["net_loan_minus_lend"]).tail(6)
    if len(j):
        w("## K. 日証金（貸借取引）")
        peak = j.net_loan_minus_lend.max()
        lastj = j.iloc[-1]
        w(f"- 差引残 {fmt_m(lastj.net_loan_minus_lend)}株（ピーク比 {lastj.net_loan_minus_lend / peak - 1:+.1%}）、"
          f"最高料率 {lastj.max_fee_yen}円/日、逆日歩 {'なし' if pd.isna(lastj.fee_yen) else lastj.fee_yen}")
        w(f"- 投げ一巡の目安（ピーク-10%）: {fmt_m(peak * 0.9)}株\n")

    # predictions log
    logp = DATA / "predictions_log.csv"
    lg = pd.read_csv(logp, dtype=str)
    actual_map = {(d.date().isoformat(), "buy_shares"): s for d, s in zip(mg.date, mg.buy_shares)}
    actual_map.update({(d.date().isoformat(), "avg_cost"): A / S for d, S, A in zip(mg.date, mg.buy_shares, mg.buy_amount)})
    if len(lg):
        lg["actual"] = [f"{actual_map[(t, mt)]:.0f}" if (t, mt) in actual_map else (ac if isinstance(ac, str) else "")
                        for t, mt, ac in zip(lg.target_date, lg.metric, lg.actual)]
        w("## L. 過去予測の検証")
        for r in lg.itertuples():
            if r.actual:
                err = float(r.actual) / float(r.predicted_median) - 1
                w(f"- {r.made_on}→{r.target_date} {r.metric}: 予測 {float(r.predicted_median):,.0f} / 実績 {float(r.actual):,.0f}（誤差 {err:+.1%}）")
        w("")
    if a.log:
        rows = [dict(made_on=dt.date.today().isoformat(), target_date=t.isoformat(), metric=mt,
                     predicted_median=f"{md:.0f}", predicted_low=f"{lo:.0f}", predicted_high=f"{hi:.0f}", actual="",
                     note=f"asof {asof}, now {now:.0f}") for t, mt, md, lo, hi in preds]
        lg = pd.concat([lg, pd.DataFrame(rows)], ignore_index=True)
        lg = lg.drop_duplicates(subset=["made_on", "target_date", "metric"], keep="last")
    if len(lg):
        lg.to_csv(logp, index=False)

    w("---\n*モデル推計であり投資助言ではない。前提はREADME参照。*")
    text = "\n".join(L)
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / f"{asof}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
