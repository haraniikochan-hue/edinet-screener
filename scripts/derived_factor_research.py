"""
Derived Factor Research: financials_all / ratios_all から派生ファクターを生成し、
株価リターンとの Spearman 相関 + 五分位分析を行う。
"""
import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

DATA = "/Users/harann/edinet-screener/data"

# ── 1. Load data ──
fin = pd.read_csv(f"{DATA}/financials_all.csv")
rat = pd.read_csv(f"{DATA}/ratios_all.csv")
prices = pd.read_csv(f"{DATA}/stock_prices.csv")
returns = pd.read_csv(f"{DATA}/historical_returns.csv")
companies = pd.read_csv(f"{DATA}/companies.csv")

print(f"financials: {fin.shape}, ratios: {rat.shape}, prices: {prices.shape}, returns: {returns.shape}, companies: {companies.shape}")
print(f"fin cols: {list(fin.columns)}")
print(f"rat cols: {list(rat.columns)}")
print(f"prices cols: {list(prices.columns)}")

# ── 2. Build edinet_code -> ticker mapping ──
# companies has sec_code (e.g. 30760 or "297A0"), ticker in returns is "3076.T" or "297A.T"
# Match fetch_stock_prices.py / fetch_historical_returns.py logic: sec_code[:4] + ".T"
def sec_to_ticker(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if len(s) < 4:
        return None
    return s[:4] + ".T"
companies["ticker"] = companies["sec_code"].apply(sec_to_ticker)
code_ticker = companies[["edinet_code", "ticker"]].dropna()

# Merge returns with edinet_code
returns_merged = returns.merge(code_ticker, on="ticker", how="inner")
print(f"returns after merge with edinet_code: {returns_merged.shape}")

# ── 3. Compute derived factors per edinet_code ──
# We need time-series features, so group by edinet_code across fiscal_years

# Merge fin and rat on edinet_code + fiscal_year
full = fin.merge(rat, on=["edinet_code", "fiscal_year", "sec_code", "company_name", "industry"],
                 suffixes=("_fin", "_rat"), how="outer")
full = full.sort_values(["edinet_code", "fiscal_year"])

print(f"full merged shape: {full.shape}")

# Helper: pick best column (fin or rat version)
def pick(df, base, prefer="_fin"):
    """Return series preferring _fin version, falling back to _rat or bare name."""
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
    """Compute derived factors for a single edinet_code group (time-series of fiscal years)."""
    g = group.sort_values("fiscal_year")
    n = len(g)
    result = {"edinet_code": g["edinet_code"].iloc[0]}

    # Need at least 3 years of data for meaningful time-series stats
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

    # --- Revenue growth stability ---
    rev_vals = revenue.dropna()
    if len(rev_vals) >= 3:
        rev_growth = rev_vals.pct_change().dropna()
        rev_growth = rev_growth.replace([np.inf, -np.inf], np.nan).dropna()
        if len(rev_growth) >= 2:
            result["revenue_growth_std"] = rev_growth.std()
            mean_rg = rev_growth.mean()
            result["revenue_growth_mean"] = mean_rg
            if abs(mean_rg) > 1e-10:
                result["revenue_growth_cv"] = rev_growth.std() / abs(mean_rg)

    # --- OI growth stability ---
    oi_vals = oi.dropna()
    if len(oi_vals) >= 3:
        oi_growth = oi_vals.pct_change().dropna()
        oi_growth = oi_growth.replace([np.inf, -np.inf], np.nan).dropna()
        if len(oi_growth) >= 2:
            result["oi_growth_std"] = oi_growth.std()
            mean_og = oi_growth.mean()
            result["oi_growth_mean"] = mean_og
            if abs(mean_og) > 1e-10:
                result["oi_growth_cv"] = oi_growth.std() / abs(mean_og)

    # --- Margin improvement trend (latest - avg of first 3 years) ---
    om_vals = op_margin.dropna()
    if len(om_vals) >= 4:
        result["margin_improvement"] = om_vals.iloc[-1] - om_vals.iloc[:3].mean()

    nm_vals = net_margin.dropna()
    if len(nm_vals) >= 4:
        result["net_margin_improvement"] = nm_vals.iloc[-1] - nm_vals.iloc[:3].mean()

    # --- Cash conversion efficiency (avg CF_op / NI) ---
    cf_ni = pd.DataFrame({"cf": cf_op, "ni": ni}).dropna()
    cf_ni = cf_ni[cf_ni["ni"].abs() > 0]
    if len(cf_ni) >= 2:
        ratios = cf_ni["cf"] / cf_ni["ni"]
        ratios = ratios.replace([np.inf, -np.inf], np.nan).dropna()
        if len(ratios) >= 2:
            result["cash_conversion_avg"] = ratios.mean()
            result["cash_conversion_std"] = ratios.std()

    # --- Asset turnover change ---
    at_data = pd.DataFrame({"rev": revenue, "ta": ta}).dropna()
    if len(at_data) >= 3:
        at = at_data["rev"] / at_data["ta"]
        at = at.replace([np.inf, -np.inf], np.nan).dropna()
        if len(at) >= 3:
            result["asset_turnover_latest"] = at.iloc[-1]
            result["asset_turnover_change"] = at.iloc[-1] - at.iloc[0]

    # --- Debt ratio trend (1 - equity_ratio) ---
    er_vals = equity_ratio.dropna()
    if len(er_vals) >= 3:
        debt_ratio = 1 - er_vals
        result["debt_ratio_change"] = debt_ratio.iloc[-1] - debt_ratio.iloc[0]
        result["equity_ratio_latest"] = er_vals.iloc[-1]
        result["equity_ratio_change"] = er_vals.iloc[-1] - er_vals.iloc[0]

    # --- Payout stability ---
    po_vals = payout.dropna()
    if len(po_vals) >= 3:
        result["payout_std"] = po_vals.std()
        result["payout_mean"] = po_vals.mean()

    # --- NI / CF_op gap (accrual proxy) ---
    if len(cf_ni) >= 2:
        gaps = (cf_ni["ni"] - cf_ni["cf"]) / cf_ni["cf"].abs().replace(0, np.nan)
        gaps = gaps.replace([np.inf, -np.inf], np.nan).dropna()
        if len(gaps) >= 2:
            result["accrual_gap_avg"] = gaps.mean()

    # --- ROA stability ---
    roa_vals = roa.dropna()
    if len(roa_vals) >= 3:
        result["roa_std"] = roa_vals.std()
        result["roa_mean"] = roa_vals.mean()
        result["roa_latest"] = roa_vals.iloc[-1]

    # --- ROE stability ---
    roe_vals = roe.dropna()
    if len(roe_vals) >= 3:
        result["roe_std"] = roe_vals.std()
        result["roe_mean"] = roe_vals.mean()
        result["roe_latest"] = roe_vals.iloc[-1]

    # --- BPS CAGR ---
    bps_vals = bps.dropna()
    if len(bps_vals) >= 3 and bps_vals.iloc[0] > 0 and bps_vals.iloc[-1] > 0:
        years = len(bps_vals) - 1
        result["bps_cagr"] = (bps_vals.iloc[-1] / bps_vals.iloc[0]) ** (1.0 / years) - 1

    # --- FCF growth ---
    fcf_vals = fcf.dropna()
    if len(fcf_vals) >= 3:
        fcf_growth = fcf_vals.pct_change().dropna()
        fcf_growth = fcf_growth.replace([np.inf, -np.inf], np.nan).dropna()
        if len(fcf_growth) >= 2:
            result["fcf_growth_mean"] = fcf_growth.mean()
            result["fcf_growth_std"] = fcf_growth.std()

    # --- Operating CF margin (CF_op / revenue) ---
    cf_rev = pd.DataFrame({"cf": cf_op, "rev": revenue}).dropna()
    cf_rev = cf_rev[cf_rev["rev"].abs() > 0]
    if len(cf_rev) >= 2:
        cfm = cf_rev["cf"] / cf_rev["rev"]
        cfm = cfm.replace([np.inf, -np.inf], np.nan).dropna()
        if len(cfm) >= 2:
            result["cf_margin_avg"] = cfm.mean()
            result["cf_margin_latest"] = cfm.iloc[-1]
            result["cf_margin_improvement"] = cfm.iloc[-1] - cfm.iloc[0]

    # --- CAPEX ratio (|CF_inv| / CF_op) ---
    capex_data = pd.DataFrame({"cf_inv": cf_inv, "cf_op": cf_op}).dropna()
    capex_data = capex_data[capex_data["cf_op"].abs() > 0]
    if len(capex_data) >= 2:
        capex_r = capex_data["cf_inv"].abs() / capex_data["cf_op"]
        capex_r = capex_r.replace([np.inf, -np.inf], np.nan).dropna()
        if len(capex_r) >= 2:
            result["capex_ratio_avg"] = capex_r.mean()
            result["capex_ratio_latest"] = capex_r.iloc[-1]

    # --- NI growth stability ---
    ni_vals = ni.dropna()
    if len(ni_vals) >= 3:
        ni_growth = ni_vals.pct_change().dropna()
        ni_growth = ni_growth.replace([np.inf, -np.inf], np.nan).dropna()
        if len(ni_growth) >= 2:
            result["ni_growth_std"] = ni_growth.std()
            result["ni_growth_mean"] = ni_growth.mean()

    # --- EPS growth stability ---
    eps_vals = eps.dropna()
    if len(eps_vals) >= 3:
        eps_growth = eps_vals.pct_change().dropna()
        eps_growth = eps_growth.replace([np.inf, -np.inf], np.nan).dropna()
        if len(eps_growth) >= 2:
            result["eps_growth_std"] = eps_growth.std()
            result["eps_growth_mean"] = eps_growth.mean()

    # --- Dividend growth ---
    div_vals = div.dropna()
    if len(div_vals) >= 3 and (div_vals > 0).all():
        years_d = len(div_vals) - 1
        if div_vals.iloc[0] > 0:
            result["div_cagr"] = (div_vals.iloc[-1] / div_vals.iloc[0]) ** (1.0 / years_d) - 1

    # --- Operating leverage (OI growth / Revenue growth sensitivity) ---
    if len(rev_vals) >= 3 and len(oi_vals) >= 3:
        rg = rev_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan)
        og = oi_vals.pct_change().dropna().replace([np.inf, -np.inf], np.nan)
        aligned = pd.DataFrame({"rg": rg, "og": og}).dropna()
        if len(aligned) >= 3 and aligned["rg"].std() > 1e-10:
            result["operating_leverage"] = aligned["og"].std() / aligned["rg"].std()

    # --- Reinvestment rate (|CF_inv| / NI) ---
    reinv_data = pd.DataFrame({"cf_inv": cf_inv, "ni": ni}).dropna()
    reinv_data = reinv_data[reinv_data["ni"].abs() > 0]
    if len(reinv_data) >= 2:
        reinv = reinv_data["cf_inv"].abs() / reinv_data["ni"]
        reinv = reinv.replace([np.inf, -np.inf], np.nan).dropna()
        if len(reinv) >= 2:
            result["reinvestment_rate_avg"] = reinv.mean()

    # --- Cash ratio (cash / total_assets) ---
    cash_ta = pd.DataFrame({"cash": cash, "ta": ta}).dropna()
    cash_ta = cash_ta[cash_ta["ta"] > 0]
    if len(cash_ta) >= 2:
        cr = cash_ta["cash"] / cash_ta["ta"]
        result["cash_ratio_latest"] = cr.iloc[-1]
        result["cash_ratio_avg"] = cr.mean()

    # --- Net assets growth (NA CAGR) ---
    na_vals = na_.dropna()
    if len(na_vals) >= 3 and na_vals.iloc[0] > 0 and na_vals.iloc[-1] > 0:
        years_na = len(na_vals) - 1
        result["net_assets_cagr"] = (na_vals.iloc[-1] / na_vals.iloc[0]) ** (1.0 / years_na) - 1

    # --- Revenue per asset latest ---
    if len(at_data) >= 1:
        at_latest = (at_data["rev"] / at_data["ta"]).iloc[-1]
        result["revenue_per_asset_latest"] = at_latest

    # --- Margin level (operating margin average + latest) ---
    if len(om_vals) >= 2:
        result["op_margin_avg"] = om_vals.mean()
        result["op_margin_latest"] = om_vals.iloc[-1]

    if len(nm_vals) >= 2:
        result["net_margin_avg"] = nm_vals.mean()
        result["net_margin_latest"] = nm_vals.iloc[-1]

    # --- Earnings quality: CF_op / NI consistency (low std = high quality) ---
    # Already in cash_conversion_std

    # --- Profit momentum: latest EPS / avg EPS ---
    if len(eps_vals) >= 3:
        avg_eps = eps_vals.iloc[:-1].mean()
        if abs(avg_eps) > 1e-10:
            result["eps_momentum"] = eps_vals.iloc[-1] / avg_eps

    # --- FCF yield proxy: FCF latest / total_assets latest ---
    if len(fcf_vals) >= 1 and len(ta.dropna()) >= 1:
        ta_latest = ta.dropna().iloc[-1]
        if ta_latest > 0:
            result["fcf_to_assets"] = fcf_vals.iloc[-1] / ta_latest

    # --- Comprehensive income vs NI gap ---
    ci = pick(g, "comprehensive_income")
    ci_ni = pd.DataFrame({"ci": ci, "ni": ni}).dropna()
    if len(ci_ni) >= 2:
        ci_ni_valid = ci_ni[ci_ni["ni"].abs() > 0]
        if len(ci_ni_valid) >= 2:
            gap = (ci_ni_valid["ci"] - ci_ni_valid["ni"]) / ci_ni_valid["ni"].abs()
            gap = gap.replace([np.inf, -np.inf], np.nan).dropna()
            if len(gap) >= 2:
                result["ci_ni_gap_avg"] = gap.mean()

    return result

