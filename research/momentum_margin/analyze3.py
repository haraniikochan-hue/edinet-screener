"""頑健性: 日付クラスタ（2025/4 関税ショック等）の影響を除いた条件付き統計と、キオクシアの週次参照価格."""
import math, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import BOT, CR, D, NAME, PX, WK, pct, q
EV = pd.read_csv(D / "events_m10.csv", parse_dates=["date"])
n225 = pd.read_csv("/tmp/claude-0/-home-user-edinet-screener/a1230b15-56c7-56c6-80e0-5bbb80a94011/scratchpad/yf_N225.csv", index_col=0, parse_dates=True)
n225r = np.log(n225.Close).diff()
EV["n225"] = EV.date.map(n225r)
EV["idio"] = EV.n225 > -0.03           # 日経が−3%以上下げていない日＝個別要因の急落
EV["cluster"] = EV.date.dt.strftime("%Y-%m")
def summ(df, label):
    if len(df) == 0: print(f"  {label}: n=0"); return
    print(f"  {label:34s} n={len(df):3d} 日付数={df.date.nunique():3d} | 翌日窓 {pct(df.gap1.median(),1)}({(df.gap1>0).mean():.0%}) | r1 {pct(df.r1.median(),1)} r5 {pct(df.r5.median(),1)}({(df.r5>0).mean():.0%}) r10 {pct(df.r10.median(),1)}({(df.r10>0).mean():.0%}) | 翌寄→5日後 {pct(df.o1_c5.median(),1)}({(df.o1_c5>0).mean():.0%}) | 最小5日 {pct(df.min5.median())}")
print("== −10%日の条件付き統計：個別要因の日（日経 > −3%）に限定")
I = EV[EV.idio]
summ(EV, "全体（参考）"); summ(I, "個別要因のみ")
summ(I[I.two <= math.log(0.80)], "個別・2日で−20%以下")
summ(I[I.dd60 <= -0.30], "個別・60日高値から−30%以下")
summ(I[I.dd60 <= -0.45], "個別・60日高値から−45%以下")
summ(I[I.rel26 >= 0.95], "個別・買い残が26週ピーク圏")
summ(I[I.rel26 < 0.75], "個別・買い残 整理済み")
summ(I[I.mchg3 > 0.05], "個別・買い残 前3週 +5%超")
summ(I[I.mchg3 < -0.05], "個別・買い残 前3週 −5%未満")
summ(I[I.gap1 > 0.02], "個別・翌日 +2%超の窓上げ")
summ(I[I.gap1 < -0.03], "個別・翌日 −3%超の窓下げ")
summ(I[I.vol_adv >= 2.0], "個別・出来高 ≥2×ADV")
summ(I[I.pos < 0.2], "個別・安値引け")
summ(I[I.pos >= 0.6], "個別・下ヒゲ")
print("  月別のイベント数（上位）:", EV.cluster.value_counts().head(6).to_dict())
# 2段階: 翌日の窓上げが維持（翌日終値 > 当日終値）した場合の、翌々日寄付からの5日
I2 = I[(I.gap1 > 0.02) & (I.r1 > 0)]
print(f"  個別・窓上げ+2%超 かつ 翌日終値が当日終値より上（確認）: n={len(I2)} 翌々日寄→5日後 {pct(I2.o2_c5.median(),1)}({(I2.o2_c5>0).mean():.0%})")
I3 = I[(I.gap1 > 0.02) & (I.r1 <= 0)]
print(f"  個別・窓上げしたが翌日終値は当日終値以下（失敗）: n={len(I3)} 翌々日寄→5日後 {pct(I3.o2_c5.median(),1)}({(I3.o2_c5>0).mean():.0%})")
print("\n== 急落イベント（−30%到達）: 2025/4 クラスタを除く")
CRx = CR[~CR.date.astype(str).str.startswith("2025-04")]
print(f"  n={len(CRx)}: 追加下落 {pct(CRx.extra_dd.median())}, 底まで {CRx.days_to_trough.median():.0f}日, 反発 {pct(CRx.rebound_from_trough.median())}, 20日 {pct(CRx.r20.median())}({(CRx.r20>0).mean():.0%}), 二番底 {CRx.retest.mean():.0%}")
for lab, m in (("前3週 買い残 増", CRx.pre3w > 0), ("前3週 買い残 減", CRx.pre3w <= 0), ("rel26≥0.9", CRx.rel26 >= 0.9), ("rel26<0.7", CRx.rel26 < 0.7)):
    g = CRx[m]
    if len(g): print(f"    {lab:14s} n={len(g):2d} 追加下落 {pct(g.extra_dd.median())} 底まで {g.days_to_trough.median():.0f}日 反発 {pct(g.rebound_from_trough.median())} 20日 {pct(g.r20.median())}")
# post-crash margin behaviour vs outcome (4週後の買い残変化で分ける)
rows = []
for e in CR.itertuples():
    w = WK[e.code]; d0 = pd.Timestamp(e.date)
    wb = w[w.date <= d0]; wa = w[(w.date > d0) & (w.date <= d0 + pd.Timedelta(days=28))]
    if len(wb) and len(wa) and wb.buy_adj.iloc[-1] > 0:
        rows.append(dict(name=e.name, date=e.date, m4=math.log(wa.buy_adj.iloc[-1] / wb.buy_adj.iloc[-1]), extra=e.extra_dd, days=e.days_to_trough, r20=e.r20, r40=e.r40, reb=e.rebound_from_trough))
PM = pd.DataFrame(rows); PM = PM[~PM.date.astype(str).str.startswith("2025-04")]
print("\n== −30%到達後4週の買い残の増減 と その後（2025/4除く）:")
for lab, m in (("4週後に買い残 −10%以上減（投げ・やれやれ）", PM.m4 <= -0.10), ("ほぼ横ばい", (PM.m4 > -0.10) & (PM.m4 < 0.10)), ("+10%以上増（買い下がり）", PM.m4 >= 0.10)):
    g = PM[m]
    print(f"  {lab:28s} n={len(g):2d} 追加下落 {pct(g.extra.median())} 底まで {g.days.median():.0f}日 反発 {pct(g.reb.median())} 20日 {pct(g.r20.median())}({(g.r20>0).mean():.0%}) 40日 {pct(g.r40.median())}({(g.r40>0).mean():.0%})")
print("\n== キオクシアの週次参照価格（VWAP×出来高の指数加重）:")
w = WK["285A"].sort_values("date")
for hl in (8, 3, 1.5):
    lam = 0.5 ** (1 / hl); num = den = 0.0
    for r in w.itertuples():
        v = r.vol_adj if pd.notna(r.vol_adj) else 0; p = r.vwap if pd.notna(r.vwap) else r.close
        if pd.notna(r.vwap) and (r.vwap / r.close > 1.5 or r.vwap / r.close < 0.67): p = r.close
        num = lam * num + v * p; den = lam * den + v
    print(f"  半減期 {hl}週: RP = {num/den:,.0f}円（10/30時点）")
print("  直近6週の VWAP:", [(d.strftime('%m/%d'), round(v)) for d, v in zip(w.date.tail(6), w.vwap.tail(6))])
