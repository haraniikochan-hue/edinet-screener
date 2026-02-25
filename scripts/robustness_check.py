"""
ファクターロバスト性検証スクリプト
- 業種別ロバスト性
- 時価総額帯別ロバスト性
- 多変量回帰 + VIF
- 偏相関（時価総額制御）
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# ============================================================
# 1. データ読み込みと結合
# ============================================================
print("=" * 80)
print("1. DATA LOADING & MERGING")
print("=" * 80)

financials = pd.read_csv("data/financials_all.csv")
ratios = pd.read_csv("data/ratios_all.csv")
prices = pd.read_csv("data/stock_prices.csv")
returns = pd.read_csv("data/historical_returns.csv")
companies = pd.read_csv("data/companies.csv")

# 最新年度のfinancials/ratiosだけ使う
latest_year = financials.groupby("edinet_code")["fiscal_year"].max().reset_index()
latest_year.columns = ["edinet_code", "latest_fy"]
fin_latest = financials.merge(latest_year, left_on=["edinet_code", "fiscal_year"],
                               right_on=["edinet_code", "latest_fy"])
rat_latest = ratios.merge(latest_year, left_on=["edinet_code", "fiscal_year"],
                           right_on=["edinet_code", "latest_fy"])

# --- 派生ファクター: 配当連続年数、増配年数、赤字年有無、BPS増加年数、ROEσ ---
def calc_derived_factors(financials_df, ratios_df):
    """edinet_code 単位で時系列から派生ファクターを算出"""
    results = []
    for code, grp in financials_df.groupby("edinet_code"):
        grp = grp.sort_values("fiscal_year")

        # 配当連続年数
        divs = grp["dividend_per_share"].dropna()
        consec_div = 0
        for v in divs.values[::-1]:
            if v > 0:
                consec_div += 1
            else:
                break

        # 増配年数
        div_vals = grp["dividend_per_share"].dropna().values
        consec_increase = 0
        for i in range(len(div_vals) - 1, 0, -1):
            if div_vals[i] > div_vals[i - 1]:
                consec_increase += 1
            else:
                break

        # 赤字年有無
        ni = grp["net_income"].dropna()
        has_loss = int((ni < 0).any())

        # BPS増加年数
        bps_vals = grp["bps"].dropna().values
        bps_increase_years = 0
        for i in range(len(bps_vals) - 1, 0, -1):
            if bps_vals[i] > bps_vals[i - 1]:
                bps_increase_years += 1
            else:
                break

        results.append({
            "edinet_code": code,
            "consecutive_dividend_years": consec_div,
            "consecutive_increase_years": consec_increase,
            "has_loss_year": has_loss,
            "bps_increase_years": bps_increase_years,
        })
    return pd.DataFrame(results)

def calc_roe_sigma(ratios_df):
    """ROEの標準偏差"""
    roe_std = ratios_df.groupby("edinet_code")["roe"].std().reset_index()
    roe_std.columns = ["edinet_code", "roe_sigma"]
    return roe_std

derived = calc_derived_factors(financials, ratios)
roe_sigma = calc_roe_sigma(ratios)

# FCF利回り = FCF / marketCap
# pricesにはmarketCapあり、ratios最新年度にfcfあり

# 結合: edinet_code ベース
df = fin_latest[["edinet_code", "sec_code", "industry"]].copy()
df = df.merge(prices[["edinet_code", "ticker", "marketCap", "priceToBook", "forwardPE",
                        "dividendYield", "currentPrice", "bookValue"]],
              on="edinet_code", how="left")
df = df.merge(rat_latest[["edinet_code", "roe", "fcf"]], on="edinet_code", how="left")
df = df.merge(derived, on="edinet_code", how="left")
df = df.merge(roe_sigma, on="edinet_code", how="left")

# historical_returns は ticker ベースで結合
df = df.merge(returns, on="ticker", how="left")

# FCF利回り算出
df["fcf_yield"] = df["fcf"] / df["marketCap"]

print(f"Merged dataset: {len(df)} rows")
print(f"With return_1y: {df['return_1y'].notna().sum()}")
print(f"With marketCap: {df['marketCap'].notna().sum()}")

# ============================================================
# 2. ファクター定義 & 前処理
# ============================================================
factor_cols = {
    "marketCap": "時価総額",
    "consecutive_dividend_years": "配当連続年数",
    "roe_sigma": "ROEσ",
    "consecutive_increase_years": "増配年数",
    "has_loss_year": "赤字年有無",
    "bps_increase_years": "BPS増加年数",
    "priceToBook": "PBR",
    "fcf_yield": "FCF利回り",
    "forwardPE": "forwardPE",
}

# 外れ値クリッピング (1%/99%)
def clip_outliers(s, lower=0.01, upper=0.99):
    lo = s.quantile(lower)
    hi = s.quantile(upper)
    return s.clip(lo, hi)

for col in factor_cols:
    if col in df.columns and df[col].dtype in [np.float64, np.int64, float, int]:
        valid = df[col].dropna()
        if len(valid) > 10:
            df[col] = clip_outliers(df[col])

# log時価総額のほうが分布が良い
df["log_marketCap"] = np.log1p(df["marketCap"])

print(f"\nFactor availability:")
for col, name in factor_cols.items():
    n = df[col].notna().sum()
    print(f"  {name:20s} ({col:30s}): {n:5d}")

# ============================================================
# 3. 業種別ロバスト性
# ============================================================
print("\n" + "=" * 80)
print("3. INDUSTRY-LEVEL ROBUSTNESS")
print("=" * 80)

# 50社以上ある業種を選定
industry_counts = df.groupby("industry").size()
large_industries = industry_counts[industry_counts >= 50].index.tolist()
print(f"\nIndustries with >= 50 companies: {len(large_industries)}")
for ind in large_industries:
    print(f"  {ind}: {industry_counts[ind]} companies")

# 業種別相関
target = "return_1y"
industry_corr = {}

for ind in large_industries:
    sub = df[df["industry"] == ind].copy()
    corrs = {}
    for col, name in factor_cols.items():
        valid = sub[[col, target]].dropna()
        if len(valid) >= 20:
            r, p = stats.spearmanr(valid[col], valid[target])
            corrs[name] = {"r": r, "p": p, "n": len(valid)}
        else:
            corrs[name] = {"r": np.nan, "p": np.nan, "n": len(valid)}
    industry_corr[ind] = corrs

# 一覧表示
print(f"\n{'Factor':<20s}", end="")
for ind in large_industries:
    short = ind[:8]
    print(f" {short:>10s}", end="")
print(f" {'Consistent':>10s}")

print("-" * (20 + 11 * (len(large_industries) + 1)))

factor_consistency = {}
for col, name in factor_cols.items():
    print(f"{name:<20s}", end="")
    signs = []
    sig_count = 0
    total_count = 0
    for ind in large_industries:
        info = industry_corr[ind].get(name, {"r": np.nan, "p": np.nan})
        r = info["r"]
        p = info["p"]
        if not np.isnan(r):
            total_count += 1
            if p < 0.1:
                sig_count += 1
                signs.append(np.sign(r))
            marker = f"{r:+.2f}" + ("*" if p < 0.05 else "'" if p < 0.1 else "")
        else:
            marker = "  N/A"
        print(f" {marker:>10s}", end="")

    # Consistency: same sign across industries
    if len(signs) >= 3:
        pos = sum(1 for s in signs if s > 0)
        neg = sum(1 for s in signs if s < 0)
        ratio = max(pos, neg) / len(signs)
        if ratio >= 0.8 and sig_count >= 3:
            consistency = "○"
        elif ratio >= 0.6 and sig_count >= 2:
            consistency = "△"
        else:
            consistency = "×"
    elif sig_count >= 1 and total_count <= 3:
        consistency = "△"
    else:
        consistency = "×"

    factor_consistency[name] = consistency
    print(f" {consistency:>10s}")

# ============================================================
# 4. 時価総額帯別ロバスト性
# ============================================================
print("\n" + "=" * 80)
print("4. MARKET CAP BAND ROBUSTNESS")
print("=" * 80)

df["cap_band"] = pd.cut(df["marketCap"],
                         bins=[0, 10e9, 100e9, np.inf],
                         labels=["Small(<100B)", "Mid(100B-1T)", "Large(>1T)"])

cap_band_results = {}
print(f"\n{'Factor':<20s} {'Small':>15s} {'Mid':>15s} {'Large':>15s} {'Stable':>8s}")
print("-" * 78)

factor_cap_stability = {}
for col, name in factor_cols.items():
    if col == "marketCap":
        # 時価総額自身は除外
        factor_cap_stability[name] = "-"
        continue

    band_corrs = {}
    for band in ["Small(<100B)", "Mid(100B-1T)", "Large(>1T)"]:
        sub = df[df["cap_band"] == band][[col, target]].dropna()
        if len(sub) >= 20:
            r, p = stats.spearmanr(sub[col], sub[target])
            band_corrs[band] = (r, p, len(sub))
        else:
            band_corrs[band] = (np.nan, np.nan, len(sub))

    cap_band_results[name] = band_corrs

    print(f"{name:<20s}", end="")
    signs = []
    for band in ["Small(<100B)", "Mid(100B-1T)", "Large(>1T)"]:
        r, p, n = band_corrs[band]
        if not np.isnan(r):
            marker = f"{r:+.3f}(n={n})"
            if p < 0.1:
                signs.append(np.sign(r))
        else:
            marker = f"N/A(n={n})"
        print(f" {marker:>15s}", end="")

    if len(signs) >= 2 and len(set(signs)) == 1:
        stability = "○"
    elif len(signs) >= 2:
        stability = "△" if len(signs) < 3 else "×"
    else:
        stability = "×"
    factor_cap_stability[name] = stability
    print(f" {stability:>8s}")

# ============================================================
# 5. 多変量回帰 + VIF
# ============================================================
print("\n" + "=" * 80)
print("5. MULTIVARIATE OLS REGRESSION + VIF")
print("=" * 80)

reg_cols = ["log_marketCap", "consecutive_dividend_years", "roe_sigma",
            "consecutive_increase_years", "has_loss_year", "bps_increase_years",
            "priceToBook", "fcf_yield", "forwardPE"]

reg_df = df[[target] + reg_cols].dropna()
print(f"\nRegression sample size: {len(reg_df)}")

# 標準化（解釈しやすくするため）
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(reg_df[reg_cols]),
                         columns=reg_cols, index=reg_df.index)
y = reg_df[target]

# OLS
X_const = sm.add_constant(X_scaled)
model = sm.OLS(y, X_const).fit()
print("\n--- OLS Summary ---")
print(f"R-squared: {model.rsquared:.4f}")
print(f"Adj R-squared: {model.rsquared_adj:.4f}")
print(f"F-statistic: {model.fvalue:.2f} (p={model.f_pvalue:.4e})")

print(f"\n{'Variable':<30s} {'Coef':>10s} {'StdErr':>10s} {'t':>10s} {'p-value':>12s} {'Sig':>5s}")
print("-" * 82)

factor_pvalues = {}
name_map = {
    "log_marketCap": "時価総額",
    "consecutive_dividend_years": "配当連続年数",
    "roe_sigma": "ROEσ",
    "consecutive_increase_years": "増配年数",
    "has_loss_year": "赤字年有無",
    "bps_increase_years": "BPS増加年数",
    "priceToBook": "PBR",
    "fcf_yield": "FCF利回り",
    "forwardPE": "forwardPE",
}

for var in reg_cols:
    coef = model.params[var]
    se = model.bse[var]
    t = model.tvalues[var]
    p = model.pvalues[var]
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "." if p < 0.1 else ""
    display_name = name_map.get(var, var)
    print(f"{display_name:<30s} {coef:>+10.4f} {se:>10.4f} {t:>+10.3f} {p:>12.4e} {sig:>5s}")
    factor_pvalues[display_name] = p

# VIF
print(f"\n--- VIF (Variance Inflation Factor) ---")
vif_data = pd.DataFrame()
vif_data["Variable"] = reg_cols
vif_data["VIF"] = [variance_inflation_factor(X_scaled.values, i) for i in range(len(reg_cols))]
vif_data["Name"] = [name_map.get(v, v) for v in reg_cols]

for _, row in vif_data.iterrows():
    flag = " *** HIGH" if row["VIF"] > 5 else " * moderate" if row["VIF"] > 2.5 else ""
    print(f"  {row['Name']:<30s} VIF={row['VIF']:.2f}{flag}")

# ============================================================
# 6. 偏相関（時価総額制御）
# ============================================================
print("\n" + "=" * 80)
print("6. PARTIAL CORRELATION (CONTROLLING FOR MARKET CAP)")
print("=" * 80)

def partial_corr(x, y, z):
    """x と y の相関から z の影響を除去"""
    valid = pd.DataFrame({"x": x, "y": y, "z": z}).dropna()
    if len(valid) < 20:
        return np.nan, np.nan
    # residualize
    from sklearn.linear_model import LinearRegression
    lr = LinearRegression()
    z_arr = valid["z"].values.reshape(-1, 1)

    lr.fit(z_arr, valid["x"])
    x_resid = valid["x"] - lr.predict(z_arr)

    lr.fit(z_arr, valid["y"])
    y_resid = valid["y"] - lr.predict(z_arr)

    r, p = stats.spearmanr(x_resid, y_resid)
    return r, p

print(f"\n{'Factor':<25s} {'Raw Corr':>10s} {'Partial':>10s} {'p-value':>12s} {'Change':>10s}")
print("-" * 72)

factor_partial = {}
for col, name in factor_cols.items():
    if col == "marketCap":
        continue

    valid = df[[col, target, "log_marketCap"]].dropna()
    if len(valid) < 20:
        factor_partial[name] = (np.nan, np.nan)
        continue

    # Raw correlation
    r_raw, p_raw = stats.spearmanr(valid[col], valid[target])

    # Partial correlation controlling for log_marketCap
    r_partial, p_partial = partial_corr(valid[col], valid[target], valid["log_marketCap"])

    factor_partial[name] = (r_partial, p_partial)

    if not np.isnan(r_partial):
        change = r_partial - r_raw
        print(f"{name:<25s} {r_raw:>+10.4f} {r_partial:>+10.4f} {p_partial:>12.4e} {change:>+10.4f}")
    else:
        print(f"{name:<25s} {r_raw:>+10.4f} {'N/A':>10s} {'N/A':>12s} {'N/A':>10s}")

# ============================================================
# 7. 総合評価サマリー
# ============================================================
print("\n" + "=" * 80)
print("7. COMPREHENSIVE ROBUSTNESS SUMMARY")
print("=" * 80)

print(f"\n{'Factor':<20s} {'Industry':>10s} {'CapBand':>10s} {'OLS p':>12s} {'PartCorr':>10s} {'Grade':>8s}")
print("-" * 75)

for col, name in factor_cols.items():
    ind_score = factor_consistency.get(name, "×")
    cap_score = factor_cap_stability.get(name, "×")
    p_val = factor_pvalues.get(name, 1.0)

    partial_r, partial_p = factor_partial.get(name, (np.nan, np.nan))
    partial_str = f"{partial_r:+.4f}" if not np.isnan(partial_r) else "N/A"

    p_str = f"{p_val:.4e}" if p_val < 1.0 else "N/A"

    # Grading logic
    score = 0
    if ind_score == "○":
        score += 3
    elif ind_score == "△":
        score += 1

    if cap_score == "○":
        score += 3
    elif cap_score == "△":
        score += 1
    elif cap_score == "-":
        score += 1  # neutral for marketCap itself

    if p_val < 0.01:
        score += 3
    elif p_val < 0.05:
        score += 2
    elif p_val < 0.1:
        score += 1

    if not np.isnan(partial_r) and not np.isnan(partial_p):
        if partial_p < 0.05 and abs(partial_r) > 0.05:
            score += 3
        elif partial_p < 0.1:
            score += 1

    if score >= 9:
        grade = "S"
    elif score >= 7:
        grade = "A"
    elif score >= 5:
        grade = "B"
    else:
        grade = "C"

    print(f"{name:<20s} {ind_score:>10s} {cap_score:>10s} {p_str:>12s} {partial_str:>10s} {grade:>8s}")

print("\n" + "=" * 80)
print("GRADING CRITERIA:")
print("  S (>=9pt): Highly robust - works across industries, cap bands, and multivariate")
print("  A (>=7pt): Robust - mostly consistent with some caveats")
print("  B (>=5pt): Moderate - works in some conditions but not universally")
print("  C (<5pt):  Weak - likely spurious or limited to specific segments")
print("=" * 80)