print("Computing derived factors...")
derived_list = []
for code, grp in full.groupby("edinet_code"):
    derived_list.append(compute_derived(grp))

derived = pd.DataFrame(derived_list)
print(f"Derived factors shape: {derived.shape}")
print(f"Factor columns: {[c for c in derived.columns if c != 'edinet_code']}")

# ── 4. Merge with returns ──
analysis = derived.merge(returns_merged, on="edinet_code", how="inner")
print(f"Analysis dataset shape (with returns): {analysis.shape}")

# Also merge stock_prices for cross-sectional factors
prices["ticker"] = prices["ticker"].astype(str)
analysis = analysis.merge(prices[["ticker", "priceToBook", "trailingPE", "forwardPE",
                                   "dividendYield", "debtToEquity", "beta", "marketCap"]],
                          on="ticker", how="left")

# ── 5. Factor list ──
return_cols = ["return_1y", "return_3y", "return_5y"]
factor_cols = [c for c in analysis.columns
               if c not in ["edinet_code", "ticker", "return_1y", "return_3y", "return_5y",
                           "priceToBook", "trailingPE", "forwardPE", "dividendYield",
                           "debtToEquity", "beta", "marketCap"]]

print(f"\nNumber of candidate factors: {len(factor_cols)}")

# ── 6. Winsorize at 1%/99% ──
def winsorize(s, lower=0.01, upper=0.99):
    q_lo = s.quantile(lower)
    q_hi = s.quantile(upper)
    return s.clip(q_lo, q_hi)

