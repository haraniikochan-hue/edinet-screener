"""リターン生成エンジン：EWMAボラ、窓／日中分解、値幅制限、イベントスタディ、ピア条件付け."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .config import P, price_limit_vec


# ------------------------------------------------------------------ EWMA
def ewma_var(r: np.ndarray, lam: float, init: float | None = None) -> np.ndarray:
    """σ²_t = λσ²_{t-1} + (1-λ) r²_{t-1}  （t 日のリターンを見る前の予測分散）."""
    r = np.asarray(r, float)
    v = np.empty(len(r))
    v[0] = init if init is not None else np.mean(r[: min(20, len(r))] ** 2)
    for t in range(1, len(r)):
        v[t] = lam * v[t - 1] + (1 - lam) * r[t - 1] ** 2
    return v


def fit_lambda(r: np.ndarray, grid=np.arange(0.80, 0.995, 0.01)) -> float:
    """ガウス擬似尤度でλを選ぶ（最初の20日は除外）."""
    best, bl = None, -np.inf
    for lam in grid:
        v = ewma_var(r, lam)[20:]
        ll = -0.5 * np.sum(np.log(v) + r[20:] ** 2 / v)
        if ll > bl:
            bl, best = ll, lam
    return float(best)


class ReturnEngine:
    """窓（夜間）と日中を別々の EWMA ボラで標準化し、残差ペアをブートストラップする."""

    def __init__(self, px: pd.DataFrame, window: int | None = None):
        d = px.dropna(subset=["ret", "gap", "intra"]).reset_index(drop=True)
        self.dates = d.date.values
        self.ret, self.gap, self.intra = d.ret.values, d.gap.values, d.intra.values
        lam = P["ewma_lambda"]
        self.lam = lam if lam else fit_lambda(self.ret)
        self.lam_g = lam if lam else fit_lambda(self.gap)
        self.lam_i = lam if lam else fit_lambda(self.intra)
        self.var = ewma_var(self.ret, self.lam)
        self.var_g = ewma_var(self.gap, self.lam_g)
        self.var_i = ewma_var(self.intra, self.lam_i)
        W = window or P["resid_window"]
        self.z = (self.ret / np.sqrt(self.var))[-W:]
        self.zg = (self.gap / np.sqrt(self.var_g))[-W:]
        self.zi = (self.intra / np.sqrt(self.var_i))[-W:]
        # 翌営業日の予測分散（直近の実績を取り込む）
        self.var_next = self.lam * self.var[-1] + (1 - self.lam) * self.ret[-1] ** 2
        self.var_g_next = self.lam_g * self.var_g[-1] + (1 - self.lam_g) * self.gap[-1] ** 2
        self.var_i_next = self.lam_i * self.var_i[-1] + (1 - self.lam_i) * self.intra[-1] ** 2

    @property
    def sigma_next(self):
        return math.sqrt(self.var_next)

    def sample_pairs(self, rng, n, h):
        """標準化残差 (z_gap, z_intra) のペアを同じ日から同時にブートストラップ（依存を保つ）."""
        idx = rng.integers(0, len(self.zg), size=(n, h))
        return self.zg[idx], self.zi[idx]

    # ---- 条件付き（マルコフ）ブートストラップ
    def _bins(self):
        if not hasattr(self, "_bin_cache"):
            W = len(self.zg)
            zprev = (self.ret / np.sqrt(self.var))[-W - 1:-1]       # 前日の標準化リターン
            self._zprev = zprev
            self._qg = np.quantile(zprev, [0.2, 0.4, 0.6, 0.8])
            self._qi = np.quantile(self.zg, [0.2, 0.4, 0.6, 0.8])
            self._bin_prev = np.searchsorted(self._qg, zprev)
            self._bin_gap = np.searchsorted(self._qi, self.zg)
            self._bin_cache = True

    def sample_gap_given_prev(self, rng, zprev_sim):
        """前日の標準化リターンの分位ビンから z_gap を引く."""
        self._bins()
        b = np.searchsorted(self._qg, zprev_sim)
        out = np.empty(len(zprev_sim))
        for k in range(5):
            m = b == k
            pool = self.zg[self._bin_prev == k]
            if m.any():
                out[m] = rng.choice(pool, m.sum())
        return out

    def sample_intra_given_gap(self, rng, zg_sim):
        """実現した（インパクト・シフト込みの）標準化窓の分位ビンから z_intra を引く."""
        self._bins()
        b = np.searchsorted(self._qi, zg_sim)
        out = np.empty(len(zg_sim))
        for k in range(5):
            m = b == k
            pool = self.zi[self._bin_gap == k]
            if m.any():
                out[m] = rng.choice(pool, m.sum())
        return out

    def conditional_table(self):
        """診断：前日リターン分位 → 翌日窓の中央値、窓分位 → 日中の中央値・勝率."""
        self._bins()
        rows = []
        for k in range(5):
            g = self.zg[self._bin_prev == k] * np.sqrt(self.var_g_next)
            i = self.zi[self._bin_gap == k] * np.sqrt(self.var_i_next)
            rows.append(dict(bin=k, gap_med=float(np.median(g)), gap_pos=float((g > 0).mean()),
                             intra_med=float(np.median(i)), intra_pos=float((i > 0).mean()), n=int((self._bin_prev == k).sum())))
        return rows


# ------------------------------------------------------------------ gap model on peers
def fit_gap_model(px: pd.DataFrame, al: pd.DataFrame, n: int = 120) -> dict:
    """窓 = a + b·SOX_prev + c·MU_prev（直近 n 日、OLS）. 返り値は係数と残差σ."""
    d = px[["date", "gap", "intra", "ret"]].merge(al, on="date").dropna(subset=["gap", "SOX_prev", "MU_prev"]).tail(n)
    X = np.c_[np.ones(len(d)), d.SOX_prev.values, d.MU_prev.values]
    b, *_ = np.linalg.lstsq(X, d.gap.values, rcond=None)
    resid = d.gap.values - X @ b
    r2 = 1 - resid.var() / d.gap.var()
    # 日中は同日の SK hynix と前夜の SOX で説明を試みる（参考）
    d2 = d.dropna(subset=["SKH_same"])
    X2 = np.c_[np.ones(len(d2)), d2.SKH_same.values, d2.SOX_prev.values]
    b2, *_ = np.linalg.lstsq(X2, d2.intra.values, rcond=None)
    r2_2 = 1 - (d2.intra.values - X2 @ b2).var() / d2.intra.var()
    # 日次リターンのピアβ（SOX_prev, SKH_same）と残差
    X3 = np.c_[np.ones(len(d2)), d2.SOX_prev.values, d2.SKH_same.values]
    b3, *_ = np.linalg.lstsq(X3, d2.ret.values, rcond=None)
    res3 = pd.Series(d2.ret.values - X3 @ b3, index=d2.date.values)
    return dict(gap_coef=b, gap_resid_sd=float(resid.std(ddof=3)), gap_r2=float(r2), n=len(d),
                intra_coef=b2, intra_r2=float(r2_2), ret_coef=b3, ret_resid=res3,
                last=d.iloc[-1][["date", "SOX_prev", "MU_prev"]].to_dict())


# ------------------------------------------------------------------ event studies
def _fwd(c: np.ndarray, i: int, k: int):
    return c[i + k] / c[i] - 1 if i + k < len(c) else np.nan


def event_study(px: pd.DataFrame) -> dict:
    d = px.reset_index(drop=True)
    c, o, h, l = d.close.values, d.open.values, d.high.values, d.low.values
    r, g, it = d.ret.values, d.gap.values, d.intra.values
    out = {}

    def summarize(idx, label):
        if len(idx) == 0:
            out[label] = None
            return
        rows = []
        for i in idx:
            if i + 1 >= len(d):
                continue
            nxt_max5 = (h[i + 1:i + 6].max() / c[i] - 1) if i + 1 < len(d) else np.nan
            nxt_min5 = (l[i + 1:i + 6].min() / c[i] - 1) if i + 1 < len(d) else np.nan
            rows.append(dict(date=d.date[i], ret=r[i], gap1=g[i + 1], intra1=it[i + 1], c1=_fwd(c, i, 1),
                             c3=_fwd(c, i, 3), c5=_fwd(c, i, 5), max5=nxt_max5, min5=nxt_min5))
        out[label] = pd.DataFrame(rows)

    summarize(np.where(r <= math.log(0.90))[0], "day_le_m10")
    summarize(np.where(r <= math.log(0.85))[0], "day_le_m15")
    two = np.where((r[1:] + r[:-1]) <= math.log(0.80))[0] + 1
    summarize(two, "two_day_le_m20")
    summarize(np.where(d.lock_dn.values)[0], "lock_dn")
    summarize(np.where(d.touch_dn.values & ~d.lock_dn.values)[0], "touch_dn_not_lock")
    # 窓開け後の日中（ギャップダウン ≥ 5%）
    gd = np.where(g <= math.log(0.95))[0]
    out["gapdown5_intra"] = pd.DataFrame(dict(date=d.date.values[gd], gap=g[gd], intra=it[gd], ret=r[gd]))
    gu = np.where(g >= math.log(1.05))[0]
    out["gapup5_intra"] = pd.DataFrame(dict(date=d.date.values[gu], gap=g[gu], intra=it[gu], ret=r[gu]))
    # 全日の窓→日中の相関（直近120日）
    mask = ~np.isnan(g) & ~np.isnan(it)
    gg, ii = g[mask][-120:], it[mask][-120:]
    out["gap_intra_corr120"] = float(np.corrcoef(gg, ii)[0, 1])
    out["intra_pos_share120"] = float(np.mean(ii > 0))
    out["gap_neg_share120"] = float(np.mean(gg < 0))
    return out


def local_bottoms(px: pd.DataFrame, win: int = 10, fwd: float = 0.15) -> pd.DataFrame:
    """局所底：前後 win 日の最安終値 かつ その後 win 日以内に +fwd 以上."""
    d = px.reset_index(drop=True)
    c = d.close.values
    rows = []
    for i in range(win, len(d) - win):
        if c[i] == c[i - win:i + win + 1].min() and c[i + 1:i + win + 1].max() / c[i] - 1 >= fwd:
            rows.append(dict(date=d.date[i], close=c[i], ret5=c[i] / c[i - 5] - 1, ret20=c[i] / c[i - 20] - 1 if i >= 20 else np.nan,
                             vol_adv=d.volume[i] / d.adv20[i] if d.adv20[i] > 0 else np.nan,
                             pos=(c[i] - d.low[i]) / max(d.high[i] - d.low[i], 1),
                             fwd10=c[i + 1:i + win + 1].max() / c[i] - 1))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ limit-aware path sampler (exogenous only)
def simulate_exo_paths(eng: ReturnEngine, rng, n: int, h: int, p0: float, gap_shift0: float = 0.0,
                       gap_sd_scale0: float = 1.0):
    """価格インパクトなしの経路（値幅制限つき）. 返り値: open (n,h), close (n,h), locked (n,h)."""
    zg, zi = eng.sample_pairs(rng, n, h)
    vg, vi = np.full(n, eng.var_g_next), np.full(n, eng.var_i_next)
    prev = np.full(n, p0, float)
    O = np.zeros((n, h)); C = np.zeros((n, h)); LK = np.zeros((n, h), bool)
    for t in range(h):
        lim = price_limit_vec(prev)
        g = np.sqrt(vg) * zg[:, t] * (gap_sd_scale0 if t == 0 else 1.0) + (gap_shift0 if t == 0 else 0.0)
        o = np.clip(prev * np.exp(g), prev - lim, prev + lim)
        c = np.clip(o * np.exp(np.sqrt(vi) * zi[:, t]), prev - lim, prev + lim)
        LK[:, t] = c <= prev - lim + 0.5
        O[:, t], C[:, t] = o, c
        rg, ri = np.log(o / prev), np.log(c / o)
        vg = eng.lam_g * vg + (1 - eng.lam_g) * rg ** 2
        vi = eng.lam_i * vi + (1 - eng.lam_i) * ri ** 2
        prev = c
    return O, C, LK


# ------------------------------------------------------------------ weekly margin elasticity (98 weeks)
def weekly_margin_stats(mgw: pd.DataFrame, bottoms: pd.DataFrame | None = None) -> dict:
    d = mgw.dropna(subset=["buy_shares"]).copy()
    d["dlogS"] = np.log(d.buy_shares).diff()
    d["r"] = np.log(d.close).diff()
    d = d.dropna()
    X = np.c_[np.ones(len(d)), d.r.values]
    b, *_ = np.linalg.lstsq(X, d.dlogS.values, rcond=None)
    resid = d.dlogS.values - X @ b
    r2 = 1 - resid.var() / d.dlogS.var()
    # 直近8週 vs 全期間の弾力性
    d8 = d.tail(8)
    X8 = np.c_[np.ones(len(d8)), d8.r.values]
    b8, *_ = np.linalg.lstsq(X8, d8.dlogS.values, rcond=None)
    # 底値の前後での信用買い残の変化（週次）
    around = []
    if bottoms is not None and len(bottoms):
        for bd in bottoms.date:
            w = d[(d.date >= bd - pd.Timedelta(days=21)) & (d.date <= bd + pd.Timedelta(days=21))]
            pre = w[w.date <= bd].dlogS.sum()
            post = w[w.date > bd].dlogS.sum()
            around.append(dict(bottom=bd.date(), pre3w=float(pre), post3w=float(post)))
    return dict(beta=float(b[1]), alpha=float(b[0]), r2=float(r2), n=len(d), beta8=float(b8[1]),
                around=pd.DataFrame(around), last=d.tail(6)[["date", "close", "buy_shares", "dlogS", "r"]])
