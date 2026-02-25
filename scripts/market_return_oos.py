"""
市場リターン OOS バックテスト
T年度末の財務特徴量 → T+1年度の実株価リターンで予測力を検証する。

BPSプロキシOOSとの差異:
  - 目的変数: yfinance株価の年次リターン（4月→翌4月、日本企業の多くが3月決算前提）
  - BPS同語反復問題が解消される
  - forwardPE等の市場データ因子は検証不可（将来情報リーク）

手法:
  - Formation year T の財務特徴量 → T+1年度の市場リターン
  - ローリング IC、プーリング IC/ICIR、五分位 L/S スプレッド
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DATA = ROOT / "data"
WINSORIZE_PCTL = (0.01, 0.99)
# 日本企業の決算は多くが3月末 → 4月初めの株価を基準にリターンを計算
# Formation year T の特徴量 → year T+1 April → year T+2 April のリターン
PRICE_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]  # April prices needed
FORMATION_YEARS = [2021, 2022, 2023, 2024]  # T features → T+1 to T+2 returns

BATCH_SIZE = 50
SLEEP_BETWEEN = 0.3


def winsorize(s: pd.Series) -> pd.Series:
    lo, hi = s.quantile(WINSORIZE_PCTL[0]), s.quantile(WINSORIZE_PCTL[1])
    return s.clip(lo, hi)


# ---------------------------------------------------------------------------
# Step 1: April stock prices for all tickers
# ---------------------------------------------------------------------------
def fetch_april_prices(tickers: list[str]) -> pd.DataFrame:
    """Fetch monthly prices and extract April close for each year."""
    print("=" * 80)
    print("STEP 1: FETCH APRIL STOCK PRICES")
    print("=" * 80)

    all_prices: dict[str, dict[int, float]] = {}
    n_batches = (len(tickers) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(tickers), BATCH_SIZE):
        batch = tickers[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        if batch_num % 10 == 1 or batch_num == n_batches:
            print(f"  Batch {batch_num}/{n_batches}...")

        try:
            data = yf.download(
                batch, start="2020-03-01", end="2025-12-31",
                interval="1mo", auto_adjust=True, progress=False, threads=True,
            )
            if data.empty:
                continue

            close = data["Close"] if "Close" in data.columns else data
            if isinstance(close, pd.Series):
                close = close.to_frame(batch[0])

            for t in batch:
                if t not in close.columns:
                    continue
                series = close[t].dropna()
                prices_by_year: dict[int, float] = {}
                for idx, val in series.items():
                    ts = pd.Timestamp(idx)
                    # Use April or May (whichever is first available after fiscal year end)
                    if ts.month in (4, 5):
                        yr = ts.year
                        if yr not in prices_by_year:
                            prices_by_year[yr] = float(val)
                if prices_by_year:
                    all_prices[t] = prices_by_year

        except Exception as e:
            print(f"  Batch error: {e}")

        if i + BATCH_SIZE < len(tickers):
            time.sleep(SLEEP_BETWEEN)

    # Build DataFrame: ticker, year, april_price
    rows = []
    for ticker, yp in all_prices.items():
        for yr, px in yp.items():
            rows.append({"ticker": ticker, "year": yr, "april_price": px})

    price_df = pd.DataFrame(rows)
    print(f"  Tickers with April prices: {len(all_prices)}")
    print(f"  Total price records: {len(price_df)}")
    return price_df


def compute_annual_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Compute 1-year forward returns: price(year+1) / price(year) - 1."""
    price_wide = price_df.pivot(index="ticker", columns="year", values="april_price")

    records = []
    for yr in PRICE_YEARS[:-1]:
        next_yr = yr + 1
        if yr not in price_wide.columns or next_yr not in price_wide.columns:
            continue
        for ticker in price_wide.index:
            p0 = price_wide.loc[ticker, yr]
            p1 = price_wide.loc[ticker, next_yr]
            if pd.notna(p0) and pd.notna(p1) and p0 > 0:
                records.append({
                    "ticker": ticker,
                    "return_year": next_yr,  # the year of the return (Apr yr to Apr yr+1)
                    "market_return": (p1 / p0) - 1,
                })

    ret_df = pd.DataFrame(records)
    print(f"\n  Annual return records: {len(ret_df)}")
    for yr in sorted(ret_df["return_year"].unique()):
        n = len(ret_df[ret_df["return_year"] == yr])
        print(f"    return_year={yr}: {n} tickers")
    return ret_df


