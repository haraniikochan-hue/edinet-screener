"""
ファクター直交化・PCA分析スクリプト
Part A: ファクター相関マトリクス
Part B: PCA（主成分分析）
Part C: 逐次残差化（Fama-MacBeth風）
Part D: 冗長ファクターの特定
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import os

DATA = "/Users/harann/edinet-screener/data"

# ============================================================
# 0. Data Loading & Factor Generation
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

# --- edinet_code -> ticker mapping ---
def sec_to_ticker(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s.isdigit():
        return None
    return f"{int(s) // 10}.T"

companies["ticker"] = companies["sec_code"].apply(sec_to_ticker)
code_ticker = companies[["edinet_code", "ticker"]].dropna()
returns_merged = returns.merge(code_ticker, on="ticker", how="inner")

# --- Merge fin + rat for time-series derived factors ---
full = fin.merge(rat, on=["edinet_code", "fiscal_year", "sec_code", "company_name", "industry"],
                 suffixes=("_fin", "_rat"), how="outer")
full = full.sort_values(["edinet_code", "fiscal_year"])


def pick(df, base, prefer="_fin"):
    if base + prefer in df.columns:
        s = df[base + prefer]
        alt = base + ("_rat" if prefer == "_fin" else "_fin")
        if alt in df.columns:
            s = s.fillna(df[alt])
        return s
    if base in df.columns:
        return df[base]
    return pd.Series(np.nan, index=df.index)


def compute_derived(group):
    """Compute time-series derived factors for a single edinet_code."""
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
        ratios_cc = (cf_ni["cf"] / cf_ni["ni"]).replace([np.inf, -np.inf], np.nan).dropna()
        if len(ratios_cc) >= 2:
            result["cash_conversion_avg"] = ratios_cc.mean()
            result["cash_conversion_std"] = ratios_cc.std()

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

    # Payout
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

    # ROA
    roa_vals = roa.dropna()
    if len(roa_vals) >= 3:
        result["roa_std"] = roa_vals.std()
        result["roa_mean"] = roa_vals.mean()
        result["roa_latest"] = roa_vals.iloc[-1]

    # ROE
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

    # CAPEX ratio
    capex_data = pd.DataFrame({"cf_inv": cf_inv, "cf_op": cf_op}).dropna()
    capex_data = capex_data[capex_data["cf_op"].abs() > 0]
    if len(capex_data) >= 2:
        capex_r = (capex_data["cf_inv"].abs() / capex_data["cf_op"]).replace(
            [np.inf, -np.inf], np.nan
        ).dropna()
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

    # Reinvestment rate
    reinv_data = pd.DataFrame({"cf_inv": cf_inv, "ni": ni}).dropna()
    reinv_data = reinv_data[reinv_data["ni"].abs() > 0]
    if len(reinv_data) >= 2:
        reinv = (reinv_data["cf_inv"].abs() / reinv_data["ni"]).replace(
            [np.inf, -np.inf], np.nan
        ).dropna()
        if len(reinv) >= 2:
            result["reinvestment_rate_avg"] = reinv.mean()

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

    # Margin levels
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

    # Consecutive dividend years
    divs = pick(g, "dividend_per_share").dropna()
    consec_div = 0
    for v in divs.values[::-1]:
        if v > 0:
            consec_div += 1
        else:
            break
    result["consecutive_dividend_years"] = consec_div

    # Consecutive increase years
    div_arr = divs.values
    consec_increase = 0
    for i in range(len(div_arr) - 1, 0, -1):
        if div_arr[i] > div_arr[i - 1]:
            consec_increase += 1
        else:
            break
    result["consecutive_increase_years"] = consec_increase

    # Has loss year
    ni_check = ni.dropna()
    result["has_loss_year"] = int((ni_check < 0).any()) if len(ni_check) > 0 else np.nan

    # BPS increase years
    bps_arr = bps.dropna().values
    bps_increase_years = 0
    for i in range(len(bps_arr) - 1, 0, -1):
        if bps_arr[i] > bps_arr[i - 1]:
            bps_increase_years += 1
        else:
            break
    result["bps_increase_years"] = bps_increase_years

    return result


print("Computing derived factors...")
derived_list = []
for code, grp in full.groupby("edinet_code"):
    derived_list.append(compute_derived(grp))

derived = pd.DataFrame(derived_list)
print(f"Derived factors shape: {derived.shape}")

# --- Merge with returns and prices ---
analysis = derived.merge(returns_merged, on="edinet_code", how="inner")
prices["ticker"] = prices["ticker"].astype(str)
analysis = analysis.merge(
    prices[["ticker", "priceToBook", "trailingPE", "forwardPE",
            "dividendYield", "debtToEquity", "beta", "marketCap"]],
    on="ticker", how="left"
)

# Add log_marketCap
analysis["log_marketCap"] = np.log1p(analysis["marketCap"])

# FCF yield
analysis["fcf_yield"] = np.where(
    analysis["marketCap"] > 0,
    analysis["fcf_to_assets"] * analysis.get("total_assets", 0),  # approximate
    np.nan,
)
# Better: use raw fcf if available via prices
if "freeCashflow" in prices.columns:
    prices_fcf = prices[["ticker", "freeCashflow"]].copy()
    analysis = analysis.merge(prices_fcf, on="ticker", how="left")
    analysis["fcf_yield"] = np.where(
        analysis["marketCap"] > 0,
        analysis["freeCashflow"] / analysis["marketCap"],
        np.nan,
    )

# --- Define factor columns ---
return_cols = ["return_1y", "return_3y", "return_5y"]
exclude_cols = {"edinet_code", "ticker", "return_1y", "return_3y", "return_5y", "freeCashflow"}

factor_cols = [c for c in analysis.columns if c not in exclude_cols and analysis[c].dtype in [np.float64, np.int64, float, int]]
# Remove factors with too few non-null values
factor_cols = [c for c in factor_cols if analysis[c].notna().sum() >= 100]

print(f"\nTotal candidate factors: {len(factor_cols)}")
print(f"Analysis dataset size: {len(analysis)}")

# --- Winsorize at 1%/99% ---
def winsorize(s, lower=0.01, upper=0.99):
    q_lo = s.quantile(lower)
    q_hi = s.quantile(upper)
    return s.clip(q_lo, q_hi)

for col in factor_cols + return_cols:
    valid = analysis[col].dropna()
    if len(valid) > 10:
        analysis[col] = winsorize(analysis[col])

print(f"Factors after filtering: {len(factor_cols)}")
print(f"Factor list: {factor_cols}")


# ============================================================
# Part A: Factor Correlation Matrix
# ============================================================
print("\n" + "=" * 100)
print("PART A: FACTOR CORRELATION MATRIX (Spearman)")
print("=" * 100)

# Compute Spearman correlation matrix among all factors
factor_data = analysis[factor_cols].copy()
corr_matrix = factor_data.corr(method="spearman")

print(f"\nCorrelation matrix shape: {corr_matrix.shape}")

# Find high-correlation pairs (|r| > 0.7)
high_corr_pairs = []
for i in range(len(factor_cols)):
    for j in range(i + 1, len(factor_cols)):
        r = corr_matrix.iloc[i, j]
        if abs(r) > 0.7:
            high_corr_pairs.append({
                "factor_1": factor_cols[i],
                "factor_2": factor_cols[j],
                "spearman_r": r,
            })

high_corr_df = pd.DataFrame(high_corr_pairs).sort_values("spearman_r", key=abs, ascending=False)
print(f"\nHigh-correlation pairs (|r| > 0.7): {len(high_corr_df)}")
print("-" * 90)
print(f"{'Factor 1':<35s} {'Factor 2':<35s} {'Spearman r':>12s}")
print("-" * 90)
for _, row in high_corr_df.iterrows():
    print(f"{row['factor_1']:<35s} {row['factor_2']:<35s} {row['spearman_r']:>+12.4f}")

# Identify correlation clusters using simple graph approach
print(f"\n--- Correlation Clusters (|r| > 0.7) ---")
from collections import defaultdict

adj = defaultdict(set)
for _, row in high_corr_df.iterrows():
    adj[row["factor_1"]].add(row["factor_2"])
    adj[row["factor_2"]].add(row["factor_1"])

visited = set()
clusters = []
for node in adj:
    if node not in visited:
        cluster = set()
        stack = [node]
        while stack:
            n = stack.pop()
            if n not in visited:
                visited.add(n)
                cluster.add(n)
                stack.extend(adj[n] - visited)
        clusters.append(sorted(cluster))

for i, cl in enumerate(clusters, 1):
    print(f"\n  Cluster {i} ({len(cl)} factors):")
    for f in cl:
        print(f"    - {f}")

# Also show moderate correlations (0.5 < |r| <= 0.7) for reference
moderate_pairs = []
for i in range(len(factor_cols)):
    for j in range(i + 1, len(factor_cols)):
        r = corr_matrix.iloc[i, j]
        if 0.5 < abs(r) <= 0.7:
            moderate_pairs.append({
                "factor_1": factor_cols[i],
                "factor_2": factor_cols[j],
                "spearman_r": r,
            })

mod_df = pd.DataFrame(moderate_pairs).sort_values("spearman_r", key=abs, ascending=False)
print(f"\n--- Moderate correlation pairs (0.5 < |r| <= 0.7): {len(mod_df)} ---")
for _, row in mod_df.head(20).iterrows():
    print(f"  {row['factor_1']:<35s} {row['factor_2']:<35s} {row['spearman_r']:>+.4f}")


# ============================================================
# Part B: PCA (Principal Component Analysis)
# ============================================================
print("\n" + "=" * 100)
print("PART B: PCA (PRINCIPAL COMPONENT ANALYSIS)")
print("=" * 100)

# Prepare data: median imputation + standardization
factor_data_pca = analysis[factor_cols].copy()
# Report missingness
miss = factor_data_pca.isnull().sum()
print(f"\nMissingness summary (top 10 by missing count):")
for col in miss.sort_values(ascending=False).head(10).index:
    pct = miss[col] / len(factor_data_pca) * 100
    print(f"  {col:<35s}: {miss[col]:>5d} ({pct:.1f}%)")

# Median imputation
for col in factor_cols:
    median_val = factor_data_pca[col].median()
    factor_data_pca[col] = factor_data_pca[col].fillna(median_val)

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(factor_data_pca)
X_scaled_df = pd.DataFrame(X_scaled, columns=factor_cols, index=factor_data_pca.index)

# PCA
pca = PCA()
pca.fit(X_scaled)

# Cumulative explained variance
cum_var = np.cumsum(pca.explained_variance_ratio_)
print(f"\n--- Cumulative Explained Variance ---")
print(f"{'PC':<6s} {'Variance Ratio':>15s} {'Cumulative':>12s}")
print("-" * 40)
for i in range(min(20, len(cum_var))):
    print(f"PC{i + 1:<4d} {pca.explained_variance_ratio_[i]:>15.4f} {cum_var[i]:>12.4f}")

# Thresholds
for thresh in [0.80, 0.90, 0.95]:
    n_comp = np.argmax(cum_var >= thresh) + 1
    print(f"  Components for {thresh * 100:.0f}% variance: {n_comp}")

# Factor loadings for top PCs
n_top_pc = min(6, len(pca.components_))
loadings = pd.DataFrame(pca.components_[:n_top_pc].T,
                         columns=[f"PC{i + 1}" for i in range(n_top_pc)],
                         index=factor_cols)

print(f"\n--- Top Factor Loadings (top {n_top_pc} PCs) ---")
for pc_name in loadings.columns:
    pc_loadings = loadings[pc_name].abs().sort_values(ascending=False)
    print(f"\n  {pc_name} (explained variance: {pca.explained_variance_ratio_[int(pc_name[2:]) - 1]:.4f}):")
    print(f"  {'Factor':<35s} {'Loading':>10s}")
    for factor_name in pc_loadings.head(8).index:
        val = loadings.loc[factor_name, pc_name]
        print(f"  {factor_name:<35s} {val:>+10.4f}")

# Interpret PCs
print(f"\n--- PC Interpretation ---")
for i in range(min(5, n_top_pc)):
    pc_name = f"PC{i + 1}"
    top_pos = loadings[pc_name].sort_values(ascending=False).head(5)
    top_neg = loadings[pc_name].sort_values(ascending=True).head(5)
    print(f"\n  {pc_name} (var: {pca.explained_variance_ratio_[i]:.4f}):")
    print(f"    Positive loadings: {', '.join([f'{n}({v:+.3f})' for n, v in top_pos.items()])}")
    print(f"    Negative loadings: {', '.join([f'{n}({v:+.3f})' for n, v in top_neg.items()])}")

# PC scores vs returns correlation
pc_scores = pca.transform(X_scaled)
print(f"\n--- PC Scores vs Returns (Spearman) ---")
print(f"{'PC':<8s}", end="")
for rcol in return_cols:
    print(f" {rcol:>15s}", end="")
print()
print("-" * (8 + 16 * len(return_cols)))

for i in range(min(10, len(pca.components_))):
    pc_name = f"PC{i + 1}"
    print(f"{pc_name:<8s}", end="")
    for rcol in return_cols:
        valid_mask = analysis[rcol].notna()
        if valid_mask.sum() < 30:
            print(f" {'N/A':>15s}", end="")
            continue
        r, p = stats.spearmanr(pc_scores[valid_mask, i], analysis.loc[valid_mask, rcol])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f" {r:>+8.4f}{sig:>4s}p={p:.3f}", end="")
    print()


# ============================================================
# Part C: Sequential Residualization (Fama-MacBeth style)
# ============================================================
print("\n" + "=" * 100)
print("PART C: SEQUENTIAL RESIDUALIZATION (Fama-MacBeth style)")
print("=" * 100)

# Target return
target_return = "return_1y"

# Ordering: log_marketCap -> roe_std/roa_std -> consecutive_dividend_years ->
#           consecutive_increase_years -> forwardPE -> ...
# We'll determine order based on raw correlation strength, but start with log_marketCap
raw_corrs = {}
for col in factor_cols:
    valid = analysis[[col, target_return]].dropna()
    if len(valid) >= 30:
        r, p = stats.spearmanr(valid[col], valid[target_return])
        raw_corrs[col] = (r, p)

# Sort by |r| for the ordered sequence, but put log_marketCap first
sorted_factors = sorted(raw_corrs.keys(), key=lambda x: abs(raw_corrs[x][0]), reverse=True)

# Move log_marketCap to front if present
priority_order = ["log_marketCap", "roe_std", "roa_std", "consecutive_dividend_years",
                  "consecutive_increase_years", "forwardPE"]
ordered = []
remaining = list(sorted_factors)
for pf in priority_order:
    if pf in remaining:
        ordered.append(pf)
        remaining.remove(pf)
ordered.extend(remaining)

print(f"\nResidualizing in order ({len(ordered)} factors):")
print(f"Target: {target_return}")

# Sequential residualization
# Step 1: start with raw return
# Step k: regress factor_k on [factor_1, ..., factor_{k-1}] -> residual
#         regress return on [factor_1, ..., factor_{k-1}] -> residual
#         compute correlation of residual_factor vs residual_return
# Also track cumulative R^2

# Prepare clean data - exclude factors with >30% missing to avoid tiny sample
high_miss_factors = [c for c in ordered
                     if analysis[c].notna().sum() / len(analysis) < 0.7]
print(f"\nExcluding {len(high_miss_factors)} high-missingness factors from residualization: "
      f"{high_miss_factors}")
resid_cols_available = [c for c in ordered
                        if c in analysis.columns and c not in high_miss_factors]
resid_data = analysis[resid_cols_available + [target_return]].dropna()
print(f"Sample size for residualization: {len(resid_data)}")

incremental_r2 = []
cumulative_r2 = 0.0
controlled = []

y = resid_data[target_return].values

print(f"\n{'Step':<5s} {'Factor':<35s} {'Raw r':>8s} {'Resid r':>10s} {'Incr R2':>10s} {'Cum R2':>10s}")
print("-" * 85)

for step, factor_name in enumerate(resid_cols_available[:20], 1):  # top 20 for readability
    raw_r, raw_p = raw_corrs.get(factor_name, (np.nan, np.nan))

    if len(controlled) == 0:
        # First factor: just raw correlation + R^2
        x = resid_data[factor_name].values.reshape(-1, 1)
        lr = LinearRegression().fit(x, y)
        r2 = lr.score(x, y)
        incr = r2
        cumulative_r2 = r2

        resid_r = raw_r
    else:
        # Residualize current factor and return against controlled set
        X_ctrl = resid_data[controlled].values

        # R^2 without this factor
        lr_without = LinearRegression().fit(X_ctrl, y)
        r2_without = lr_without.score(X_ctrl, y)

        # R^2 with this factor
        X_with = np.column_stack([X_ctrl, resid_data[factor_name].values])
        lr_with = LinearRegression().fit(X_with, y)
        r2_with = lr_with.score(X_with, y)

        incr = r2_with - r2_without
        cumulative_r2 = r2_with

        # Residual correlation
        lr_f = LinearRegression().fit(X_ctrl, resid_data[factor_name].values)
        factor_resid = resid_data[factor_name].values - lr_f.predict(X_ctrl)

        lr_y = LinearRegression().fit(X_ctrl, y)
        y_resid = y - lr_y.predict(X_ctrl)

        if np.std(factor_resid) > 1e-10 and np.std(y_resid) > 1e-10:
            resid_r, _ = stats.spearmanr(factor_resid, y_resid)
        else:
            resid_r = 0.0

    controlled.append(factor_name)

    incremental_r2.append({
        "step": step,
        "factor": factor_name,
        "raw_r": raw_r,
        "residual_r": resid_r,
        "incremental_r2": incr,
        "cumulative_r2": cumulative_r2,
    })

    print(f"{step:<5d} {factor_name:<35s} {raw_r:>+8.4f} {resid_r:>+10.4f} {incr:>10.6f} {cumulative_r2:>10.6f}")

incr_df = pd.DataFrame(incremental_r2)

# Highlight factors with incremental R^2 < 0.001 (near zero)
print(f"\n--- Factors with negligible incremental R2 (<0.001) ---")
negligible = incr_df[incr_df["incremental_r2"] < 0.001]
for _, row in negligible.iterrows():
    print(f"  Step {row['step']}: {row['factor']:<35s} incr_R2={row['incremental_r2']:.6f}")


# ============================================================
# Part D: Redundant Factor Identification
# ============================================================
print("\n" + "=" * 100)
print("PART D: REDUNDANT FACTOR IDENTIFICATION")
print("=" * 100)

# Strategy:
# 1. Factors in the same PCA cluster (high loading on same PC)
# 2. AND incremental R^2 near zero after controlling for earlier factors
# -> Redundant

# For each factor, find which PC it loads most on
factor_primary_pc = {}
for f in factor_cols:
    if f in loadings.index:
        abs_loadings = loadings.loc[f].abs()
        primary_pc = abs_loadings.idxmax()
        primary_loading = loadings.loc[f, primary_pc]
        factor_primary_pc[f] = (primary_pc, primary_loading)

# Build redundancy table
print(f"\n--- Factor Analysis Summary ---")
print(f"{'Factor':<35s} {'Primary PC':>10s} {'Loading':>10s} {'Raw r':>8s} {'Incr R2':>10s} {'Verdict':>12s}")
print("-" * 100)

independent_factors = []
redundant_factors = []

for f in factor_cols:
    pc_info = factor_primary_pc.get(f, ("?", 0.0))
    raw_r_val = raw_corrs.get(f, (0.0, 1.0))[0]
    incr_row = incr_df[incr_df["factor"] == f]
    incr_val = incr_row["incremental_r2"].values[0] if len(incr_row) > 0 else np.nan

    # High-corr cluster membership
    in_cluster = any(f in cl for cl in clusters)

    # Verdict
    if pd.isna(incr_val):
        verdict = "NOT_TESTED"
    elif incr_val < 0.0005 and in_cluster:
        verdict = "REDUNDANT"
        redundant_factors.append(f)
    elif incr_val < 0.001 and in_cluster:
        verdict = "LIKELY_REDUND"
        redundant_factors.append(f)
    elif incr_val < 0.001:
        verdict = "LOW_VALUE"
    elif abs(raw_r_val) < 0.03 and incr_val < 0.002:
        verdict = "WEAK"
    else:
        verdict = "INDEPENDENT"
        independent_factors.append(f)

    print(f"{f:<35s} {pc_info[0]:>10s} {pc_info[1]:>+10.4f} {raw_r_val:>+8.4f} "
          f"{incr_val if not pd.isna(incr_val) else 0:>10.6f} {verdict:>12s}")

# Within each cluster, recommend which to keep
print(f"\n--- Cluster Redundancy Resolution ---")
for i, cl in enumerate(clusters, 1):
    print(f"\n  Cluster {i}: {cl}")
    # Keep the one with highest |raw_r| with return_1y
    best_factor = None
    best_r = 0
    for f in cl:
        r_val = abs(raw_corrs.get(f, (0.0, 1.0))[0])
        if r_val > best_r:
            best_r = r_val
            best_factor = f
    for f in cl:
        r_val = raw_corrs.get(f, (0.0, 1.0))[0]
        keep = " << KEEP (highest |r|)" if f == best_factor else "    drop"
        print(f"    {f:<35s} raw_r={r_val:>+.4f} {keep}")

# Final recommended independent factor set
print(f"\n{'=' * 100}")
print("FINAL RECOMMENDED INDEPENDENT FACTOR SET")
print(f"{'=' * 100}")

# Deduplicate: from independent_factors + best from each cluster
final_set = set(independent_factors)
# Ensure cluster representatives are included
for i, cl in enumerate(clusters):
    best_factor = None
    best_r = 0
    for f in cl:
        r_val = abs(raw_corrs.get(f, (0.0, 1.0))[0])
        if r_val > best_r:
            best_r = r_val
            best_factor = f
    if best_factor:
        final_set.add(best_factor)

# Remove truly redundant ones
for f in redundant_factors:
    # Only remove if there's a better representative in the same cluster
    for cl in clusters:
        if f in cl:
            best = max(cl, key=lambda x: abs(raw_corrs.get(x, (0.0, 1.0))[0]))
            if f != best:
                final_set.discard(f)

# Sort by |raw_r|
final_list = sorted(final_set, key=lambda x: abs(raw_corrs.get(x, (0.0, 1.0))[0]), reverse=True)

print(f"\nTotal original factors: {len(factor_cols)}")
print(f"Redundant factors removed: {len(factor_cols) - len(final_list)}")
print(f"Final independent factors: {len(final_list)}")

print(f"\n{'Rank':<6s} {'Factor':<35s} {'Raw r (1y)':>12s} {'Primary PC':>12s} {'Loading':>10s}")
print("-" * 80)
for rank, f in enumerate(final_list, 1):
    r_val = raw_corrs.get(f, (0.0, 1.0))[0]
    pc_info = factor_primary_pc.get(f, ("?", 0.0))
    print(f"{rank:<6d} {f:<35s} {r_val:>+12.4f} {pc_info[0]:>12s} {pc_info[1]:>+10.4f}")

# Also check these final factors for return correlation across horizons
print(f"\n--- Final Factor Set: Correlation with Returns ---")
print(f"{'Factor':<35s} {'return_1y':>12s} {'return_3y':>12s} {'return_5y':>12s}")
print("-" * 75)
for f in final_list:
    print(f"{f:<35s}", end="")
    for rcol in return_cols:
        valid = analysis[[f, rcol]].dropna()
        if len(valid) >= 30:
            r, p = stats.spearmanr(valid[f], valid[rcol])
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f" {r:>+8.4f}{sig:<3s}", end="")
        else:
            print(f" {'N/A':>11s}", end="")
    print()

print(f"\n{'=' * 100}")
print("ANALYSIS COMPLETE")
print(f"{'=' * 100}")