for col in factor_cols + return_cols:
    valid = analysis[col].dropna()
    if len(valid) > 10:
        analysis[col] = winsorize(analysis[col])

# ── 7. Spearman correlations ──
results = []
for fcol in factor_cols:
    for rcol in return_cols:
        valid = analysis[[fcol, rcol]].dropna()
        if len(valid) < 30:
            continue
        corr, pval = stats.spearmanr(valid[fcol], valid[rcol])
        results.append({
            "factor": fcol,
            "return_horizon": rcol,
            "spearman_r": corr,
            "p_value": pval,
            "n": len(valid),
        })

corr_df = pd.DataFrame(results)
corr_df = corr_df.sort_values("p_value")

# Filter: p < 0.01 and |r| > 0.05
sig = corr_df[(corr_df["p_value"] < 0.01) & (corr_df["spearman_r"].abs() > 0.05)].copy()
sig = sig.sort_values("spearman_r", key=abs, ascending=False)
print(f"\n=== Significant factors (p<0.01, |r|>0.05): {len(sig)} ===")

# ── 8. Quintile analysis ──
def quintile_analysis(df, factor_col, return_col):
    """Compute Q1-Q5 return spreads."""
    valid = df[[factor_col, return_col]].dropna()
    if len(valid) < 50:
        return None, None, None
    valid["quintile"] = pd.qcut(valid[factor_col], 5, labels=[1,2,3,4,5], duplicates="drop")
    if valid["quintile"].isna().all():
        return None, None, None
    qmeans = valid.groupby("quintile")[return_col].mean()
    if 1 in qmeans.index and 5 in qmeans.index:
        spread = qmeans[5] - qmeans[1]
        # Monotonicity check: correlation of quintile rank with mean return
        q_vals = qmeans.reset_index()
        q_vals["quintile"] = q_vals["quintile"].astype(int)
        if len(q_vals) >= 3:
            mono_corr, _ = stats.spearmanr(q_vals["quintile"], q_vals[return_col])
        else:
            mono_corr = None
        return spread, mono_corr, qmeans.to_dict()
    return None, None, None