# ---------------------------------------------------------------------------
# Step 2: Build feature panel (reuse from BPS OOS backtest)
# ---------------------------------------------------------------------------
def build_feature_panel() -> pd.DataFrame:
    """Build features for each (edinet_code, formation_year)."""
    print("\n" + "=" * 80)
    print("STEP 2: BUILD FEATURE PANEL")
    print("=" * 80)

    fin = pd.read_csv(DATA / "financials_all.csv")
    rat = pd.read_csv(DATA / "ratios_all.csv")
    companies = pd.read_csv(DATA / "companies.csv")

    # sec_to_ticker
    def sec_to_ticker(x):
        if pd.isna(x):
            return None
        s = str(x).strip()
        if len(s) < 4:
            return None
        return s[:4] + ".T"

    companies["ticker"] = companies["sec_code"].apply(sec_to_ticker)
    code_ticker = companies[["edinet_code", "ticker"]].dropna(subset=["ticker"])

    records = []
    for formation_year in FORMATION_YEARS:
        # Features computed from data up to formation_year
        fin_up_to = fin[fin["fiscal_year"] <= formation_year]
        rat_up_to = rat[rat["fiscal_year"] <= formation_year]

        # Latest year financial data
        fin_latest = fin_up_to.sort_values("fiscal_year").groupby("edinet_code").last()
        rat_latest = rat_up_to.sort_values("fiscal_year").groupby("edinet_code").last()

        for code in fin_latest.index:
            ft = fin_latest.loc[code]
            rt = rat_latest.loc[code] if code in rat_latest.index else pd.Series(dtype=float)

            ticker_row = code_ticker[code_ticker["edinet_code"] == code]
            if ticker_row.empty:
                continue
            ticker = ticker_row.iloc[0]["ticker"]

            row = {
                "edinet_code": code,
                "ticker": ticker,
                "formation_year": formation_year,
            }

            # --- Snapshot features ---
            row["net_margin"] = pd.to_numeric(rt.get("net_margin"), errors="coerce") if hasattr(rt, 'get') else np.nan
            row["operating_margin"] = pd.to_numeric(rt.get("operating_margin"), errors="coerce") if hasattr(rt, 'get') else np.nan
            row["equity_ratio"] = pd.to_numeric(rt.get("equity_ratio"), errors="coerce") if hasattr(rt, 'get') else np.nan

            ta_val = pd.to_numeric(ft.get("total_assets"), errors="coerce") if hasattr(ft, 'get') else np.nan
            na_val = pd.to_numeric(ft.get("net_assets"), errors="coerce") if hasattr(ft, 'get') else np.nan
            if pd.notna(ta_val) and pd.notna(na_val) and na_val > 0:
                row["debt_to_equity"] = (ta_val - na_val) / na_val
            else:
                row["debt_to_equity"] = np.nan

            # --- Time-series features ---
            rh = rat_up_to[rat_up_to["edinet_code"] == code].sort_values("fiscal_year")
            fh = fin_up_to[fin_up_to["edinet_code"] == code].sort_values("fiscal_year")

            # ROE/ROA std
            roe_vals = pd.to_numeric(rh["roe"], errors="coerce").dropna()
            roa_vals = pd.to_numeric(rh["roa"], errors="coerce").dropna()
            row["roe_std"] = roe_vals.std() if len(roe_vals) >= 3 else np.nan
            row["roa_std"] = roa_vals.std() if len(roa_vals) >= 3 else np.nan

            # EPS momentum
            eps_vals = pd.to_numeric(rh["eps"], errors="coerce").dropna().values
            if len(eps_vals) >= 3:
                denom = np.mean(eps_vals[-3:-1])
                row["eps_momentum"] = eps_vals[-1] / denom if denom > 0 else np.nan
            else:
                row["eps_momentum"] = np.nan

            # Dividend features
            dps_vals = pd.to_numeric(fh["dividend_per_share"], errors="coerce")
            consec_div = 0
            for v in reversed(dps_vals.values):
                if pd.notna(v) and v > 0:
                    consec_div += 1
                else:
                    break
            row["consecutive_dividend_years"] = consec_div

            consec_increase = 0
            dps_clean = dps_vals.dropna().values
            if len(dps_clean) >= 2:
                for j in range(len(dps_clean) - 1, 0, -1):
                    if dps_clean[j] > dps_clean[j - 1]:
                        consec_increase += 1
                    else:
                        break
            row["consecutive_div_increase_years"] = consec_increase

            if len(dps_clean) >= 3 and dps_clean[-3] > 0:
                row["div_cagr_3y"] = (dps_clean[-1] / dps_clean[-3]) ** (1 / 2) - 1
            else:
                row["div_cagr_3y"] = np.nan

            # BPS increase years
            bps_vals = pd.to_numeric(fh["bps"], errors="coerce").dropna().values
            row["bps_increase_years"] = int((np.diff(bps_vals) > 0).sum()) if len(bps_vals) > 1 else 0

            # has_loss
            ni_vals = pd.to_numeric(fh["net_income"], errors="coerce").dropna()
            row["has_loss"] = int((ni_vals < 0).any()) if len(ni_vals) > 0 else np.nan

            # Net margin improvement
            nm_vals = pd.to_numeric(rh["net_margin"], errors="coerce").dropna()
            if len(nm_vals) >= 4:
                row["net_margin_improvement"] = float(nm_vals.iloc[-1]) - float(nm_vals.iloc[:3].mean())
            else:
                row["net_margin_improvement"] = np.nan

            # NI growth std
            ni_growth_vals = pd.to_numeric(fh["net_income"], errors="coerce").dropna()
            if len(ni_growth_vals) >= 3:
                ni_g = ni_growth_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan).dropna()
                row["ni_growth_std"] = ni_g.std() if len(ni_g) >= 2 else np.nan
            else:
                row["ni_growth_std"] = np.nan

            records.append(row)

        print(f"  Formation year {formation_year}: {sum(1 for r in records if r['formation_year'] == formation_year)} companies")

    panel = pd.DataFrame(records)
    print(f"  Total panel records: {len(panel)}")
    return panel


