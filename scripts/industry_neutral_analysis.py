"""
Industry-Neutral Factor Analysis with Quintile Portfolios
==========================================================
Part A: Industry neutralization (percentile rank within industry)
Part B: Quintile portfolio construction (top 10 factors)
Part C: Multi-factor composite portfolio
Part D: Risk-adjusted evaluation
Part E: Double neutralization (industry + market cap)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats

DATA = "/Users/harann/edinet-screener/data"

# ============================================================
# 0. Load & merge data
# ============================================================
print("=" * 100)
print("0. DATA LOADING & FACTOR GENERATION")
print("=" * 100)

fin = pd.read_csv(f"{DATA}/financials_all.csv")
rat = pd.read_csv(f"{DATA}/ratios_all.csv")
prices = pd.read_csv(f"{DATA}/stock_prices.csv")
returns = pd.read_csv(f"{DATA}/historical_returns.csv")
companies = pd.read_csv(f"{DATA}/companies.csv")

print(f"financials: {fin.shape}, ratios: {rat.shape}, prices: {prices.shape}, "
      f"returns: {returns.shape}, companies: {companies.shape}")

# --- Build edinet_code -> ticker mapping ---
def sec_to_ticker(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s.isdigit():
        return None
    return f"{int(s)//10}.T"

companies["ticker"] = companies["sec_code"].apply(sec_to_ticker)
code_ticker = companies[["edinet_code", "ticker"]].dropna()
returns_merged = returns.merge(code_ticker, on="ticker", how="inner")

# --- Compute derived factors (from derived_factor_research.py logic) ---
full = fin.merge(rat, on=["edinet_code", "fiscal_year", "sec_code", "company_name", "industry"],
                 suffixes=("_fin", "_rat"), how="outer")
full = full.sort_values(["edinet_code", "fiscal_year"])


def pick(df: pd.DataFrame, base: str, prefer: str = "_fin") -> pd.Series:
    if base + prefer in df.columns:
        s = df[base + prefer]
        alt = base + ("_rat" if prefer == "_fin" else "_fin")
        if alt in df.columns:
            s = s.fillna(df[alt])
        return s
    if base in df.columns:
        return df[base]
    return pd.Series(np.nan, index=df.index)


def compute_derived(group: pd.DataFrame) -> dict:
    g = group.sort_values("fiscal_year")
    n = len(g)
    result = {"edinet_code": g["edinet_code"].iloc[0]}
    if n < 3:
        return result

    revenue = pick(g, "revenue")
    oi = pick(g, "operating_income")
    ni = pick(g, "net_income")
    ta = pick(g, "total_assets")
    na_ = pick(g, "net_assets")
    cf_op = pick(g, "cf_operating")
    cf_inv = pick(g, "cf_investing")
    cash = pick(g, "cash")
    bps = pick(g, "bps")
    eps = pick(g, "eps")
    div = pick(g, "dividend_per_share")
    payout = pick(g, "payout_ratio")
    roe = pick(g, "roe")
    roa = pick(g, "roa")
    op_margin = pick(g, "operating_margin")
    net_margin = pick(g, "net_margin")
    equity_ratio = pick(g, "equity_ratio")
    fcf = pick(g, "fcf")

    # Revenue growth stability
    rev_vals = revenue.dropna()
    if len(rev_vals) >= 3:
        rev_growth = rev_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan).dropna()
        if len(rev_growth) >= 2:
            result["revenue_growth_std"] = rev_growth.std()
            result["revenue_growth_mean"] = rev_growth.mean()
            mean_rg = rev_growth.mean()
            if abs(mean_rg) > 1e-10:
                result["revenue_growth_cv"] = rev_growth.std() / abs(mean_rg)

    # OI growth stability
    oi_vals = oi.dropna()
    if len(oi_vals) >= 3:
        oi_growth = oi_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan).dropna()
        if len(oi_growth) >= 2:
            result["oi_growth_std"] = oi_growth.std()
            result["oi_growth_mean"] = oi_growth.mean()

    # Margin improvement
    om_vals = op_margin.dropna()
    if len(om_vals) >= 4:
        result["margin_improvement"] = om_vals.iloc[-1] - om_vals.iloc[:3].mean()
    nm_vals = net_margin.dropna()
    if len(nm_vals) >= 4:
        result["net_margin_improvement"] = nm_vals.iloc[-1] - nm_vals.iloc[:3].mean()

    # Cash conversion
    cf_ni = pd.DataFrame({"cf": cf_op, "ni": ni}).dropna()
    cf_ni = cf_ni[cf_ni["ni"].abs() > 0]
    if len(cf_ni) >= 2:
        ratios_series = (cf_ni["cf"] / cf_ni["ni"]).replace([np.inf, -np.inf], np.nan).dropna()
        if len(ratios_series) >= 2:
            result["cash_conversion_avg"] = ratios_series.mean()
            result["cash_conversion_std"] = ratios_series.std()

    # Asset turnover
    at_data = pd.DataFrame({"rev": revenue, "ta": ta}).dropna()
    if len(at_data) >= 3:
        at = (at_data["rev"] / at_data["ta"]).replace([np.inf, -np.inf], np.nan).dropna()
        if len(at) >= 3:
            result["asset_turnover_latest"] = at.iloc[-1]
            result["asset_turnover_change"] = at.iloc[-1] - at.iloc[0]

    # Equity ratio
    er_vals = equity_ratio.dropna()
    if len(er_vals) >= 3:
        result["equity_ratio_latest"] = er_vals.iloc[-1]
        result["equity_ratio_change"] = er_vals.iloc[-1] - er_vals.iloc[0]

    # Payout stability
    po_vals = payout.dropna()
    if len(po_vals) >= 3:
        result["payout_std"] = po_vals.std()
        result["payout_mean"] = po_vals.mean()

    # Accrual gap
    if len(cf_ni) >= 2:
        gaps = ((cf_ni["ni"] - cf_ni["cf"]) / cf_ni["cf"].abs().replace(0, np.nan))
        gaps = gaps.replace([np.inf, -np.inf], np.nan).dropna()
        if len(gaps) >= 2:
            result["accrual_gap_avg"] = gaps.mean()

    # ROA stability
    roa_vals = roa.dropna()
    if len(roa_vals) >= 3:
        result["roa_std"] = roa_vals.std()
        result["roa_mean"] = roa_vals.mean()
        result["roa_latest"] = roa_vals.iloc[-1]

    # ROE stability
    roe_vals = roe.dropna()
    if len(roe_vals) >= 3:
        result["roe_std"] = roe_vals.std()
        result["roe_mean"] = roe_vals.mean()
        result["roe_latest"] = roe_vals.iloc[-1]

    # BPS CAGR
    bps_vals = bps.dropna()
    if len(bps_vals) >= 3 and bps_vals.iloc[0] > 0 and bps_vals.iloc[-1] > 0:
        years = len(bps_vals) - 1
        result["bps_cagr"] = (bps_vals.iloc[-1] / bps_vals.iloc[0]) ** (1.0 / years) - 1

    # FCF growth
    fcf_vals = fcf.dropna()
    if len(fcf_vals) >= 3:
        fcf_growth = fcf_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan).dropna()
        if len(fcf_growth) >= 2:
            result["fcf_growth_mean"] = fcf_growth.mean()
            result["fcf_growth_std"] = fcf_growth.std()

    # CF margin
    cf_rev = pd.DataFrame({"cf": cf_op, "rev": revenue}).dropna()
    cf_rev = cf_rev[cf_rev["rev"].abs() > 0]
    if len(cf_rev) >= 2:
        cfm = (cf_rev["cf"] / cf_rev["rev"]).replace([np.inf, -np.inf], np.nan).dropna()
        if len(cfm) >= 2:
            result["cf_margin_avg"] = cfm.mean()
            result["cf_margin_latest"] = cfm.iloc[-1]
            result["cf_margin_improvement"] = cfm.iloc[-1] - cfm.iloc[0]

    # CAPEX ratio
    capex_data = pd.DataFrame({"cf_inv": cf_inv, "cf_op": cf_op}).dropna()
    capex_data = capex_data[capex_data["cf_op"].abs() > 0]
    if len(capex_data) >= 2:
        capex_r = (capex_data["cf_inv"].abs() / capex_data["cf_op"]).replace(
            [np.inf, -np.inf], np.nan).dropna()
        if len(capex_r) >= 2:
            result["capex_ratio_avg"] = capex_r.mean()

    # NI growth
    ni_vals = ni.dropna()
    if len(ni_vals) >= 3:
        ni_growth = ni_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan).dropna()
        if len(ni_growth) >= 2:
            result["ni_growth_std"] = ni_growth.std()
            result["ni_growth_mean"] = ni_growth.mean()

    # EPS growth
    eps_vals = eps.dropna()
    if len(eps_vals) >= 3:
        eps_growth = eps_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan).dropna()
        if len(eps_growth) >= 2:
            result["eps_growth_std"] = eps_growth.std()
            result["eps_growth_mean"] = eps_growth.mean()

    # Dividend CAGR
    div_vals = div.dropna()
    if len(div_vals) >= 3 and (div_vals > 0).all() and div_vals.iloc[0] > 0:
        years_d = len(div_vals) - 1
        result["div_cagr"] = (div_vals.iloc[-1] / div_vals.iloc[0]) ** (1.0 / years_d) - 1

    # Operating leverage
    if len(rev_vals) >= 3 and len(oi_vals) >= 3:
        rg = rev_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan)
        og = oi_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan)
        aligned = pd.DataFrame({"rg": rg, "og": og}).dropna()
        if len(aligned) >= 3 and aligned["rg"].std() > 1e-10:
            result["operating_leverage"] = aligned["og"].std() / aligned["rg"].std()

    # Cash ratio
    cash_ta = pd.DataFrame({"cash": cash, "ta": ta}).dropna()
    cash_ta = cash_ta[cash_ta["ta"] > 0]
    if len(cash_ta) >= 2:
        cr = cash_ta["cash"] / cash_ta["ta"]
        result["cash_ratio_latest"] = cr.iloc[-1]
        result["cash_ratio_avg"] = cr.mean()

    # Net assets CAGR
    na_vals = na_.dropna()
    if len(na_vals) >= 3 and na_vals.iloc[0] > 0 and na_vals.iloc[-1] > 0:
        years_na = len(na_vals) - 1
        result["net_assets_cagr"] = (na_vals.iloc[-1] / na_vals.iloc[0]) ** (1.0 / years_na) - 1

    # Margin level
    if len(om_vals) >= 2:
        result["op_margin_avg"] = om_vals.mean()
        result["op_margin_latest"] = om_vals.iloc[-1]
    if len(nm_vals) >= 2:
        result["net_margin_avg"] = nm_vals.mean()
        result["net_margin_latest"] = nm_vals.iloc[-1]

    # EPS momentum
    if len(eps_vals) >= 3:
        avg_eps = eps_vals.iloc[:-1].mean()
        if abs(avg_eps) > 1e-10:
            result["eps_momentum"] = eps_vals.iloc[-1] / avg_eps

    # FCF to assets
    if len(fcf_vals) >= 1 and len(ta.dropna()) >= 1:
        ta_latest = ta.dropna().iloc[-1]
        if ta_latest > 0:
            result["fcf_to_assets"] = fcf_vals.iloc[-1] / ta_latest

    return result


print("Computing derived factors...")
derived_list = []
for code, grp in full.groupby("edinet_code"):
    derived_list.append(compute_derived(grp))
derived = pd.DataFrame(derived_list)
print(f"Derived factors shape: {derived.shape}")

# --- Merge all ---
analysis = derived.merge(returns_merged, on="edinet_code", how="inner")
analysis = analysis.merge(
    prices[["ticker", "priceToBook", "trailingPE", "forwardPE",
            "dividendYield", "debtToEquity", "beta", "marketCap", "industry"]],
    on="ticker", how="left"
)
# Also get industry from companies for edinet codes
analysis = analysis.merge(
    companies[["edinet_code", "industry"]].rename(columns={"industry": "industry_comp"}),
    on="edinet_code", how="left"
)
# Use industry from prices first, fallback to companies
analysis["industry"] = analysis["industry"].fillna(analysis["industry_comp"])
analysis.drop(columns=["industry_comp"], inplace=True)

print(f"Analysis dataset: {analysis.shape[0]} companies, industry coverage: {analysis['industry'].notna().sum()}")

# --- Define factor columns ---
return_cols = ["return_1y", "return_3y", "return_5y"]
meta_cols = ["edinet_code", "ticker"] + return_cols + [
    "priceToBook", "trailingPE", "forwardPE", "dividendYield",
    "debtToEquity", "beta", "marketCap", "industry"
]
# Market factors from prices
market_factor_cols = ["priceToBook", "trailingPE", "forwardPE", "dividendYield",
                      "debtToEquity", "beta"]
derived_factor_cols = [c for c in analysis.columns if c not in meta_cols]
all_factor_cols = derived_factor_cols + market_factor_cols
print(f"Total factor candidates: {len(all_factor_cols)} (derived: {len(derived_factor_cols)}, market: {len(market_factor_cols)})")

# --- Winsorize at 1%/99% ---
def winsorize(s: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    q_lo = s.quantile(lower)
    q_hi = s.quantile(upper)
    return s.clip(q_lo, q_hi)

for col in all_factor_cols + return_cols:
    valid = analysis[col].dropna()
    if len(valid) > 10:
        analysis[col] = winsorize(analysis[col])

print(f"\nData ready. N={len(analysis)}, Industries={analysis['industry'].nunique()}")

# ============================================================
# PART A: Industry Neutralization
# ============================================================
print("\n" + "=" * 100)
print("PART A: INDUSTRY NEUTRALIZATION")
print("=" * 100)

# Exclude industries with < 10 companies
industry_counts = analysis.groupby("industry").size()
small_industries = industry_counts[industry_counts < 10].index.tolist()
print(f"\nExcluding {len(small_industries)} industries with < 10 companies: {small_industries}")

# Create industry-neutral versions
for fcol in all_factor_cols:
    col_name = f"{fcol}_ineutral"
    # Only rank within industries with >= 10 companies
    def rank_within(group):
        if group.name in small_industries:
            return pd.Series(np.nan, index=group.index)
        return group.rank(pct=True)
    analysis[col_name] = analysis.groupby("industry")[fcol].transform(rank_within)

ineutral_cols = [f"{c}_ineutral" for c in all_factor_cols]

# Spearman correlation: raw vs industry-neutral
print(f"\n{'Factor':<32s} {'Horizon':<10s} {'Raw r':>8s} {'Raw p':>12s} {'Neutral r':>10s} {'Neutral p':>12s} {'Delta r':>9s} {'Retained':>10s}")
print("-" * 115)

corr_results = []
for fcol in all_factor_cols:
    ncol = f"{fcol}_ineutral"
    for rcol in return_cols:
        # Raw correlation
        valid_raw = analysis[[fcol, rcol]].dropna()
        if len(valid_raw) < 30:
            continue
        r_raw, p_raw = stats.spearmanr(valid_raw[fcol], valid_raw[rcol])

        # Neutral correlation
        valid_neu = analysis[[ncol, rcol]].dropna()
        if len(valid_neu) < 30:
            continue
        r_neu, p_neu = stats.spearmanr(valid_neu[ncol], valid_neu[rcol])

        delta = r_neu - r_raw
        retained = abs(r_neu) / max(abs(r_raw), 1e-10) if abs(r_raw) > 0.01 else np.nan

        corr_results.append({
            "factor": fcol,
            "return_horizon": rcol,
            "r_raw": r_raw,
            "p_raw": p_raw,
            "r_neutral": r_neu,
            "p_neutral": p_neu,
            "delta_r": delta,
            "retained_pct": retained,
            "n_raw": len(valid_raw),
            "n_neutral": len(valid_neu),
        })

corr_df = pd.DataFrame(corr_results)

# Print significant factors (sorted by |r_neutral|)
sig_neutral = corr_df[corr_df["p_neutral"] < 0.05].copy()
sig_neutral["abs_r_neu"] = sig_neutral["r_neutral"].abs()
sig_neutral = sig_neutral.sort_values("abs_r_neu", ascending=False)

for _, row in sig_neutral.head(60).iterrows():
    ret_str = f"{row['retained_pct']:.0%}" if pd.notna(row["retained_pct"]) else "N/A"
    print(f"{row['factor']:<32s} {row['return_horizon']:<10s} "
          f"{row['r_raw']:>+8.4f} {row['p_raw']:>12.2e} "
          f"{row['r_neutral']:>+10.4f} {row['p_neutral']:>12.2e} "
          f"{row['delta_r']:>+9.4f} {ret_str:>10s}")

# Summary table: factors that survive vs disappear
print(f"\n--- SUMMARY: Neutralization Impact ---")
print(f"Total factor-horizon pairs tested: {len(corr_df)}")
sig_raw = corr_df[corr_df["p_raw"] < 0.05]
sig_neu = corr_df[corr_df["p_neutral"] < 0.05]
survived = corr_df[(corr_df["p_raw"] < 0.05) & (corr_df["p_neutral"] < 0.05)]
disappeared = corr_df[(corr_df["p_raw"] < 0.05) & (corr_df["p_neutral"] >= 0.05)]
new_sig = corr_df[(corr_df["p_raw"] >= 0.05) & (corr_df["p_neutral"] < 0.05)]

print(f"Significant raw: {len(sig_raw)}")
print(f"Significant neutral: {len(sig_neu)}")
print(f"Survived neutralization: {len(survived)} (true cross-industry effect)")
print(f"Disappeared: {len(disappeared)} (industry proxy)")
print(f"Newly significant: {len(new_sig)} (hidden by industry noise)")

# ============================================================
# PART B: Quintile Portfolio Construction
# ============================================================
print("\n" + "=" * 100)
print("PART B: QUINTILE PORTFOLIO CONSTRUCTION (TOP 10 FACTORS)")
print("=" * 100)

# Select top 10 factors by avg |r_neutral| across horizons
factor_avg_r = corr_df.groupby("factor")["r_neutral"].apply(lambda x: x.abs().mean())
top10_factors = factor_avg_r.sort_values(ascending=False).head(10).index.tolist()

print(f"\nTop 10 factors (by avg |neutral r|):")
for i, f in enumerate(top10_factors, 1):
    avg_r = factor_avg_r[f]
    print(f"  {i:>2}. {f:<30s} avg|r|={avg_r:.4f}")


def quintile_portfolio_stats(df: pd.DataFrame, factor_col: str, return_col: str) -> dict | None:
    """Compute detailed quintile portfolio statistics."""
    valid = df[[factor_col, return_col]].dropna()
    if len(valid) < 50:
        return None

    valid["quintile"] = pd.qcut(valid[factor_col], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    if valid["quintile"].isna().all():
        return None

    result = {}
    for q in [1, 2, 3, 4, 5]:
        qdata = valid[valid["quintile"] == q][return_col]
        if len(qdata) < 5:
            continue
        result[f"Q{q}_mean"] = qdata.mean()
        result[f"Q{q}_median"] = qdata.median()
        result[f"Q{q}_std"] = qdata.std()
        result[f"Q{q}_sharpe"] = qdata.mean() / qdata.std() if qdata.std() > 0 else np.nan
        result[f"Q{q}_min"] = qdata.min()
        result[f"Q{q}_win_rate"] = (qdata > 0).mean()
        result[f"Q{q}_n"] = len(qdata)
        result[f"Q{q}_tail5pct"] = qdata.quantile(0.05)

    if "Q5_mean" in result and "Q1_mean" in result:
        result["spread_Q5_Q1"] = result["Q5_mean"] - result["Q1_mean"]
        # t-test for Q5 vs Q1
        q5_data = valid[valid["quintile"] == 5][return_col]
        q1_data = valid[valid["quintile"] == 1][return_col]
        t_stat, t_pval = stats.ttest_ind(q5_data, q1_data, equal_var=False)
        result["spread_t_stat"] = t_stat
        result["spread_p_value"] = t_pval

    # Information Coefficient (rank correlation)
    rank_factor = valid[factor_col].rank()
    rank_return = valid[return_col].rank()
    ic, ic_p = stats.spearmanr(rank_factor, rank_return)
    result["IC"] = ic
    result["IC_p"] = ic_p

    # Monotonicity
    q_means = valid.groupby("quintile")[return_col].mean()
    if len(q_means) >= 3:
        mono_r, _ = stats.spearmanr(q_means.index.astype(int), q_means.values)
        result["monotonicity"] = mono_r

    return result


# Run quintile analysis for top 10 factors
for fcol in top10_factors:
    ncol = f"{fcol}_ineutral"
    print(f"\n{'='*90}")
    print(f"Factor: {fcol}")
    print(f"{'='*90}")

    for rcol in return_cols:
        # Use industry-neutral version
        qstats = quintile_portfolio_stats(analysis, ncol, rcol)
        if qstats is None:
            print(f"  {rcol}: insufficient data")
            continue

        print(f"\n  {rcol}:")
        print(f"    {'Quintile':<10s} {'Mean':>10s} {'Median':>10s} {'Std':>10s} {'Sharpe':>10s} {'WinRate':>10s} {'Min':>10s} {'N':>6s}")
        print(f"    {'-'*76}")
        for q in [1, 2, 3, 4, 5]:
            if f"Q{q}_mean" in qstats:
                print(f"    Q{q:<9d} {qstats[f'Q{q}_mean']:>+10.4f} {qstats[f'Q{q}_median']:>+10.4f} "
                      f"{qstats[f'Q{q}_std']:>10.4f} {qstats[f'Q{q}_sharpe']:>10.4f} "
                      f"{qstats[f'Q{q}_win_rate']:>10.1%} {qstats[f'Q{q}_min']:>+10.4f} {qstats[f'Q{q}_n']:>6.0f}")

        spread = qstats.get("spread_Q5_Q1", np.nan)
        t_stat = qstats.get("spread_t_stat", np.nan)
        t_pval = qstats.get("spread_p_value", np.nan)
        ic = qstats.get("IC", np.nan)
        mono = qstats.get("monotonicity", np.nan)
        sig_mark = "***" if t_pval < 0.001 else "**" if t_pval < 0.01 else "*" if t_pval < 0.05 else ""
        print(f"    Long-Short (Q5-Q1): {spread:+.4f}  t={t_stat:.3f}  p={t_pval:.4e} {sig_mark}")
        print(f"    IC={ic:.4f}  Monotonicity={mono:.4f}")


# ============================================================
# PART C: Multi-Factor Composite Portfolio
# ============================================================
print("\n" + "=" * 100)
print("PART C: MULTI-FACTOR COMPOSITE PORTFOLIO")
print("=" * 100)

# Select top 5 factors
top5_factors = top10_factors[:5]
print(f"\nTop 5 factors for composite: {top5_factors}")

# Build composite: equal-weight rank average of industry-neutral factors
composite_cols = [f"{f}_ineutral" for f in top5_factors]
valid_mask = analysis[composite_cols].notna().all(axis=1)
composite_df = analysis[valid_mask].copy()

# Rank each factor (higher = better, assuming positive correlation direction)
for i, fcol in enumerate(top5_factors):
    ncol = f"{fcol}_ineutral"
    # Check if factor has positive or negative correlation with returns
    avg_r = corr_df[corr_df["factor"] == fcol]["r_neutral"].mean()
    if avg_r < 0:
        # Negative correlation: reverse rank so lower values get higher rank
        composite_df[f"rank_{i}"] = composite_df[ncol].rank(ascending=True, pct=True)
    else:
        composite_df[f"rank_{i}"] = composite_df[ncol].rank(ascending=True, pct=True)

rank_cols = [f"rank_{i}" for i in range(len(top5_factors))]
composite_df["composite_score"] = composite_df[rank_cols].mean(axis=1)

print(f"Composite dataset: {len(composite_df)} companies")

# Quintile analysis on composite
print(f"\n--- Composite Factor Quintile Analysis ---")
for rcol in return_cols:
    qstats = quintile_portfolio_stats(composite_df, "composite_score", rcol)
    if qstats is None:
        print(f"  {rcol}: insufficient data")
        continue

    print(f"\n  {rcol}:")
    print(f"    {'Quintile':<10s} {'Mean':>10s} {'Median':>10s} {'Std':>10s} {'Sharpe':>10s} {'WinRate':>10s} {'N':>6s}")
    print(f"    {'-'*62}")
    for q in [1, 2, 3, 4, 5]:
        if f"Q{q}_mean" in qstats:
            print(f"    Q{q:<9d} {qstats[f'Q{q}_mean']:>+10.4f} {qstats[f'Q{q}_median']:>+10.4f} "
                  f"{qstats[f'Q{q}_std']:>10.4f} {qstats[f'Q{q}_sharpe']:>10.4f} "
                  f"{qstats[f'Q{q}_win_rate']:>10.1%} {qstats[f'Q{q}_n']:>6.0f}")

    spread = qstats.get("spread_Q5_Q1", np.nan)
    t_stat = qstats.get("spread_t_stat", np.nan)
    t_pval = qstats.get("spread_p_value", np.nan)
    ic = qstats.get("IC", np.nan)
    mono = qstats.get("monotonicity", np.nan)
    sig_mark = "***" if t_pval < 0.001 else "**" if t_pval < 0.01 else "*" if t_pval < 0.05 else ""
    print(f"    Long-Short (Q5-Q1): {spread:+.4f}  t={t_stat:.3f}  p={t_pval:.4e} {sig_mark}")
    print(f"    IC={ic:.4f}  Monotonicity={mono:.4f}")

# Compare single vs composite
print(f"\n--- Single Factor vs Composite: Spread & Sharpe Comparison ---")
print(f"{'Factor':<32s} {'1Y Spread':>12s} {'1Y Sharpe Q5':>14s} {'3Y Spread':>12s} {'5Y Spread':>12s}")
print("-" * 90)

for fcol in top5_factors:
    ncol = f"{fcol}_ineutral"
    spreads = {}
    sharpes = {}
    for rcol in return_cols:
        qs = quintile_portfolio_stats(analysis, ncol, rcol)
        if qs:
            spreads[rcol] = qs.get("spread_Q5_Q1", np.nan)
            sharpes[rcol] = qs.get("Q5_sharpe", np.nan)
        else:
            spreads[rcol] = np.nan
            sharpes[rcol] = np.nan

    print(f"{fcol:<32s} {spreads.get('return_1y', np.nan):>+12.4f} "
          f"{sharpes.get('return_1y', np.nan):>14.4f} "
          f"{spreads.get('return_3y', np.nan):>+12.4f} "
          f"{spreads.get('return_5y', np.nan):>+12.4f}")

# Composite row
comp_spreads = {}
comp_sharpes = {}
for rcol in return_cols:
    qs = quintile_portfolio_stats(composite_df, "composite_score", rcol)
    if qs:
        comp_spreads[rcol] = qs.get("spread_Q5_Q1", np.nan)
        comp_sharpes[rcol] = qs.get("Q5_sharpe", np.nan)
    else:
        comp_spreads[rcol] = np.nan
        comp_sharpes[rcol] = np.nan

print(f"{'** COMPOSITE **':<32s} {comp_spreads.get('return_1y', np.nan):>+12.4f} "
      f"{comp_sharpes.get('return_1y', np.nan):>14.4f} "
      f"{comp_spreads.get('return_3y', np.nan):>+12.4f} "
      f"{comp_spreads.get('return_5y', np.nan):>+12.4f}")


# ============================================================
# PART D: Risk-Adjusted Evaluation
# ============================================================
print("\n" + "=" * 100)
print("PART D: RISK-ADJUSTED EVALUATION")
print("=" * 100)

print(f"\n--- Risk Metrics by Quintile (Composite Factor, return_1y) ---")
rcol = "return_1y"
valid = composite_df[["composite_score", rcol]].dropna()
valid["quintile"] = pd.qcut(valid["composite_score"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")

print(f"\n{'Quintile':<10s} {'Mean':>10s} {'Std(Vol)':>10s} {'Sharpe':>10s} {'Tail5%':>10s} {'WinRate':>10s} {'MaxDD':>10s} {'N':>6s}")
print("-" * 76)

for q in [1, 2, 3, 4, 5]:
    qdata = valid[valid["quintile"] == q][rcol]
    if len(qdata) < 5:
        continue
    mean_r = qdata.mean()
    std_r = qdata.std()
    sharpe = mean_r / std_r if std_r > 0 else np.nan
    tail5 = qdata.quantile(0.05)
    win_rate = (qdata > 0).mean()
    max_dd = qdata.min()  # worst individual stock return
    n = len(qdata)
    print(f"Q{q:<9d} {mean_r:>+10.4f} {std_r:>10.4f} {sharpe:>10.4f} {tail5:>+10.4f} {win_rate:>10.1%} {max_dd:>+10.4f} {n:>6d}")

# Do the same for each top factor individually
for fcol in top5_factors:
    ncol = f"{fcol}_ineutral"
    print(f"\n--- Risk Metrics: {fcol} (return_1y) ---")
    valid_f = analysis[[ncol, rcol]].dropna()
    if len(valid_f) < 50:
        print("  insufficient data")
        continue
    valid_f["quintile"] = pd.qcut(valid_f[ncol], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")

    print(f"{'Quintile':<10s} {'Mean':>10s} {'Std(Vol)':>10s} {'Sharpe':>10s} {'Tail5%':>10s} {'WinRate':>10s} {'N':>6s}")
    print("-" * 62)
    for q in [1, 2, 3, 4, 5]:
        qdata = valid_f[valid_f["quintile"] == q][rcol]
        if len(qdata) < 5:
            continue
        mean_r = qdata.mean()
        std_r = qdata.std()
        sharpe = mean_r / std_r if std_r > 0 else np.nan
        tail5 = qdata.quantile(0.05)
        win_rate = (qdata > 0).mean()
        n = len(qdata)
        print(f"Q{q:<9d} {mean_r:>+10.4f} {std_r:>10.4f} {sharpe:>10.4f} {tail5:>+10.4f} {win_rate:>10.1%} {n:>6d}")


# ============================================================
# PART E: Double Neutralization (Industry + Market Cap)
# ============================================================
print("\n" + "=" * 100)
print("PART E: DOUBLE NEUTRALIZATION (INDUSTRY + MARKET CAP)")
print("=" * 100)

# Split market cap into 3 groups
analysis["mcap_group"] = pd.qcut(
    analysis["marketCap"].rank(method="first"),
    3, labels=["Small", "Mid", "Large"]
)
analysis["ind_mcap_cell"] = analysis["industry"].astype(str) + "_" + analysis["mcap_group"].astype(str)

cell_counts = analysis.groupby("ind_mcap_cell").size()
small_cells = cell_counts[cell_counts < 10].index.tolist()
print(f"Total cells (industry x mcap): {len(cell_counts)}")
print(f"Cells with < 10 companies (excluded from ranking): {len(small_cells)}")

# Double-neutralize all factors
for fcol in all_factor_cols:
    col_name = f"{fcol}_dneutral"

    def rank_within_cell(group):
        if group.name in small_cells:
            return pd.Series(np.nan, index=group.index)
        return group.rank(pct=True)

    analysis[col_name] = analysis.groupby("ind_mcap_cell")[fcol].transform(rank_within_cell)

# Compute correlations for double-neutral factors
dneutral_results = []
for fcol in all_factor_cols:
    dcol = f"{fcol}_dneutral"
    ncol = f"{fcol}_ineutral"
    for rcol in return_cols:
        # Double-neutral
        valid_d = analysis[[dcol, rcol]].dropna()
        if len(valid_d) < 30:
            continue
        r_d, p_d = stats.spearmanr(valid_d[dcol], valid_d[rcol])

        # Raw
        valid_raw = analysis[[fcol, rcol]].dropna()
        r_raw, p_raw = (np.nan, np.nan)
        if len(valid_raw) >= 30:
            r_raw, p_raw = stats.spearmanr(valid_raw[fcol], valid_raw[rcol])

        # Industry-neutral
        valid_n = analysis[[ncol, rcol]].dropna()
        r_n, p_n = (np.nan, np.nan)
        if len(valid_n) >= 30:
            r_n, p_n = stats.spearmanr(valid_n[ncol], valid_n[rcol])

        dneutral_results.append({
            "factor": fcol,
            "return_horizon": rcol,
            "r_raw": r_raw,
            "p_raw": p_raw,
            "r_ineutral": r_n,
            "p_ineutral": p_n,
            "r_dneutral": r_d,
            "p_dneutral": p_d,
        })

dneutral_df = pd.DataFrame(dneutral_results)

# Final ranking: factors that survive double neutralization
sig_double = dneutral_df[dneutral_df["p_dneutral"] < 0.05].copy()
sig_double["abs_r_d"] = sig_double["r_dneutral"].abs()
sig_double = sig_double.sort_values("abs_r_d", ascending=False)

print(f"\n--- Factors surviving double neutralization (p<0.05): {len(sig_double)} ---")
print(f"{'Factor':<32s} {'Horizon':<10s} {'Raw r':>8s} {'Ind-Neu r':>10s} {'Dbl-Neu r':>10s} {'p(dbl)':>12s}")
print("-" * 95)

for _, row in sig_double.head(40).iterrows():
    print(f"{row['factor']:<32s} {row['return_horizon']:<10s} "
          f"{row['r_raw']:>+8.4f} {row['r_ineutral']:>+10.4f} "
          f"{row['r_dneutral']:>+10.4f} {row['p_dneutral']:>12.2e}")

# Final factor ranking: average |r_dneutral| across horizons
final_ranking = dneutral_df.groupby("factor").agg(
    avg_abs_r_raw=("r_raw", lambda x: x.abs().mean()),
    avg_abs_r_ind=("r_ineutral", lambda x: x.abs().mean()),
    avg_abs_r_dbl=("r_dneutral", lambda x: x.abs().mean()),
    min_p_dbl=("p_dneutral", "min"),
    horizons_sig=("p_dneutral", lambda x: (x < 0.05).sum()),
).sort_values("avg_abs_r_dbl", ascending=False)

print(f"\n{'='*100}")
print("FINAL FACTOR RANKING (by avg |double-neutral r|)")
print(f"{'='*100}")
print(f"{'Rank':<6s} {'Factor':<32s} {'|r| Raw':>8s} {'|r| Ind':>8s} {'|r| Dbl':>8s} {'min p(dbl)':>12s} {'#Sig':>6s}")
print("-" * 88)

for i, (factor, row) in enumerate(final_ranking.head(20).iterrows(), 1):
    print(f"{i:<6d} {factor:<32s} {row['avg_abs_r_raw']:>8.4f} {row['avg_abs_r_ind']:>8.4f} "
          f"{row['avg_abs_r_dbl']:>8.4f} {row['min_p_dbl']:>12.2e} {row['horizons_sig']:>6.0f}")

# ============================================================
# PART F: Practical Recommendations
# ============================================================
print("\n" + "=" * 100)
print("PART F: PRACTICAL RECOMMENDATIONS FOR SCREENER")
print("=" * 100)

# Identify top factors that pass all filters
# Criteria: double-neutral p < 0.05 in at least 2 horizons, |r| > 0.04
robust_factors = final_ranking[
    (final_ranking["horizons_sig"] >= 2) & (final_ranking["avg_abs_r_dbl"] > 0.04)
].head(10)

print(f"\nRecommended factors for screener ({len(robust_factors)} factors):")
print(f"These survived industry + market-cap neutralization with p<0.05 in >=2 return horizons.\n")

total_weight = len(robust_factors)
for i, (factor, row) in enumerate(robust_factors.iterrows(), 1):
    weight = round(100 / total_weight)

    # Get direction (positive or negative correlation with returns)
    factor_corrs = dneutral_df[dneutral_df["factor"] == factor]
    avg_sign = factor_corrs["r_dneutral"].mean()
    direction = "higher is better" if avg_sign > 0 else "lower is better"

    print(f"  {i:>2}. {factor:<30s}  weight={weight}%  ({direction})")
    print(f"      |r| raw={row['avg_abs_r_raw']:.4f}  ind-neutral={row['avg_abs_r_ind']:.4f}  "
          f"double-neutral={row['avg_abs_r_dbl']:.4f}  sig_horizons={row['horizons_sig']:.0f}/3")

# Proposed weight scheme
print(f"\nProposed scoring formula:")
print(f"  composite_score = weighted_avg(rank(factor_i)) for i in recommended factors")
print(f"  Equal weight ({round(100/max(len(robust_factors),1))}% each) as baseline")
print(f"  Consider up-weighting factors with higher |r| double-neutral values")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
