#!/usr/bin/env python3
"""モメンタム銘柄44種の『底局面の信用需給』横断分析.

出力: data/events_bottoms.csv, data/events_crash.csv, data/current_cross.csv と標準出力の要約（report.md の素材）.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
D = BASE / "data"

uni = pd.read_csv(BASE / "universe.csv", dtype=str)
NAME = dict(zip(uni.code, uni.name))
GROUP = dict(zip(uni.code, uni.group))
px = pd.read_csv(D / "prices_all.csv", dtype={"code": str}, parse_dates=["date"]).sort_values(["code", "date"])
wk = pd.read_csv(D / "margin_weekly_all.csv", dtype={"code": str}, parse_dates=["date"]).sort_values(["code", "date"])
dy = pd.read_csv(D / "margin_daily_all.csv", dtype={"code": str}, parse_dates=["date"]).sort_values(["code", "date"])
sp = pd.read_csv(D / "splits_all.csv", dtype={"code": str}, parse_dates=["date"]) if (D / "splits_all.csv").stat().st_size > 10 else pd.DataFrame(columns=["code", "date", "ratio"])


# ------------------------------------------------------------------ 1. split-adjust weekly margin shares
def adjust_splits(wk, sp):
    wk = wk.copy()
    wk["buy_adj"], wk["sell_adj"], wk["vol_adj"] = wk.buy, wk.sell, wk.volume
    for r in sp.itertuples():
        m = (wk.code == r.code) & (wk.date < r.date)
        wk.loc[m, ["buy_adj", "sell_adj", "vol_adj"]] = wk.loc[m, ["buy_adj", "sell_adj", "vol_adj"]].values * r.ratio
    # kabutan の週次 売買高 は分割調整済みか不明 → 価格の連続性で判定: 終値は調整済みなので vwap と close の比で確認
    return wk


wk = adjust_splits(wk, sp)
# sanity: residual jumps in buy_adj (x>2.5 or x<0.4 week-over-week with no split) を報告
jumps = []
for code, g in wk.groupby("code"):
    g = g.sort_values("date")
    r = g.buy_adj / g.buy_adj.shift(1)
    bad = g[(r > 2.5) | (r < 0.4)]
    for b in bad.itertuples():
        jumps.append((code, NAME[code], b.date.date(), round(float(r.loc[b.Index]), 2)))
print("== 分割調整後に残る週次買い残の不連続（要確認）:", jumps[:20], file=sys.stderr)


# ------------------------------------------------------------------ 2. per-stock daily features
def prep_px(g):
    g = g.sort_values("date").reset_index(drop=True).copy()
    g["ret"] = np.log(g.close).diff()
    g["gap"] = np.log(g.open / g.close.shift(1))
    g["intra"] = np.log(g.close / g.open)
    g["adv20"] = g.volume.rolling(20, min_periods=5).mean().shift(1)
    g["hi60"] = g.close.rolling(60, min_periods=20).max()
    g["dd60"] = g.close / g.hi60 - 1
    g["pos"] = (g.close - g.low) / np.maximum(g.high - g.low, 1e-9)
    g["ret5"] = np.log(g.close / g.close.shift(5))
    g["ret20"] = np.log(g.close / g.close.shift(20))
    return g


PX = {c: prep_px(g) for c, g in px.groupby("code")}


# ------------------------------------------------------------------ 3. weekly reference price (volume-weighted EWMA of VWAP) & CGO
def weekly_rp(g, half_life=8):
    g = g.sort_values("date").reset_index(drop=True).copy()
    lam = 0.5 ** (1 / half_life)
    rp = np.full(len(g), np.nan)
    num = den = 0.0
    for i, r in g.iterrows():
        v = r.vol_adj if pd.notna(r.vol_adj) and r.vol_adj > 0 else 0.0
        p = r.vwap if pd.notna(r.vwap) else r.close
        # 分割前の vwap は未調整の可能性 → close/vwap 比が 1.5 倍以上ずれていれば close を使う
        if pd.notna(r.vwap) and pd.notna(r.close) and (r.vwap / r.close > 1.5 or r.vwap / r.close < 0.67):
            p = r.close
        num = lam * num + v * p
        den = lam * den + v
        rp[i] = num / den if den > 0 else np.nan
    g["rp"] = rp
    g["cgo"] = (g.close - g.rp) / g.close
    return g


WK = {c: weekly_rp(g) for c, g in wk.groupby("code")}


# ------------------------------------------------------------------ 4. local bottoms (daily) and margin context (weekly)
def local_bottoms(g, win=10, fwd=0.15):
    c = g.close.values
    out = []
    for i in range(win, len(g) - win):
        if c[i] == c[i - win:i + win + 1].min() and c[i + 1:i + win + 1].max() / c[i] - 1 >= fwd:
            out.append(i)
    return out


def margin_context(code, bdate):
    w = WK[code]
    before = w[w.date <= bdate]
    after = w[w.date > bdate]
    if len(before) < 6 or len(after) < 4:
        return None
    b0 = before.iloc[-1]          # 底の直前の金曜（底の週を含む場合あり）
    def chg(a, b):
        return math.log(b / a) if (a and b and a > 0 and b > 0) else np.nan
    pre1 = chg(before.buy_adj.iloc[-2], b0.buy_adj)
    pre3 = chg(before.buy_adj.iloc[-4], b0.buy_adj)
    post1 = chg(b0.buy_adj, after.buy_adj.iloc[0])
    post3 = chg(b0.buy_adj, after.buy_adj.iloc[min(2, len(after) - 1)])
    peak26 = before.buy_adj.iloc[-26:].max()
    rel26 = b0.buy_adj / peak26 if peak26 else np.nan
    # 信用買い残ピークの週と底の週の差（週）
    pk_idx = before.buy_adj.iloc[-26:].idxmax()
    lead = (b0.date - before.loc[pk_idx, "date"]).days / 7
    # 底の後に買い残がピークをつけるか（+8週以内）
    post_peak = after.buy_adj.iloc[:8].max()
    return dict(pre1w=pre1, pre3w=pre3, post1w=post1, post3w=post3, rel26=rel26, lead_weeks=lead,
                post_higher=float(post_peak > b0.buy_adj * 1.05), ratio=b0.ratio, cgo=b0.cgo,
                rp=b0.rp, ratio_chg3w=(b0.ratio / before.ratio.iloc[-4] - 1) if before.ratio.iloc[-4] else np.nan)


bot_rows = []
for code, g in PX.items():
    for i in local_bottoms(g):
        r = g.iloc[i]
        mc = margin_context(code, r.date)
        if mc is None:
            continue
        nxt = g.iloc[i + 1]
        bot_rows.append(dict(code=code, name=NAME[code], group=GROUP[code], date=r.date.date(), close=r.close, ret5=r.ret5, ret20=r.ret20, dd60=r.dd60,
                             vol_adv=r.volume / r.adv20 if r.adv20 else np.nan, pos=r.pos, ret_day=r.ret, gap_next=nxt.gap, intra_next=nxt.intra,
                             fwd10=g.close.iloc[i + 1:i + 11].max() / r.close - 1, **mc))
BOT = pd.DataFrame(bot_rows)
BOT.to_csv(D / "events_bottoms.csv", index=False)


# ------------------------------------------------------------------ 5. crash playbook: first day with dd60 <= -30% (fresh episode), follow 40 days
def crash_events(g, thr=-0.30, cooldown=40, horizon=40):
    out = []
    last = -10 ** 9
    dd = g.dd60.values
    for i in range(60, len(g) - 5):
        if dd[i] <= thr and i - last > cooldown and (dd[i - 1] > thr):
            last = i
            seg = g.iloc[i: i + horizon + 1]
            c0 = g.close.iloc[i]
            trough_i = int(seg.close.values.argmin())
            trough = seg.close.iloc[trough_i]
            tdate = seg.date.iloc[trough_i]
            reb = seg.close.iloc[trough_i:].max() / trough - 1 if trough_i < len(seg) - 1 else np.nan
            # 最初の +15% 反発の後に、安値+5%以内へ再接近したか（二番底）
            post = g.iloc[i + trough_i: i + trough_i + 60]
            first_reb_i = None
            for k in range(1, len(post)):
                if post.close.iloc[k] / trough - 1 >= 0.15:
                    first_reb_i = k
                    break
            retest = np.nan
            if first_reb_i is not None:
                tail = post.iloc[first_reb_i:first_reb_i + 30]
                retest = float((tail.close.min() / trough - 1) <= 0.05)
            out.append(dict(date=g.date.iloc[i].date(), close=c0, dd60=dd[i], trough_date=tdate.date(), days_to_trough=trough_i,
                            extra_dd=trough / c0 - 1, rebound_from_trough=reb, retest=retest,
                            r10=g.close.iloc[min(i + 10, len(g) - 1)] / c0 - 1, r20=g.close.iloc[min(i + 20, len(g) - 1)] / c0 - 1,
                            r40=g.close.iloc[min(i + 40, len(g) - 1)] / c0 - 1, vol_adv=g.volume.iloc[i] / g.adv20.iloc[i] if g.adv20.iloc[i] else np.nan,
                            ret20_before=g.ret20.iloc[i]))
    return out


cr_rows = []
for code, g in PX.items():
    for e in crash_events(g):
        mc = margin_context(code, pd.Timestamp(e["date"]))
        cr_rows.append(dict(code=code, name=NAME[code], group=GROUP[code], **e, **(mc or {})))
CR = pd.DataFrame(cr_rows)
CR.to_csv(D / "events_crash.csv", index=False)


# ------------------------------------------------------------------ 6. summaries
def q(s, p):
    return float(np.nanpercentile(s.dropna(), p)) if s.notna().any() else np.nan


def pct(x, d=0):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x * 100:+.{d}f}%"


print("\n== 局所底（前後10日の最安値→10日以内に+15%）:", len(BOT), "件 /", BOT.code.nunique(), "銘柄")
print(f"底の前1週の買い残変化: 中央値 {pct(BOT.pre1w.median())}, 増加していた比率 {(BOT.pre1w > 0).mean():.0%} (n={BOT.pre1w.notna().sum()})")
print(f"底の前3週の買い残変化: 中央値 {pct(BOT.pre3w.median())}, 増加していた比率 {(BOT.pre3w > 0).mean():.0%}")
print(f"底の後1週: 中央値 {pct(BOT.post1w.median())}, 増加 {(BOT.post1w > 0).mean():.0%} / 後3週: 中央値 {pct(BOT.post3w.median())}, 増加 {(BOT.post3w > 0).mean():.0%}")
print(f"底の後8週以内に買い残がさらに+5%以上のピーク: {BOT.post_higher.mean():.0%}")
print(f"買い残 / 直近26週ピーク: 中央値 {BOT.rel26.median():.2f}, p25 {q(BOT.rel26, 25):.2f}, p75 {q(BOT.rel26, 75):.2f}")
print(f"買い残ピーク→価格の底のリード（週）: 中央値 {BOT.lead_weeks.median():.0f}, 0週(同時/後)の比率 {(BOT.lead_weeks <= 0).mean():.0%}, 4週以上前 {(BOT.lead_weeks >= 4).mean():.0%}")
print(f"底の日: 出来高/ADV 中央値 {BOT.vol_adv.median():.2f} (≥1.5: {(BOT.vol_adv >= 1.5).mean():.0%}), 終値位置 中央値 {BOT.pos.median():.0%} (≥60%: {(BOT.pos >= 0.6).mean():.0%}), 当日リターン 中央値 {pct(BOT.ret_day.median(), 1)}")
print(f"底の翌日: 窓 中央値 {pct(BOT.gap_next.median(), 1)} (正 {(BOT.gap_next > 0).mean():.0%}), 日中 中央値 {pct(BOT.intra_next.median(), 1)} (正 {(BOT.intra_next > 0).mean():.0%})")
print(f"底での週次CGO(終値−参照価格)/終値: 中央値 {pct(BOT.cgo.median())}, p25 {pct(q(BOT.cgo, 25))}, p75 {pct(q(BOT.cgo, 75))}; 5日 {pct(BOT.ret5.median())}, 20日 {pct(BOT.ret20.median())}, 60日高値から {pct(BOT.dd60.median())}")
print("\nグループ別（前3週の買い残変化の中央値 / 増加比率 / n）:")
for gname, g in BOT.groupby("group"):
    print(f"  {gname:14s} {pct(g.pre3w.median()):>6} / {(g.pre3w > 0).mean():.0%} / {len(g)}")
print("\n深い底（60日高値から−30%以下）に限る:")
deep = BOT[BOT.dd60 <= -0.30]
print(f"  n={len(deep)}: 前3週 中央値 {pct(deep.pre3w.median())} 増加 {(deep.pre3w > 0).mean():.0%}; 後3週 {pct(deep.post3w.median())} 増加 {(deep.post3w > 0).mean():.0%}; rel26 {deep.rel26.median():.2f}; 終値位置 {deep.pos.median():.0%}; 翌日窓 {pct(deep.gap_next.median(), 1)}; CGO {pct(deep.cgo.median())}")

print("\n== 急落イベント（60日高値から−30%に初到達）:", len(CR), "件")
print(f"到達後の追加下落（40日内の最安値まで）: 中央値 {pct(CR.extra_dd.median())}, p25 {pct(q(CR.extra_dd, 25))}, p75 {pct(q(CR.extra_dd, 75))}; 追加下落なし(=到達日が底)の比率 {(CR.days_to_trough == 0).mean():.0%}")
print(f"底までの日数: 中央値 {CR.days_to_trough.median():.0f}, p25 {q(CR.days_to_trough, 25):.0f}, p75 {q(CR.days_to_trough, 75):.0f}")
print(f"底からの反発（40日内）: 中央値 {pct(CR.rebound_from_trough.median())}, p25 {pct(q(CR.rebound_from_trough, 25))}, p75 {pct(q(CR.rebound_from_trough, 75))}")
print(f"最初の+15%反発後に安値+5%以内へ再接近（二番底）: {CR.retest.mean():.0%} (n={CR.retest.notna().sum()})")
print(f"到達日からのリターン: 10日 中央値 {pct(CR.r10.median())} (正 {(CR.r10 > 0).mean():.0%}), 20日 {pct(CR.r20.median())} (正 {(CR.r20 > 0).mean():.0%}), 40日 {pct(CR.r40.median())} (正 {(CR.r40 > 0).mean():.0%})")
if "pre3w" in CR:
    up = CR[CR.pre3w > 0]; dn = CR[CR.pre3w <= 0]
    print(f"到達時点で前3週に買い残が増えていた群 (n={len(up)}): 追加下落 {pct(up.extra_dd.median())}, 20日 {pct(up.r20.median())}, 底までの日数 {up.days_to_trough.median():.0f}")
    print(f"減っていた群 (n={len(dn)}): 追加下落 {pct(dn.extra_dd.median())}, 20日 {pct(dn.r20.median())}, 底までの日数 {dn.days_to_trough.median():.0f}")
print("\n急落イベント一覧（新しい順、上位25）:")
cols = ["name", "date", "dd60", "days_to_trough", "extra_dd", "rebound_from_trough", "retest", "r20", "pre3w", "post3w", "rel26"]
print(CR.sort_values("date", ascending=False)[cols].head(25).to_string(index=False, float_format=lambda x: f"{x:.2f}"))
