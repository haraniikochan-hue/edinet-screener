#!/usr/bin/env python3
"""非線形関係・交互作用効果・閾値効果の分析スクリプト (v2: 外れ値処理修正)"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

DATA_DIR = "/Users/harann/edinet-screener/data"

# --- 1. データ読み込み・結合 ---
print("=" * 80)
print("STEP 1: データ読み込みと結合")
print("=" * 80)

companies = pd.read_csv(f"{DATA_DIR}/companies.csv")
stock_prices = pd.read_csv(f"{DATA_DIR}/stock_prices.csv")
historical_returns = pd.read_csv(f"{DATA_DIR}/historical_returns.csv")
ratios_all = pd.read_csv(f"{DATA_DIR}/ratios_all.csv")
financials_all = pd.read_csv(f"{DATA_DIR}/financials_all.csv")

sp_key = stock_prices[["edinet_code", "ticker"]].drop_duplicates()
returns = historical_returns.merge(sp_key, on="ticker", how="inner")
print(f"historical_returns: {len(historical_returns)} rows -> merged: {len(returns)} rows")

ratios_latest = ratios_all.sort_values("fiscal_year").groupby("edinet_code").last().reset_index()
fin_latest = financials_all.sort_values("fiscal_year").groupby("edinet_code").last().reset_index()

sp_cols = ["edinet_code", "ticker", "currentPrice", "marketCap", "priceToBook",
           "dividendYield", "trailingPE", "forwardPE", "bookValue", "totalRevenue",
           "returnOnEquity", "debtToEquity", "freeCashflow", "beta",
           "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "fiftyDayAverage", "twoHundredDayAverage"]
sp_data = stock_prices[sp_cols].drop_duplicates(subset="edinet_code")

df = returns.merge(sp_data, on="edinet_code", how="inner")
df = df.merge(ratios_latest[["edinet_code", "roe", "roe_official", "operating_margin",
                              "payout_ratio", "fcf", "eps", "eps_growth",
                              "revenue_growth", "ni_growth", "equity_ratio",
                              "bps", "bps_growth"]], on="edinet_code", how="left")
df = df.merge(fin_latest[["edinet_code", "dividend_per_share"]], on="edinet_code", how="left")
df = df.merge(companies[["edinet_code", "industry"]], on="edinet_code", how="left")

# 派生ファクター
df["fcf_yield"] = df["freeCashflow"] / df["marketCap"]
df["fcf_yield"] = df["fcf_yield"].replace([np.inf, -np.inf], np.nan)

roe_ts = ratios_all.groupby("edinet_code")["roe"].agg(["mean", "std", "count"]).reset_index()
roe_ts.columns = ["edinet_code", "roe_mean", "roe_std", "roe_count"]
df = df.merge(roe_ts, on="edinet_code", how="left")

def calc_dividend_streaks(fin_df):
    results = []
    for code, grp in fin_df.groupby("edinet_code"):
        grp = grp.sort_values("fiscal_year")
        divs = grp["dividend_per_share"].dropna()
        if len(divs) == 0:
            results.append({"edinet_code": code, "consecutive_div_years": 0, "div_increase_years": 0})
            continue
        consec = 0
        for v in reversed(divs.values):
            if v > 0:
                consec += 1
            else:
                break
        inc = 0
        vals = divs.values
        for i in range(len(vals) - 1, 0, -1):
            if vals[i] > vals[i - 1]:
                inc += 1
            else:
                break
        results.append({"edinet_code": code, "consecutive_div_years": consec, "div_increase_years": inc})
    return pd.DataFrame(results)

div_streaks = calc_dividend_streaks(financials_all)
df = df.merge(div_streaks, on="edinet_code", how="left")

# 時価総額を兆円単位に変換（可読性向上）
df["marketCap_trillion"] = df["marketCap"] / 1e12

print(f"結合後データ: {len(df)} rows, {len(df.columns)} columns")

# --- 外れ値クリッピング: 全数値列に適用（リターンも含む）---
RETURN_VARS = ["return_1y", "return_3y", "return_5y"]
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
for col in numeric_cols:
    lower = df[col].quantile(0.01)
    upper = df[col].quantile(0.99)
    df[col] = df[col].clip(lower, upper)

print(f"外れ値クリッピング(1%/99%)適用済み")
for rv in RETURN_VARS:
    print(f"  {rv}: min={df[rv].min():.3f}, max={df[rv].max():.3f}, median={df[rv].median():.3f}")

# ========================================================================
# STEP 2: 十分位分析（非線形関係の検証）
# ========================================================================
print("\n" + "=" * 80)
print("STEP 2: 十分位（デシル）分析 -- 非線形関係の検証")
print("=" * 80)

FACTORS = {
    "marketCap_trillion": "時価総額(兆円)",
    "roe_std": "ROE標準偏差(σ)",
    "roe_mean": "ROE平均",
    "consecutive_div_years": "配当連続年数",
    "div_increase_years": "増配年数",
    "priceToBook": "PBR",
    "forwardPE": "フォワードPE",
    "trailingPE": "トレーリングPE",
    "dividendYield": "配当利回り",
    "fcf_yield": "FCF利回り",
    "operating_margin": "営業利益率",
    "payout_ratio": "配当性向",
    "equity_ratio": "自己資本比率",
    "beta": "ベータ",
    "debtToEquity": "D/E比率",
    "revenue_growth": "売上成長率",
    "eps_growth": "EPS成長率",
}

def decile_analysis(df, factor, return_var, n_quantiles=10):
    subset = df[[factor, return_var]].dropna()
    if len(subset) < 50:
        return None
    try:
        subset["decile"] = pd.qcut(subset[factor], n_quantiles, labels=False, duplicates="drop")
    except ValueError:
        return None

    actual_groups = subset["decile"].nunique()
    if actual_groups < 4:
        return None

    result = subset.groupby("decile").agg(
        mean_return=(return_var, "mean"),
        median_return=(return_var, "median"),
        count=(return_var, "count"),
        factor_mean=(factor, "mean"),
        factor_median=(factor, "median"),
    ).reset_index()

    sp_r, sp_p = stats.spearmanr(result["decile"], result["mean_return"])

    x = subset[factor].values
    y = subset[return_var].values
    x_norm = (x - x.mean()) / (x.std() + 1e-10)
    try:
        coeffs_lin = np.polyfit(x_norm, y, 1)
        residuals_lin = y - np.polyval(coeffs_lin, x_norm)
        ss_res_lin = np.sum(residuals_lin ** 2)

        coeffs_quad = np.polyfit(x_norm, y, 2)
        residuals_quad = y - np.polyval(coeffs_quad, x_norm)
        ss_res_quad = np.sum(residuals_quad ** 2)

        n = len(y)
        f_stat = ((ss_res_lin - ss_res_quad) / 1) / (ss_res_quad / (n - 3))
        f_p = 1 - stats.f.cdf(f_stat, 1, n - 3)
    except Exception:
        f_stat, f_p = np.nan, np.nan
        coeffs_quad = [0, 0, 0]

    return {
        "decile_data": result,
        "n_samples": len(subset),
        "monotonic_r": sp_r,
        "monotonic_p": sp_p,
        "quad_coeff": coeffs_quad[0] if len(coeffs_quad) >= 3 else 0,
        "nonlinear_f": f_stat,
        "nonlinear_p": f_p,
        "d1_return": result.iloc[0]["mean_return"],
        "d10_return": result.iloc[-1]["mean_return"],
        "spread_d10_d1": result.iloc[-1]["mean_return"] - result.iloc[0]["mean_return"],
    }

nonlinear_findings = []

for return_var in RETURN_VARS:
    print(f"\n--- リターン変数: {return_var} ---")
    print(f"{'ファクター':<20} {'N':>5} {'D1平均':>8} {'D10平均':>8} {'D10-D1':>8} {'単調r':>7} {'単調p':>10} {'二次係数':>8} {'非線形F':>8} {'非線形p':>10}")
    print("-" * 120)

    for factor, factor_name in FACTORS.items():
        result = decile_analysis(df, factor, return_var)
        if result is None:
            continue

        print(f"{factor_name:<20} {result['n_samples']:>5} {result['d1_return']:>8.3f} {result['d10_return']:>8.3f} "
              f"{result['spread_d10_d1']:>8.3f} {result['monotonic_r']:>7.3f} {result['monotonic_p']:>10.2e} "
              f"{result['quad_coeff']:>8.4f} {result['nonlinear_f']:>8.2f} {result['nonlinear_p']:>10.2e}")

        if result['nonlinear_p'] < 0.05 or abs(result['spread_d10_d1']) > 0.1:
            pattern = "U字型" if result['quad_coeff'] > 0.001 else "逆U字型" if result['quad_coeff'] < -0.001 else "線形"
            nonlinear_findings.append({
                "factor": factor_name,
                "factor_key": factor,
                "return_var": return_var,
                "n_samples": result["n_samples"],
                "spread": result["spread_d10_d1"],
                "monotonic_r": result["monotonic_r"],
                "monotonic_p": result["monotonic_p"],
                "quad_coeff": result["quad_coeff"],
                "nonlinear_p": result["nonlinear_p"],
                "pattern": pattern,
            })

    # 十分位詳細（主要ファクター）
    key_factors = ["marketCap_trillion", "roe_std", "roe_mean", "priceToBook", "forwardPE",
                   "consecutive_div_years", "div_increase_years", "fcf_yield", "dividendYield"]
    for factor in key_factors:
        if factor not in FACTORS:
            continue
        result = decile_analysis(df, factor, return_var)
        if result is None:
            continue
        print(f"\n  [{FACTORS[factor]}] 十分位別 {return_var} 詳細:")
        for _, row in result["decile_data"].iterrows():
            bar_len = int(abs(row["mean_return"]) * 10)
            bar_len = min(bar_len, 40)
            bar = "+" * bar_len if row["mean_return"] >= 0 else "-" * bar_len
            print(f"    D{int(row['decile'])+1:>2}: ret={row['mean_return']:>7.3f} | med={row['median_return']:>7.3f} | "
                  f"n={int(row['count']):>4} | fac_avg={row['factor_mean']:>10.4f} | {bar}")

# ========================================================================
# STEP 3: 交互作用効果の検証
# ========================================================================
print("\n\n" + "=" * 80)
print("STEP 3: 交互作用効果の検証（2x2マトリクス）")
print("=" * 80)

INTERACTIONS = [
    ("roe_std", "marketCap_trillion", "ROEσ × 時価総額", True, False),
    ("consecutive_div_years", "priceToBook", "配当連続年数 × PBR", False, True),
    ("fcf_yield", "div_increase_years", "FCF利回り × 増配年数", False, False),
    ("forwardPE", "operating_margin", "フォワードPE × 営業利益率", True, False),
    ("roe_std", "div_increase_years", "ROEσ × 増配年数", True, False),
]

def interaction_analysis(df, factor1, factor2, return_var, invert1=False, invert2=False):
    subset = df[[factor1, factor2, return_var]].dropna()
    if len(subset) < 100:
        return None

    med1 = subset[factor1].median()
    med2 = subset[factor2].median()

    if invert1:
        subset["g1"] = (subset[factor1] <= med1).map({True: "High", False: "Low"})
    else:
        subset["g1"] = (subset[factor1] > med1).map({True: "High", False: "Low"})

    if invert2:
        subset["g2"] = (subset[factor2] <= med2).map({True: "High", False: "Low"})
    else:
        subset["g2"] = (subset[factor2] > med2).map({True: "High", False: "Low"})

    groups = {}
    for g1 in ["Low", "High"]:
        for g2 in ["Low", "High"]:
            mask = (subset["g1"] == g1) & (subset["g2"] == g2)
            grp = subset.loc[mask, return_var]
            groups[(g1, g2)] = {
                "mean": grp.mean(),
                "median": grp.median(),
                "count": len(grp),
                "std": grp.std(),
            }

    base = groups[("Low", "Low")]["mean"]
    f1_only = groups[("High", "Low")]["mean"] - base
    f2_only = groups[("Low", "High")]["mean"] - base
    combined = groups[("High", "High")]["mean"] - base
    interaction = combined - (f1_only + f2_only)

    try:
        data_for_anova = []
        for g1 in ["Low", "High"]:
            for g2 in ["Low", "High"]:
                mask = (subset["g1"] == g1) & (subset["g2"] == g2)
                vals = subset.loc[mask, return_var].values
                for v in vals:
                    data_for_anova.append({"g1": g1, "g2": g2, "ret": v})
        anova_df = pd.DataFrame(data_for_anova)
        anova_df["g1_num"] = (anova_df["g1"] == "High").astype(int)
        anova_df["g2_num"] = (anova_df["g2"] == "High").astype(int)
        anova_df["interact"] = anova_df["g1_num"] * anova_df["g2_num"]

        from numpy.linalg import lstsq
        X = anova_df[["g1_num", "g2_num", "interact"]].values
        X = np.column_stack([np.ones(len(X)), X])
        y = anova_df["ret"].values

        beta_full, _, _, _ = lstsq(X, y, rcond=None)
        ss_res_full = np.sum((y - X @ beta_full) ** 2)

        X_red = X[:, :3]
        beta_red, _, _, _ = lstsq(X_red, y, rcond=None)
        ss_res_red = np.sum((y - X_red @ beta_red) ** 2)

        n = len(y)
        f_interact = ((ss_res_red - ss_res_full) / 1) / (ss_res_full / (n - 4))
        p_interact = 1 - stats.f.cdf(f_interact, 1, n - 4)
    except Exception:
        f_interact, p_interact = np.nan, np.nan

    return {
        "groups": groups,
        "base": base,
        "f1_only_effect": f1_only,
        "f2_only_effect": f2_only,
        "combined_effect": combined,
        "interaction_effect": interaction,
        "interaction_f": f_interact,
        "interaction_p": p_interact,
        "n_total": len(subset),
    }

interaction_findings = []

for factor1, factor2, name, inv1, inv2 in INTERACTIONS:
    f1_name = FACTORS.get(factor1, factor1)
    f2_name = FACTORS.get(factor2, factor2)
    print(f"\n### {name} ###")
    # invert の説明
    if inv1:
        print(f"  (注: {f1_name} は低い方を 'High' とする: 低σ=安定, 低PE=割安)")
    if inv2:
        print(f"  (注: {f2_name} は低い方を 'High' とする: 低PBR=割安)")

    for return_var in RETURN_VARS:
        result = interaction_analysis(df, factor1, factor2, return_var, inv1, inv2)
        if result is None:
            print(f"  {return_var}: データ不足でスキップ")
            continue

        g = result["groups"]
        print(f"\n  [{return_var}] N={result['n_total']}")
        print(f"  {'':>25} | {'Low '+f2_name:>22} | {'High '+f2_name:>22}")
        print(f"  {'-'*75}")
        print(f"  {'Low '+f1_name:>25} | mean={g[('Low','Low')]['mean']:>7.3f} n={g[('Low','Low')]['count']:>4} | mean={g[('Low','High')]['mean']:>7.3f} n={g[('Low','High')]['count']:>4}")
        print(f"  {'High '+f1_name:>25} | mean={g[('High','Low')]['mean']:>7.3f} n={g[('High','Low')]['count']:>4} | mean={g[('High','High')]['mean']:>7.3f} n={g[('High','High')]['count']:>4}")
        print(f"  効果分解: F1のみ={result['f1_only_effect']:>+.4f}, F2のみ={result['f2_only_effect']:>+.4f}, "
              f"加法予測={result['f1_only_effect']+result['f2_only_effect']:>+.4f}, 実際={result['combined_effect']:>+.4f}")
        print(f"  交互作用効果={result['interaction_effect']:>+.4f} | F={result['interaction_f']:.2f} | p={result['interaction_p']:.4f}")

        synergy = "相乗効果あり" if result['interaction_effect'] > 0 and result['interaction_p'] < 0.1 else \
                  "相殺効果" if result['interaction_effect'] < 0 and result['interaction_p'] < 0.1 else \
                  "有意な交互作用なし"
        print(f"  判定: {synergy}")
        # HH vs LL のスプレッド
        hh_ll_spread = g[("High", "High")]["mean"] - g[("Low", "Low")]["mean"]
        # HH vs 全体平均
        total_mean = df[return_var].mean()
        hh_vs_avg = g[("High", "High")]["mean"] - total_mean
        print(f"  HH-LL spread={hh_ll_spread:>+.4f} | HH vs 全体平均={hh_vs_avg:>+.4f}")

        interaction_findings.append({
            "name": name,
            "return_var": return_var,
            "n_total": result["n_total"],
            "f1_effect": result["f1_only_effect"],
            "f2_effect": result["f2_only_effect"],
            "combined": result["combined_effect"],
            "interaction": result["interaction_effect"],
            "interaction_p": result["interaction_p"],
            "synergy": synergy,
            "hh_mean": g[("High", "High")]["mean"],
            "ll_mean": g[("Low", "Low")]["mean"],
            "hh_ll_spread": hh_ll_spread,
            "hh_n": g[("High", "High")]["count"],
        })

# ========================================================================
# STEP 4: 閾値効果の検証
# ========================================================================
print("\n\n" + "=" * 80)
print("STEP 4: 閾値効果の検証")
print("=" * 80)

def threshold_analysis(df, factor, return_var, thresholds):
    subset = df[[factor, return_var]].dropna()
    if len(subset) < 50:
        return None
    results = []
    for thresh in thresholds:
        below = subset.loc[subset[factor] <= thresh, return_var]
        above = subset.loc[subset[factor] > thresh, return_var]
        if len(below) < 20 or len(above) < 20:
            continue
        t_stat, t_p = stats.ttest_ind(above, below, equal_var=False)
        results.append({
            "threshold": thresh,
            "n_below": len(below),
            "n_above": len(above),
            "mean_below": below.mean(),
            "mean_above": above.mean(),
            "diff": above.mean() - below.mean(),
            "t_stat": t_stat,
            "t_p": t_p,
        })
    return results

THRESHOLD_CONFIGS = {
    "priceToBook": {
        "name": "PBR",
        "thresholds": [0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0],
        "format": lambda x: f"{x:.1f}",
    },
    "marketCap_trillion": {
        "name": "時価総額(兆円)",
        "thresholds": [0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 5.0],
        "format": lambda x: f"{x:.2f}兆",
    },
    "consecutive_div_years": {
        "name": "配当連続年数",
        "thresholds": [0, 1, 2, 3, 4, 5],
        "format": lambda x: f"{x:.0f}年",
    },
    "div_increase_years": {
        "name": "増配年数",
        "thresholds": [0, 1, 2, 3, 4],
        "format": lambda x: f"{x:.0f}年",
    },
    "roe_std": {
        "name": "ROEσ",
        "thresholds": [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15],
        "format": lambda x: f"{x:.2f}",
    },
    "forwardPE": {
        "name": "フォワードPE",
        "thresholds": [5, 8, 10, 12, 15, 20, 30, 50],
        "format": lambda x: f"{x:.0f}",
    },
    "dividendYield": {
        "name": "配当利回り(%)",
        "thresholds": [1.0, 2.0, 3.0, 4.0, 5.0],
        "format": lambda x: f"{x:.1f}%",
    },
    "operating_margin": {
        "name": "営業利益率",
        "thresholds": [0.0, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20],
        "format": lambda x: f"{x*100:.0f}%",
    },
    "fcf_yield": {
        "name": "FCF利回り",
        "thresholds": [-0.02, 0.0, 0.02, 0.05, 0.08, 0.10],
        "format": lambda x: f"{x*100:.0f}%",
    },
    "roe_mean": {
        "name": "ROE平均",
        "thresholds": [0.0, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20],
        "format": lambda x: f"{x*100:.0f}%",
    },
}

threshold_findings = []

for factor, config in THRESHOLD_CONFIGS.items():
    print(f"\n### {config['name']} ({factor}) ###")
    fmt = config.get("format", lambda x: f"{x:.2f}")

    for return_var in RETURN_VARS:
        results = threshold_analysis(df, factor, return_var, config["thresholds"])
        if not results:
            continue

        print(f"\n  [{return_var}]")
        print(f"  {'閾値':>12} | {'以下N':>5} {'以下平均':>8} | {'超N':>5} {'超平均':>8} | {'差':>8} | {'t値':>7} {'p値':>10}")
        print(f"  {'-'*85}")

        best_split = max(results, key=lambda x: abs(x["t_stat"]))

        for r in results:
            sig = "***" if r["t_p"] < 0.001 else "**" if r["t_p"] < 0.01 else "*" if r["t_p"] < 0.05 else " "
            marker = " <-- BEST" if r == best_split else ""
            print(f"  {fmt(r['threshold']):>12} | {r['n_below']:>5} {r['mean_below']:>8.3f} | {r['n_above']:>5} {r['mean_above']:>8.3f} | "
                  f"{r['diff']:>+8.3f} | {r['t_stat']:>7.2f} {r['t_p']:>10.4f} {sig}{marker}")

        if best_split["t_p"] < 0.05:
            threshold_findings.append({
                "factor": config["name"],
                "factor_key": factor,
                "return_var": return_var,
                "threshold": best_split["threshold"],
                "threshold_formatted": fmt(best_split["threshold"]),
                "diff": best_split["diff"],
                "t_stat": best_split["t_stat"],
                "t_p": best_split["t_p"],
                "n_below": best_split["n_below"],
                "n_above": best_split["n_above"],
            })

# ========================================================================
# STEP 5: 総合サマリー
# ========================================================================
print("\n\n" + "=" * 80)
print("STEP 5: 総合サマリー")
print("=" * 80)

# A. 非線形
print("\n### A. 非線形関係（有意なもの, p<0.05 のみ） ###")
sig_nl = [f for f in nonlinear_findings if f["nonlinear_p"] < 0.05]
print(f"{'ファクター':<20} {'リターン':>10} {'N':>5} {'スプレッド':>10} {'二次係数':>10} {'非線形p':>10} {'パターン':>8}")
print("-" * 85)
for f in sorted(sig_nl, key=lambda x: x["nonlinear_p"]):
    print(f"{f['factor']:<20} {f['return_var']:>10} {f['n_samples']:>5} {f['spread']:>+10.3f} "
          f"{f['quad_coeff']:>10.4f} {f['nonlinear_p']:>10.4f} {f['pattern']:>8}")
print(f"\n有意な非線形関係: {len(sig_nl)} 件 (p<0.05)")

# 全件表示（スプレッドが大きいもの）
print("\n### A'. スプレッドが大きいファクター（|D10-D1| > 0.15, 5年リターン） ###")
big_spread = [f for f in nonlinear_findings if f["return_var"] == "return_5y" and abs(f["spread"]) > 0.15]
print(f"{'ファクター':<20} {'N':>5} {'D10-D1スプレッド':>15} {'単調r':>7} {'単調p':>10} {'パターン':>8}")
print("-" * 75)
for f in sorted(big_spread, key=lambda x: abs(x["spread"]), reverse=True):
    print(f"{f['factor']:<20} {f['n_samples']:>5} {f['spread']:>+15.3f} {f['monotonic_r']:>7.3f} {f['monotonic_p']:>10.2e} {f['pattern']:>8}")

# B. 交互作用
print("\n### B. 交互作用効果 ###")
print(f"{'組み合わせ':<25} {'リターン':>10} {'N':>5} {'F1効果':>8} {'F2効果':>8} {'交互作用':>10} {'p値':>8} {'判定':>15} {'HH-LL':>8}")
print("-" * 115)
for f in sorted(interaction_findings, key=lambda x: x["interaction_p"]):
    print(f"{f['name']:<25} {f['return_var']:>10} {f['n_total']:>5} {f['f1_effect']:>+8.3f} {f['f2_effect']:>+8.3f} "
          f"{f['interaction']:>+10.4f} {f['interaction_p']:>8.4f} {f['synergy']:>15} {f['hh_ll_spread']:>+8.3f}")

sig_interactions = [f for f in interaction_findings if f["interaction_p"] < 0.1]
print(f"\n有意な交互作用: {len(sig_interactions)} / {len(interaction_findings)} 件 (p<0.1)")

# C. 閾値
print("\n### C. 閾値効果（有意なもの, p<0.05） ###")
print(f"{'ファクター':<18} {'リターン':>10} {'閾値':>10} {'以下N':>5} {'超N':>5} {'差':>8} {'t値':>7} {'p値':>10}")
print("-" * 85)
for f in sorted(threshold_findings, key=lambda x: x["t_p"]):
    print(f"{f['factor']:<18} {f['return_var']:>10} {f['threshold_formatted']:>10} {f['n_below']:>5} {f['n_above']:>5} "
          f"{f['diff']:>+8.3f} {f['t_stat']:>7.2f} {f['t_p']:>10.4f}")
print(f"\n有意な閾値効果: {len(threshold_findings)} 件 (p<0.05)")

# ========================================================================
# KEY FINDINGS
# ========================================================================
print("\n\n" + "=" * 80)
print("KEY FINDINGS（最重要発見）")
print("=" * 80)

for rv_label, rv in [("1年", "return_1y"), ("3年", "return_3y"), ("5年", "return_5y")]:
    print(f"\n--- {rv_label}リターン ---")

    # 非線形 Top3
    nl_rv = [f for f in nonlinear_findings if f["return_var"] == rv and f["nonlinear_p"] < 0.1]
    if nl_rv:
        print(f"  [非線形 Top3]")
        for i, f in enumerate(sorted(nl_rv, key=lambda x: x["nonlinear_p"])[:3]):
            print(f"    {i+1}. {f['factor']} ({f['pattern']}, 二次係数={f['quad_coeff']:.4f}, p={f['nonlinear_p']:.4f}, N={f['n_samples']})")

    # スプレッド Top3
    spread_rv = [f for f in nonlinear_findings if f["return_var"] == rv]
    if spread_rv:
        print(f"  [スプレッド Top3 (D10-D1)]")
        for i, f in enumerate(sorted(spread_rv, key=lambda x: abs(x["spread"]), reverse=True)[:3]):
            print(f"    {i+1}. {f['factor']} (spread={f['spread']:+.3f}, 単調r={f['monotonic_r']:.3f}, N={f['n_samples']})")

    # 交互作用
    int_rv = [f for f in interaction_findings if f["return_var"] == rv and f["interaction_p"] < 0.15]
    if int_rv:
        print(f"  [交互作用]")
        for f in sorted(int_rv, key=lambda x: x["interaction_p"]):
            print(f"    {f['name']} (交互作用={f['interaction']:+.4f}, p={f['interaction_p']:.4f}, {f['synergy']}, HH-LL={f['hh_ll_spread']:+.3f})")

    # 閾値
    th_rv = [f for f in threshold_findings if f["return_var"] == rv]
    if th_rv:
        print(f"  [閾値効果 Top3]")
        for i, f in enumerate(sorted(th_rv, key=lambda x: x["t_p"])[:3]):
            print(f"    {i+1}. {f['factor']} 閾値={f['threshold_formatted']} (差={f['diff']:+.3f}, t={f['t_stat']:.2f}, p={f['t_p']:.4f})")

print("\n分析完了。")
