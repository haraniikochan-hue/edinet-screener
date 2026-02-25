"""
時系列 Out-of-Sample バックテスト
T年度末の特徴量 → T+1年度のリターン（BPS成長率プロキシ）

目的: クロスセクショナル分析で見つかった相関が、真の予測力を持つか検証する。
手法:
  - Plan A: BPS成長率 + 配当利回りを疑似リターンプロキシとして使用（全社、即時）
  - ローリングIC, プーリングIC/ICIR, 五分位L/Sスプレッドを年度別に報告
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.data_loader import load_financials, load_ratios

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
WINSORIZE_PCTL = (0.01, 0.99)
# 特徴量を計算するために最低限必要な過去データ年数（roa_std等で3年必要）
MIN_HISTORY_YEARS = 3
# ローリング検証対象の formation year（T年度の特徴量 → T+1年度リターン）
# fiscal_year 2020は663件しかないので、2021起点で特徴量を組み、2022以降をOOS
FORMATION_YEARS = [2021, 2022, 2023, 2024]  # T+1=2022,2023,2024,2025


def winsorize(s: pd.Series, pctl: tuple = WINSORIZE_PCTL) -> pd.Series:
    lo, hi = s.quantile(pctl[0]), s.quantile(pctl[1])
    return s.clip(lo, hi)


# ---------------------------------------------------------------------------
# Step 1: リターンプロキシ（BPS成長率 + 配当利回り）
# ---------------------------------------------------------------------------
def compute_return_proxies(fin: pd.DataFrame) -> pd.DataFrame:
    """
    各 (edinet_code, fiscal_year=T+1) について:
      bps_return = (BPS[T+1] - BPS[T]) / BPS[T]
      div_yield  = dividend_per_share[T+1] / BPS[T]  (簿価配当利回り)
      total_return_proxy = bps_return + div_yield
    """
    fin = fin.sort_values(["edinet_code", "fiscal_year"]).copy()
    fin["bps_num"] = pd.to_numeric(fin["bps"], errors="coerce")
    fin["dps_num"] = pd.to_numeric(fin["dividend_per_share"], errors="coerce")

    records = []
    for code, grp in fin.groupby("edinet_code"):
        grp = grp.sort_values("fiscal_year").reset_index(drop=True)
        for i in range(1, len(grp)):
            bps_prev = grp.loc[i - 1, "bps_num"]
            bps_curr = grp.loc[i, "bps_num"]
            dps_curr = grp.loc[i, "dps_num"]
            fy_curr = grp.loc[i, "fiscal_year"]
            fy_prev = grp.loc[i - 1, "fiscal_year"]

            # 連続年度のみ（gap がある場合はスキップ）
            if fy_curr - fy_prev != 1:
                continue
            if pd.isna(bps_prev) or pd.isna(bps_curr) or bps_prev <= 0:
                continue

            bps_ret = (bps_curr - bps_prev) / bps_prev
            div_yield = (dps_curr / bps_prev) if pd.notna(dps_curr) else 0.0
            total_ret = bps_ret + div_yield

            records.append({
                "edinet_code": code,
                "return_year": int(fy_curr),  # リターンが実現する年度
                "formation_year": int(fy_prev),  # 特徴量を計算する年度
                "bps_return": bps_ret,
                "div_yield_proxy": div_yield,
                "total_return_proxy": total_ret,
            })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Step 2: 特徴量の計算（各formation_year Tについて、T年度までの累積データで計算）
# ---------------------------------------------------------------------------
def compute_features_at_year(fin: pd.DataFrame, ratios: pd.DataFrame,
                             formation_year: int) -> pd.DataFrame:
    """
    formation_year=T 時点で観測可能な特徴量のみを使って特徴量を計算。
    look-ahead bias を厳密に回避。
    """
    # T年度以前のデータのみ使用
    fin_up_to_t = fin[fin["fiscal_year"] <= formation_year].copy()
    rat_up_to_t = ratios[ratios["fiscal_year"] <= formation_year].copy()

    # T年度のスナップショット
    fin_t = fin[fin["fiscal_year"] == formation_year].copy()
    rat_t = ratios[ratios["fiscal_year"] == formation_year].copy()

    records = []
    for code in rat_t["edinet_code"].unique():
        row = {}
        row["edinet_code"] = code
        row["formation_year"] = formation_year

        # --- T年度のスナップショット指標 ---
        rt = rat_t[rat_t["edinet_code"] == code]
        ft = fin_t[fin_t["edinet_code"] == code]
        if len(rt) == 0 or len(ft) == 0:
            continue
        rt = rt.iloc[0]
        ft = ft.iloc[0]

        row["roe"] = pd.to_numeric(rt.get("roe"), errors="coerce")
        row["roa"] = pd.to_numeric(rt.get("roa"), errors="coerce")
        row["operating_margin"] = pd.to_numeric(rt.get("operating_margin"), errors="coerce")
        row["net_margin"] = pd.to_numeric(rt.get("net_margin"), errors="coerce")
        row["equity_ratio"] = pd.to_numeric(rt.get("equity_ratio"), errors="coerce")
        row["payout_ratio"] = pd.to_numeric(rt.get("payout_ratio"), errors="coerce")

        bps_val = pd.to_numeric(ft.get("bps"), errors="coerce")
        ta_val = pd.to_numeric(ft.get("total_assets"), errors="coerce")
        na_val = pd.to_numeric(ft.get("net_assets"), errors="coerce")
        eps_val = pd.to_numeric(rt.get("eps"), errors="coerce")
        dps_val = pd.to_numeric(ft.get("dividend_per_share"), errors="coerce")

        # debtToEquity
        if pd.notna(ta_val) and pd.notna(na_val) and na_val > 0:
            row["debt_to_equity"] = (ta_val - na_val) / na_val
        else:
            row["debt_to_equity"] = np.nan

        # --- 時系列指標（T年度まで） ---
        rh = rat_up_to_t[rat_up_to_t["edinet_code"] == code].sort_values("fiscal_year")
        fh = fin_up_to_t[fin_up_to_t["edinet_code"] == code].sort_values("fiscal_year")
        n_years = len(rh)

        # ROE std / ROA std（3年以上で計算）
        roe_vals = pd.to_numeric(rh["roe"], errors="coerce").dropna()
        roa_vals = pd.to_numeric(rh["roa"], errors="coerce").dropna()
        row["roe_std"] = roe_vals.std() if len(roe_vals) >= 3 else np.nan
        row["roa_std"] = roa_vals.std() if len(roa_vals) >= 3 else np.nan
        row["roe_mean"] = roe_vals.mean() if len(roe_vals) >= 2 else np.nan

        # 配当連続年数
        dps_vals = pd.to_numeric(fh["dividend_per_share"], errors="coerce")
        consec_div = 0
        for v in reversed(dps_vals.values):
            if pd.notna(v) and v > 0:
                consec_div += 1
            else:
                break
        row["consecutive_dividend_years"] = consec_div

        # 連続増配年数
        consec_increase = 0
        dps_clean = dps_vals.dropna().values
        if len(dps_clean) >= 2:
            for j in range(len(dps_clean) - 1, 0, -1):
                if dps_clean[j] > dps_clean[j - 1]:
                    consec_increase += 1
                else:
                    break
        row["consecutive_div_increase_years"] = consec_increase

        # 配当CAGR（3年）
        if len(dps_clean) >= 3 and dps_clean[-3] > 0:
            row["div_cagr_3y"] = (dps_clean[-1] / dps_clean[-3]) ** (1 / 2) - 1
        else:
            row["div_cagr_3y"] = np.nan

        # EPS momentum: EPS[T] / mean(EPS[T-2:T-1])
        eps_vals = pd.to_numeric(rh["eps"], errors="coerce").dropna().values
        if len(eps_vals) >= 3:
            denom = np.mean(eps_vals[-3:-1])
            if denom > 0:
                row["eps_momentum"] = eps_vals[-1] / denom
            else:
                row["eps_momentum"] = np.nan
        else:
            row["eps_momentum"] = np.nan

        # BPS increase years
        bps_vals = pd.to_numeric(fh["bps"], errors="coerce").dropna().values
        bps_inc = 0
        if len(bps_vals) > 1:
            bps_inc = int((np.diff(bps_vals) > 0).sum())
        row["bps_increase_years"] = bps_inc

        # has_loss_year
        ni_vals = pd.to_numeric(fh["net_income"], errors="coerce").dropna()
        row["has_loss"] = int((ni_vals < 0).any()) if len(ni_vals) > 0 else np.nan

        # accrual_ratio (latest year)
        ni = pd.to_numeric(ft.get("net_income"), errors="coerce")
        cfo = pd.to_numeric(ft.get("cf_operating"), errors="coerce")
        ta = pd.to_numeric(ft.get("total_assets"), errors="coerce")
        if pd.notna(ni) and pd.notna(cfo) and pd.notna(ta) and ta > 0:
            row["accrual_ratio"] = (ni - cfo) / ta
        else:
            row["accrual_ratio"] = np.nan

        # FCF positive years
        cfo_vals = pd.to_numeric(fh["cf_operating"], errors="coerce")
        cfi_vals = pd.to_numeric(fh["cf_investing"], errors="coerce")
        fcf_vals = (cfo_vals + cfi_vals).dropna()
        row["fcf_positive_years"] = int((fcf_vals > 0).sum()) if len(fcf_vals) > 0 else 0

        # Operating margin CV
        om_vals = pd.to_numeric(rh["operating_margin"], errors="coerce").dropna()
        if len(om_vals) >= 3 and om_vals.mean() != 0:
            row["om_cv"] = om_vals.std() / abs(om_vals.mean())
        else:
            row["om_cv"] = np.nan

        records.append(row)

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Step 3-5: ローリング相関 + プーリングOOS + L/S検証
# ---------------------------------------------------------------------------
FACTOR_COLS = [
    "roe", "roa", "operating_margin", "net_margin", "equity_ratio",
    "payout_ratio", "debt_to_equity", "roe_std", "roa_std", "roe_mean",
    "consecutive_dividend_years", "consecutive_div_increase_years",
    "div_cagr_3y", "eps_momentum", "bps_increase_years", "has_loss",
    "accrual_ratio", "fcf_positive_years", "om_cv",
]

RETURN_COL = "total_return_proxy"


def compute_rolling_ic(panel: pd.DataFrame) -> pd.DataFrame:
    """年度別のIC（Spearman相関）を計算"""
    results = []
    for fy in sorted(panel["formation_year"].unique()):
        sub = panel[panel["formation_year"] == fy].copy()
        n = len(sub)
        row = {"formation_year": fy, "n_companies": n}

        ret = sub[RETURN_COL]
        for fc in FACTOR_COLS:
            vals = sub[fc]
            mask = vals.notna() & ret.notna()
            if mask.sum() >= 30:
                corr, pval = stats.spearmanr(vals[mask], ret[mask])
                row[f"ic_{fc}"] = corr
                row[f"pval_{fc}"] = pval
            else:
                row[f"ic_{fc}"] = np.nan
                row[f"pval_{fc}"] = np.nan
        results.append(row)

    return pd.DataFrame(results)


def compute_pooled_ic(panel: pd.DataFrame) -> pd.DataFrame:
    """年度ダミーで制御したプーリングICを計算"""
    results = []
    ret = panel[RETURN_COL]

    # 年度平均を引いて年度効果を除去
    panel = panel.copy()
    year_mean = panel.groupby("formation_year")[RETURN_COL].transform("mean")
    ret_demeaned = ret - year_mean

    for fc in FACTOR_COLS:
        vals = panel[fc].copy()
        # 特徴量も年度平均を引く（年度内のクロスセクショナルランキングに注目）
        fc_year_mean = panel.groupby("formation_year")[fc].transform("mean")
        vals_demeaned = vals - fc_year_mean

        mask = vals_demeaned.notna() & ret_demeaned.notna()
        if mask.sum() >= 50:
            corr, pval = stats.spearmanr(vals_demeaned[mask], ret_demeaned[mask])
            results.append({
                "factor": fc,
                "pooled_ic": corr,
                "pooled_pval": pval,
                "n_obs": int(mask.sum()),
            })
        else:
            results.append({
                "factor": fc,
                "pooled_ic": np.nan,
                "pooled_pval": np.nan,
                "n_obs": int(mask.sum()),
            })

    return pd.DataFrame(results)


def compute_icir(rolling_ic: pd.DataFrame) -> pd.DataFrame:
    """IC平均, IC標準偏差, ICIRを計算"""
    results = []
    for fc in FACTOR_COLS:
        col = f"ic_{fc}"
        vals = rolling_ic[col].dropna()
        if len(vals) >= 2:
            ic_mean = vals.mean()
            ic_std = vals.std()
            icir = ic_mean / ic_std if ic_std > 0 else np.nan
        else:
            ic_mean = vals.mean() if len(vals) == 1 else np.nan
            ic_std = np.nan
            icir = np.nan
        results.append({
            "factor": fc,
            "ic_mean": ic_mean,
            "ic_std": ic_std,
            "icir": icir,
            "n_periods": int(len(vals)),
        })
    return pd.DataFrame(results)


def compute_quintile_spread(panel: pd.DataFrame) -> pd.DataFrame:
    """年度別に五分位ポートフォリオを構築し、Q5-Q1スプレッドを報告"""
    results = []
    for fy in sorted(panel["formation_year"].unique()):
        sub = panel[panel["formation_year"] == fy].copy()
        ret = sub[RETURN_COL]

        for fc in FACTOR_COLS:
            vals = sub[fc]
            mask = vals.notna() & ret.notna()
            valid = sub[mask].copy()
            if len(valid) < 50:
                continue

            valid["quintile"] = pd.qcut(valid[fc], 5, labels=False, duplicates="drop")
            if valid["quintile"].nunique() < 5:
                continue

            q_means = valid.groupby("quintile")[RETURN_COL].mean()
            q1_ret = q_means.iloc[0]  # lowest quintile
            q5_ret = q_means.iloc[-1]  # highest quintile
            spread = q5_ret - q1_ret
            monotonicity = stats.spearmanr(
                q_means.index.astype(float), q_means.values
            )[0]

            results.append({
                "formation_year": fy,
                "factor": fc,
                "q1_return": q1_ret,
                "q5_return": q5_ret,
                "q5_q1_spread": spread,
                "monotonicity": monotonicity,
                "n_companies": len(valid),
            })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 80)
    print("Time-Series Out-of-Sample Backtest")
    print("T年度末の特徴量 -> T+1年度のBPS成長率リターンプロキシ")
    print("=" * 80)

    # Load data
    fin = load_financials()
    ratios = load_ratios()
    print(f"\nLoaded: financials={len(fin)} rows, ratios={len(ratios)} rows")
    print(f"Fiscal years: {sorted(fin.fiscal_year.unique())}")

    # Step 1: Return proxies
    print("\n--- Step 1: Computing return proxies (BPS growth + dividend yield) ---")
    returns_df = compute_return_proxies(fin)
    print(f"Return proxies computed: {len(returns_df)} company-year pairs")
    print(f"Return years: {sorted(returns_df.return_year.unique())}")
    print(f"\nReturn proxy stats by year:")
    print(returns_df.groupby("return_year")["total_return_proxy"].describe()
          .round(4).to_string())

    # Step 2: Features at each formation year
    print("\n--- Step 2: Computing features at each formation year ---")
    panels = []
    for fy in FORMATION_YEARS:
        features = compute_features_at_year(fin, ratios, fy)
        # Merge with returns (return_year = fy+1)
        ret_sub = returns_df[returns_df["formation_year"] == fy][
            ["edinet_code", RETURN_COL, "bps_return", "div_yield_proxy"]
        ]
        merged = features.merge(ret_sub, on="edinet_code", how="inner")
        print(f"  Formation year {fy}: {len(features)} features, "
              f"{len(merged)} with returns (T+1={fy+1})")
        panels.append(merged)

    panel = pd.concat(panels, ignore_index=True)
    print(f"\nTotal panel: {len(panel)} observations, "
          f"{panel.edinet_code.nunique()} unique companies")

    # Winsorize
    print("\n--- Winsorizing factors and returns at 1%/99% ---")
    for col in FACTOR_COLS + [RETURN_COL, "bps_return", "div_yield_proxy"]:
        if col in panel.columns:
            valid = panel[col].notna()
            if valid.sum() > 10:
                panel.loc[valid, col] = winsorize(panel.loc[valid, col])

    # Step 3: Rolling IC
    print("\n" + "=" * 80)
    print("Step 3: Rolling IC (Spearman correlation) by formation year")
    print("=" * 80)
    rolling_ic = compute_rolling_ic(panel)

    # Display rolling IC table
    ic_cols = [c for c in rolling_ic.columns if c.startswith("ic_")]
    display_ic = rolling_ic[["formation_year", "n_companies"] + ic_cols].copy()
    display_ic.columns = [c.replace("ic_", "") if c.startswith("ic_") else c
                          for c in display_ic.columns]
    print("\n年度別IC（Spearman相関）:")
    print(display_ic.round(4).to_string(index=False))

    # Significance markers
    print("\n年度別IC p<0.05 のファクター:")
    for _, row in rolling_ic.iterrows():
        fy = int(row["formation_year"])
        sig_factors = []
        for fc in FACTOR_COLS:
            pval = row.get(f"pval_{fc}")
            ic = row.get(f"ic_{fc}")
            if pd.notna(pval) and pval < 0.05:
                sig_factors.append(f"{fc}({ic:+.3f})")
        if sig_factors:
            print(f"  FY{fy}: {', '.join(sig_factors)}")

    # Step 4: Pooled IC and ICIR
    print("\n" + "=" * 80)
    print("Step 4: Pooled IC and ICIR")
    print("=" * 80)

    pooled_ic = compute_pooled_ic(panel)
    icir_df = compute_icir(rolling_ic)

    summary = icir_df.merge(pooled_ic, on="factor", how="outer")
    summary = summary.sort_values("ic_mean", key=abs, ascending=False)

    print("\nファクター | IC平均 | IC_std | ICIR | Pooled_IC | Pooled_pval | N_obs")
    print("-" * 90)
    for _, r in summary.iterrows():
        ic_mean = f"{r['ic_mean']:+.4f}" if pd.notna(r["ic_mean"]) else "   N/A"
        ic_std = f"{r['ic_std']:.4f}" if pd.notna(r["ic_std"]) else "  N/A"
        icir = f"{r['icir']:+.3f}" if pd.notna(r["icir"]) else "  N/A"
        pic = f"{r['pooled_ic']:+.4f}" if pd.notna(r["pooled_ic"]) else "   N/A"
        ppval = f"{r['pooled_pval']:.4f}" if pd.notna(r["pooled_pval"]) else "  N/A"
        nobs = f"{r['n_obs']:.0f}" if pd.notna(r.get("n_obs")) else "  N/A"
        print(f"  {r['factor']:<35s} {ic_mean}  {ic_std}  {icir}  {pic}  {ppval}  {nobs}")

    # Step 5: Quintile spread
    print("\n" + "=" * 80)
    print("Step 5: Quintile Long/Short Spread (Q5-Q1)")
    print("=" * 80)

    qs_df = compute_quintile_spread(panel)
    if len(qs_df) > 0:
        # Pivot: factor x formation_year
        spread_pivot = qs_df.pivot_table(
            index="factor", columns="formation_year",
            values="q5_q1_spread", aggfunc="first"
        )
        spread_pivot["mean_spread"] = spread_pivot.mean(axis=1)
        spread_pivot["spread_std"] = spread_pivot.iloc[:, :-1].std(axis=1)
        spread_pivot["sign_consistent"] = (
            (spread_pivot.iloc[:, :-2] > 0).all(axis=1) |
            (spread_pivot.iloc[:, :-2] < 0).all(axis=1)
        )
        spread_pivot = spread_pivot.sort_values("mean_spread", key=abs, ascending=False)

        print("\nQ5-Q1 Spread by formation year:")
        print(spread_pivot.round(4).to_string())

        # Monotonicity
        mono_pivot = qs_df.pivot_table(
            index="factor", columns="formation_year",
            values="monotonicity", aggfunc="first"
        )
        mono_pivot["mean_mono"] = mono_pivot.mean(axis=1)
        print("\nMonotonicity (quintile rank vs return correlation):")
        print(mono_pivot.round(3).to_string())

    # ---------------------------------------------------------------------------
    # Final Summary
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    # Identify OOS-consistent vs OOS-failed factors
    print("\n[A] OOSでも一貫して効くファクター（推奨）:")
    print("  基準: |IC_mean|>=0.03 かつ 全年度で同符号 かつ |ICIR|>=0.5")
    recommended = []
    for _, r in summary.iterrows():
        if pd.isna(r["ic_mean"]) or pd.isna(r["icir"]):
            continue
        fc = r["factor"]
        ic_col = f"ic_{fc}"
        vals = rolling_ic[ic_col].dropna()
        if len(vals) < 2:
            continue
        all_positive = (vals > 0).all()
        all_negative = (vals < 0).all()
        sign_consistent = all_positive or all_negative
        if abs(r["ic_mean"]) >= 0.03 and sign_consistent and abs(r["icir"]) >= 0.5:
            direction = "+" if r["ic_mean"] > 0 else "-"
            recommended.append(fc)
            print(f"  * {fc}: IC_mean={r['ic_mean']:+.4f}, ICIR={r['icir']:+.3f}, "
                  f"direction={direction}")

    if not recommended:
        print("  (該当なし — 基準を |IC_mean|>=0.02, |ICIR|>=0.3 に緩和して再検索)")
        for _, r in summary.iterrows():
            if pd.isna(r["ic_mean"]) or pd.isna(r["icir"]):
                continue
            fc = r["factor"]
            ic_col = f"ic_{fc}"
            vals = rolling_ic[ic_col].dropna()
            if len(vals) < 2:
                continue
            all_positive = (vals > 0).all()
            all_negative = (vals < 0).all()
            sign_consistent = all_positive or all_negative
            if abs(r["ic_mean"]) >= 0.02 and sign_consistent and abs(r["icir"]) >= 0.3:
                direction = "+" if r["ic_mean"] > 0 else "-"
                recommended.append(fc)
                print(f"  * {fc}: IC_mean={r['ic_mean']:+.4f}, ICIR={r['icir']:+.3f}, "
                      f"direction={direction}")

    print("\n[B] クロスセクショナルでは有意だがOOSで消えたファクター:")
    print("  基準: |Pooled_IC|<0.02 or 符号が年度で反転")
    disappeared = []
    for _, r in summary.iterrows():
        if pd.isna(r["ic_mean"]):
            continue
        fc = r["factor"]
        ic_col = f"ic_{fc}"
        vals = rolling_ic[ic_col].dropna()
        if len(vals) < 2:
            continue
        all_positive = (vals > 0).all()
        all_negative = (vals < 0).all()
        sign_consistent = all_positive or all_negative

        # 符号反転 or ICが小さい
        if not sign_consistent or abs(r["ic_mean"]) < 0.02:
            if fc not in recommended:
                disappeared.append(fc)
                sign_info = "sign_flip" if not sign_consistent else "weak"
                print(f"  * {fc}: IC_mean={r['ic_mean']:+.4f}, "
                      f"ICIR={r['icir']:+.3f}, reason={sign_info}")

    print("\n[C] 年度別IC符号の安定性マトリクス:")
    for fc in FACTOR_COLS:
        ic_col = f"ic_{fc}"
        if ic_col not in rolling_ic.columns:
            continue
        signs = []
        for _, row in rolling_ic.iterrows():
            v = row[ic_col]
            if pd.isna(v):
                signs.append("?")
            elif v > 0:
                signs.append("+")
            else:
                signs.append("-")
        sign_str = " ".join(signs)
        ic_vals = rolling_ic[ic_col].dropna()
        mean_ic = ic_vals.mean() if len(ic_vals) > 0 else np.nan
        tag = ""
        if fc in recommended:
            tag = " <<< RECOMMENDED"
        elif fc in disappeared:
            tag = " (weak/flip)"
        print(f"  {fc:<35s} [{sign_str}] mean={mean_ic:+.4f}{tag}"
              if pd.notna(mean_ic) else f"  {fc:<35s} [{sign_str}] mean=N/A")

    # Save results
    out_dir = ROOT / "data"
    rolling_ic.to_csv(out_dir / "oos_rolling_ic.csv", index=False)
    summary.to_csv(out_dir / "oos_icir_summary.csv", index=False)
    if len(qs_df) > 0:
        qs_df.to_csv(out_dir / "oos_quintile_spreads.csv", index=False)
    panel.to_csv(out_dir / "oos_panel.csv", index=False)
    print(f"\nResults saved to {out_dir}/oos_*.csv")


if __name__ == "__main__":
    main()
