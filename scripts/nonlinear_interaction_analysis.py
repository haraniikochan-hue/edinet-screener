#!/usr/bin/env python3
"""非線形関係・交互作用効果・閾値効果の分析スクリプト"""

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

# ticker -> sec_code 結合のために stock_prices から ticker, edinet_code を取得
# stock_prices に edinet_code と ticker がある
sp_key = stock_prices[["edinet_code", "ticker"]].drop_duplicates()

# historical_returns に edinet_code を付与
returns = historical_returns.merge(sp_key, on="ticker", how="inner")
print(f"historical_returns: {len(historical_returns)} rows -> merged: {len(returns)} rows")

# ratios_all の最新年度を取得
ratios_latest = ratios_all.sort_values("fiscal_year").groupby("edinet_code").last().reset_index()
print(f"ratios_all latest year: {len(ratios_latest)} rows")

# financials_all の最新年度を取得
fin_latest = financials_all.sort_values("fiscal_year").groupby("edinet_code").last().reset_index()
print(f"financials_all latest year: {len(fin_latest)} rows")

# stock_prices からマーケットデータ
sp_cols = ["edinet_code", "ticker", "currentPrice", "marketCap", "priceToBook",
           "dividendYield", "trailingPE", "forwardPE", "bookValue", "totalRevenue",
           "returnOnEquity", "debtToEquity", "freeCashflow", "beta",
           "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "fiftyDayAverage", "twoHundredDayAverage"]
sp_data = stock_prices[sp_cols].drop_duplicates(subset="edinet_code")

# 結合
df = returns.merge(sp_data, on="edinet_code", how="inner")
df = df.merge(ratios_latest[["edinet_code", "roe", "roe_official", "operating_margin",
                              "payout_ratio", "fcf", "eps", "eps_growth",
                              "revenue_growth", "ni_growth", "equity_ratio",
                              "bps", "bps_growth"]], on="edinet_code", how="left")
df = df.merge(fin_latest[["edinet_code", "dividend_per_share"]], on="edinet_code", how="left")

# companies から industry 等
df = df.merge(companies[["edinet_code", "industry"]], on="edinet_code", how="left")

print(f"\n結合後データ: {len(df)} rows, {len(df.columns)} columns")

# --- 派生ファクター計算 ---
# FCF利回り
df["fcf_yield"] = df["freeCashflow"] / df["marketCap"]
df["fcf_yield"] = df["fcf_yield"].replace([np.inf, -np.inf], np.nan)

# ROEの安定性（roe_official は最新年度のみなので roe を使う）
# ratios_all から ROE の時系列標準偏差を計算
roe_ts = ratios_all.groupby("edinet_code")["roe"].agg(["mean", "std", "count"]).reset_index()
roe_ts.columns = ["edinet_code", "roe_mean", "roe_std", "roe_count"]
df = df.merge(roe_ts, on="edinet_code", how="left")

# 配当連続年数・増配年数の計算
def calc_dividend_streaks(fin_df):
    """配当連続年数と増配年数を計算"""
    results = []
    for code, grp in fin_df.groupby("edinet_code"):
        grp = grp.sort_values("fiscal_year")
        divs = grp["dividend_per_share"].dropna()
        if len(divs) == 0:
            results.append({"edinet_code": code, "consecutive_div_years": 0, "div_increase_years": 0})
            continue
        # 配当連続年数（直近から逆順に0でない年を数える）
        consec = 0
        for v in reversed(divs.values):
            if v > 0:
                consec += 1
            else:
                break
        # 増配年数（直近から逆順に前年比増を数える）
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

print(f"派生ファクター追加後: {len(df)} rows, {len(df.columns)} columns")
print(f"カラム一覧: {sorted(df.columns.tolist())}")

# --- 外れ値クリッピング (1%/99%) ---
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
for col in numeric_cols:
    if col in ["return_1y", "return_3y", "return_5y"]:
        continue  # リターンはクリッピングしない（従属変数）
    lower = df[col].quantile(0.01)
    upper = df[col].quantile(0.99)
    df[col] = df[col].clip(lower, upper)

# ========================================================================
# STEP 2: 十分位分析（非線形関係の検証）
# ========================================================================
print("\n" + "=" * 80)
print("STEP 2: 十分位（デシル）分析 — 非線形関係の検証")
print("=" * 80)

RETURN_VARS = ["return_1y", "return_3y", "return_5y"]
FACTORS = {
    "marketCap": "時価総額",
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
    """十分位分析: ファクターで10分位に分けてリターンの平均を計算"""
    subset = df[[factor, return_var]].dropna()
    if len(subset) < 50:
        return None
    try:
        subset["decile"] = pd.qcut(subset[factor], n_quantiles, labels=False, duplicates="drop")
    except ValueError:
        return None

    result = subset.groupby("decile").agg(
        mean_return=(return_var, "mean"),
        median_return=(return_var, "median"),
        count=(return_var, "count"),
        factor_mean=(factor, "mean"),
        factor_median=(factor, "median"),
    ).reset_index()

    # 単調性テスト（Spearman相関）
    sp_r, sp_p = stats.spearmanr(result["decile"], result["mean_return"])

    # 非線形性テスト: 二次項の有意性
    x = subset[factor].values
    y = subset[return_var].values
    x_norm = (x - x.mean()) / (x.std() + 1e-10)
    try:
        # 線形 vs 二次モデル
        coeffs_lin = np.polyfit(x_norm, y, 1)
        residuals_lin = y - np.polyval(coeffs_lin, x_norm)
        ss_res_lin = np.sum(residuals_lin ** 2)

        coeffs_quad = np.polyfit(x_norm, y, 2)
        residuals_quad = y - np.polyval(coeffs_quad, x_norm)
        ss_res_quad = np.sum(residuals_quad ** 2)

        n = len(y)
        # F-test for nested models
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
        "d1_return": result.iloc[0]["mean_return"] if len(result) > 0 else np.nan,
        "d10_return": result.iloc[-1]["mean_return"] if len(result) > 0 else np.nan,
        "spread_d10_d1": (result.iloc[-1]["mean_return"] - result.iloc[0]["mean_return"]) if len(result) > 1 else np.nan,
    }

print("\n### 十分位分析の結果サマリー ###\n")
nonlinear_findings = []

for return_var in RETURN_VARS:
    print(f"\n--- リターン変数: {return_var} ---")
    print(f"{'ファクター':<25} {'N':>5} {'D1平均':>8} {'D10平均':>8} {'D10-D1':>8} {'単調r':>7} {'単調p':>10} {'二次係数':>8} {'非線形F':>8} {'非線形p':>10}")
    print("-" * 130)

    for factor, factor_name in FACTORS.items():
        result = decile_analysis(df, factor, return_var)
        if result is None:
            continue

        print(f"{factor_name:<25} {result['n_samples']:>5} {result['d1_return']:>8.3f} {result['d10_return']:>8.3f} "
              f"{result['spread_d10_d1']:>8.3f} {result['monotonic_r']:>7.3f} {result['monotonic_p']:>10.2e} "
              f"{result['quad_coeff']:>8.4f} {result['nonlinear_f']:>8.2f} {result['nonlinear_p']:>10.2e}")

        # 非線形性が有意なもの、またはスプレッドが大きいものを記録
        if result['nonlinear_p'] < 0.05 or abs(result['spread_d10_d1']) > 0.1:
            pattern = "U字型" if result['quad_coeff'] > 0 else "逆U字型" if result['quad_coeff'] < 0 else "線形"
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

    # 十分位の詳細表示（主要ファクター）
    key_factors = ["marketCap", "roe_std", "priceToBook", "forwardPE", "consecutive_div_years", "div_increase_years"]
    for factor in key_factors:
        if factor not in FACTORS:
            continue
        result = decile_analysis(df, factor, return_var)
        if result is None:
            continue
        print(f"\n  [{FACTORS[factor]}] 十分位別 {return_var} 詳細:")
        for _, row in result["decile_data"].iterrows():
            bar = "█" * int(abs(row["mean_return"]) * 20)
            sign = "+" if row["mean_return"] >= 0 else "-"
            print(f"    D{int(row['decile'])+1:>2}: mean={row['mean_return']:>7.3f} | median={row['median_return']:>7.3f} | "
                  f"n={int(row['count']):>4} | factor_avg={row['factor_mean']:>12.2f} | {sign}{bar}")

# ========================================================================
# STEP 3: 交互作用効果の検証
# ========================================================================
print("\n\n" + "=" * 80)
print("STEP 3: 交互作用効果の検証（2x2マトリクス）")
print("=" * 80)

INTERACTIONS = [
    ("roe_std", "marketCap", "ROEσ × 時価総額", True, False),  # (factor1, factor2, name, invert1, invert2)
    ("consecutive_div_years", "priceToBook", "配当連続年数 × PBR", False, True),
    ("fcf_yield", "div_increase_years", "FCF利回り × 増配年数", False, False),
    ("forwardPE", "operating_margin", "フォワードPE × 営業利益率", True, False),
    ("roe_std", "div_increase_years", "ROEσ × 増配年数", True, False),
]

def interaction_analysis(df, factor1, factor2, return_var, invert1=False, invert2=False):
    """
    2x2マトリクスで交互作用を検証。
    invert=True の場合、中央値以下を「High」（低い方が良い）として扱う。
    """
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

    # 交互作用の計算
    # Low-Low をベースライン
    base = groups[("Low", "Low")]["mean"]
    f1_only = groups[("High", "Low")]["mean"] - base  # factor1 のみの効果
    f2_only = groups[("Low", "High")]["mean"] - base  # factor2 のみの効果
    combined = groups[("High", "High")]["mean"] - base  # 両方の効果
    interaction = combined - (f1_only + f2_only)  # 交互作用 = 実際 - 加法的予測

    # ANOVA (2-way)
    try:
        from itertools import product
        data_for_anova = []
        for g1, g2 in product(["Low", "High"], repeat=2):
            mask = (subset["g1"] == g1) & (subset["g2"] == g2)
            vals = subset.loc[mask, return_var].values
            for v in vals:
                data_for_anova.append({"g1": g1, "g2": g2, "ret": v})
        anova_df = pd.DataFrame(data_for_anova)

        # Simple interaction F-test
        anova_df["g1_num"] = (anova_df["g1"] == "High").astype(int)
        anova_df["g2_num"] = (anova_df["g2"] == "High").astype(int)
        anova_df["interact"] = anova_df["g1_num"] * anova_df["g2_num"]

        from numpy.linalg import lstsq
        X = anova_df[["g1_num", "g2_num", "interact"]].values
        X = np.column_stack([np.ones(len(X)), X])
        y = anova_df["ret"].values

        # Full model
        beta_full, res_full, _, _ = lstsq(X, y, rcond=None)
        ss_res_full = np.sum((y - X @ beta_full) ** 2)

        # Reduced model (no interaction)
        X_red = X[:, :3]
        beta_red, res_red, _, _ = lstsq(X_red, y, rcond=None)
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
    print(f"\n### {name} ###")
    for return_var in RETURN_VARS:
        result = interaction_analysis(df, factor1, factor2, return_var, inv1, inv2)
        if result is None:
            print(f"  {return_var}: データ不足でスキップ")
            continue

        g = result["groups"]
        inv1_label = f"{'低' if inv1 else '高'}{FACTORS.get(factor1, factor1)}"
        inv2_label = f"{'低' if inv2 else '高'}{FACTORS.get(factor2, factor2)}"

        print(f"\n  [{return_var}] N={result['n_total']}")
        print(f"  {'':>20} | {'Low '+FACTORS.get(factor2,factor2):>20} | {'High '+FACTORS.get(factor2,factor2):>20}")
        print(f"  {'-'*65}")
        print(f"  {'Low '+FACTORS.get(factor1,factor1):>20} | mean={g[('Low','Low')]['mean']:>7.3f} n={g[('Low','Low')]['count']:>4} | mean={g[('Low','High')]['mean']:>7.3f} n={g[('Low','High')]['count']:>4}")
        print(f"  {'High '+FACTORS.get(factor1,factor1):>20} | mean={g[('High','Low')]['mean']:>7.3f} n={g[('High','Low')]['count']:>4} | mean={g[('High','High')]['mean']:>7.3f} n={g[('High','High')]['count']:>4}")
        print(f"  効果分解: F1のみ={result['f1_only_effect']:>+.3f}, F2のみ={result['f2_only_effect']:>+.3f}, "
              f"合計(加法)={result['f1_only_effect']+result['f2_only_effect']:>+.3f}, 実際={result['combined_effect']:>+.3f}")
        print(f"  交互作用効果={result['interaction_effect']:>+.4f} | F統計量={result['interaction_f']:.2f} | p値={result['interaction_p']:.4f}")

        synergy = "相乗効果あり" if result['interaction_effect'] > 0 and result['interaction_p'] < 0.1 else \
                  "相殺効果" if result['interaction_effect'] < 0 and result['interaction_p'] < 0.1 else \
                  "有意な交互作用なし"
        print(f"  判定: {synergy}")

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
        })

