"""
FDR補正 + ブートストラップ信頼区間 + 効果量分析
- Part A: 全ファクター(派生50+既存9) x リターン3期間 の Spearman 相関 + BH-FDR 補正
- Part B: FDR補正後上位20ファクターの95% BCaブートストラップCI
- Part C: Cohen's d 効果量 (Q1 vs Q5)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import bootstrap
from statsmodels.stats.multitest import multipletests

DATA = "/Users/harann/edinet-screener/data"

# ============================================================
# 1. データ読込
# ============================================================
print("=" * 100)
print("1. DATA LOADING")
print("=" * 100)

fin = pd.read_csv(f"{DATA}/financials_all.csv")
rat = pd.read_csv(f"{DATA}/ratios_all.csv")
prices = pd.read_csv(f"{DATA}/stock_prices.csv")
returns = pd.read_csv(f"{DATA}/historical_returns.csv")
companies = pd.read_csv(f"{DATA}/companies.csv")

print(f"financials: {fin.shape}, ratios: {rat.shape}, prices: {prices.shape}")
print(f"returns: {returns.shape}, companies: {companies.shape}")

# ============================================================
# 2. edinet_code <-> ticker マッピング
# ============================================================
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
print(f"returns with edinet_code: {returns_merged.shape}")

# ============================================================
# 3. 派生ファクター生成（derived_factor_research.py のロジック流用）
# ============================================================
print("\n" + "=" * 100)
print("2. COMPUTING DERIVED FACTORS (50 factors)")
print("=" * 100)

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
    cf_fin_col = pick(g, "cf_financing")
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
            mean_rg = rev_growth.mean()
            result["revenue_growth_mean"] = mean_rg
            if abs(mean_rg) > 1e-10:
                result["revenue_growth_cv"] = rev_growth.std() / abs(mean_rg)

    # OI growth stability
    oi_vals = oi.dropna()
    if len(oi_vals) >= 3:
        oi_growth = oi_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan).dropna()
        if len(oi_growth) >= 2:
            result["oi_growth_std"] = oi_growth.std()
            mean_og = oi_growth.mean()
            result["oi_growth_mean"] = mean_og
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
        gaps = ((cf_ni["ni"] - cf_ni["cf"]) / cf_ni["cf"].abs().replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).dropna()
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
            gap = ((ci_ni_valid["ci"] - ci_ni_valid["ni"]) / ci_ni_valid["ni"].abs()).replace([np.inf, -np.inf], np.nan).dropna()
            if len(gap) >= 2:
                result["ci_ni_gap_avg"] = gap.mean()

    # --- robustness_check.py 由来の追加ファクター ---
    # 配当連続年数
    divs = div.dropna()
    consec_div = 0
    for v in divs.values[::-1]:
        if v > 0:
            consec_div += 1
        else:
            break
    result["consecutive_dividend_years"] = consec_div

    # 増配年数
    div_raw = div.dropna().values
    consec_increase = 0
    for i in range(len(div_raw) - 1, 0, -1):
        if div_raw[i] > div_raw[i - 1]:
            consec_increase += 1
        else:
            break
    result["consecutive_increase_years"] = consec_increase

    # 赤字年有無
    ni_raw = ni.dropna()
    result["has_loss_year"] = int((ni_raw < 0).any()) if len(ni_raw) > 0 else np.nan

    # BPS増加年数
    bps_raw = bps.dropna().values
    bps_inc = 0
    for i in range(len(bps_raw) - 1, 0, -1):
        if bps_raw[i] > bps_raw[i - 1]:
            bps_inc += 1
        else:
            break
    result["bps_increase_years"] = bps_inc

    return result

print("Computing derived factors per edinet_code...")
derived_list = []
for code, grp in full.groupby("edinet_code"):
    derived_list.append(compute_derived(grp))

derived = pd.DataFrame(derived_list)
print(f"Derived factors shape: {derived.shape}")

# ============================================================
# 4. リターンと結合 + 既存ファクター追加
# ============================================================
analysis = derived.merge(returns_merged, on="edinet_code", how="inner")

# stock_prices から既存ファクター追加
existing_factor_cols_from_prices = ["priceToBook", "trailingPE", "forwardPE",
                                     "dividendYield", "debtToEquity", "beta",
                                     "marketCap", "returnOnEquity", "freeCashflow"]
available_price_cols = [c for c in existing_factor_cols_from_prices if c in prices.columns]
prices["ticker"] = prices["ticker"].astype(str)
analysis = analysis.merge(prices[["ticker"] + available_price_cols], on="ticker", how="left")

# log_marketCap
if "marketCap" in analysis.columns:
    analysis["log_marketCap"] = np.log1p(analysis["marketCap"])

print(f"Analysis dataset: {analysis.shape}")

# ============================================================
# 5. ファクター列定義
# ============================================================
return_cols = ["return_1y", "return_3y", "return_5y"]
exclude = {"edinet_code", "ticker"} | set(return_cols)
factor_cols = [c for c in analysis.columns if c not in exclude]
print(f"Total factor count: {len(factor_cols)}")

# ============================================================
# 6. Winsorize (1%/99%)
# ============================================================
def winsorize(s, lower=0.01, upper=0.99):
    q_lo = s.quantile(lower)
    q_hi = s.quantile(upper)
    return s.clip(q_lo, q_hi)

for col in factor_cols + return_cols:
    valid = analysis[col].dropna()
    if len(valid) > 10:
        analysis[col] = winsorize(analysis[col])

# ============================================================
# PART A: 全ファクター Spearman 相関 + BH-FDR 補正
# ============================================================
print("\n" + "=" * 100)
print("PART A: SPEARMAN CORRELATIONS + BENJAMINI-HOCHBERG FDR CORRECTION")
print("=" * 100)

raw_results = []
for fcol in factor_cols:
    for rcol in return_cols:
        valid = analysis[[fcol, rcol]].dropna()
        if len(valid) < 30:
            continue
        corr, pval = stats.spearmanr(valid[fcol], valid[rcol])
        raw_results.append({
            "factor": fcol,
            "return_horizon": rcol,
            "spearman_r": corr,
            "p_value": pval,
            "n": len(valid),
        })

corr_df = pd.DataFrame(raw_results)
total_tests = len(corr_df)
print(f"Total tests performed: {total_tests}")

# BH-FDR correction
reject, q_values, _, _ = multipletests(corr_df["p_value"].values, alpha=0.05, method="fdr_bh")
corr_df["q_value"] = q_values
corr_df["fdr_significant"] = reject

# Before/after comparison
n_sig_before = (corr_df["p_value"] < 0.05).sum()
n_sig_after = corr_df["fdr_significant"].sum()
print(f"\nBefore FDR correction (p < 0.05): {n_sig_before} significant tests")
print(f"After  FDR correction (q < 0.05): {n_sig_after} significant tests")
print(f"Tests removed by FDR: {n_sig_before - n_sig_after}")

# FDR-significant results sorted by |r|
fdr_sig = corr_df[corr_df["fdr_significant"]].copy()
fdr_sig = fdr_sig.sort_values("spearman_r", key=abs, ascending=False)

print(f"\n--- FDR-significant factors (q < 0.05): {len(fdr_sig)} tests ---")
print(f"{'Factor':<35s} {'Horizon':<12s} {'r':>8s} {'p-value':>12s} {'q-value':>12s} {'N':>6s}")
print("-" * 90)
for _, row in fdr_sig.iterrows():
    print(f"{row['factor']:<35s} {row['return_horizon']:<12s} {row['spearman_r']:>8.4f} "
          f"{row['p_value']:>12.2e} {row['q_value']:>12.4f} {row['n']:>6.0f}")

# Unique FDR-significant factors
fdr_unique_factors = fdr_sig["factor"].unique()
print(f"\nUnique FDR-significant factors: {len(fdr_unique_factors)}")

# ============================================================
# PART B: ブートストラップ 95% BCa CI（上位20ファクター）
# ============================================================
print("\n" + "=" * 100)
print("PART B: BOOTSTRAP 95% BCa CONFIDENCE INTERVALS (top 20 factors)")
print("=" * 100)

# Select top 20 by |r| from FDR-significant results
# Use unique factor-horizon pairs, rank by |r|
top20_candidates = fdr_sig.head(20).copy() if len(fdr_sig) >= 20 else fdr_sig.copy()
if len(top20_candidates) < 20:
    # Supplement from non-FDR-significant but strongest
    remaining = corr_df[~corr_df.index.isin(top20_candidates.index)].copy()
    remaining = remaining.sort_values("spearman_r", key=abs, ascending=False)
    needed = 20 - len(top20_candidates)
    top20_candidates = pd.concat([top20_candidates, remaining.head(needed)])

print(f"Analyzing {len(top20_candidates)} factor-horizon pairs")
print(f"Bootstrap: 10,000 resamples, BCa method\n")

N_BOOT = 10000

def spearman_statistic(x, y):
    """Compute Spearman r for bootstrap."""
    r, _ = stats.spearmanr(x, y)
    return r

bootstrap_results = []
for idx, row in top20_candidates.iterrows():
    fcol = row["factor"]
    rcol = row["return_horizon"]
    valid = analysis[[fcol, rcol]].dropna()

    x_data = valid[fcol].values
    y_data = valid[rcol].values

    # BCa bootstrap
    try:
        res = bootstrap(
            (x_data, y_data),
            statistic=spearman_statistic,
            n_resamples=N_BOOT,
            confidence_level=0.95,
            method="BCa",
            paired=True,
            random_state=42,
        )
        ci_low = res.confidence_interval.low
        ci_high = res.confidence_interval.high
    except Exception as e:
        # Fallback to percentile method
        boot_corrs = []
        rng = np.random.RandomState(42)
        n_samples = len(x_data)
        for _ in range(N_BOOT):
            idx_boot = rng.choice(n_samples, size=n_samples, replace=True)
            r_boot, _ = stats.spearmanr(x_data[idx_boot], y_data[idx_boot])
            boot_corrs.append(r_boot)
        boot_corrs = np.array(boot_corrs)
        ci_low = np.percentile(boot_corrs, 2.5)
        ci_high = np.percentile(boot_corrs, 97.5)

    ci_width = ci_high - ci_low
    zero_excluded = (ci_low > 0) or (ci_high < 0)

    bootstrap_results.append({
        "factor": fcol,
        "return_horizon": rcol,
        "spearman_r": row["spearman_r"],
        "q_value": row["q_value"],
        "fdr_sig": row["fdr_significant"],
        "ci_low": ci_low,
        "ci_high": ci_high,
        "ci_width": ci_width,
        "zero_excluded": zero_excluded,
        "n": row["n"],
    })
    status = "ROBUST" if zero_excluded else "CI includes 0"
    print(f"  {fcol:<32s} {rcol:<12s} r={row['spearman_r']:+.4f}  "
          f"CI=[{ci_low:+.4f}, {ci_high:+.4f}]  width={ci_width:.4f}  {status}")

boot_df = pd.DataFrame(bootstrap_results)

# Sort by CI width (narrower = more stable)
boot_df_sorted = boot_df.sort_values("ci_width")
robust_factors = boot_df[boot_df["zero_excluded"] & boot_df["fdr_sig"]]
print(f"\nFactors with CI excluding zero AND FDR q<0.05: {len(robust_factors)}")

# ============================================================
# PART C: Cohen's d 効果量（Q1 vs Q5）
# ============================================================
print("\n" + "=" * 100)
print("PART C: COHEN'S d EFFECT SIZE (Q1 vs Q5)")
print("=" * 100)

def cohens_d(group1, group2):
    """Cohen's d with pooled standard deviation."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return np.nan
    var1 = group1.var(ddof=1)
    var2 = group2.var(ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std < 1e-10:
        return np.nan
    return (group2.mean() - group1.mean()) / pooled_std

def classify_effect(d):
    d_abs = abs(d)
    if d_abs >= 0.8:
        return "Large"
    elif d_abs >= 0.5:
        return "Medium"
    elif d_abs >= 0.2:
        return "Small"
    else:
        return "Negligible"

effect_results = []
# Use all FDR-significant + top20 candidates
target_pairs = boot_df[["factor", "return_horizon"]].values.tolist()

for fcol, rcol in target_pairs:
    valid = analysis[[fcol, rcol]].dropna()
    if len(valid) < 50:
        continue

    try:
        valid["quintile"] = pd.qcut(valid[fcol], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    except ValueError:
        continue

    q1 = valid[valid["quintile"] == 1][rcol]
    q5 = valid[valid["quintile"] == 5][rcol]

    if len(q1) < 5 or len(q5) < 5:
        continue

    d = cohens_d(q1, q5)
    if np.isnan(d):
        continue

    # Quintile means for context
    qmeans = valid.groupby("quintile")[rcol].mean()

    # Monotonicity
    q_vals = qmeans.reset_index()
    q_vals["quintile"] = q_vals["quintile"].astype(int)
    mono_corr = np.nan
    if len(q_vals) >= 3:
        mono_corr, _ = stats.spearmanr(q_vals["quintile"], q_vals[rcol])

    effect_results.append({
        "factor": fcol,
        "return_horizon": rcol,
        "cohens_d": d,
        "effect_class": classify_effect(d),
        "Q1_mean": q1.mean(),
        "Q5_mean": q5.mean(),
        "Q5_Q1_spread": q5.mean() - q1.mean(),
        "monotonicity": mono_corr,
        "n_Q1": len(q1),
        "n_Q5": len(q5),
    })

effect_df = pd.DataFrame(effect_results)
effect_df = effect_df.sort_values("cohens_d", key=abs, ascending=False)

print(f"\n{'Factor':<35s} {'Horizon':<12s} {'d':>8s} {'Class':>12s} {'Q1_mean':>10s} {'Q5_mean':>10s} {'Spread':>10s} {'Mono':>6s}")
print("-" * 108)
for _, row in effect_df.iterrows():
    mono_str = f"{row['monotonicity']:.2f}" if not np.isnan(row["monotonicity"]) else "N/A"
    print(f"{row['factor']:<35s} {row['return_horizon']:<12s} {row['cohens_d']:>+8.3f} "
          f"{row['effect_class']:>12s} {row['Q1_mean']:>10.4f} {row['Q5_mean']:>10.4f} "
          f"{row['Q5_Q1_spread']:>+10.4f} {mono_str:>6s}")

# ============================================================
# FINAL SUMMARY: 確実にロバストなファクター
# ============================================================
print("\n" + "=" * 100)
print("FINAL SUMMARY: DEFINITIVELY ROBUST FACTORS")
print("=" * 100)
print("Criteria: FDR q < 0.05 AND bootstrap 95% CI excludes zero")
print()

# Merge all results
final = boot_df[boot_df["zero_excluded"] & boot_df["fdr_sig"]].copy()
final = final.merge(effect_df[["factor", "return_horizon", "cohens_d", "effect_class",
                                "Q5_Q1_spread", "monotonicity"]],
                     on=["factor", "return_horizon"], how="left")
final = final.sort_values("spearman_r", key=abs, ascending=False)

print(f"Total definitively robust factor-horizon pairs: {len(final)}")
print(f"Unique robust factors: {len(final['factor'].unique())}")
print()

print(f"{'#':>3s} {'Factor':<35s} {'Horizon':<12s} {'r':>8s} {'q':>8s} "
      f"{'CI_low':>8s} {'CI_high':>8s} {'Width':>7s} {'d':>8s} {'Effect':>10s} {'Mono':>6s}")
print("-" * 120)

for i, (_, row) in enumerate(final.iterrows(), 1):
    d_str = f"{row['cohens_d']:+.3f}" if pd.notna(row.get("cohens_d")) else "N/A"
    eff_str = row.get("effect_class", "N/A") if pd.notna(row.get("effect_class")) else "N/A"
    mono_str = f"{row['monotonicity']:.2f}" if pd.notna(row.get("monotonicity")) else "N/A"
    print(f"{i:>3d} {row['factor']:<35s} {row['return_horizon']:<12s} {row['spearman_r']:>+8.4f} "
          f"{row['q_value']:>8.4f} {row['ci_low']:>+8.4f} {row['ci_high']:>+8.4f} "
          f"{row['ci_width']:>7.4f} {d_str:>8s} {eff_str:>10s} {mono_str:>6s}")

# Summary by return horizon
print("\n--- Robust factor count by return horizon ---")
for rcol in return_cols:
    subset = final[final["return_horizon"] == rcol]
    print(f"  {rcol}: {len(subset)} factor-horizon pairs")

# Summary by effect size
print("\n--- Effect size distribution ---")
if "effect_class" in final.columns:
    for cls in ["Large", "Medium", "Small", "Negligible"]:
        n = (final["effect_class"] == cls).sum()
        if n > 0:
            print(f"  {cls}: {n}")

# Top factors by stability (narrowest CI)
print("\n--- Top 10 most stable factors (narrowest CI) ---")
stable = final.sort_values("ci_width").head(10)
for i, (_, row) in enumerate(stable.iterrows(), 1):
    print(f"  {i:>2d}. {row['factor']:<32s} {row['return_horizon']:<12s} "
          f"r={row['spearman_r']:+.4f}  CI_width={row['ci_width']:.4f}")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
