#!/usr/bin/env python3
"""
Unified Factor Gate: 全候補ファクターに対して6フィルターを一括実行し、機械判定ゲート表を出力する。

Codex v2 指摘8件を全て根本解決:
  1. [Critical] 母集団不一致 → sec_to_ticker() を統一（s[:4]+".T"）
  2. [Critical] 直交化がreturn_1y固定 → return_1y/3y/5y全てで逐次残差化
  3. [High] 非線形検証にroa_std等が未含 → 全候補ファクターで十分位分析
  4. [High] ロバスト性検証が旧9因子のみ → 全候補ファクターで実施
  5. [High] LASSOにconsecutive_dividend_yearsが未投入 → 全因子投入
  6. [High] 業種中立の複合スコアで負相関因子の方向バグ → ascending逆転
  7. [High] ブートストラップCIが上位20ペア限定 → FDR通過全ペアで実施
  8. [Medium] 業種中立がFDR未補正 → FDR補正を業種中立にも適用
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
from sklearn.linear_model import LassoCV, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import time

DATA = "/Users/harann/edinet-screener/data"
RETURN_COLS = ["return_1y", "return_3y", "return_5y"]
N_BOOTSTRAP = 1000
RNG_SEED = 42

# ============================================================
# 0. 統一 sec_to_ticker（全スクリプト統一: Codex指摘#1 解決）
# ============================================================
def sec_to_ticker(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if len(s) < 4:
        return None
    return s[:4] + ".T"


def pick(df: pd.DataFrame, base: str, prefer: str = "_fin") -> pd.Series:
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


def winsorize(s: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    q_lo = s.quantile(lower)
    q_hi = s.quantile(upper)
    return s.clip(q_lo, q_hi)


def compute_derived(group: pd.DataFrame) -> dict:
    """Compute time-series derived factors for a single edinet_code group."""
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
    eps_s = pick(g, "eps")
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
            [np.inf, -np.inf], np.nan
        ).dropna()
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
    eps_vals = eps_s.dropna()
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

    # --- 配当系派生ファクター ---
    divs = div.dropna()
    consec_div = 0
    for v in divs.values[::-1]:
        if v > 0:
            consec_div += 1
        else:
            break
    result["consecutive_dividend_years"] = consec_div

    div_arr = divs.values
    consec_increase = 0
    for i in range(len(div_arr) - 1, 0, -1):
        if div_arr[i] > div_arr[i - 1]:
            consec_increase += 1
        else:
            break
    result["consecutive_increase_years"] = consec_increase

    ni_check = ni.dropna()
    result["has_loss_year"] = int((ni_check < 0).any()) if len(ni_check) > 0 else np.nan

    bps_arr = bps.dropna().values
    bps_inc = 0
    for i in range(len(bps_arr) - 1, 0, -1):
        if bps_arr[i] > bps_arr[i - 1]:
            bps_inc += 1
        else:
            break
    result["bps_increase_years"] = bps_inc

    return result


# ============================================================
# 1. 統一ユニバース構築
# ============================================================
def build_universe() -> tuple[pd.DataFrame, list[str]]:
    """Build unified universe. Returns (analysis_df, factor_cols)."""
    print("=" * 100)
    print("STEP 1: UNIFIED UNIVERSE CONSTRUCTION")
    print("=" * 100)

    fin = pd.read_csv(f"{DATA}/financials_all.csv")
    rat = pd.read_csv(f"{DATA}/ratios_all.csv")
    prices = pd.read_csv(f"{DATA}/stock_prices.csv")
    returns = pd.read_csv(f"{DATA}/historical_returns.csv")
    companies = pd.read_csv(f"{DATA}/companies.csv")

    print(f"  financials: {fin.shape}, ratios: {rat.shape}")
    print(f"  prices: {prices.shape}, returns: {returns.shape}, companies: {companies.shape}")

    # --- Unified sec_to_ticker (Codex #1) ---
    companies["ticker"] = companies["sec_code"].apply(sec_to_ticker)
    code_ticker = companies[["edinet_code", "ticker", "industry"]].dropna(subset=["ticker"])
    returns_merged = returns.merge(code_ticker, on="ticker", how="inner")
    print(f"  returns with edinet_code: {returns_merged.shape[0]} companies")

    # --- Derived factors ---
    full = fin.merge(
        rat,
        on=["edinet_code", "fiscal_year", "sec_code", "company_name", "industry"],
        suffixes=("_fin", "_rat"),
        how="outer",
    )
    full = full.sort_values(["edinet_code", "fiscal_year"])

    print("  Computing derived factors...")
    derived_list = [compute_derived(grp) for _, grp in full.groupby("edinet_code")]
    derived = pd.DataFrame(derived_list)
    print(f"  Derived factors shape: {derived.shape}")

    # --- Merge: derived + returns ---
    analysis = derived.merge(returns_merged, on="edinet_code", how="inner")

    # --- Market factors from stock_prices ---
    market_factor_names = [
        "marketCap", "priceToBook", "forwardPE", "dividendYield",
        "beta", "returnOnEquity", "debtToEquity",
    ]
    prices["ticker"] = prices["ticker"].astype(str)
    avail_mkt = [c for c in market_factor_names if c in prices.columns]
    analysis = analysis.merge(prices[["ticker"] + avail_mkt], on="ticker", how="left")

    # log_marketCap
    if "marketCap" in analysis.columns:
        analysis["log_marketCap"] = np.log1p(analysis["marketCap"])

    # --- Factor column list ---
    exclude = {
        "edinet_code", "ticker", "industry",
        "return_1y", "return_3y", "return_5y",
        "marketCap",  # use log_marketCap instead
    }
    factor_cols = [
        c for c in analysis.columns
        if c not in exclude
        and analysis[c].dtype in [np.float64, np.int64, float, int]
        and analysis[c].notna().sum() >= 30
    ]

    print(f"\n  Unified universe: N = {len(analysis)} companies")
    print(f"  Total candidate factors: {len(factor_cols)}")

    # --- Winsorize at 1%/99% ---
    for col in factor_cols + RETURN_COLS:
        valid = analysis[col].dropna()
        if len(valid) > 10:
            analysis[col] = winsorize(analysis[col])

    return analysis, factor_cols


# ============================================================
# Filter A: FDR + Bootstrap CI (Codex #7, #8 fixes)
# ============================================================
def filter_a_fdr_bootstrap(
    analysis: pd.DataFrame, factor_cols: list[str]
) -> dict[str, bool]:
    """Filter A: BH-FDR correction + bootstrap 95% CI for ALL FDR-passing pairs."""
    print("\n" + "=" * 100)
    print("FILTER A: FDR CORRECTION + BOOTSTRAP CI")
    print("=" * 100)

    # Raw Spearman correlations
    raw_results = []
    for fcol in factor_cols:
        for rcol in RETURN_COLS:
            valid = analysis[[fcol, rcol]].dropna()
            if len(valid) < 30:
                continue
            corr, pval = stats.spearmanr(valid[fcol], valid[rcol])
            raw_results.append({
                "factor": fcol, "return_horizon": rcol,
                "spearman_r": corr, "p_value": pval, "n": len(valid),
            })

    corr_df = pd.DataFrame(raw_results)
    print(f"  Total tests: {len(corr_df)}")

    # BH-FDR
    reject, q_values, _, _ = multipletests(corr_df["p_value"].values, alpha=0.05, method="fdr_bh")
    corr_df["q_value"] = q_values
    corr_df["fdr_sig"] = reject

    fdr_sig = corr_df[corr_df["fdr_sig"]].copy()
    print(f"  FDR-significant pairs (q < 0.05): {len(fdr_sig)}")

    # Bootstrap CI for ALL FDR-passing pairs (Codex #7: not top-20 limited)
    # Use fast manual bootstrap (scipy.stats.bootstrap is too slow for paired data)
    pass_factors: dict[str, bool] = {f: False for f in factor_cols}
    n_ci_done = 0
    rng = np.random.RandomState(RNG_SEED)

    for idx_row, row in fdr_sig.iterrows():
        fcol, rcol = row["factor"], row["return_horizon"]
        valid = analysis[[fcol, rcol]].dropna()
        x_data, y_data = valid[fcol].values, valid[rcol].values
        ns = len(x_data)

        boot_corrs = np.empty(N_BOOTSTRAP)
        for b in range(N_BOOTSTRAP):
            idx = rng.randint(0, ns, size=ns)
            boot_corrs[b] = stats.spearmanr(x_data[idx], y_data[idx])[0]

        ci_low = np.percentile(boot_corrs, 2.5)
        ci_high = np.percentile(boot_corrs, 97.5)

        zero_excluded = (ci_low > 0) or (ci_high < 0)
        if zero_excluded:
            pass_factors[fcol] = True

        n_ci_done += 1
        if n_ci_done % 20 == 0:
            print(f"    Bootstrap progress: {n_ci_done}/{len(fdr_sig)}")

    print(f"  Bootstrap CIs computed: {n_ci_done}")
    n_pass = sum(1 for v in pass_factors.values() if v)
    print(f"  Factors passing Filter A: {n_pass}")

    # Store raw correlations for later use
    filter_a_corr = corr_df.copy()

    return pass_factors, filter_a_corr


# ============================================================
# Filter B: LASSO (Codex #5: consecutive_dividend_years included)
# ============================================================
def filter_b_lasso(
    analysis: pd.DataFrame, factor_cols: list[str]
) -> dict[str, bool]:
    """Filter B: LassoCV, pass if non-zero in >=2 of 3 horizons."""
    print("\n" + "=" * 100)
    print("FILTER B: LASSO REGULARIZATION")
    print("=" * 100)

    # Median impute + scale
    X_raw = analysis[factor_cols].copy()
    for col in factor_cols:
        X_raw[col] = X_raw[col].fillna(X_raw[col].median())

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(
        scaler.fit_transform(X_raw), columns=factor_cols, index=analysis.index
    )

    nonzero_counts: dict[str, int] = {f: 0 for f in factor_cols}

    for target in RETURN_COLS:
        mask = analysis[target].notna()
        X = X_scaled.loc[mask]
        y = analysis.loc[mask, target]
        if len(y) < 50:
            print(f"  {target}: too few samples ({len(y)}), skipping")
            continue

        lasso = LassoCV(cv=5, n_alphas=100, random_state=RNG_SEED, max_iter=10000)
        lasso.fit(X, y)

        coefs = pd.Series(lasso.coef_, index=factor_cols)
        nonzero = coefs[coefs.abs() > 1e-8]
        print(f"  {target}: alpha={lasso.alpha_:.6f}, non-zero={len(nonzero)}/{len(factor_cols)}")

        for f in nonzero.index:
            nonzero_counts[f] += 1

    pass_factors = {f: (cnt >= 2) for f, cnt in nonzero_counts.items()}
    n_pass = sum(1 for v in pass_factors.values() if v)
    print(f"  Factors passing Filter B (non-zero in >=2 horizons): {n_pass}")
    return pass_factors


# ============================================================
# Filter C: Independence (PCA + Sequential Residualization)
# (Codex #2: all 3 return horizons, not return_1y only)
# ============================================================
def filter_c_independence(
    analysis: pd.DataFrame, factor_cols: list[str]
) -> dict[str, bool]:
    """Filter C: PCA cluster + sequential residualization across all horizons."""
    print("\n" + "=" * 100)
    print("FILTER C: INDEPENDENCE (PCA + SEQUENTIAL RESIDUALIZATION)")
    print("=" * 100)

    # Median impute + scale for PCA
    X_raw = analysis[factor_cols].copy()
    for col in factor_cols:
        X_raw[col] = X_raw[col].fillna(X_raw[col].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    X_scaled_df = pd.DataFrame(X_scaled, columns=factor_cols, index=analysis.index)

    # PCA
    pca = PCA()
    pca.fit(X_scaled)
    n_pcs = min(len(factor_cols), len(analysis))
    loadings = pd.DataFrame(
        pca.components_[:n_pcs].T,
        columns=[f"PC{i+1}" for i in range(n_pcs)],
        index=factor_cols,
    )

    # Primary PC for each factor
    factor_pc: dict[str, str] = {}
    for f in factor_cols:
        abs_load = loadings.loc[f].abs()
        factor_pc[f] = abs_load.idxmax()

    cum_var = np.cumsum(pca.explained_variance_ratio_)
    n_90 = int(np.argmax(cum_var >= 0.90)) + 1
    print(f"  PCA: {n_90} components for 90% variance")

    # Sequential residualization for EACH return horizon (Codex #2)
    INCR_R2_THRESHOLD = 0.001  # 0.1%

    has_independent_info: dict[str, bool] = {f: False for f in factor_cols}

    for target in RETURN_COLS:
        # Sort factors by |raw r| for this target
        raw_corrs = {}
        for col in factor_cols:
            valid = analysis[[col, target]].dropna()
            if len(valid) >= 30:
                r, _ = stats.spearmanr(valid[col], valid[target])
                raw_corrs[col] = abs(r)
        sorted_factors = sorted(raw_corrs.keys(), key=lambda x: raw_corrs[x], reverse=True)

        # Need complete-case data
        resid_data = analysis[sorted_factors + [target]].dropna()
        if len(resid_data) < 50:
            continue

        y = resid_data[target].values
        controlled = []

        for factor_name in sorted_factors:
            if len(controlled) == 0:
                x = resid_data[factor_name].values.reshape(-1, 1)
                lr = LinearRegression().fit(x, y)
                incr = lr.score(x, y)
            else:
                X_ctrl = resid_data[controlled].values
                lr_without = LinearRegression().fit(X_ctrl, y)
                r2_without = lr_without.score(X_ctrl, y)

                X_with = np.column_stack([X_ctrl, resid_data[factor_name].values])
                lr_with = LinearRegression().fit(X_with, y)
                r2_with = lr_with.score(X_with, y)
                incr = r2_with - r2_without

            controlled.append(factor_name)

            if incr > INCR_R2_THRESHOLD:
                has_independent_info[factor_name] = True

    # Pass: different PC OR incremental R^2 > threshold in any horizon
    # "Different PC" means the factor occupies a different principal component than
    # the factor that ranks higher in |r|. We simplify: if factor has independent info
    # from residualization, it passes.
    pass_factors = has_independent_info.copy()
    # Also mark factors that are sole representatives of their PC
    pc_counts: dict[str, list[str]] = {}
    for f, pc in factor_pc.items():
        pc_counts.setdefault(pc, []).append(f)
    for pc, members in pc_counts.items():
        if len(members) == 1:
            pass_factors[members[0]] = True

    n_pass = sum(1 for v in pass_factors.values() if v)
    print(f"  Factors passing Filter C: {n_pass}")
    return pass_factors


# ============================================================
# Filter D: Industry Neutralization + FDR (Codex #8)
# ============================================================
def filter_d_industry_neutral(
    analysis: pd.DataFrame, factor_cols: list[str]
) -> dict[str, bool]:
    """Filter D: Industry-neutral percentile rank + Spearman + FDR."""
    print("\n" + "=" * 100)
    print("FILTER D: INDUSTRY NEUTRALIZATION + FDR")
    print("=" * 100)

    # Need industry column
    if "industry" not in analysis.columns:
        print("  WARNING: 'industry' column not found. Skipping Filter D.")
        return {f: True for f in factor_cols}

    # Industry-neutral percentile rank
    neutral_results = []
    for fcol in factor_cols:
        # Rank within industry
        neutralized = analysis.groupby("industry")[fcol].rank(pct=True)

        for rcol in RETURN_COLS:
            valid_mask = neutralized.notna() & analysis[rcol].notna()
            if valid_mask.sum() < 30:
                continue
            r, p = stats.spearmanr(neutralized[valid_mask], analysis.loc[valid_mask, rcol])
            neutral_results.append({
                "factor": fcol, "return_horizon": rcol,
                "spearman_r": r, "p_value": p, "n": int(valid_mask.sum()),
            })

    neutral_df = pd.DataFrame(neutral_results)
    if len(neutral_df) == 0:
        return {f: False for f in factor_cols}

    # FDR correction on industry-neutral results (Codex #8)
    reject, q_values, _, _ = multipletests(
        neutral_df["p_value"].values, alpha=0.05, method="fdr_bh"
    )
    neutral_df["q_value"] = q_values
    neutral_df["fdr_sig"] = reject

    fdr_sig = neutral_df[neutral_df["fdr_sig"]]
    sig_factors = set(fdr_sig["factor"].unique())

    pass_factors = {f: (f in sig_factors) for f in factor_cols}
    n_pass = sum(1 for v in pass_factors.values() if v)
    print(f"  Industry-neutral FDR-significant factors: {n_pass}")
    return pass_factors


# ============================================================
# Filter E: Non-linear Analysis (Codex #3: ALL factors)
# ============================================================
def filter_e_nonlinear(
    analysis: pd.DataFrame, factor_cols: list[str]
) -> dict[str, bool]:
    """Filter E: Decile/quantile analysis + monotonicity + F-test for ALL factors.

    Codex v3 #8 fixes:
      - FDR correction across all factor-horizon F-test p-values
      - Discrete/binary factors use quantile with duplicates="drop" and lower min-group threshold
    """
    print("\n" + "=" * 100)
    print("FILTER E: NON-LINEAR ANALYSIS (all factors, FDR-corrected)")
    print("=" * 100)

    # Collect all test results first, then apply FDR
    test_results: list[dict] = []

    for fcol in factor_cols:
        n_unique = analysis[fcol].dropna().nunique()
        is_discrete = n_unique <= 10

        for rcol in RETURN_COLS:
            valid = analysis[[fcol, rcol]].dropna()
            if len(valid) < 50:
                continue

            # Quantile analysis: use fewer bins for discrete factors
            n_bins = min(n_unique, 10) if is_discrete else 10
            if n_bins < 3:
                # Binary: just compare group means via Mann-Whitney
                groups = valid.groupby(fcol)[rcol].apply(list).values
                if len(groups) == 2 and all(len(g) >= 10 for g in groups):
                    u_stat, u_pval = stats.mannwhitneyu(groups[0], groups[1], alternative="two-sided")
                    test_results.append({
                        "factor": fcol, "return_horizon": rcol,
                        "mono_r": np.nan, "f_pval": u_pval, "test_type": "mann_whitney",
                    })
                continue

            try:
                valid = valid.copy()
                valid["quantile"] = pd.qcut(valid[fcol], n_bins, labels=False, duplicates="drop")
            except ValueError:
                continue

            q_means = valid.groupby("quantile")[rcol].mean()
            if len(q_means) < 3:
                continue

            mono_r, _ = stats.spearmanr(q_means.index, q_means.values)

            # Quadratic F-test
            x = valid[fcol].values
            y_vals = valid[rcol].values
            x_std = (x - x.mean()) / (x.std() + 1e-10)

            X_lin = np.column_stack([np.ones(len(x)), x_std])
            try:
                beta_lin = np.linalg.lstsq(X_lin, y_vals, rcond=None)[0]
                resid_lin = y_vals - X_lin @ beta_lin
                ss_lin = np.sum(resid_lin ** 2)
            except np.linalg.LinAlgError:
                continue

            X_quad = np.column_stack([np.ones(len(x)), x_std, x_std ** 2])
            try:
                beta_quad = np.linalg.lstsq(X_quad, y_vals, rcond=None)[0]
                resid_quad = y_vals - X_quad @ beta_quad
                ss_quad = np.sum(resid_quad ** 2)
            except np.linalg.LinAlgError:
                continue

            n_obs = len(x)
            df_resid = n_obs - 3
            if df_resid <= 0 or ss_quad <= 0:
                continue
            f_stat = ((ss_lin - ss_quad) / 1) / (ss_quad / df_resid)
            f_pval = 1 - stats.f.cdf(f_stat, 1, df_resid)

            test_results.append({
                "factor": fcol, "return_horizon": rcol,
                "mono_r": mono_r, "f_pval": f_pval, "test_type": "f_test",
            })

    # FDR correction across all F-test / Mann-Whitney p-values (Codex v3 #8)
    if len(test_results) == 0:
        return {f: False for f in factor_cols}

    test_df = pd.DataFrame(test_results)
    reject, q_values, _, _ = multipletests(test_df["f_pval"].values, alpha=0.05, method="fdr_bh")
    test_df["q_value"] = q_values
    test_df["fdr_sig"] = reject

    n_fdr_sig = test_df["fdr_sig"].sum()
    print(f"  Total tests: {len(test_df)}, FDR-significant: {n_fdr_sig}")

    pass_factors: dict[str, bool] = {f: False for f in factor_cols}
    for fcol in factor_cols:
        sub = test_df[test_df["factor"] == fcol]
        if len(sub) == 0:
            continue
        # Pass if: (monotonicity |r| > 0.5 in any horizon) OR (FDR-significant in any horizon)
        has_mono = sub["mono_r"].abs().max() > 0.5 if sub["mono_r"].notna().any() else False
        has_fdr_sig = sub["fdr_sig"].any()
        if has_mono or has_fdr_sig:
            pass_factors[fcol] = True

    n_pass = sum(1 for v in pass_factors.values() if v)
    print(f"  Factors passing Filter E: {n_pass}")
    return pass_factors


# ============================================================
# Filter F: Robustness (Codex #4: ALL factors)
# ============================================================
def filter_f_robustness(
    analysis: pd.DataFrame, factor_cols: list[str]
) -> dict[str, bool]:
    """Filter F: Industry-level + market-cap-tier robustness for ALL factors."""
    print("\n" + "=" * 100)
    print("FILTER F: ROBUSTNESS CHECK (all factors)")
    print("=" * 100)

    pass_factors: dict[str, bool] = {f: False for f in factor_cols}

    # Industry groups (>=50 companies)
    if "industry" not in analysis.columns:
        print("  WARNING: no industry column. Skipping industry robustness.")
        industry_groups = {}
    else:
        ind_counts = analysis["industry"].value_counts()
        large_industries = ind_counts[ind_counts >= 50].index.tolist()
        industry_groups = {
            ind: analysis[analysis["industry"] == ind].index
            for ind in large_industries
        }
        print(f"  Industries with >=50 companies: {len(industry_groups)}")

    # Market cap tiers
    if "log_marketCap" in analysis.columns:
        mc = analysis["log_marketCap"].dropna()
        q33 = mc.quantile(0.33)
        q67 = mc.quantile(0.67)
        cap_tiers = {
            "small": analysis[analysis["log_marketCap"] <= q33].index,
            "mid": analysis[(analysis["log_marketCap"] > q33) & (analysis["log_marketCap"] <= q67)].index,
            "large": analysis[analysis["log_marketCap"] > q67].index,
        }
    else:
        cap_tiers = {}

    # Codex v3 #7 fix: test ALL return horizons, not just return_1y
    for fcol in factor_cols:
        # Industry robustness: same sign in >=50% of (industry, horizon) pairs
        industry_pass = True
        if len(industry_groups) >= 2:
            signs = []
            for rcol in RETURN_COLS:
                for ind, idx in industry_groups.items():
                    sub = analysis.loc[idx, [fcol, rcol]].dropna()
                    if len(sub) < 10:
                        continue
                    r, _ = stats.spearmanr(sub[fcol], sub[rcol])
                    signs.append(np.sign(r))
            if len(signs) >= 2:
                pos_frac = sum(1 for s in signs if s > 0) / len(signs)
                neg_frac = sum(1 for s in signs if s < 0) / len(signs)
                industry_pass = (pos_frac >= 0.5) or (neg_frac >= 0.5)
            else:
                industry_pass = False
        else:
            industry_pass = True

        # Market cap tier robustness: same sign in >=2/3 of (tier, horizon) pairs
        cap_pass = True
        if len(cap_tiers) >= 2:
            signs = []
            for rcol in RETURN_COLS:
                for tier_name, idx in cap_tiers.items():
                    sub = analysis.loc[idx, [fcol, rcol]].dropna()
                    if len(sub) < 20:
                        continue
                    r, _ = stats.spearmanr(sub[fcol], sub[rcol])
                    signs.append(np.sign(r))
            if len(signs) >= 2:
                pos_frac = sum(1 for s in signs if s > 0) / len(signs)
                neg_frac = sum(1 for s in signs if s < 0) / len(signs)
                cap_pass = (pos_frac >= 2 / 3) or (neg_frac >= 2 / 3)
            else:
                cap_pass = False

        pass_factors[fcol] = industry_pass and cap_pass

    n_pass = sum(1 for v in pass_factors.values() if v)
    print(f"  Factors passing Filter F: {n_pass}")
    return pass_factors


# ============================================================
# Gate Table Output
# ============================================================
def print_gate_table(
    factor_cols: list[str],
    filter_results: dict[str, dict[str, bool]],
    corr_df: pd.DataFrame,
    analysis: pd.DataFrame,
) -> pd.DataFrame:
    """Print the unified gate table and return as DataFrame."""
    print("\n" + "=" * 120)
    print("UNIFIED FACTOR GATE TABLE")
    print("=" * 120)

    filter_names = ["A(FDR+CI)", "B(LASSO)", "C(Indep)", "D(Neutral)", "E(NonLin)", "F(Robust)"]
    filter_keys = ["A", "B", "C", "D", "E", "F"]

    rows = []
    for f in factor_cols:
        row = {"Factor": f}
        n_pass = 0
        for key, name in zip(filter_keys, filter_names):
            passed = filter_results[key].get(f, False)
            row[name] = "PASS" if passed else "FAIL"
            if passed:
                n_pass += 1
        row["Pass"] = f"{n_pass}/6"
        row["n_pass"] = n_pass

        # Spearman r for each horizon
        for rcol in RETURN_COLS:
            subset = corr_df[(corr_df["factor"] == f) & (corr_df["return_horizon"] == rcol)]
            if len(subset) > 0:
                row[rcol.replace("return_", "") + "_r"] = subset.iloc[0]["spearman_r"]
            else:
                row[rcol.replace("return_", "") + "_r"] = np.nan
        rows.append(row)

    gate_df = pd.DataFrame(rows)
    gate_df = gate_df.sort_values("n_pass", ascending=False)

    # Print header
    header = (
        f"{'Factor':<30s} {'A(FDR+CI)':>10s} {'B(LASSO)':>10s} {'C(Indep)':>10s} "
        f"{'D(Neutral)':>11s} {'E(NonLin)':>10s} {'F(Robust)':>10s} {'Pass':>6s} "
        f"{'1Y_r':>8s} {'3Y_r':>8s} {'5Y_r':>8s}"
    )
    print(header)
    print("-" * len(header))

    for _, row in gate_df.iterrows():
        r1 = f"{row['1y_r']:+.4f}" if pd.notna(row.get("1y_r")) else "  N/A"
        r3 = f"{row['3y_r']:+.4f}" if pd.notna(row.get("3y_r")) else "  N/A"
        r5 = f"{row['5y_r']:+.4f}" if pd.notna(row.get("5y_r")) else "  N/A"
        print(
            f"{row['Factor']:<30s} {row['A(FDR+CI)']:>10s} {row['B(LASSO)']:>10s} "
            f"{row['C(Indep)']:>10s} {row['D(Neutral)']:>11s} {row['E(NonLin)']:>10s} "
            f"{row['F(Robust)']:>10s} {row['Pass']:>6s} {r1:>8s} {r3:>8s} {r5:>8s}"
        )

    return gate_df


# ============================================================
# Composite Score with Direction Bug Fix (Codex #6)
# ============================================================
def build_composite_score(
    analysis: pd.DataFrame,
    top_factors: list[str],
    corr_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build industry-neutral composite score with correct direction handling."""
    print("\n" + "=" * 100)
    print("COMPOSITE SCORE (direction-corrected, Codex #6)")
    print("=" * 100)

    # Determine direction for each factor from return_1y correlation
    factor_direction: dict[str, str] = {}
    for f in top_factors:
        sub = corr_df[(corr_df["factor"] == f) & (corr_df["return_horizon"] == "return_1y")]
        if len(sub) > 0:
            r = sub.iloc[0]["spearman_r"]
            factor_direction[f] = "negative" if r < 0 else "positive"
        else:
            factor_direction[f] = "positive"

    # Build composite (Codex #6 fix: ascending=False for negative factors)
    composite = pd.Series(0.0, index=analysis.index)
    used = 0

    for factor in top_factors:
        if factor not in analysis.columns:
            continue
        if analysis[factor].notna().sum() < 30:
            continue

        if "industry" in analysis.columns:
            if factor_direction[factor] == "negative":
                ranks = analysis.groupby("industry")[factor].rank(pct=True, ascending=False)
            else:
                ranks = analysis.groupby("industry")[factor].rank(pct=True, ascending=True)
        else:
            if factor_direction[factor] == "negative":
                ranks = analysis[factor].rank(pct=True, ascending=False)
            else:
                ranks = analysis[factor].rank(pct=True, ascending=True)

        composite += ranks.fillna(0.5)
        used += 1

    if used > 0:
        composite /= used

    print(f"  Factors used: {used}")
    print(f"  Factor directions:")
    for f in top_factors:
        print(f"    {f:<35s} -> {factor_direction.get(f, '?')}")

    # Evaluate composite vs returns
    for rcol in RETURN_COLS:
        valid_mask = composite.notna() & analysis[rcol].notna()
        if valid_mask.sum() < 30:
            continue
        r, p = stats.spearmanr(composite[valid_mask], analysis.loc[valid_mask, rcol])
        print(f"  Composite vs {rcol}: r={r:+.4f}, p={p:.2e}")

    analysis["composite_score"] = composite
    return analysis


