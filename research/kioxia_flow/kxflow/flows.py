"""大口フロー：東芝の売却と次回報告のタイミング、寄付の需給インバランス、パッシブ需要."""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

from .config import P, next_bdays


def toshiba_timing(px: pd.DataFrame, hold: pd.DataFrame, adv: float) -> dict:
    """直近の変更報告（計算日・保有比率）から、次の1%減の報告がいつ出うるかを参加率別に推計."""
    rep = hold[(hold.entity == "Toshiba") & (hold.kind == "major_holder")].dropna(subset=["pct"]).sort_values("calc_date").iloc[-1]
    thr = P["shares_total"] * 0.01
    after = px[px.date > rep.calc_date]
    sales = hold[(hold.entity == "Toshiba") & (hold.kind == "market_sale")].merge(px[["date", "volume"]], left_on="calc_date", right_on="date")
    part_obs = (sales.shares / sales.volume).values if len(sales) else np.array(P["toshiba_participation"])
    rows = []
    for u in sorted(set(list(P["toshiba_participation"]) + [float(part_obs.mean())])):
        cum = (after.volume * u).cumsum()
        hit = after[cum >= thr]
        if len(hit):
            cross = hit.date.iloc[0].date()
            due = next_bdays(cross, 5)[-1]
            rows.append(dict(rate=u, sold=float(cum.iloc[-1]), cross=cross, due=due, status="到達済み（報告は5営業日以内）"))
        else:
            remain = thr - float(cum.iloc[-1]) if len(cum) else thr
            rows.append(dict(rate=u, sold=float(cum.iloc[-1]) if len(cum) else 0.0, cross=None, due=None,
                             status=f"未到達（あと{remain / 1e6:.1f}M株＝ADV×{u:.1%}で約{remain / (u * adv):.0f}日）"))
    return dict(last_pct=float(rep.pct), last_date=rep.calc_date.date(), shares=float(rep.shares), threshold=thr,
                part_obs=part_obs, rows=pd.DataFrame(rows), days_since=len(after))


def opening_imbalance(due_forced, due_cure, w, adv: float, toshiba_rate: float, open_share: float = 0.12) -> dict:
    """翌営業日の寄付：予定売り（強制＋一部売却）＋東芝の推定売り vs 寄付の典型出来高（ADV×open_share）."""
    q_f = np.average(due_forced, weights=w)
    q_c = np.average(due_cure, weights=w)
    open_vol = adv * open_share
    tosh = toshiba_rate * open_vol
    tot = q_f + q_c + tosh
    return dict(forced=q_f, cure=q_c, toshiba=tosh, total=tot, open_vol=open_vol, ratio=tot / open_vol)


def passive_demand(adv: float, price: float, margin_last: float, sigma: float) -> pd.DataFrame:
    add = P["shares_total"] * P["topix_ffw_step"]
    rows = []
    for s in P["passive_share"]:
        d = add * s
        rows.append(dict(share=s, shares=d, adv_days=d / adv, x_margin=d / margin_last, yen=d * price,
                         impact=P["impact_Y"] * sigma * np.sqrt(d / adv)))
    return pd.DataFrame(rows)


def sample_toshiba(rng, n, V, p_active=0.7, lo=0.02, hi=0.12):
    """MC 用：当日の東芝売り株数（参加率 U(lo,hi)×出来高、確率 p_active で売る）."""
    act = rng.random(n) < p_active
    u = rng.uniform(lo, hi, n)
    return np.where(act, u * V, 0.0)
