"""
全財務指標 vs 株価リターンの相関分析。
どの財務指標が実際の株価パフォーマンスと相関するかを特定する。
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.data_loader import build_company_profiles


def compute_return_proxies(df: pd.DataFrame) -> pd.DataFrame:
    """既存データからリターン代理変数を計算"""
    df = df.copy()

    price = pd.to_numeric(df["currentPrice"], errors="coerce")
    ma200 = pd.to_numeric(df["twoHundredDayAverage"], errors="coerce")
    ma50 = pd.to_numeric(df["fiftyDayAverage"], errors="coerce")
    high52 = pd.to_numeric(df["fiftyTwoWeekHigh"], errors="coerce")
    low52 = pd.to_numeric(df["fiftyTwoWeekLow"], errors="coerce")

    # リターン代理変数
    df["ret_vs_200ma"] = (price / ma200) - 1  # ~10ヶ月リターン代理
    df["ret_vs_52low"] = (price / low52) - 1  # 52週安値からの上昇率
    df["ret_52range_pos"] = (price - low52) / (high52 - low52)  # 52週レンジ内の位置
    df["momentum_50_200"] = (ma50 / ma200) - 1  # 短期vs長期モメンタム

    # 実リターンデータがあれば追加
    returns_path = ROOT / "data" / "historical_returns.csv"
    if returns_path.exists():
        rets = pd.read_csv(returns_path)
        df = df.merge(rets, on="ticker", how="left")
        print(f"Historical returns loaded: {rets['return_1y'].notna().sum()} tickers with 1y data")

    return df


def run_correlation_analysis(df: pd.DataFrame) -> None:
    """全財務指標とリターンの相関分析"""

    # リターン変数（ターゲット）
    return_cols = ["ret_vs_200ma", "ret_vs_52low", "momentum_50_200"]
    if "return_1y" in df.columns:
        return_cols = ["return_1y", "return_3y", "return_5y"] + return_cols

    # 財務指標（特徴量）— 使えそうなもの全て
    feature_cols = [
        # ROE関連
        "roe_mean", "roe_min", "roe_std", "roe_above_10_count", "roe_above_15_count",
        # 営業利益率
        "om_mean", "om_cv",
        # 成長
        "eps_increase_years", "bps_increase_years",
        "eps_cagr_5y", "revenue_cagr_5y",
        # 財務健全性
        "equity_ratio", "equity_ratio_improving",
        "accrual_ratio",
        # FCF
        "fcf_positive_years", "fcf_growing",
        # 配当
        "dps_positive_years", "dps_increase_years",
        # バリュエーション
        "trailingPE", "forwardPE", "priceToBook", "dividendYield",
        # 市場データ
        "marketCap", "beta",
        "debtToEquity", "returnOnEquity",
        "freeCashflow",
        # 利益関連
        "has_loss",
        "n_years",
    ]

    # 存在するカラムだけ
    available_features = [c for c in feature_cols if c in df.columns]
    available_returns = [c for c in return_cols if c in df.columns]

    print(f"\n{'='*70}")
    print(f"相関分析: {len(available_features)}個の財務指標 × {len(available_returns)}個のリターン変数")
    print(f"{'='*70}")

    # メインのリターン変数を選択
    primary_return = "return_1y" if "return_1y" in df.columns else "ret_vs_200ma"
    print(f"\nプライマリリターン変数: {primary_return}")

    results = []

    for feat in available_features:
        feat_data = pd.to_numeric(df[feat], errors="coerce")
        for ret_col in available_returns:
            ret_data = pd.to_numeric(df[ret_col], errors="coerce")

            # 外れ値除去（1%/99%クリッピング）
            feat_data = feat_data.astype(float)
            mask = feat_data.notna() & ret_data.notna()
            if mask.sum() < 50:
                continue

            x = feat_data[mask].astype(float)
            y = ret_data[mask].astype(float)

            # 外れ値クリッピング
            x_clip = x.clip(float(x.quantile(0.01)), float(x.quantile(0.99)))
            y_clip = y.clip(float(y.quantile(0.01)), float(y.quantile(0.99)))

            # ピアソン相関
            corr, pval = stats.pearsonr(x_clip, y_clip)

            # スピアマン順位相関（非線形関係も捉える）
            scorr, spval = stats.spearmanr(x_clip, y_clip)

            # 五分位分析（最もパフォーマンスが良い/悪いグループの差）
            quintiles = pd.qcut(x, 5, labels=False, duplicates="drop")
            if quintiles.nunique() >= 5:
                q1_ret = y[quintiles == 0].median()
                q5_ret = y[quintiles == 4].median()
                q_spread = q5_ret - q1_ret
            else:
                q_spread = None

            results.append({
                "feature": feat,
                "return_var": ret_col,
                "pearson_r": corr,
                "pearson_p": pval,
                "spearman_r": scorr,
                "spearman_p": spval,
                "quintile_spread": q_spread,
                "n_samples": mask.sum(),
            })

    results_df = pd.DataFrame(results)

    # プライマリリターンでの結果を表示
    primary_results = results_df[results_df["return_var"] == primary_return].copy()
    primary_results["abs_spearman"] = primary_results["spearman_r"].abs()
    primary_results = primary_results.sort_values("abs_spearman", ascending=False)

    print(f"\n{'='*70}")
    print(f"■ {primary_return} との相関ランキング（スピアマン順位相関）")
    print(f"{'='*70}")
    print(f"{'指標':<30} {'Spearman':>10} {'Pearson':>10} {'p値':>10} {'Q5-Q1':>10} {'N':>6}")
    print("-" * 80)

    for _, row in primary_results.head(30).iterrows():
        q_str = f"{row['quintile_spread']:.3f}" if pd.notna(row.get("quintile_spread")) else "N/A"
        sig = "***" if row["spearman_p"] < 0.001 else "**" if row["spearman_p"] < 0.01 else "*" if row["spearman_p"] < 0.05 else ""
        print(f"{row['feature']:<30} {row['spearman_r']:>+.4f}{sig:<3} {row['pearson_r']:>+.4f} {row['spearman_p']:>10.2e} {q_str:>10} {row['n_samples']:>6.0f}")

    # 各リターン変数での上位5指標
    print(f"\n{'='*70}")
    print("■ 各リターン変数での上位5指標")
    print(f"{'='*70}")

    for ret_col in available_returns:
        subset = results_df[results_df["return_var"] == ret_col].copy()
        subset["abs_spearman"] = subset["spearman_r"].abs()
        subset = subset.sort_values("abs_spearman", ascending=False)
        print(f"\n--- {ret_col} ---")
        for _, row in subset.head(5).iterrows():
            direction = "+" if row["spearman_r"] > 0 else "-"
            print(f"  {direction} {row['feature']:<28} r={row['spearman_r']:+.4f}  (N={row['n_samples']:.0f})")

    # 五分位分析の詳細（上位指標）
    print(f"\n{'='*70}")
    print(f"■ 五分位分析詳細（{primary_return}）")
    print(f"{'='*70}")

    top_features = primary_results.head(10)["feature"].tolist()
    ret_data = pd.to_numeric(df[primary_return], errors="coerce")

    for feat in top_features:
        feat_data = pd.to_numeric(df[feat], errors="coerce")
        mask = feat_data.notna() & ret_data.notna()
        if mask.sum() < 100:
            continue

        x = feat_data[mask]
        y = ret_data[mask]

        try:
            quintiles = pd.qcut(x, 5, labels=["Q1(低)", "Q2", "Q3", "Q4", "Q5(高)"], duplicates="drop")
            if quintiles.nunique() < 3:
                continue
            q_analysis = y.groupby(quintiles).agg(["median", "mean", "count"])
            print(f"\n--- {feat} ---")
            for q_name, row in q_analysis.iterrows():
                bar_len = int(max(0, min(30, (row["median"] + 0.5) * 30)))
                bar = "█" * bar_len
                print(f"  {q_name:<8} median={row['median']:>+.3f}  mean={row['mean']:>+.3f}  n={row['count']:.0f}  {bar}")
        except Exception:
            pass

    # CSVに保存
    results_df.to_csv(ROOT / "data" / "factor_correlations.csv", index=False)
    print(f"\n結果をdata/factor_correlations.csvに保存しました")


def main():
    print("Loading data...")
    profiles = build_company_profiles()
    print(f"Companies: {len(profiles)}")

    profiles = compute_return_proxies(profiles)

    # 基本統計
    for col in ["ret_vs_200ma", "ret_vs_52low", "return_1y"]:
        if col in profiles.columns:
            data = pd.to_numeric(profiles[col], errors="coerce").dropna()
            print(f"\n{col}: N={len(data)}, median={data.median():.3f}, mean={data.mean():.3f}, std={data.std():.3f}")

    run_correlation_analysis(profiles)


if __name__ == "__main__":
    main()
