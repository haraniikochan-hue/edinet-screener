"""株主全体の取得コスト分布（Grinblatt–Han 型の回転率減衰）、CGO、苦痛指数、底値類似度、戻り売りラダー."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import P
from .data import float_shares


def cohort_history(px: pd.DataFrame, alpha: float | None = None) -> dict:
    """全履歴で、毎日 出来高×α/浮動株 の保有者が当日の典型価格で入れ替わるとみなす.
    返り値: 日次の参照価格 RP、CGO=(P−RP)/P、含み損の保有者比率、最終日のコスト分布."""
    alpha = alpha or P["turnover_alpha"]
    F = float_shares()
    costs, w = [], []
    rp, under, legacy = np.zeros(len(px)), np.zeros(len(px)), np.zeros(len(px))
    pre = 1.0   # 上場前からの保有者（初日に初値で取得したとみなす）
    for i, row in enumerate(px.itertuples()):
        f = min(alpha * row.volume / F, 0.95)
        pre *= 1 - f
        w = [x * (1 - f) for x in w]
        costs.append(row.tp)
        w.append(f)
        wa = np.array(w)
        ca = np.array(costs)
        tot = wa.sum() + pre
        c0 = px.tp.iloc[0]
        rp[i] = ((ca * wa).sum() + pre * c0) / tot
        under[i] = (wa[ca > row.close].sum() + (pre if c0 > row.close else 0)) / tot
        legacy[i] = pre / tot
    cgo = (px.close.values - rp) / px.close.values
    return dict(rp=rp, cgo=cgo, underwater=under, legacy_share=legacy, costs=np.array(costs), weights=np.array(w), pre=pre)


def pain_index(px: pd.DataFrame, coh: dict) -> pd.DataFrame:
    """苦痛指数：CGO(−)、5日・20日リターン(−)、含み損比率(+)、実現ボラ20(+)、高値からの日数(+) を z 化して平均.
    値が大きいほど苦しい。全履歴に対するパーセンタイルも返す."""
    d = pd.DataFrame(dict(date=px.date, close=px.close))
    d["cgo"] = coh["cgo"]
    d["under"] = coh["underwater"]
    d["ret5"] = np.log(px.close / px.close.shift(5))
    d["ret20"] = np.log(px.close / px.close.shift(20))
    d["rv20"] = px.ret.rolling(20).std()
    d["dd"] = px.close / px.close.cummax() - 1
    comp = pd.DataFrame(dict(cgo=-d.cgo, under=d.under, ret5=-d.ret5, ret20=-d.ret20, rv20=d.rv20, dd=-d.dd))
    z = (comp - comp.mean()) / comp.std()
    d["pain"] = z.mean(axis=1)
    d["pain_pct"] = d.pain.rank(pct=True)
    return d


def bottom_similarity(px: pd.DataFrame, pain: pd.DataFrame, bottoms: pd.DataFrame, k: int = 25, near: int = 2) -> dict:
    """kNN：特徴量（ret5, ret20, 出来高/ADV, 終値位置, CGO, 含み損比率）の標準化距離で、
    直近日に近い過去 k 日のうち『局所底の±near日』だった比率を返す（ノンパラメトリックな底値類似度）."""
    d = px.reset_index(drop=True)
    feat = pd.DataFrame(dict(
        ret5=np.log(d.close / d.close.shift(5)), ret20=np.log(d.close / d.close.shift(20)),
        vol=d.volume / d.adv20, pos=(d.close - d.low) / np.maximum(d.high - d.low, 1),
        cgo=pain.cgo.values, under=pain.under.values))
    ok = feat.notna().all(axis=1).values
    X = feat.values
    mu, sd = np.nanmean(X[ok], 0), np.nanstd(X[ok], 0)
    Z = (X - mu) / sd
    is_bottom = np.zeros(len(d), bool)
    bidx = d.index[d.date.isin(bottoms.date)].values
    for b in bidx:
        is_bottom[max(0, b - near): b + near + 1] = True
    cur = Z[-1]
    cand = np.where(ok)[0]
    cand = cand[cand < len(d) - 10]   # 直近10日は底かどうか未確定なので除外
    dist = np.sqrt(((Z[cand] - cur) ** 2).sum(1))
    nn = cand[np.argsort(dist)[:k]]
    share = is_bottom[nn].mean()
    base = is_bottom[cand].mean()
    return dict(share=float(share), base=float(base), lift=float(share / base) if base > 0 else np.nan,
                nn_dates=list(d.date.values[nn[:8]]), features=dict(zip(feat.columns, X[-1])),
                bottoms_feat=feat.iloc[bidx].assign(date=d.date.values[bidx]))


def supply_ladder(now: float, coh: dict, vint_sh: np.ndarray, vint_cost: np.ndarray, w: np.ndarray, adv: float, sigma: float,
                  lo: float | None = None, hi: float | None = None, step: int = 1000) -> pd.DataFrame:
    """価格帯ごとの『やれやれ売り』供給：信用は建値±band で be_sell_margin、現物は be_sell_cash が手放すと仮定."""
    F = float_shares()
    lo = lo or int(now // step * step)
    hi = hi or int(min(now * 1.8, 20000) // step * step)
    rows = []
    for a in range(lo, hi, step):
        b = a + step
        mar = np.average(((vint_cost >= a) & (vint_cost < b)) * vint_sh, axis=0, weights=w).sum() * P["be_sell_margin"]
        cash = coh["weights"][(coh["costs"] >= a) & (coh["costs"] < b)].sum() * F * P["be_sell_cash"]
        tot = mar + cash
        if tot <= 0:
            continue
        imp = P["impact_Y"] * sigma * np.sqrt(tot / adv)
        rows.append(dict(lo=a, hi=b - 1, margin=mar, cash=cash, total=tot, adv_days=tot / adv, impact=imp))
    return pd.DataFrame(rows)