# ============================================================
# Main
# ============================================================
def main():
    t0 = time.time()

    # 1. Build universe
    analysis, factor_cols = build_universe()

    # 2. Run all 6 filters
    filter_a_result, filter_a_corr = filter_a_fdr_bootstrap(analysis, factor_cols)
    filter_b_result = filter_b_lasso(analysis, factor_cols)
    filter_c_result = filter_c_independence(analysis, factor_cols)
    filter_d_result = filter_d_industry_neutral(analysis, factor_cols)
    filter_e_result = filter_e_nonlinear(analysis, factor_cols)
    filter_f_result = filter_f_robustness(analysis, factor_cols)

    filter_results = {
        "A": filter_a_result,
        "B": filter_b_result,
        "C": filter_c_result,
        "D": filter_d_result,
        "E": filter_e_result,
        "F": filter_f_result,
    }

    # 3. Gate table
    gate_df = print_gate_table(factor_cols, filter_results, filter_a_corr, analysis)

    # Codex v3 #11: Save gate table to CSV for audit/reproducibility
    gate_csv_path = f"{DATA}/unified_gate_table.csv"
    gate_df.to_csv(gate_csv_path, index=False)
    print(f"\n  Gate table saved to: {gate_csv_path}")

    # Codex v3 #10: Mark factors with max |r| < 0.02 across all horizons as "weak effect"
    MIN_EFFECT_SIZE = 0.02
    r_cols = ["1y_r", "3y_r", "5y_r"]
    gate_df["max_abs_r"] = gate_df[r_cols].abs().max(axis=1)
    weak_mask = gate_df["max_abs_r"] < MIN_EFFECT_SIZE
    if weak_mask.any():
        weak_factors = gate_df.loc[weak_mask, "Factor"].tolist()
        print(f"\n  WARNING: {len(weak_factors)} factor(s) pass gate but max|r| < {MIN_EFFECT_SIZE}:")
        for wf in weak_factors:
            print(f"    - {wf}")
        print("  These are flagged as WEAK_EFFECT and excluded from recommendations.")

    # 4. Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)

    # Exclude weak-effect factors from pass counts
    effective_gate = gate_df[~weak_mask] if weak_mask.any() else gate_df
    all_pass = effective_gate[effective_gate["n_pass"] == 6]["Factor"].tolist()
    five_plus = effective_gate[effective_gate["n_pass"] >= 5]["Factor"].tolist()

    print(f"\n  Universe: N = {len(analysis)} companies")
    print(f"  Total candidate factors: {len(factor_cols)}")

    print(f"\n  [6/6] All filters passed ({len(all_pass)} factors):")
    for f in all_pass:
        row = gate_df[gate_df["Factor"] == f].iloc[0]
        r1 = f"{row['1y_r']:+.4f}" if pd.notna(row.get("1y_r")) else "N/A"
        print(f"    - {f:<35s}  1Y_r={r1}")

    print(f"\n  [>=5/6] Five or more filters passed ({len(five_plus)} factors):")
    for f in five_plus:
        row = gate_df[gate_df["Factor"] == f].iloc[0]
        r1 = f"{row['1y_r']:+.4f}" if pd.notna(row.get("1y_r")) else "N/A"
        print(f"    - {f:<35s}  Pass={row['Pass']}  1Y_r={r1}")

    # 5. Recommended final factor set
    print(f"\n  Recommended final factor set (>=5/6 filters):")
    for i, f in enumerate(five_plus, 1):
        print(f"    {i}. {f}")

    # 6. Composite score
    if len(five_plus) > 0:
        analysis = build_composite_score(analysis, five_plus, filter_a_corr)

    elapsed = time.time() - t0
    print(f"\n  Total execution time: {elapsed:.1f} seconds")
    print("\n" + "=" * 100)
    print("DONE")
    print("=" * 100)


if __name__ == "__main__":
    main()
