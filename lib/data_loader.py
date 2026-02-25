"""
全CSVデータを読み込み、企業単位で統合するデータローダー。
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_financials() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "financials_all.csv")
    df = df.sort_values(["edinet_code", "fiscal_year"])
    return df


def load_ratios() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "ratios_all.csv")
    df = df.sort_values(["edinet_code", "fiscal_year"])
    return df


def load_companies() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "companies.csv")


def load_stock_prices() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "stock_prices.csv")


def load_industries_summary() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "industries_summary.csv")


def load_historical_returns() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "historical_returns.csv")


def build_company_profiles() -> pd.DataFrame:
    """企業ごとの最新年データ + 時系列統計を1行にまとめる。"""
    fin = load_financials()
    ratios = load_ratios()
    prices = load_stock_prices()
    companies = load_companies()

    # --- 最新年のratios ---
    latest_ratios = ratios.sort_values("fiscal_year").groupby("edinet_code").last().reset_index()

    # --- 最新年のfinancials ---
    latest_fin = fin.sort_values("fiscal_year").groupby("edinet_code").last().reset_index()

    # --- 時系列集計（企業単位） ---
    ts_stats = _compute_timeseries_stats(fin, ratios)

    # --- マージ ---
    profile = companies.merge(latest_ratios, on="edinet_code", how="left", suffixes=("", "_r"))
    profile = profile.merge(
        latest_fin[["edinet_code", "net_income", "cf_operating", "cf_investing",
                     "total_assets", "net_assets", "revenue", "operating_income",
                     "cash", "fiscal_year"]],
        on="edinet_code", how="left", suffixes=("", "_fin"),
    )
    # stock_prices.csv に industry / name がある場合は merge 前に除外して suffix を防ぐ
    prices_cols_to_drop = [c for c in ["industry", "name"] if c in prices.columns and c in profile.columns]
    if prices_cols_to_drop:
        prices = prices.drop(columns=prices_cols_to_drop)
    profile = profile.merge(prices, on="edinet_code", how="left", suffixes=("", "_price"))
    profile = profile.merge(ts_stats, on="edinet_code", how="left")

    # --- 株価リターン ---
    hist = load_historical_returns()
    if "ticker" in profile.columns and "ticker" in hist.columns:
        profile = profile.merge(hist, on="ticker", how="left", suffixes=("", "_hist"))

    # --- suffix 付きカラム除去 (ratios / stock_prices merge 由来) ---
    suffix_cols = [c for c in profile.columns if c.endswith(("_r", "_price"))]
    if suffix_cols:
        profile = profile.drop(columns=suffix_cols)

    # --- yahooquery 業種 (127カテゴリ) ---
    yf_path = DATA_DIR / "yf_sectors.csv"
    if yf_path.exists():
        yf = pd.read_csv(yf_path)
        # sectorKey / industryKey は merge 後に重複カラムになるため事前に除外
        yf = yf.drop(columns=["sectorKey", "industryKey"], errors="ignore")
        profile = profile.merge(yf, on="ticker", how="left")

    return profile


def get_company_timeseries(edinet_code: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """特定企業の時系列データ（financials, ratios）を返す。"""
    fin = load_financials()
    ratios = load_ratios()
    return (
        fin[fin["edinet_code"] == edinet_code].sort_values("fiscal_year"),
        ratios[ratios["edinet_code"] == edinet_code].sort_values("fiscal_year"),
    )


def get_industry_benchmark(
    industry: str, profiles: pd.DataFrame, industry_col: str = "industry",
) -> dict[str, float]:
    """同業種企業の主要指標中央値とパーセンタイル情報を返す。"""
    ind = profiles[profiles[industry_col] == industry]
    n = len(ind)

    def _med(col: str) -> float | None:
        if col not in ind.columns:
            return None
        vals = pd.to_numeric(ind[col], errors="coerce").dropna()
        return float(vals.median()) if len(vals) > 0 else None

    return {
        "company_count": n,
        "roe_median": _med("roe"),
        "operating_margin_median": _med("operating_margin"),
        "net_margin_median": _med("net_margin"),
        "equity_ratio_median": _med("equity_ratio"),
        "marketCap_median": _med("marketCap"),
        "dividendYield_median": _med("dividendYield"),
        "forwardPE_median": _med("forwardPE"),
        "priceToBook_median": _med("priceToBook"),
        "debtToEquity_median": _med("debtToEquity"),
        "return_1y_median": _med("return_1y"),
    }


def get_industry_percentile(
    value: float, col: str, industry: str, profiles: pd.DataFrame,
    industry_col: str = "industry",
) -> float | None:
    """業種内でのパーセンタイル順位を返す (0-100)。高いほど上位。"""
    ind = profiles[profiles[industry_col] == industry]
    if col not in ind.columns:
        return None
    vals = pd.to_numeric(ind[col], errors="coerce").dropna()
    if len(vals) == 0 or pd.isna(value):
        return None
    return float((vals < value).mean() * 100)


def get_peer_companies(
    edinet_code: str,
    industry: str,
    profiles: pd.DataFrame,
    n: int = 5,
    industry_col: str = "industry",
) -> pd.DataFrame:
    """同業種内で事業特性が類似する企業を返す（自社除く）。

    マッチング戦略:
      1. industry_col（デフォルトは industry_yf 127カテゴリ）で同業種フィルタ
      2. 同業種が5社未満 → sector（yahooquery セクター）にフォールバック
      3. sector も5社未満 → EDINET industry（33カテゴリ）にフォールバック
      4. 同業種内で時価総額距離 + 財務類似度でランキング
      5. 時価総額レンジは 0.05x〜20x（同業種内なのでレンジ広め）
    """
    all_others = profiles[profiles["edinet_code"] != edinet_code].copy()

    if len(all_others) == 0:
        return all_others.head(0)

    self_rows = profiles[profiles["edinet_code"] == edinet_code]
    if len(self_rows) == 0:
        return all_others.sort_values("marketCap", ascending=False).head(n)
    self_row = self_rows.iloc[0]

    # --- 段階的業種フィルタ ---
    candidates = pd.DataFrame()
    used_industry_col = industry_col

    # Step 1: industry_col（industry_yf 等）で絞る
    if industry_col in all_others.columns and pd.notna(industry) and str(industry) != "nan":
        candidates = all_others[all_others[industry_col] == industry].copy()

    # Step 2: 5社未満 → sector にフォールバック
    if len(candidates) < 5 and "sector" in all_others.columns:
        self_sector = self_row.get("sector")
        if pd.notna(self_sector) and str(self_sector) != "nan":
            candidates = all_others[all_others["sector"] == self_sector].copy()
            used_industry_col = "sector"

    # Step 3: まだ5社未満 → EDINET industry にフォールバック
    if len(candidates) < 5 and "industry" in all_others.columns:
        self_edinet_ind = self_row.get("industry")
        if pd.notna(self_edinet_ind) and str(self_edinet_ind) != "nan":
            candidates = all_others[all_others["industry"] == self_edinet_ind].copy()
            used_industry_col = "industry"

    # Step 4: それでも候補がいなければ全企業
    if len(candidates) == 0:
        candidates = all_others.copy()

    # --- 時価総額レンジフィルタ (0.05x〜20x — 同業種内なので広め) ---
    self_mcap = pd.to_numeric(self_row.get("marketCap"), errors="coerce")
    if pd.notna(self_mcap) and self_mcap > 0:
        cand_mcap = pd.to_numeric(candidates["marketCap"], errors="coerce")
        filtered = candidates[(cand_mcap >= self_mcap * 0.05) & (cand_mcap <= self_mcap * 20)].copy()
        if len(filtered) >= 3:
            candidates = filtered

    # --- 多指標類似度スコアリング ---
    sim_features = [
        ("roe", 2.0),
        ("operating_margin", 2.0),
        ("net_margin", 2.0),
        ("equity_ratio", 1.0),
        ("debtToEquity", 1.0),
        ("forwardPE", 1.0),
        ("priceToBook", 1.0),
        ("revenue_cagr_3y", 1.5),
    ]

    dist = pd.Series(0.0, index=candidates.index)
    total_weight = pd.Series(0.0, index=candidates.index)

    for col, weight in sim_features:
        if col not in candidates.columns:
            continue
        self_val = pd.to_numeric(self_row.get(col), errors="coerce")
        if pd.isna(self_val):
            continue
        col_vals = pd.to_numeric(candidates[col], errors="coerce")

        all_vals = col_vals.dropna()
        if len(all_vals) < 5:
            continue
        p5, p95 = all_vals.quantile(0.05), all_vals.quantile(0.95)
        if p95 == p5:
            continue
        self_norm = (np.clip(self_val, p5, p95) - p5) / (p95 - p5)
        col_norm = (col_vals.clip(p5, p95) - p5) / (p95 - p5)

        d = ((col_norm - self_norm) ** 2) * weight
        valid_mask = col_norm.notna()
        dist = dist.add(d.fillna(0))
        total_weight = total_weight.add(valid_mask.astype(float) * weight)

    # 時価総額距離も加味（log スケール）
    if pd.notna(self_mcap) and self_mcap > 0:
        cand_mcap = pd.to_numeric(candidates["marketCap"], errors="coerce")
        mcap_ratio = (cand_mcap / self_mcap).clip(0.01, 100)
        mcap_dist = np.log10(mcap_ratio).abs()
        mcap_weight = 1.5
        valid_mcap = cand_mcap.notna()
        dist = dist.add((mcap_dist ** 2 * mcap_weight).fillna(0))
        total_weight = total_weight.add(valid_mcap.astype(float) * mcap_weight)

    total_weight = total_weight.replace(0, 1)
    candidates["_similarity_dist"] = dist / total_weight

    candidates = candidates.sort_values("_similarity_dist").head(n)

    keep_cols = [
        "edinet_code", "name", "ticker", "marketCap", "industry", "industry_yf",
        "roe", "operating_margin", "net_margin", "equity_ratio",
        "forwardPE", "priceToBook", "dividendYield",
        "return_1y", "return_3y",
    ]
    return candidates[[c for c in keep_cols if c in candidates.columns]]


def _compute_timeseries_stats(fin: pd.DataFrame, ratios: pd.DataFrame) -> pd.DataFrame:
    """企業ごとに6年分の時系列統計を計算する。"""
    records = []

    for code, grp in ratios.groupby("edinet_code"):
        grp = grp.sort_values("fiscal_year")
        n_years = len(grp)

        roe_values = pd.to_numeric(grp["roe"], errors="coerce").dropna()
        om_values = pd.to_numeric(grp["operating_margin"], errors="coerce").dropna()
        eps_values = pd.to_numeric(grp["eps"], errors="coerce").dropna()
        eq_values = pd.to_numeric(grp["equity_ratio"], errors="coerce").dropna()
        bps_values = pd.to_numeric(grp["bps"], errors="coerce").dropna()
        dps_values = pd.to_numeric(grp["dividend_per_share"], errors="coerce").dropna()
        fcf_values = pd.to_numeric(grp["fcf"], errors="coerce").dropna()

        # ROE stats
        roe_mean = roe_values.mean() if len(roe_values) > 0 else None
        roe_min = roe_values.min() if len(roe_values) > 0 else None
        roe_std = roe_values.std() if len(roe_values) > 1 else None
        roe_above_10_count = (roe_values > 0.10).sum() if len(roe_values) > 0 else 0
        roe_above_15_count = (roe_values > 0.15).sum() if len(roe_values) > 0 else 0

        # Operating margin stats
        om_mean = om_values.mean() if len(om_values) > 0 else None
        om_cv = (om_values.std() / abs(om_values.mean())) if len(om_values) > 1 and om_values.mean() != 0 else None

        # EPS increase years
        eps_increase_years = 0
        if len(eps_values) > 1:
            eps_increase_years = (eps_values.diff().dropna() > 0).sum()

        # Any loss year
        has_loss = False
        fin_grp = fin[fin["edinet_code"] == code]
        ni_values = pd.to_numeric(fin_grp["net_income"], errors="coerce").dropna()
        if len(ni_values) > 0:
            has_loss = (ni_values < 0).any()

        # Equity ratio trend
        eq_improving = False
        if len(eq_values) >= 3:
            eq_improving = eq_values.iloc[-1] > eq_values.iloc[0]

        # FCF positive years
        fcf_positive_years = (fcf_values > 0).sum() if len(fcf_values) > 0 else 0
        fcf_growing = False
        if len(fcf_values) >= 4:
            fcf_growing = fcf_values.iloc[-1] > fcf_values.iloc[-min(4, len(fcf_values))]

        # BPS growth consistency
        bps_increase_years = 0
        if len(bps_values) > 1:
            bps_increase_years = (bps_values.diff().dropna() > 0).sum()

        # Dividend consistency
        dps_positive_years = (dps_values > 0).sum() if len(dps_values) > 0 else 0
        dps_increase_years = 0
        if len(dps_values) > 1:
            dps_increase_years = (dps_values.diff().dropna() > 0).sum()

        # Accrual ratio (latest year)
        accrual_ratio = None
        if len(fin_grp) > 0:
            latest = fin_grp.sort_values("fiscal_year").iloc[-1]
            ni = pd.to_numeric(latest.get("net_income"), errors="coerce")
            cfo = pd.to_numeric(latest.get("cf_operating"), errors="coerce")
            ta = pd.to_numeric(latest.get("total_assets"), errors="coerce")
            if pd.notna(ni) and pd.notna(cfo) and pd.notna(ta) and ta > 0:
                accrual_ratio = (ni - cfo) / ta

        # EPS momentum: latest EPS / mean(prev 2 years EPS)
        eps_momentum = None
        if len(eps_values) >= 3:
            denom = eps_values.iloc[-3:-1].mean()
            if denom > 0:
                eps_momentum = float(eps_values.iloc[-1] / denom)

        # Dividend CAGR (full period)
        div_cagr = None
        if len(dps_values) >= 3 and (dps_values > 0).all() and dps_values.iloc[0] > 0:
            years_d = len(dps_values) - 1
            div_cagr = float((dps_values.iloc[-1] / dps_values.iloc[0]) ** (1.0 / years_d) - 1)

        # Consecutive dividend increase years (from latest backward)
        consecutive_div_increase = 0
        if len(dps_values) >= 2:
            arr = dps_values.values
            for j in range(len(arr) - 1, 0, -1):
                if arr[j] > arr[j - 1]:
                    consecutive_div_increase += 1
                else:
                    break

        # Net margin improvement (latest vs first 3 years average)
        nm_values = pd.to_numeric(grp["net_margin"], errors="coerce").dropna()
        net_margin_improvement = None
        if len(nm_values) >= 4:
            net_margin_improvement = float(nm_values.iloc[-1] - nm_values.iloc[:3].mean())

        # Net margin latest
        net_margin_latest = None
        if len(nm_values) >= 1:
            net_margin_latest = float(nm_values.iloc[-1])

        records.append({
            "edinet_code": code,
            "n_years": n_years,
            "roe_mean": roe_mean,
            "roe_min": roe_min,
            "roe_std": roe_std,
            "roe_above_10_count": int(roe_above_10_count),
            "roe_above_15_count": int(roe_above_15_count),
            "om_mean": om_mean,
            "om_cv": om_cv,
            "eps_increase_years": int(eps_increase_years),
            "has_loss": has_loss,
            "equity_ratio_improving": eq_improving,
            "fcf_positive_years": int(fcf_positive_years),
            "fcf_growing": fcf_growing,
            "bps_increase_years": int(bps_increase_years),
            "dps_positive_years": int(dps_positive_years),
            "dps_increase_years": int(dps_increase_years),
            "accrual_ratio": accrual_ratio,
            "eps_momentum": eps_momentum,
            "div_cagr": div_cagr,
            "consecutive_div_increase": consecutive_div_increase,
            "net_margin_improvement": net_margin_improvement,
            "net_margin_latest": net_margin_latest,
        })

    return pd.DataFrame(records)
