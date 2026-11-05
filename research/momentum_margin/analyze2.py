#!/usr/bin/env python3
"""追加分析: 急落日後の条件付きリターン、今回局面の横断比較、深い急落の類似事例、反発の停止位置、混雑度."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import BOT, CR, D, GROUP, NAME, PX, WK, dy, pct, q  # noqa: E402


def wk_feature_asof(code, date):
    """date 時点で『既知』の週次信用データ（金曜計算・翌週火曜公表 → 4営業日ラグとして date-6日以前の金曜）."""
    w = WK[code]
    w = w[w.date <= date - pd.Timedelta(days=6)]
    if len(w) < 5:
        return None
    b0 = w.iloc[-1]
    chg3 = math.log(b0.buy_adj / w.buy_adj.iloc[-4]) if w.buy_adj.iloc[-4] > 0 else np.nan
    rel26 = b0.buy_adj / w.buy_adj.iloc[-26:].max()
    return dict(mchg3=chg3, rel26=rel26, ratio=b0.ratio, cgo=b0.cgo, rp=b0.rp)


# ------------------------------------------------------------------ 1. after -10% days: conditional forward returns
rows = []
for code, g in PX.items():
    c = g.close.values
    for i in range(30, len(g) - 11):
        if g.ret.iloc[i] <= math.log(0.90):
            f = wk_feature_asof(code, g.date.iloc[i])
            if f is None:
                continue
            o1, c1 = g.open.iloc[i + 1], c[i + 1]
            rows.append(dict(code=code, name=NAME[code], group=GROUP[code], date=g.date.iloc[i].date(), ret=g.ret.iloc[i], dd60=g.dd60.iloc[i],
                             two=g.ret.iloc[i] + g.ret.iloc[i - 1], vol_adv=g.volume.iloc[i] / g.adv20.iloc[i] if g.adv20.iloc[i] else np.nan, pos=g.pos.iloc[i],
                             gap1=g.gap.iloc[i + 1], intra1=g.intra.iloc[i + 1], r1=c[i + 1] / c[i] - 1, r3=c[i + 3] / c[i] - 1, r5=c[i + 5] / c[i] - 1, r10=c[i + 10] / c[i] - 1,
                             o1_c5=c[i + 5] / o1 - 1, o1_c1=c1 / o1 - 1, o2_c5=c[i + 5] / g.open.iloc[i + 2] - 1 if i + 2 < len(g) else np.nan,
                             max5=g.high.iloc[i + 1:i + 6].max() / c[i] - 1, min5=g.low.iloc[i + 1:i + 6].min() / c[i] - 1, **f))
EV = pd.DataFrame(rows)
EV.to_csv(D / "events_m10.csv", index=False)


def summarize(df, label):
    if len(df) == 0:
        print(f"  {label}: n=0"); return
    print(f"  {label:38s} n={len(df):3d} | 翌日窓 {pct(df.gap1.median(), 1)}({(df.gap1 > 0).mean():.0%}) 日中 {pct(df.intra1.median(), 1)}({(df.intra1 > 0).mean():.0%})"
          f" | 終値ベース r1 {pct(df.r1.median(), 1)} r3 {pct(df.r3.median(), 1)} r5 {pct(df.r5.median(), 1)}({(df.r5 > 0).mean():.0%}) r10 {pct(df.r10.median(), 1)}({(df.r10 > 0).mean():.0%})"
          f" | 翌寄→5日後 {pct(df.o1_c5.median(), 1)}({(df.o1_c5 > 0).mean():.0%}) | 5日内 最大 {pct(df.max5.median())} 最小 {pct(df.min5.median())}")


print("\n== 日次 −10% 以下の日（44銘柄、2024/11〜）:", len(EV))
summarize(EV, "全体")
summarize(EV[EV.ret <= math.log(0.85)], "−15%以下")
summarize(EV[EV.two <= math.log(0.80)], "2日で−20%以下")
summarize(EV[EV.dd60 <= -0.30], "60日高値から−30%以下の局面")
summarize(EV[EV.dd60 <= -0.45], "60日高値から−45%以下の局面")
print("  -- 直前（既知）の週次買い残トレンドで分割:")
summarize(EV[EV.mchg3 > 0.05], "買い残 前3週 +5%超（買い下がり中）")
summarize(EV[EV.mchg3 < -0.05], "買い残 前3週 −5%未満（整理中）")
summarize(EV[(EV.mchg3 >= -0.05) & (EV.mchg3 <= 0.05)], "買い残 ほぼ横ばい")
print("  -- 混雑度（買い残/26週ピーク）で分割:")
summarize(EV[EV.rel26 >= 0.95], "買い残が26週ピーク圏（≥0.95）")
summarize(EV[EV.rel26 < 0.75], "買い残がピークから−25%以上整理済み")
print("  -- 週次CGO（終値−参照価格）/終値 で分割:")
summarize(EV[EV.cgo <= -0.25], "CGO ≤ −25%（買い方の平均コストを大きく下回る）")
summarize(EV[EV.cgo > -0.10], "CGO > −10%")
print("  -- 当日の形で分割:")
summarize(EV[EV.pos >= 0.6], "終値位置 ≥60%（下ヒゲ）")
summarize(EV[EV.pos < 0.2], "終値位置 <20%（安値引け）")
summarize(EV[EV.vol_adv >= 2.0], "出来高 ≥2×ADV")
print("  -- 翌日の窓で分割（翌日の寄付で判定できる）:")
summarize(EV[EV.gap1 > 0.02], "翌日 +2%超の窓上げ")
summarize(EV[EV.gap1 < -0.03], "翌日 −3%超の窓下げ")
g_up = EV[EV.gap1 > 0.02]
print(f"     窓上げ(+2%超)の日の日中: 中央値 {pct(g_up.intra1.median(), 1)} 陽線 {(g_up.intra1 > 0).mean():.0%} / 翌寄→翌引 {pct(g_up.o1_c1.median(), 1)}")
g_dn = EV[EV.gap1 < -0.03]
print(f"     窓下げ(−3%超)の日の日中: 中央値 {pct(g_dn.intra1.median(), 1)} 陽線 {(g_dn.intra1 > 0).mean():.0%} / 翌寄→翌引 {pct(g_dn.o1_c1.median(), 1)}")

# ------------------------------------------------------------------ 2. current episode cross-section (daily margin since 9/29)
rows = []
for code, g in dy.groupby("code"):
    g = g.sort_values("date")
    if len(g) < 10:
        continue
    a, b = g.iloc[0], g.iloc[-1]
    p = PX[code]
    p0, p1 = p[p.date == a.date], p[p.date == b.date]
    if len(p0) == 0 or len(p1) == 0:
        continue
    avg_cost = b.buy_amt / b.buy if b.buy else np.nan
    hi = p[(p.date >= "2026-06-01") & (p.date <= b.date)].close.max()
    # 10/1→10/23 の買い残変化と 10/23→11/4 のリターン（局面内の予測力）
    m1 = g[g.date <= "2026-10-23"]
    pre = math.log(m1.buy.iloc[-1] / g.buy.iloc[0]) if len(m1) and g.buy.iloc[0] else np.nan
    pr = p[(p.date >= "2026-10-23") & (p.date <= b.date)]
    late = math.log(pr.close.iloc[-1] / pr.close.iloc[0]) if len(pr) > 1 else np.nan
    rows.append(dict(code=code, name=NAME[code], group=GROUP[code], ret=math.log(b.close / a.close), mchg=math.log(b.buy / a.buy), ratio0=a.ratio, ratio1=b.ratio,
                     avg_cost=avg_cost, pl=b.close / avg_cost - 1, dd_hi=b.close / hi - 1, buy1=b.buy, pre=pre, late=late,
                     buy_yen=b.buy_amt))
CX = pd.DataFrame(rows).sort_values("mchg", ascending=False)
CX.to_csv(D / "current_cross.csv", index=False)
print("\n== 今回局面（9/29→11/4、日々公表の信用残）:")
print(f"  44銘柄の中央値: 株価 {pct(CX.ret.median())}, 買い残 {pct(CX.mchg.median())}, 買い方の損益 {pct(CX.pl.median())}, 信用倍率 {CX.ratio0.median():.1f}→{CX.ratio1.median():.1f}")
print(f"  買い残が増えた銘柄 {(CX.mchg > 0).mean():.0%}; 株価が下がった銘柄 {(CX.ret < 0).mean():.0%}")
k = CX[CX.code == "285A"].iloc[0]
print(f"  キオクシア: 株価 {pct(k.ret)}, 買い残 {pct(k.mchg)}（{(CX.mchg < k.mchg).mean():.0%}分位）, 買い方の損益 {pct(k.pl)}（{(CX.pl > k.pl).mean():.0%}の銘柄より悪い）, 信用倍率 {k.ratio0:.0f}→{k.ratio1:.0f}, 買い残 {k.buy_yen / 1e8:,.0f}億円（全体 {CX.buy_yen.sum() / 1e8:,.0f}億円の {k.buy_yen / CX.buy_yen.sum():.0%}）")
print("  局面内の予測力: 10/1→10/23 の買い残変化 と 10/23→11/4 のリターンの相関 "
      f"{CX[['pre', 'late']].dropna().corr().iloc[0, 1]:+.2f} (n={CX[['pre', 'late']].dropna().shape[0]})")
print("  グループ別（株価 / 買い残 / 買い方損益 の中央値）:")
for gname, g in CX.groupby("group"):
    print(f"    {gname:14s} {pct(g.ret.median()):>6} / {pct(g.mchg.median()):>6} / {pct(g.pl.median()):>6}  n={len(g)}")
print("  買い残の増加上位・下位:")
cols = ["name", "ret", "mchg", "pl", "ratio1", "dd_hi"]
print(CX[cols].head(8).to_string(index=False, float_format=lambda x: f"{x:.2f}"))
print(CX[cols].tail(6).to_string(index=False, float_format=lambda x: f"{x:.2f}"))

# ------------------------------------------------------------------ 3. deep-crash comparables (dd from 120d high <= -50%)
rows = []
for code, g in PX.items():
    g = g.copy()
    g["hi120"] = g.close.rolling(120, min_periods=40).max()
    g["dd120"] = g.close / g.hi120 - 1
    dd = g.dd120.values
    last = -10 ** 9
    for i in range(120, len(g)):
        if dd[i] <= -0.50 and dd[i - 1] > -0.50 and i - last > 60:
            last = i
            seg = g.iloc[i:i + 61]
            ti = int(seg.close.values.argmin())
            trough = seg.close.iloc[ti]
            reb20 = g.close.iloc[i + ti:i + ti + 21].max() / trough - 1 if i + ti + 1 < len(g) else np.nan
            f = wk_feature_asof(code, g.date.iloc[i])
            mc_after = None
            w = WK[code]
            wa = w[(w.date > g.date.iloc[i]) & (w.date <= g.date.iloc[i] + pd.Timedelta(days=28))]
            wb = w[w.date <= g.date.iloc[i]]
            if len(wa) and len(wb):
                mc_after = math.log(wa.buy_adj.iloc[-1] / wb.buy_adj.iloc[-1])
            rows.append(dict(name=NAME[code], date=g.date.iloc[i].date(), dd120=dd[i], days_to_trough=ti, extra_dd=trough / g.close.iloc[i] - 1,
                             reb20=reb20, r20=g.close.iloc[min(i + 20, len(g) - 1)] / g.close.iloc[i] - 1, r60=g.close.iloc[min(i + 60, len(g) - 1)] / g.close.iloc[i] - 1,
                             margin_4w_after=mc_after, **(f or {})))
DC = pd.DataFrame(rows)
print("\n== 120日高値から−50%に初到達（キオクシア級）:", len(DC), "件")
if len(DC):
    print(DC.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print(f"  追加下落 中央値 {pct(DC.extra_dd.median())}, 底まで {DC.days_to_trough.median():.0f}日, 底から20日の反発 {pct(DC.reb20.median())}, 20日 {pct(DC.r20.median())}, 60日 {pct(DC.r60.median())}")

# ------------------------------------------------------------------ 4. where do rebounds stall? CGO at the post-trough rebound peak (crash events)
rows = []
for e in CR.itertuples():
    g = PX[e.code]
    i0 = g.index[g.date == pd.Timestamp(e.date)][0]
    seg = g.iloc[i0:i0 + 41]
    ti = int(seg.close.values.argmin())
    post = g.iloc[i0 + ti:i0 + ti + 41]
    if len(post) < 5:
        continue
    pi = int(post.close.values.argmax())
    pk = post.iloc[pi]
    w = WK[e.code]
    wb = w[w.date <= pk.date]
    if not len(wb):
        continue
    rp = wb.rp.iloc[-1]
    rows.append(dict(name=e.name, trough=post.date.iloc[0].date(), peak=pk.date.date(), days=pi, reb=pk.close / post.close.iloc[0] - 1, cgo_peak=(pk.close - rp) / pk.close,
                     cgo_trough=(post.close.iloc[0] - wb.rp.iloc[-1]) / post.close.iloc[0]))
RB = pd.DataFrame(rows)
print("\n== 急落後の反発ピーク（底から40日内の高値）と買い方の参照価格:")
print(f"  反発ピークでのCGO=(P−RP)/P: 中央値 {pct(RB.cgo_peak.median())}, p25 {pct(q(RB.cgo_peak, 25))}, p75 {pct(q(RB.cgo_peak, 75))} | 参照価格を超えた比率 {(RB.cgo_peak > 0).mean():.0%} (n={len(RB)})")
print(f"  底でのCGO: 中央値 {pct(RB.cgo_trough.median())} → 反発は『参照価格（買い方の平均コスト）付近で止まる』が中央的。底から反発ピークまで 中央値 {RB.days.median():.0f}日, 反発 {pct(RB.reb.median())}")

# ------------------------------------------------------------------ 5. crowdedness vs crash depth / recovery (crash events)
print("\n== 混雑度と急落の深さ・回復（−30%到達イベント）:")
for lab, m in (("買い残が26週ピーク圏（rel26≥0.9）", CR.rel26 >= 0.9), ("整理済み（rel26<0.7）", CR.rel26 < 0.7), ("信用倍率 ≥20", CR.ratio >= 20), ("信用倍率 <5", CR.ratio < 5)):
    g = CR[m]
    if len(g):
        print(f"  {lab:28s} n={len(g):2d} 追加下落 {pct(g.extra_dd.median())} 底まで {g.days_to_trough.median():.0f}日 反発 {pct(g.rebound_from_trough.median())} 20日 {pct(g.r20.median())} 二番底 {g.retest.mean():.0%}")

# bottoms: how often margin at bottom is at its 26w peak (Kioxia-like)
print(f"\n== 局所底のうち、底の時点で買い残が26週ピーク圏（rel26≥0.95）だった比率: {(BOT.rel26 >= 0.95).mean():.0%} (n={len(BOT)}); その群の翌日窓 {pct(BOT[BOT.rel26 >= 0.95].gap_next.median(), 1)}, fwd10 {pct(BOT[BOT.rel26 >= 0.95].fwd10.median())}")
print(f"   底の時点のCGOが −30% 以下だった比率: {(BOT.cgo <= -0.30).mean():.0%}; 最も深い5件: {BOT.nsmallest(5, 'cgo')[['name', 'date', 'cgo']].values.tolist()}")
