"""
キオクシア (285A) の需給分析: 東芝の市場内売却の検証。

入力:
    data/kioxia/price_daily_yahoo.csv     日足 (分割調整済み, Yahoo Finance)
    data/kioxia/holder_transactions.csv   scripts/kioxia_shareholding.py の出力

出力:
    data/kioxia/toshiba_daily_panel.csv   日次パネル (出来高, 東芝売却数, 参加率など)
    data/kioxia/toshiba_campaigns.csv     売却キャンペーン別の集計
    標準出力に検定結果

株価・出来高は分割調整済み (1:3, 権利落ち 2026-09-29) なので、
東芝の数量も qty_split_adj (分割後株数) で比較する。
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
KDIR = ROOT / "data" / "kioxia"

TOSHIBA = "株式会社東芝"
SPLIT_EX_DATE = pd.Timestamp("2026-09-29")
LAST_REPORT_DATE = pd.Timestamp("2026-10-01")   # 直近変更報告書の報告義務発生日
LAST_REPORT_HOLDING = 194_193_100               # 同日時点の保有株数 (分割後)
LAST_REPORT_RATIO = 11.80
SHARES_OUTSTANDING = 1_645_194_564

# 60日表に載っていないが、取得資金欄の期間合計から売却があったと分かる日
# (日別内訳は不明なので検定からは除外する)
UNKNOWN_DAYS = {
    pd.Timestamp("2025-10-20"), pd.Timestamp("2025-10-21"),   # 計 5,056,700株 (分割前)
    pd.Timestamp("2026-05-12"), pd.Timestamp("2026-05-13"),
    pd.Timestamp("2026-05-14"), pd.Timestamp("2026-05-15"),   # 計 1,821,740株 (分割前)
}

# 取得資金欄に記載された売却期間 (この期間外は売却ゼロ)
CAMPAIGNS = [
    ("C1 2025秋 (担保解除分)", "2025-09-17", "2025-10-21"),
    ("C2 2026年2-3月", "2026-02-24", "2026-03-19"),
    ("C3 2026年4-5月", "2026-04-28", "2026-05-15"),
    ("C4 2026年6-10月", "2026-06-22", "2026-10-01"),
]


def load_panel() -> pd.DataFrame:
    px = pd.read_csv(KDIR / "price_daily_yahoo.csv", parse_dates=["date"]).set_index("date")
    px["prev_close"] = px["close"].shift(1)
    px["ret"] = px["close"] / px["prev_close"] - 1
    px["gap"] = px["open"] / px["prev_close"] - 1
    px["intraday"] = px["close"] / px["open"] - 1
    px["high_vs_prev"] = px["high"] / px["prev_close"] - 1
    px["vol_ratio20"] = px["volume"] / px["volume"].rolling(20).median().shift(1)
    px["typical"] = (px["high"] + px["low"] + px["close"]) / 3

    tx = pd.read_csv(KDIR / "holder_transactions.csv", parse_dates=["trade_date"])
    sells = tx[(tx["holder"] == TOSHIBA) & (tx["venue"] == "市場内") & (tx["side"] == "処分")]
    daily = sells.groupby("trade_date").agg(qty=("qty", "sum"), qty_adj=("qty_split_adj", "sum"))

    px["toshiba_qty_raw"] = daily["qty"].reindex(px.index)
    px["toshiba_sold_adj"] = daily["qty_adj"].reindex(px.index).fillna(0.0)
    px["campaign"] = ""
    for name, start, end in CAMPAIGNS:
        px.loc[start:end, "campaign"] = name
    px["known"] = ~px.index.isin(UNKNOWN_DAYS) & (px.index <= LAST_REPORT_DATE)
    px.loc[~px["known"], "toshiba_sold_adj"] = np.nan
    px["sale_day"] = px["toshiba_sold_adj"] > 0
    px["participation"] = px["toshiba_sold_adj"] / px["volume"]
    return px


def campaign_table(px: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, start, end in CAMPAIGNS:
        w = px.loc[start:end]
        k = w[w["known"]]
        sold = k["toshiba_sold_adj"]
        rows.append({
            "campaign": name,
            "start": start,
            "end": end,
            "trading_days": len(w),
            "sale_days": int((sold > 0).sum()),
            "sold_adj_known": int(sold.sum()),
            "share_of_volume": sold.sum() / k["volume"].sum(),
            "median_participation_on_sale_days": k.loc[sold > 0, "participation"].median(),
            "max_participation": k["participation"].max(),
            "sale_weighted_price": (k["typical"] * sold).sum() / sold.sum(),
            "campaign_avg_price": k["typical"].mean(),
            "est_proceeds_jpy_bn": (k["typical"] * sold).sum() / 1e9,
        })
    return pd.DataFrame(rows)


def lot_size_test(px: pd.DataFrame) -> None:
    """日次売却数量の端数分布。1万株(分割前)/3万株(分割後)の発注単位仮説の検証。"""
    raw = px.dropna(subset=["toshiba_qty_raw"])
    pre = raw.loc[raw.index < SPLIT_EX_DATE, "toshiba_qty_raw"].astype(int)
    post = raw.loc[raw.index >= SPLIT_EX_DATE, "toshiba_qty_raw"].astype(int)
    print("\n[発注単位の検定] 日次売却数量 (分割前の日は分割前株数)")
    for label, q in [("2025年キャンペーン", pre[pre.index < "2026-01-01"]),
                     ("2026年 分割前", pre[pre.index >= "2026-01-01"])]:
        n = len(q)
        for unit, p0 in [(10_000, 0.01), (1_000, 0.10)]:
            k = int((q % unit == 0).sum())
            pval = stats.binomtest(k, n, p0, alternative="greater").pvalue
            print(f"  {label}: {unit:>6,}株の倍数 {k}/{n} 日 (偶然なら {p0:.0%}, p={pval:.2g})")
        print(f"    1万株で割った端数: {sorted((q % 10_000).tolist())}")
    print(f"  分割後: {post.tolist()} -> 3万株で割った端数 {[(v % 30_000) for v in post]}")


def sale_day_tests(px: pd.DataFrame) -> None:
    """売却キャンペーン期間内で、売却日と非売却日の値動きを比較する。"""
    print("\n[売却日と非売却日の比較] (各キャンペーン期間内, 日別内訳不明日を除く)")
    for name, start, end in CAMPAIGNS[1:] + [("2026年全体 (C2-C4)", "2026-02-24", "2026-10-01")]:
        w = px.loc[start:end]
        w = w[w["known"]]
        s, ns = w[w["sale_day"]], w[~w["sale_day"]]
        print(f"  {name}: 売却 {len(s)} 日 / 非売却 {len(ns)} 日")
        for col, label in [("ret", "終値騰落率"), ("gap", "寄付ギャップ"),
                           ("high_vs_prev", "高値/前日終値"), ("vol_ratio20", "出来高/20日中央値")]:
            a, b = s[col].dropna(), ns[col].dropna()
            if len(a) < 3 or len(b) < 3:
                continue
            u = stats.mannwhitneyu(a, b, alternative="two-sided")
            print(f"    {label:<12} 売却日 中央値 {a.median():+.3f} / 非売却日 {b.median():+.3f}  (MW p={u.pvalue:.2f})")
        sd = s.dropna(subset=["ret"])
        if len(sd) >= 5:
            rho, pv = stats.spearmanr(sd["toshiba_sold_adj"], sd["high_vs_prev"])
            print(f"    売却日内: 売却数量 vs 高値/前日終値 Spearman {rho:+.2f} (p={pv:.2f})")
        # 寄付ギャップ別の売却確率 (指値で上に置いた売りが約定する日かどうか)
        for label, mask in [("GU +3%以上", w["gap"] >= 0.03), ("GU 0〜3%", (w["gap"] >= 0) & (w["gap"] < 0.03)),
                            ("GD", w["gap"] < 0)]:
            g = w[mask]
            if len(g):
                print(f"    {label:<9} 売却日率 {g['sale_day'].mean():.0%} ({int(g['sale_day'].sum())}/{len(g)}), "
                      f"平均売却 {g['toshiba_sold_adj'].mean():,.0f} 株")


def pace_projection(px: pd.DataFrame) -> None:
    c4 = px.loc["2026-06-22":"2026-10-01"]
    c4 = c4[c4["known"]]
    days = len(c4)
    sold = c4["toshiba_sold_adj"].sum()
    pace = sold / days
    recent = px.loc["2026-09-01":"2026-10-01", "toshiba_sold_adj"]
    pace_recent = recent.sum() / len(recent)
    # 次の変更報告書: 直前報告比で保有割合が1ポイント以上減少したとき
    threshold_holding = SHARES_OUTSTANDING * (LAST_REPORT_RATIO - 1.0) / 100
    to_next = LAST_REPORT_HOLDING - threshold_holding
    print("\n[ペースと次回報告の目安]")
    print(f"  C4 (6/22-10/1) 平均 {pace:,.0f} 株/営業日 (分割後換算, {days}営業日)")
    print(f"  9月 平均 {pace_recent:,.0f} 株/営業日")
    print(f"  次回変更報告の発生に必要な追加売却: 約 {to_next:,.0f} 株 (保有 {threshold_holding:,.0f} 株以下)")
    for label, v in [("C4ペース", pace), ("9月ペース", pace_recent)]:
        print(f"    {label}なら {to_next / v:.0f} 営業日後, 全株売却まで {LAST_REPORT_HOLDING / v:.0f} 営業日")


def gap_bucket(gap: float) -> str:
    if gap >= 0.03:
        return "GU3+"
    return "GU0-3" if gap >= 0 else "GD"


def estimate_after_last_report(px: pd.DataFrame) -> None:
    """直近報告 (10/1) 以降は売却が開示されていないため、C4 の寄付ギャップ別の
    平均売却数量を当てはめて「売っていた場合の想定量」を出す (あくまで参考値)。"""
    c4 = px.loc["2026-06-22":"2026-10-01"]
    c4 = c4[c4["known"]].copy()
    c4["bucket"] = c4["gap"].map(gap_bucket)
    mean_by_bucket = c4.groupby("bucket")["toshiba_sold_adj"].mean()
    after = px.loc[px.index > LAST_REPORT_DATE].copy()
    after["bucket"] = after["gap"].map(gap_bucket)
    after["expected_sold"] = after["bucket"].map(mean_by_bucket)
    after["expected_share_of_volume"] = after["expected_sold"] / after["volume"]
    print("\n[10/1 以降の想定売却量] (C4 のギャップ別平均を当てはめた参考値)")
    print(after[["open", "close", "gap", "bucket", "volume", "expected_sold", "expected_share_of_volume"]]
          .to_string(float_format=lambda v: f"{v:,.3f}"))
    total = after["expected_sold"].sum()
    print(f"  合計 {total:,.0f} 株 / 期間出来高の {total / after['volume'].sum():.1%}")


def main() -> None:
    px = load_panel()
    camp = campaign_table(px)
    pd.set_option("display.width", 200)
    print("[キャンペーン別]")
    print(camp.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    lot_size_test(px)
    sale_day_tests(px)
    pace_projection(px)
    estimate_after_last_report(px)

    out = px.loc["2025-09-01":, ["open", "high", "low", "close", "volume", "ret", "high_vs_prev",
                                 "vol_ratio20", "campaign", "known", "toshiba_qty_raw",
                                 "toshiba_sold_adj", "participation"]]
    out.to_csv(KDIR / "toshiba_daily_panel.csv", float_format="%.6g")
    camp.to_csv(KDIR / "toshiba_campaigns.csv", index=False, float_format="%.6g")


if __name__ == "__main__":
    main()