# ---------------------------------------------------------------------------
# Step 3: OOS analysis
# ---------------------------------------------------------------------------
FACTOR_COLS = [
    "net_margin", "operating_margin", "equity_ratio", "debt_to_equity",
    "roe_std", "roa_std", "eps_momentum",
    "consecutive_dividend_years", "consecutive_div_increase_years",
    "div_cagr_3y", "bps_increase_years", "has_loss",
    "net_margin_improvement", "ni_growth_std",
]


def run_oos_analysis(panel: pd.DataFrame, returns: pd.DataFrame) -> None:
    """Run rolling IC, pooled IC, and quintile analysis."""
    print("\n" + "=" * 80)
    print("STEP 3: OOS ANALYSIS (MARKET RETURNS)")
    print("=" * 80)

    # Merge: formation_year T features + return_year T+1 market returns
    # formation_year=2021 → return_year=2022 (April 2022 to April 2023)
    merged = panel.merge(
        returns,
        left_on=["ticker", pd.Series(panel["formation_year"] + 1, name="return_year_key")],
        right_on=["ticker", "return_year"],
        how="inner",
    )
    # Alternative merge approach if the above doesn't work
    if len(merged) == 0:
        panel["return_year_key"] = panel["formation_year"] + 1
        merged = panel.merge(returns, left_on=["ticker", "return_year_key"], right_on=["ticker", "return_year"], how="inner")
        merged = merged.drop(columns=["return_year_key"])

    print(f"  Merged panel-returns: {len(merged)} records")

    # Winsorize
    for col in FACTOR_COLS:
        if col in merged.columns:
            valid = merged[col].dropna()
            if len(valid) > 10:
                merged[col] = winsorize(merged[col])
    merged["market_return"] = winsorize(merged["market_return"])

    # --- Rolling IC ---
    print("\n  --- Rolling IC (by formation year) ---")
    ic_records = []
    for fy in sorted(merged["formation_year"].unique()):
        sub = merged[merged["formation_year"] == fy]
        n = len(sub)
        print(f"\n  Formation year {fy} (N={n}):")

        for fcol in FACTOR_COLS:
            valid = sub[[fcol, "market_return"]].dropna()
            if len(valid) < 30:
                continue
            ic, pval = stats.spearmanr(valid[fcol], valid["market_return"])
            ic_records.append({
                "formation_year": fy, "factor": fcol,
                "ic": ic, "pval": pval, "n": len(valid),
            })
            sig = "*" if pval < 0.05 else ""
            print(f"    {fcol:<35s}  IC={ic:+.4f}  p={pval:.4f} {sig}  N={len(valid)}")

    ic_df = pd.DataFrame(ic_records)

    # --- Pooled IC ---
    print("\n  --- Pooled IC (all years combined) ---")
    print(f"  {'Factor':<35s}  {'IC_mean':>8s}  {'IC_std':>8s}  {'ICIR':>8s}  {'Pooled_IC':>10s}  {'p':>10s}  {'N':>6s}")
    print("  " + "-" * 100)

    summary_records = []
    for fcol in FACTOR_COLS:
        sub = ic_df[ic_df["factor"] == fcol]
        if len(sub) == 0:
            continue

        ic_mean = sub["ic"].mean()
        ic_std = sub["ic"].std()
        icir = ic_mean / ic_std if ic_std > 1e-10 else 0.0
        n_periods = len(sub)

        # Pooled
        valid = merged[[fcol, "market_return"]].dropna()
        if len(valid) < 30:
            continue
        pooled_ic, pooled_p = stats.spearmanr(valid[fcol], valid["market_return"])

        summary_records.append({
            "factor": fcol, "ic_mean": ic_mean, "ic_std": ic_std,
            "icir": icir, "n_periods": n_periods,
            "pooled_ic": pooled_ic, "pooled_pval": pooled_p, "n_obs": len(valid),
        })

        sig = "***" if pooled_p < 0.001 else ("**" if pooled_p < 0.01 else ("*" if pooled_p < 0.05 else ""))
        print(f"  {fcol:<35s}  {ic_mean:+.4f}  {ic_std:8.4f}  {icir:+.4f}  {pooled_ic:+.6f}  {pooled_p:10.2e}  {len(valid):>6d}  {sig}")

    summary_df = pd.DataFrame(summary_records).sort_values("pooled_ic", key=abs, ascending=False)

    # --- Quintile L/S ---
    print("\n  --- Quintile Long/Short Spreads ---")
    qs_records = []
    for fy in sorted(merged["formation_year"].unique()):
        sub = merged[merged["formation_year"] == fy]
        for fcol in FACTOR_COLS:
            valid = sub[[fcol, "market_return"]].dropna()
            if len(valid) < 50:
                continue
            try:
                valid["q"] = pd.qcut(valid[fcol], 5, labels=False, duplicates="drop")
            except ValueError:
                continue
            q_means = valid.groupby("q")["market_return"].mean()
            if len(q_means) >= 2:
                qs_records.append({
                    "formation_year": fy, "factor": fcol,
                    "q1_return": q_means.iloc[0], "q5_return": q_means.iloc[-1],
                    "spread": q_means.iloc[-1] - q_means.iloc[0],
                    "n": len(valid),
                })

    qs_df = pd.DataFrame(qs_records)

    # --- Save ---
    ic_df.to_csv(DATA / "market_oos_rolling_ic.csv", index=False)
    summary_df.to_csv(DATA / "market_oos_summary.csv", index=False)
    qs_df.to_csv(DATA / "market_oos_quintile.csv", index=False)
    print(f"\n  Saved to: market_oos_rolling_ic.csv, market_oos_summary.csv, market_oos_quintile.csv")

    # --- Final comparison with BPS proxy ---
    print("\n" + "=" * 80)
    print("COMPARISON: MARKET RETURNS vs BPS PROXY")
    print("=" * 80)

    bps_summary = None
    bps_path = DATA / "oos_icir_summary.csv"
    if bps_path.exists():
        bps_summary = pd.read_csv(bps_path)

    print(f"\n  {'Factor':<35s}  {'Market IC':>10s}  {'BPS IC':>10s}  {'Match?':>8s}")
    print("  " + "-" * 70)

    for _, row in summary_df.iterrows():
        fcol = row["factor"]
        mkt_ic = row["pooled_ic"]

        bps_ic = np.nan
        if bps_summary is not None:
            bps_row = bps_summary[bps_summary["factor"] == fcol]
            if len(bps_row) > 0:
                bps_ic = bps_row.iloc[0]["pooled_ic"]

        if pd.notna(bps_ic):
            same_sign = np.sign(mkt_ic) == np.sign(bps_ic)
            match_str = "YES" if same_sign else "NO !!!"
        else:
            match_str = "N/A"

        print(f"  {fcol:<35s}  {mkt_ic:+.6f}  {bps_ic:+.6f}  {match_str:>8s}")


def main():
    t0 = time.time()

    # Load tickers
    companies = pd.read_csv(DATA / "companies.csv")
    tickers = []
    for _, r in companies.iterrows():
        sc = str(r.get("sec_code", "")).strip()
        if len(sc) >= 4:
            tickers.append(sc[:4] + ".T")
    tickers = sorted(set(tickers))
    print(f"Total tickers: {len(tickers)}")

    # Step 1: Fetch prices
    price_df = fetch_april_prices(tickers)

    # Step 2: Compute annual returns
    returns = compute_annual_returns(price_df)

    # Step 3: Build features
    panel = build_feature_panel()

    # Step 4: OOS analysis
    run_oos_analysis(panel, returns)

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.0f} seconds")


if __name__ == "__main__":
    main()