quintile_results = []
for _, row in sig.iterrows():
    spread, mono, qmeans = quintile_analysis(analysis, row["factor"], row["return_horizon"])
    quintile_results.append({
        "factor": row["factor"],
        "return_horizon": row["return_horizon"],
        "spearman_r": row["spearman_r"],
        "p_value": row["p_value"],
        "n": row["n"],
        "Q5_Q1_spread": spread,
        "monotonicity": mono,
        "Q_means": qmeans,
    })

qdf = pd.DataFrame(quintile_results)
qdf = qdf.sort_values("spearman_r", key=abs, ascending=False)

# ── 9. Output ──
print("\n" + "="*120)
print("DERIVED FACTOR RESEARCH RESULTS")
print("="*120)

# Factor definitions
definitions = {
    "revenue_growth_std": "売上成長率の標準偏差（低いほど安定）",
    "revenue_growth_mean": "売上成長率の平均",
    "revenue_growth_cv": "売上成長率の変動係数 (σ/μ)",
    "oi_growth_std": "営業利益成長率の標準偏差",
    "oi_growth_mean": "営業利益成長率の平均",
    "oi_growth_cv": "営業利益成長率の変動係数",
    "margin_improvement": "営業利益率の改善度（最新 - 過去3年平均）",
    "net_margin_improvement": "純利益率の改善度（最新 - 過去3年平均）",
    "cash_conversion_avg": "キャッシュ変換効率の平均（営業CF/純利益）",
    "cash_conversion_std": "キャッシュ変換効率の標準偏差",
    "asset_turnover_latest": "直近の総資産回転率",
    "asset_turnover_change": "総資産回転率の変化（直近 - 最古）",
    "debt_ratio_change": "負債比率の変化トレンド",
    "equity_ratio_latest": "直近の自己資本比率",
    "equity_ratio_change": "自己資本比率の変化",
    "payout_std": "配当性向の標準偏差（安定性）",
    "payout_mean": "配当性向の平均",
    "accrual_gap_avg": "アクルーアル・ギャップ平均 ((NI-CF_op)/|CF_op|)",
    "roa_std": "ROAの標準偏差（安定性）",
    "roa_mean": "ROAの平均",
    "roa_latest": "直近ROA",
    "roe_std": "ROEの標準偏差",
    "roe_mean": "ROEの平均",
    "roe_latest": "直近ROE",
    "bps_cagr": "BPS成長率 (CAGR)",
    "fcf_growth_mean": "FCF成長率の平均",
    "fcf_growth_std": "FCF成長率の標準偏差",
    "cf_margin_avg": "営業CFマージンの平均（営業CF/売上）",
    "cf_margin_latest": "直近の営業CFマージン",
    "cf_margin_improvement": "営業CFマージンの改善度",
    "capex_ratio_avg": "CAPEX比率の平均（|投資CF|/営業CF）",
    "capex_ratio_latest": "直近のCAPEX比率",
    "ni_growth_std": "純利益成長率の標準偏差",
    "ni_growth_mean": "純利益成長率の平均",
    "eps_growth_std": "EPS成長率の標準偏差",
    "eps_growth_mean": "EPS成長率の平均",
    "div_cagr": "配当CAGR",
    "operating_leverage": "オペレーティングレバレッジ（OI成長σ/売上成長σ）",
    "reinvestment_rate_avg": "再投資率の平均（|投資CF|/純利益）",
    "cash_ratio_latest": "直近キャッシュ比率（現金/総資産）",
    "cash_ratio_avg": "キャッシュ比率の平均",
    "net_assets_cagr": "純資産CAGR",
    "revenue_per_asset_latest": "直近の売上/総資産",
    "op_margin_avg": "営業利益率の平均",
    "op_margin_latest": "直近の営業利益率",
    "net_margin_avg": "純利益率の平均",
    "net_margin_latest": "直近の純利益率",
    "eps_momentum": "EPSモメンタム（直近EPS/過去平均EPS）",
    "fcf_to_assets": "FCF/総資産（直近）",
    "ci_ni_gap_avg": "包括利益と純利益の乖離率の平均",
}