# ========================================================================
# STEP 4: 閾値効果の検証
# ========================================================================
print("\n\n" + "=" * 80)
print("STEP 4: 閾値効果の検証")
print("=" * 80)

def threshold_analysis(df, factor, return_var, thresholds):
    """各閾値でファクターを2群に分け、リターン差のt検定を行う"""
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
    },
    "marketCap": {
        "name": "時価総額",
        "thresholds": [1e10, 5e10, 1e11, 3e11, 5e11, 1e12, 5e12],  # 100億 ~ 5兆
        "format": lambda x: f"{x/1e12:.1f}兆" if x >= 1e12 else f"{x/1e10:.0f}00億",
    },
    "consecutive_div_years": {
        "name": "配当連続年数",
        "thresholds": [0, 1, 2, 3, 4, 5],
    },
    "div_increase_years": {
        "name": "増配年数",
        "thresholds": [0, 1, 2, 3, 4],
    },
    "roe_std": {
        "name": "ROEσ",
        "thresholds": [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15],
    },
    "forwardPE": {
        "name": "フォワードPE",
        "thresholds": [5, 8, 10, 12, 15, 20, 30, 50],
    },
    "dividendYield": {
        "name": "配当利回り",
        "thresholds": [1.0, 2.0, 3.0, 4.0, 5.0],
    },
    "operating_margin": {
        "name": "営業利益率",
        "thresholds": [0.0, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20],
    },
    "fcf_yield": {
        "name": "FCF利回り",
        "thresholds": [-0.02, 0.0, 0.02, 0.05, 0.08, 0.10],
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

        best_split = max(results, key=lambda x: abs(x["diff"]))

        for r in results:
            sig = "***" if r["t_p"] < 0.001 else "**" if r["t_p"] < 0.01 else "*" if r["t_p"] < 0.05 else ""
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

print("\n### A. 非線形関係（有意なもの） ###")
print(f"{'ファクター':<25} {'リターン':>10} {'N':>5} {'スプレッド':>10} {'二次係数':>8} {'非線形p':>10} {'パターン':>10}")
print("-" * 90)
for f in sorted(nonlinear_findings, key=lambda x: x["nonlinear_p"]):
    print(f"{f['factor']:<25} {f['return_var']:>10} {f['n_samples']:>5} {f['spread']:>+10.3f} "
          f"{f['quad_coeff']:>8.4f} {f['nonlinear_p']:>10.4f} {f['pattern']:>10}")

print(f"\n合計: {len(nonlinear_findings)} 件の有意な非線形関係を検出")

print("\n### B. 交互作用効果 ###")
print(f"{'組み合わせ':<30} {'リターン':>10} {'N':>5} {'F1効果':>8} {'F2効果':>8} {'交互作用':>10} {'p値':>10} {'判定':>15}")
print("-" * 110)
for f in sorted(interaction_findings, key=lambda x: x["interaction_p"]):
    print(f"{f['name']:<30} {f['return_var']:>10} {f['n_total']:>5} {f['f1_effect']:>+8.3f} {f['f2_effect']:>+8.3f} "
          f"{f['interaction']:>+10.4f} {f['interaction_p']:>10.4f} {f['synergy']:>15}")

sig_interactions = [f for f in interaction_findings if f["interaction_p"] < 0.1]
print(f"\n合計: {len(sig_interactions)} / {len(interaction_findings)} 件の有意な（p<0.1）交互作用を検出")

print("\n### C. 閾値効果（有意なもの） ###")
print(f"{'ファクター':<20} {'リターン':>10} {'閾値':>12} {'以下N':>5} {'超N':>5} {'リターン差':>10} {'p値':>10}")
print("-" * 85)
for f in sorted(threshold_findings, key=lambda x: x["t_p"]):
    print(f"{f['factor']:<20} {f['return_var']:>10} {f['threshold_formatted']:>12} {f['n_below']:>5} {f['n_above']:>5} "
          f"{f['diff']:>+10.3f} {f['t_p']:>10.4f}")

print(f"\n合計: {len(threshold_findings)} 件の有意な閾値効果を検出")

# 最も重要な発見
print("\n\n" + "=" * 80)
print("KEY FINDINGS（最重要発見）")
print("=" * 80)

# 非線形: return_5y で非線形pが最も有意なもの
nl_5y = [f for f in nonlinear_findings if f["return_var"] == "return_5y"]
if nl_5y:
    nl_5y_sorted = sorted(nl_5y, key=lambda x: x["nonlinear_p"])
    print("\n[非線形] 5年リターンに対して最も非線形なファクター TOP5:")
    for i, f in enumerate(nl_5y_sorted[:5]):
        print(f"  {i+1}. {f['factor']} (二次係数={f['quad_coeff']:.4f}, p={f['nonlinear_p']:.4f}, パターン={f['pattern']})")

# 交互作用: return_5y で最も有意なもの
int_5y = [f for f in interaction_findings if f["return_var"] == "return_5y"]
if int_5y:
    int_5y_sorted = sorted(int_5y, key=lambda x: x["interaction_p"])
    print("\n[交互作用] 5年リターンに対して最も有意な交互作用 TOP3:")
    for i, f in enumerate(int_5y_sorted[:3]):
        print(f"  {i+1}. {f['name']} (交互作用={f['interaction']:+.4f}, p={f['interaction_p']:.4f}, {f['synergy']})")

# 閾値: return_5y で最も有意なもの
th_5y = [f for f in threshold_findings if f["return_var"] == "return_5y"]
if th_5y:
    th_5y_sorted = sorted(th_5y, key=lambda x: x["t_p"])
    print("\n[閾値] 5年リターンに対して最も有意な閾値 TOP5:")
    for i, f in enumerate(th_5y_sorted[:5]):
        print(f"  {i+1}. {f['factor']} 閾値={f['threshold_formatted']} (差={f['diff']:+.3f}, p={f['t_p']:.4f})")

print("\n分析完了。")
