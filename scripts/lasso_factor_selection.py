"""
LASSO / Elastic Net Factor Selection Analysis
- Part A: Data preparation (derived + market factors, winsorize, standardize)
- Part B: LassoCV (L1)
- Part C: ElasticNetCV (L1+L2)
- Part D: Bootstrap LASSO stability
- Part E: OLS comparison
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LassoCV, ElasticNetCV, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import statsmodels.api as sm

DATA = "/Users/harann/edinet-screener/data"

# ============================================================
# Part A: Data Preparation
# ============================================================
print("=" * 100)
print("PART A: DATA PREPARATION")
print("=" * 100)

fin = pd.read_csv(f"{DATA}/financials_all.csv")
rat = pd.read_csv(f"{DATA}/ratios_all.csv")
prices = pd.read_csv(f"{DATA}/stock_prices.csv")
returns = pd.read_csv(f"{DATA}/historical_returns.csv")
companies = pd.read_csv(f"{DATA}/companies.csv")

print(f"financials: {fin.shape}, ratios: {rat.shape}, prices: {prices.shape}, returns: {returns.shape}")

# --- Merge financials + ratios ---
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
    """Compute derived factors for a single edinet_code group."""
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
            mean_og = oi_growth.mean()
            if abs(mean_og) > 1e-10:
                result["oi_growth_cv"] = oi_growth.std() / abs(mean_og)

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
        ratios_vals = (cf_ni["cf"] / cf_ni["ni"]).replace([np.inf, -np.inf], np.nan).dropna()
        if len(ratios_vals) >= 2:
            result["cash_conversion_avg"] = ratios_vals.mean()
            result["cash_conversion_std"] = ratios_vals.std()

    # Asset turnover
    at_data = pd.DataFrame({"rev": revenue, "ta": ta}).dropna()
    if len(at_data) >= 3:
        at = (at_data["rev"] / at_data["ta"]).replace([np.inf, -np.inf], np.nan).dropna()
        if len(at) >= 3:
            result["asset_turnover_latest"] = at.iloc[-1]
            result["asset_turnover_change"] = at.iloc[-1] - at.iloc[0]

    # Debt/equity ratio trend
    er_vals = equity_ratio.dropna()
    if len(er_vals) >= 3:
        result["debt_ratio_change"] = (1 - er_vals.iloc[-1]) - (1 - er_vals.iloc[0])
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
        capex_r = (capex_data["cf_inv"].abs() / capex_data["cf_op"]).replace([np.inf, -np.inf], np.nan).dropna()
        if len(capex_r) >= 2:
            result["capex_ratio_avg"] = capex_r.mean()
            result["capex_ratio_latest"] = capex_r.iloc[-1]

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
        reinv = (reinv_data["cf_inv"].abs() / reinv_data["ni"]).replace([np.inf, -np.inf], np.nan).dropna()
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

    # Revenue per asset latest
    if len(at_data) >= 1:
        result["revenue_per_asset_latest"] = (at_data["rev"] / at_data["ta"]).iloc[-1]

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

    # CI-NI gap
    ci = pick(g, "comprehensive_income")
    ci_ni = pd.DataFrame({"ci": ci, "ni": ni}).dropna()
    if len(ci_ni) >= 2:
        ci_ni_valid = ci_ni[ci_ni["ni"].abs() > 0]
        if len(ci_ni_valid) >= 2:
            gap = ((ci_ni_valid["ci"] - ci_ni_valid["ni"]) / ci_ni_valid["ni"].abs())
            gap = gap.replace([np.inf, -np.inf], np.nan).dropna()
            if len(gap) >= 2:
                result["ci_ni_gap_avg"] = gap.mean()

    return result

print("Computing derived factors...")
derived_list = []
for code, grp in full.groupby("edinet_code"):
    derived_list.append(compute_derived(grp))
derived = pd.DataFrame(derived_list)

# --- Merge with returns via prices (edinet_code -> ticker) ---
# prices has edinet_code and ticker
prices_map = prices[["edinet_code", "ticker"]].dropna().drop_duplicates("edinet_code")
derived_with_ticker = derived.merge(prices_map, on="edinet_code", how="inner")
analysis = derived_with_ticker.merge(returns, on="ticker", how="inner")

# Add market-based factors from stock_prices
market_factors = ["marketCap", "priceToBook", "forwardPE", "dividendYield", "beta",
                  "returnOnEquity", "debtToEquity"]
market_data = prices[["edinet_code"] + [c for c in market_factors if c in prices.columns]].copy()
if "marketCap" in market_data.columns:
    market_data["log_marketCap"] = np.log1p(market_data["marketCap"])
analysis = analysis.merge(market_data, on="edinet_code", how="left")

print(f"Derived factors shape: {derived.shape}")
print(f"Analysis dataset (with returns): {analysis.shape}")

# --- Define factor columns ---
return_cols = ["return_1y", "return_3y", "return_5y"]
exclude_cols = {"edinet_code", "ticker", "return_1y", "return_3y", "return_5y", "marketCap"}
factor_cols = [c for c in analysis.columns if c not in exclude_cols and analysis[c].dtype in [np.float64, np.int64, float, int]]

print(f"Total candidate factors: {len(factor_cols)}")
print(f"Factor names: {factor_cols}")

# --- Winsorize at 1%/99% ---
def winsorize(s, lower=0.01, upper=0.99):
    q_lo = s.quantile(lower)
    q_hi = s.quantile(upper)
    return s.clip(q_lo, q_hi)

for col in factor_cols + return_cols:
    valid = analysis[col].dropna()
    if len(valid) > 10:
        analysis[col] = winsorize(analysis[col])

# --- Median imputation for LASSO ---
for col in factor_cols:
    median_val = analysis[col].median()
    analysis[col] = analysis[col].fillna(median_val)

# --- StandardScaler ---
scaler = StandardScaler()
X_all = analysis[factor_cols].copy()
X_scaled = pd.DataFrame(scaler.fit_transform(X_all), columns=factor_cols, index=analysis.index)

print(f"\nAfter imputation+scaling: X shape={X_scaled.shape}, no NaN={not X_scaled.isna().any().any()}")

# Check return availability
for rc in return_cols:
    n_valid = analysis[rc].notna().sum()
    print(f"  {rc}: {n_valid} valid observations")


# ============================================================
# Part B: LASSO (L1)
# ============================================================
print("\n" + "=" * 100)
print("PART B: LassoCV (L1 Regularization)")
print("=" * 100)

lasso_results = {}
for target in return_cols:
    mask = analysis[target].notna()
    X = X_scaled.loc[mask]
    y = analysis.loc[mask, target]

    if len(y) < 50:
        print(f"\n  {target}: too few samples ({len(y)}), skipping")
        continue

    lasso = LassoCV(cv=5, n_alphas=100, random_state=42, max_iter=10000)
    lasso.fit(X, y)

    coefs = pd.Series(lasso.coef_, index=factor_cols)
    nonzero = coefs[coefs.abs() > 1e-8].sort_values(key=abs, ascending=False)

    # CV R^2
    cv_scores = cross_val_score(
        LassoCV(cv=5, n_alphas=100, random_state=42, max_iter=10000),
        X, y, cv=5, scoring="r2"
    )

    lasso_results[target] = {
        "model": lasso,
        "nonzero_coefs": nonzero,
        "best_alpha": lasso.alpha_,
        "cv_r2_mean": cv_scores.mean(),
        "cv_r2_std": cv_scores.std(),
        "n_samples": len(y),
        "n_selected": len(nonzero),
    }

    print(f"\n--- {target} ---")
    print(f"  Samples: {len(y)}")
    print(f"  Best alpha: {lasso.alpha_:.6f}")
    print(f"  CV R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print(f"  Non-zero factors: {len(nonzero)} / {len(factor_cols)}")
    print(f"  Selected factors (by |coef|):")
    for fname, coef_val in nonzero.items():
        print(f"    {fname:<35s} coef={coef_val:+.6f}")


# ============================================================
# Part C: Elastic Net (L1 + L2)
# ============================================================
print("\n" + "=" * 100)
print("PART C: ElasticNetCV (L1 + L2 Regularization)")
print("=" * 100)

l1_ratios = [0.1, 0.3, 0.5, 0.7, 0.9, 0.95]
enet_results = {}

for target in return_cols:
    mask = analysis[target].notna()
    X = X_scaled.loc[mask]
    y = analysis.loc[mask, target]

    if len(y) < 50:
        print(f"\n  {target}: too few samples ({len(y)}), skipping")
        continue

    enet = ElasticNetCV(cv=5, l1_ratio=l1_ratios, n_alphas=100, random_state=42, max_iter=10000)
    enet.fit(X, y)

    coefs = pd.Series(enet.coef_, index=factor_cols)
    nonzero = coefs[coefs.abs() > 1e-8].sort_values(key=abs, ascending=False)

    cv_scores = cross_val_score(
        ElasticNetCV(cv=5, l1_ratio=l1_ratios, n_alphas=100, random_state=42, max_iter=10000),
        X, y, cv=5, scoring="r2"
    )

    enet_results[target] = {
        "model": enet,
        "nonzero_coefs": nonzero,
        "best_alpha": enet.alpha_,
        "best_l1_ratio": enet.l1_ratio_,
        "cv_r2_mean": cv_scores.mean(),
        "cv_r2_std": cv_scores.std(),
        "n_samples": len(y),
        "n_selected": len(nonzero),
    }

    print(f"\n--- {target} ---")
    print(f"  Samples: {len(y)}")
    print(f"  Best alpha: {enet.alpha_:.6f}, Best l1_ratio: {enet.l1_ratio_}")
    print(f"  CV R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print(f"  Non-zero factors: {len(nonzero)} / {len(factor_cols)}")
    print(f"  Selected factors (by |coef|):")
    for fname, coef_val in nonzero.items():
        print(f"    {fname:<35s} coef={coef_val:+.6f}")

# --- Comparison: LASSO vs Elastic Net ---
print("\n" + "-" * 100)
print("LASSO vs Elastic Net: Factor Comparison")
print("-" * 100)

for target in return_cols:
    if target not in lasso_results or target not in enet_results:
        continue

    lasso_set = set(lasso_results[target]["nonzero_coefs"].index)
    enet_set = set(enet_results[target]["nonzero_coefs"].index)
    both = lasso_set & enet_set
    lasso_only = lasso_set - enet_set
    enet_only = enet_set - lasso_set

    print(f"\n--- {target} ---")
    print(f"  LASSO selected:       {len(lasso_set)}")
    print(f"  Elastic Net selected: {len(enet_set)}")
    print(f"  Both (consistent):    {len(both)}")
    if both:
        print(f"    {sorted(both)}")
    if lasso_only:
        print(f"  LASSO only:           {sorted(lasso_only)}")
    if enet_only:
        print(f"  Elastic Net only:     {sorted(enet_only)}")


# ============================================================
# Part D: Bootstrap LASSO Stability
# ============================================================
print("\n" + "=" * 100)
print("PART D: Bootstrap LASSO Stability (100 iterations)")
print("=" * 100)

N_BOOT = 100
boot_results = {}

for target in return_cols:
    mask = analysis[target].notna()
    X = X_scaled.loc[mask]
    y = analysis.loc[mask, target]

    if len(y) < 50:
        continue

    n = len(y)
    selection_counts = pd.Series(0, index=factor_cols)
    coef_sums = pd.Series(0.0, index=factor_cols)

    rng = np.random.RandomState(42)
    for i in range(N_BOOT):
        idx = rng.choice(n, size=int(n * 0.8), replace=False)
        X_boot = X.iloc[idx]
        y_boot = y.iloc[idx]

        lasso_boot = LassoCV(cv=5, n_alphas=50, random_state=i, max_iter=10000)
        lasso_boot.fit(X_boot, y_boot)

        coefs = pd.Series(lasso_boot.coef_, index=factor_cols)
        selected = coefs.abs() > 1e-8
        selection_counts[selected] += 1
        coef_sums += coefs

    avg_coefs = coef_sums / N_BOOT
    stability = selection_counts.sort_values(ascending=False)

    boot_results[target] = {
        "selection_counts": stability,
        "avg_coefs": avg_coefs,
    }

    print(f"\n--- {target} ---")
    print(f"  {'Factor':<35s} {'Freq':>6s} {'Pct':>8s} {'Avg Coef':>12s} {'Stable':>8s}")
    print(f"  {'-'*75}")
    for fname, cnt in stability.items():
        if cnt > 0:
            pct = cnt / N_BOOT * 100
            avg_c = avg_coefs[fname]
            stable = "***" if cnt >= 80 else "**" if cnt >= 50 else "*" if cnt >= 20 else ""
            print(f"  {fname:<35s} {cnt:>6d} {pct:>7.1f}% {avg_c:>+12.6f} {stable:>8s}")


# ============================================================
# Part E: OLS Comparison
# ============================================================
print("\n" + "=" * 100)
print("PART E: OLS vs LASSO R2 Comparison")
print("=" * 100)

comparison_table = []

for target in return_cols:
    if target not in lasso_results:
        continue

    mask = analysis[target].notna()
    X_full = X_scaled.loc[mask]
    y = analysis.loc[mask, target]

    # Full OLS (all factors)
    X_full_const = sm.add_constant(X_full)
    ols_full = sm.OLS(y, X_full_const).fit()

    # LASSO-selected OLS
    lasso_factors = list(lasso_results[target]["nonzero_coefs"].index)
    if len(lasso_factors) == 0:
        comparison_table.append({
            "target": target,
            "ols_full_r2": ols_full.rsquared,
            "ols_full_adj_r2": ols_full.rsquared_adj,
            "ols_full_n_factors": len(factor_cols),
            "lasso_r2": np.nan,
            "lasso_adj_r2": np.nan,
            "lasso_n_factors": 0,
            "r2_drop": np.nan,
            "lasso_cv_r2": lasso_results[target]["cv_r2_mean"],
        })
        continue

    X_lasso = X_full[lasso_factors]
    X_lasso_const = sm.add_constant(X_lasso)
    ols_lasso = sm.OLS(y, X_lasso_const).fit()

    # CV R2 for LASSO-selected OLS
    lr = LinearRegression()
    cv_lasso_ols = cross_val_score(lr, X_lasso, y, cv=5, scoring="r2")

    # CV R2 for full OLS
    cv_full_ols = cross_val_score(lr, X_full, y, cv=5, scoring="r2")

    comparison_table.append({
        "target": target,
        "ols_full_r2": ols_full.rsquared,
        "ols_full_adj_r2": ols_full.rsquared_adj,
        "ols_full_n_factors": len(factor_cols),
        "ols_full_cv_r2": cv_full_ols.mean(),
        "lasso_ols_r2": ols_lasso.rsquared,
        "lasso_ols_adj_r2": ols_lasso.rsquared_adj,
        "lasso_n_factors": len(lasso_factors),
        "lasso_ols_cv_r2": cv_lasso_ols.mean(),
        "lasso_cv_r2": lasso_results[target]["cv_r2_mean"],
        "r2_drop": ols_full.rsquared - ols_lasso.rsquared,
        "adj_r2_drop": ols_full.rsquared_adj - ols_lasso.rsquared_adj,
    })

    print(f"\n--- {target} ---")
    print(f"  Full OLS ({len(factor_cols)} factors):")
    print(f"    R2={ols_full.rsquared:.4f}, Adj-R2={ols_full.rsquared_adj:.4f}, CV-R2={cv_full_ols.mean():.4f}")
    print(f"  LASSO-selected OLS ({len(lasso_factors)} factors):")
    print(f"    R2={ols_lasso.rsquared:.4f}, Adj-R2={ols_lasso.rsquared_adj:.4f}, CV-R2={cv_lasso_ols.mean():.4f}")
    print(f"  LASSO CV-R2: {lasso_results[target]['cv_r2_mean']:.4f}")
    print(f"  R2 drop (full->LASSO-selected): {ols_full.rsquared - ols_lasso.rsquared:.4f}")
    print(f"  Adj-R2 drop: {ols_full.rsquared_adj - ols_lasso.rsquared_adj:.4f}")
    print(f"  ** Overfitting indicator: Full OLS CV-R2={cv_full_ols.mean():.4f} vs in-sample R2={ols_full.rsquared:.4f} (gap={ols_full.rsquared - cv_full_ols.mean():.4f})")

    # OLS coefficients for LASSO-selected factors
    print(f"\n  LASSO-selected OLS coefficients:")
    print(f"  {'Factor':<35s} {'OLS Coef':>10s} {'p-value':>12s} {'Sig':>5s}")
    for var in lasso_factors:
        coef = ols_lasso.params[var]
        p = ols_lasso.pvalues[var]
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "." if p < 0.1 else ""
        print(f"  {var:<35s} {coef:>+10.4f} {p:>12.4e} {sig:>5s}")


# ============================================================
# Summary Table
# ============================================================
print("\n" + "=" * 100)
print("SUMMARY: R2 COMPARISON TABLE")
print("=" * 100)

comp_df = pd.DataFrame(comparison_table)
print(f"\n{'Target':<12s} {'Full OLS R2':>12s} {'Full CV-R2':>12s} {'LASSO OLS R2':>13s} {'LASSO CV-R2':>12s} {'N factors':>10s} {'Overfit Gap':>12s}")
print("-" * 90)
for _, row in comp_df.iterrows():
    full_cv = row.get("ols_full_cv_r2", np.nan)
    lasso_ols_r2 = row.get("lasso_ols_r2", np.nan)
    lasso_ols_cv = row.get("lasso_ols_cv_r2", np.nan)
    n_sel = int(row.get("lasso_n_factors", 0))
    overfit_gap = row["ols_full_r2"] - full_cv if not np.isnan(full_cv) else np.nan
    print(f"{row['target']:<12s} {row['ols_full_r2']:>12.4f} {full_cv:>12.4f} {lasso_ols_r2:>13.4f} {row['lasso_cv_r2']:>12.4f} {n_sel:>10d} {overfit_gap:>12.4f}")


# ============================================================
# Final Recommendation: Minimum Reliable Factor Set
# ============================================================
print("\n" + "=" * 100)
print("FINAL RECOMMENDATION: Minimum Reliable Factor Set")
print("=" * 100)

# Criteria: selected by BOTH LASSO and Elastic Net for at least 2 return horizons,
# AND bootstrap stability >= 50%
all_consistent = {}  # factor -> count of horizons where consistent
all_boot_freq = {}   # factor -> max bootstrap frequency across horizons

for target in return_cols:
    if target in lasso_results and target in enet_results:
        lasso_set = set(lasso_results[target]["nonzero_coefs"].index)
        enet_set = set(enet_results[target]["nonzero_coefs"].index)
        both = lasso_set & enet_set
        for f in both:
            all_consistent[f] = all_consistent.get(f, 0) + 1

    if target in boot_results:
        counts = boot_results[target]["selection_counts"]
        for f, cnt in counts.items():
            freq = cnt / N_BOOT
            all_boot_freq[f] = max(all_boot_freq.get(f, 0), freq)

# Tier 1: Consistent across methods AND stable
print("\n[Tier 1] Consistent (LASSO+ENet, >=2 horizons) AND Bootstrap stable (>=50%)")
print(f"  {'Factor':<35s} {'Horizons':>8s} {'Max Boot%':>10s}")
print(f"  {'-'*58}")
tier1 = []
for f, count in sorted(all_consistent.items(), key=lambda x: -x[1]):
    boot_pct = all_boot_freq.get(f, 0) * 100
    if count >= 2 and boot_pct >= 50:
        print(f"  {f:<35s} {count:>8d} {boot_pct:>9.1f}%")
        tier1.append(f)

if not tier1:
    print("  (none met both criteria)")

# Tier 2: Consistent across methods OR highly stable in bootstrap
print(f"\n[Tier 2] Consistent (>=2 horizons) OR Bootstrap stable (>=80%)")
print(f"  {'Factor':<35s} {'Horizons':>8s} {'Max Boot%':>10s}")
print(f"  {'-'*58}")
tier2 = []
for f in set(list(all_consistent.keys()) + list(all_boot_freq.keys())):
    if f in tier1:
        continue
    count = all_consistent.get(f, 0)
    boot_pct = all_boot_freq.get(f, 0) * 100
    if count >= 2 or boot_pct >= 80:
        print(f"  {f:<35s} {count:>8d} {boot_pct:>9.1f}%")
        tier2.append(f)

if not tier2:
    print("  (none met criteria beyond Tier 1)")

# Tier 3: Selected at least once with moderate stability
print(f"\n[Tier 3] Selected in at least 1 horizon, Bootstrap >=30%")
print(f"  {'Factor':<35s} {'Horizons':>8s} {'Max Boot%':>10s}")
print(f"  {'-'*58}")
tier3 = []
for f in set(list(all_consistent.keys()) + list(all_boot_freq.keys())):
    if f in tier1 or f in tier2:
        continue
    count = all_consistent.get(f, 0)
    boot_pct = all_boot_freq.get(f, 0) * 100
    if count >= 1 or boot_pct >= 30:
        print(f"  {f:<35s} {count:>8d} {boot_pct:>9.1f}%")
        tier3.append(f)

if not tier3:
    print("  (none)")

print(f"\n{'='*100}")
print(f"MINIMUM RELIABLE FACTOR SET (Tier 1 + Tier 2): {len(tier1) + len(tier2)} factors")
print(f"{'='*100}")
for f in tier1 + tier2:
    print(f"  - {f}")

print("\nDone.")