print(f"\n総ファクター数: {len(factor_cols)}")
print(f"有意なファクター数 (p<0.01, |r|>0.05): {len(sig)}")
print(f"分析対象企業数: {len(analysis)}")

print("\n" + "-"*120)
print(f"{'Factor':<30} {'Definition':<40} {'Horizon':<12} {'r':>8} {'p-value':>12} {'N':>6} {'Q5-Q1':>10} {'Mono':>8}")
print("-"*120)

for _, row in qdf.iterrows():
    defn = definitions.get(row["factor"], "")[:38]
    spread_str = f"{row['Q5_Q1_spread']:.4f}" if pd.notna(row.get("Q5_Q1_spread")) else "N/A"
    mono_str = f"{row['monotonicity']:.2f}" if pd.notna(row.get("monotonicity")) else "N/A"
    print(f"{row['factor']:<30} {defn:<40} {row['return_horizon']:<12} {row['spearman_r']:>8.4f} {row['p_value']:>12.2e} {row['n']:>6} {spread_str:>10} {mono_str:>8}")

# ── 10. Top factors summary by return horizon ──
for rcol in return_cols:
    subset = qdf[qdf["return_horizon"] == rcol].head(15)
    if len(subset) == 0:
        continue
    print(f"\n{'='*80}")
    print(f"TOP 15 FACTORS for {rcol}")
    print(f"{'='*80}")
    for i, (_, row) in enumerate(subset.iterrows(), 1):
        defn = definitions.get(row["factor"], "")
        spread_str = f"{row['Q5_Q1_spread']:.4f}" if pd.notna(row.get("Q5_Q1_spread")) else "N/A"
        mono_str = f"{row['monotonicity']:.2f}" if pd.notna(row.get("monotonicity")) else "N/A"
        print(f"  {i:>2}. {row['factor']:<28} r={row['spearman_r']:>7.4f}  p={row['p_value']:.2e}  Q5-Q1={spread_str:>10}  mono={mono_str}")
        print(f"      {defn}")

# ── 11. Quintile detail for top factors ──
print(f"\n{'='*80}")
print("QUINTILE DETAIL (top 10 by |r| across all horizons)")
print(f"{'='*80}")
top10 = qdf.head(10)
for _, row in top10.iterrows():
    qm = row.get("Q_means", {})
    if qm:
        q_str = "  ".join([f"Q{k}={v:.4f}" for k, v in sorted(qm.items())])
    else:
        q_str = "N/A"
    print(f"\n  {row['factor']} ({row['return_horizon']}):")
    print(f"    r={row['spearman_r']:.4f}  p={row['p_value']:.2e}  Q5-Q1={row.get('Q5_Q1_spread', 'N/A')}")
    print(f"    {q_str}")

print("\n\nDone.")
