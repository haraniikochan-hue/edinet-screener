"""データ読み込みと整形."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import DATA, P


def float_shares() -> float:
    return P["shares_total"] - P["treasury"] - P["toshiba_shares"] - P["shares_total"] * P["skhynix_pct"]


def load_all() -> dict:
    px = pd.read_csv(DATA / "prices.csv", parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    px["tp"] = (px.high + px.low + px.close) / 3
    px["ret"] = np.log(px.close).diff()
    px["gap"] = np.log(px.open / px.close.shift(1))
    px["intra"] = np.log(px.close / px.open)
    px["adv20"] = px.volume.rolling(20, min_periods=5).mean().shift(1)
    prev = px.close.shift(1)
    from .config import price_limit_vec
    lim = price_limit_vec(prev.fillna(px.close))
    px["lim"] = lim
    px["lock_dn"] = (px.close <= prev - lim + 0.5) & (px.high <= prev - lim + 0.5)   # 終日張り付き
    px["touch_dn"] = px.low <= prev - lim + 0.5
    px["lock_up"] = (px.close >= prev + lim - 0.5) & (px.low >= prev + lim - 0.5)
    px["touch_up"] = px.high >= prev + lim - 0.5

    mg = pd.read_csv(DATA / "margin_daily.csv", parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    mgw = pd.read_csv(DATA / "margin_weekly.csv", parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    jsf = pd.read_csv(DATA / "jsf_daily.csv", parse_dates=["trade_date"]).sort_values("trade_date").reset_index(drop=True)
    hold = pd.read_csv(DATA / "holders.csv", parse_dates=["calc_date"])
    ev = pd.read_csv(DATA / "events.csv", parse_dates=["date"])
    peers = pd.read_csv(DATA / "peers.csv", parse_dates=["date"])
    return dict(px=px, mg=mg, mgw=mgw, jsf=jsf, hold=hold, ev=ev, peers=peers)


def align_peers(px: pd.DataFrame, peers: pd.DataFrame) -> pd.DataFrame:
    """東京の日付 t に対して、米国は t より前の最新セッション、韓国・日本は同日のリターンを付ける."""
    out = px[["date"]].copy()
    for tk in sorted(peers.ticker.unique()):
        d = peers[peers.ticker == tk].sort_values("date")
        d = d.assign(r=np.log(d.close).diff()).dropna(subset=["r"])[["date", "r"]]
        if tk in ("MU", "SNDK", "SOX"):
            # 米国セッション（日付 d）は東京の d+1 の寄付前に終わる → t より厳密に前の最新 d
            m = pd.merge_asof(out, d.rename(columns={"r": f"{tk}_prev"}), on="date", allow_exact_matches=False, direction="backward")
            out[f"{tk}_prev"] = m[f"{tk}_prev"].values
        else:
            m = out.merge(d.rename(columns={"r": f"{tk}_same"}), on="date", how="left")
            out[f"{tk}_same"] = m[f"{tk}_same"].values
    return out


def latest_peer_session(peers: pd.DataFrame) -> dict:
    """最新の米国セッションのリターン（当日分は暫定の可能性あり）."""
    res = {}
    for tk in ("MU", "SNDK", "SOX"):
        d = peers[peers.ticker == tk].sort_values("date")
        if len(d) >= 2:
            res[tk] = dict(date=d.date.iloc[-1].date(), ret=float(np.log(d.close.iloc[-1] / d.close.iloc[-2])))
    return res
