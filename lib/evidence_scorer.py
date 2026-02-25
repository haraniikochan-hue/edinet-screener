"""
エビデンスベース・スコアリングエンジン v3（6軸・30点満点）

三重検証（6フィルターGate + BPSプロキシOOS + 市場リターンOOS）+ チーム再検証。

v2.1→v3 主要変更:
  - E1 roe_std: 1pt→3pt（Market IC=-0.224、IC 2位なのに1ptは致命的過小評価）
  - B1 連続増配: max閾値 5年→4年（n_years=5制限で5年以上は0.2%のみ達成不能）
  - C1 BPS増加: max閾値 5年→4年（同上）
  - B2 配当CAGR: 4pt→3pt（双峰分布で弁別力低下）
  - A1 純利益率: 3pt→2pt（IC=0.077は3pt分の予測力なし）
  - C2 利益率改善: 2pt→1pt（IC=0.052が全ファクター最低）
  - E2 debtToEquity: 除外（Gate方向とOOS方向が矛盾）
  - D2 PBR: 2pt→1pt（OOS未検証、エビデンス薄）
  - D3 配当利回り: 復活 1pt（Gate 5/6）
  - F1 時価総額: 2pt→4pt（5y_r=+0.483 最強ファクター）

検証済みファクター（Market OOS IC / Gate n_pass）:
  roe_std             IC=-0.224  Gate 5/6  — 利益安定性（低い=良い）
  consec_div_increase IC=+0.220  Gate 5/6  — 連続増配年数
  eps_momentum        IC=+0.123  Gate 6/6  — EPS加速度
  div_cagr            IC=+0.120  Gate 5/6  — 配当成長率
  has_loss            IC=-0.109  Gate 6/6  — 赤字年の有無
  bps_increase_years  IC=+0.103  Gate 6/6  — BPS増加年数
  net_margin          IC=+0.077  Gate 6/6  — 純利益率
  net_margin_improv   IC=+0.052  Gate 6/6  — 利益率改善
  forwardPE           Gate 6/6 r=+0.27     — 予想PER（バンド型）
  log_marketCap       Gate 5/6 5y_r=+0.483 — 時価総額

バックテスト実績（v2.1時点）:
  Spearman rho=+0.294 (p<1e-73), Q5-Q1=+16.6%, S>A>B>C>D 完全単調

配点設計（30点）:
  A. 利益力 (Earnings Power)         — 7pt  (net_margin 2, eps_momentum 3, has_loss 2)
  B. 株主還元力 (Shareholder Returns) — 7pt  (consec_div_increase 4, div_cagr 3)
  C. 企業価値蓄積 (Value Accum.)     — 4pt  (bps_increase_years 3, net_margin_improv 1)
  D. バリュエーション (Valuation)     — 4pt  (forwardPE 2, PBR 1, dividendYield 1)
  E. 財務健全性・安定性 (Stability)  — 4pt  (roe_std 3, FCF 1)
  F. 市場評価 (Market Quality)        — 4pt  (marketCap 4)
  合計 = 30点
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class ScoreDetail:
    """各軸のスコア詳細"""
    name: str
    name_en: str
    score: float
    max_score: int
    details: list[str] = field(default_factory=list)

    @property
    def pct(self) -> float:
        return self.score / self.max_score if self.max_score > 0 else 0.0


@dataclass
class EvidenceReport:
    """1企業のエビデンスベーススコアレポート"""
    edinet_code: str
    company_name: str
    industry: str
    ticker: str
    sections: list[ScoreDetail]
    strengths: list[str]
    concerns: list[str]

    @property
    def score_total(self) -> float:
        return round(sum(s.score for s in self.sections), 1)

    @property
    def max_total(self) -> int:
        return sum(s.max_score for s in self.sections)

    @property
    def rank(self) -> str:
        s = self.score_total
        if s >= 22:
            return "S"
        elif s >= 17:
            return "A"
        elif s >= 12:
            return "B"
        elif s >= 7:
            return "C"
        else:
            return "D"


def score_company(row: pd.Series, industry_medians: pd.DataFrame | None = None) -> EvidenceReport:
    """1企業の行データからエビデンスベーススコアを計算する。"""
    sections: list[ScoreDetail] = []
    strengths: list[str] = []
    concerns: list[str] = []

    n_years = _safe_int(row.get("n_years"), 0)

    # === A. 利益力 (0-7) ===
    a_score = 0.0
    a_details = []

    # A1: 純利益率 (0-2) — Market IC=+0.077, Gate 6/6
    net_margin = _safe_float(row.get("net_margin_latest")) or _safe_float(row.get("net_margin"))
    if net_margin is not None:
        nm_pct = net_margin * 100 if abs(net_margin) < 1 else net_margin
        if nm_pct >= 5:
            a1 = 2
        elif nm_pct >= 2:
            a1 = 1
        else:
            a1 = 0
        a_details.append(f"純利益率: {nm_pct:.1f}% -> {a1}/2点")
        if a1 == 2:
            strengths.append(f"純利益率{nm_pct:.1f}%")
        elif a1 == 0:
            concerns.append(f"純利益率が低い（{nm_pct:.1f}%）")
    else:
        a1 = 0
        a_details.append("純利益率: データなし -> 0/2点")
    a_score += a1

    # A2: EPS加速度 (0-3) — Market IC=+0.123, Gate 6/6
    eps_mom = _safe_float(row.get("eps_momentum"))
    if eps_mom is not None:
        if eps_mom >= 1.5:
            a2 = 3
        elif eps_mom >= 1.2:
            a2 = 2
        elif eps_mom >= 1.0:
            a2 = 1
        else:
            a2 = 0
        a_details.append(f"EPS加速度: {eps_mom:.2f}x -> {a2}/3点")
        if a2 >= 2:
            strengths.append(f"EPS加速{eps_mom:.2f}x")
        elif a2 == 0:
            concerns.append("EPS減速中")
    else:
        a2 = 0
        a_details.append("EPS加速度: データなし -> 0/3点")
    a_score += a2

    # A3: 赤字年なし (0-2) — Market IC=-0.109, Gate 6/6
    has_loss = row.get("has_loss", True)
    a3 = 2 if not has_loss else 0
    a_score += a3
    a_details.append(f"赤字年なし: {'なし' if not has_loss else 'あり'} -> {a3}/2点")
    if not has_loss:
        strengths.append(f"{n_years}年連続黒字")
    else:
        concerns.append("過去に赤字年あり")

    sections.append(ScoreDetail("利益力", "Earnings Power", a_score, 7, a_details))

    # === B. 株主還元力 (0-7) ===
    b_score = 0.0
    b_details = []

    # B1: 連続増配年数 (0-4) — Market IC=+0.220, Gate 5/6
    # n_years=5 制限のため max閾値を 5年→4年に引き下げ
    consec_inc = _safe_int(row.get("consecutive_div_increase"), 0)
    if consec_inc == 0:
        consec_inc = _safe_int(row.get("dps_increase_years"), 0)
    if consec_inc >= 4:
        b1 = 4
    elif consec_inc >= 3:
        b1 = 3
    elif consec_inc >= 2:
        b1 = 2
    elif consec_inc >= 1:
        b1 = 1
    else:
        b1 = 0
    b_score += b1
    b_details.append(f"連続増配年数: {consec_inc}年 -> {b1}/4点")
    if b1 >= 3:
        strengths.append(f"{consec_inc}年連続増配")

    # B2: 配当成長率 (0-3) — Market IC=+0.120, Gate 5/6
    # 双峰分布対策で閾値調整: 10/7/4/1% → 8/5/2%
    div_cagr = _safe_float(row.get("div_cagr"))
    if div_cagr is not None:
        dc_pct = div_cagr * 100
        if dc_pct >= 8:
            b2 = 3
        elif dc_pct >= 5:
            b2 = 2
        elif dc_pct >= 2:
            b2 = 1
        else:
            b2 = 0
        b_details.append(f"配当成長率(CAGR): {dc_pct:.1f}% -> {b2}/3点")
        if b2 >= 2:
            strengths.append(f"配当CAGR {dc_pct:.1f}%")
    else:
        b2 = 0
        dps_pos = _safe_int(row.get("dps_positive_years"), 0)
        if dps_pos >= n_years and n_years >= 5:
            b2 = 1
        b_details.append(f"配当成長率: データなし (配当連続{dps_pos}年で代替) -> {b2}/3点")
    b_score += b2

    sections.append(ScoreDetail("株主還元力", "Shareholder Returns", b_score, 7, b_details))

    # === C. 企業価値蓄積 (0-4) ===
    c_score = 0.0
    c_details = []

    # C1: BPS増加年数 (0-3) — Market IC=+0.103, Gate 6/6
    # n_years=5 制限のため max閾値を 5年→4年に引き下げ
    bps_inc = _safe_int(row.get("bps_increase_years"), 0)
    if bps_inc >= 4:
        c1 = 3
    elif bps_inc >= 3:
        c1 = 2
    elif bps_inc >= 2:
        c1 = 1
    else:
        c1 = 0
    c_score += c1
    c_details.append(f"BPS増加年数: {bps_inc}年 -> {c1}/3点")
    if c1 >= 2:
        strengths.append(f"BPS {bps_inc}年増加")

    # C2: 純利益率改善 (0-1) — Market IC=+0.052, Gate 6/6
    # IC最低のため2pt→1ptに削減
    nm_improv = _safe_float(row.get("net_margin_improvement"))
    if nm_improv is not None:
        improv_pct = nm_improv * 100 if abs(nm_improv) < 1 else nm_improv
        c2 = 1 if improv_pct >= 2 else 0
        c_details.append(f"利益率改善: {improv_pct:+.1f}%pt -> {c2}/1点")
    else:
        c2 = 0
        c_details.append("利益率改善: データなし -> 0/1点")
    c_score += c2

    sections.append(ScoreDetail("企業価値蓄積", "Value Accumulation", c_score, 4, c_details))

    # === D. バリュエーション (0-4) ===
    d_score = 0.0
    d_details = []
    industry = row.get("industry", "")

    ind_pbr_med = None
    ind_per_med = None
    if industry_medians is not None and industry:
        med_row = industry_medians[industry_medians["industry"] == industry]
        if len(med_row) > 0:
            ind_pbr_med = _safe_float(med_row.iloc[0].get("priceToBook_median"))
            ind_per_med = _safe_float(med_row.iloc[0].get("forwardPE_median"))

    # D1: 予想PER — バンド型 (0-2) — Gate 6/6, r=+0.27
    fwd_pe = _safe_float(row.get("forwardPE"))
    if fwd_pe is not None and fwd_pe > 0:
        if ind_per_med and ind_per_med > 0:
            pe_ratio = fwd_pe / ind_per_med
            if 0.7 <= pe_ratio <= 1.3:
                d1 = 2
            elif 0.5 <= pe_ratio <= 1.6:
                d1 = 1
            else:
                d1 = 0
            d_details.append(f"予想PER: {fwd_pe:.1f} (業種中央値比: {pe_ratio:.2f}) -> {d1}/2点")
        else:
            if 10 <= fwd_pe <= 25:
                d1 = 2
            elif 5 <= fwd_pe <= 40:
                d1 = 1
            else:
                d1 = 0
            d_details.append(f"予想PER: {fwd_pe:.1f} -> {d1}/2点")
    else:
        d1 = 0
        d_details.append("予想PER: データなし -> 0/2点")
    d_score += d1

    # D2: PBR — 業種相対 (0-1) — Gate 5/6、OOS未検証のため1ptに削減
    pbr = _safe_float(row.get("priceToBook"))
    if pbr is not None and pbr > 0:
        if ind_pbr_med and ind_pbr_med > 0:
            pbr_ratio = pbr / ind_pbr_med
            d2 = 1 if pbr_ratio < 0.7 else 0
            d_details.append(f"PBR: {pbr:.2f} (業種中央値比: {pbr_ratio:.2f}) -> {d2}/1点")
        else:
            d2 = 1 if pbr < 0.8 else 0
            d_details.append(f"PBR: {pbr:.2f} -> {d2}/1点")
    else:
        d2 = 0
        d_details.append("PBR: データなし -> 0/1点")
    d_score += d2

    # D3: 配当利回り (0-1) — Gate 5/6
    div_yield = _safe_float(row.get("dividendYield"))
    if div_yield is not None:
        dy_pct = div_yield * 100 if div_yield < 1 else div_yield
        d3 = 1 if dy_pct >= 2.5 else 0
        d_details.append(f"配当利回り: {dy_pct:.2f}% -> {d3}/1点")
    else:
        d3 = 0
        d_details.append("配当利回り: データなし -> 0/1点")
    d_score += d3

    sections.append(ScoreDetail("バリュエーション", "Valuation", d_score, 4, d_details))

    # === E. 財務健全性・安定性 (0-4) ===
    e_score = 0.0
    e_details = []

    # E1: 利益安定性 / ROE標準偏差 (0-3) — Market IC=-0.224, Gate 5/6
    # v2.1で1ptだったが、IC 2位の致命的過小評価を解消
    roe_std = _safe_float(row.get("roe_std"))
    if roe_std is not None:
        if roe_std < 0.02:
            e1 = 3
        elif roe_std < 0.05:
            e1 = 2
        elif roe_std < 0.10:
            e1 = 1
        else:
            e1 = 0
        e_details.append(f"利益安定性(ROE std): {roe_std:.3f} -> {e1}/3点")
        if e1 >= 2:
            strengths.append(f"利益安定(ROE std {roe_std:.3f})")
        elif e1 == 0:
            concerns.append(f"利益不安定(ROE std {roe_std:.3f})")
    else:
        e1 = 0
        e_details.append("利益安定性: データなし -> 0/3点")
    e_score += e1

    # E2: FCF黒字年数 (0-1)
    # debtToEquity は Gate方向(低D/E=良) と OOS方向(高D/E=良) が矛盾するため除外
    fcf_pos = _safe_int(row.get("fcf_positive_years"), 0)
    e2 = 1 if fcf_pos >= 4 else 0
    e_score += e2
    e_details.append(f"FCF黒字年数: {fcf_pos}/{n_years}年 -> {e2}/1点")

    sections.append(ScoreDetail("財務健全性・安定性", "Financial Stability", e_score, 4, e_details))

    # === F. 市場評価 (0-4) ===
    # log_marketCap: Gate 5/6, 5y_r=+0.483（最強ファクター）
    f_score = 0.0
    f_details = []

    mcap = _safe_float(row.get("marketCap"))
    if mcap is not None:
        mcap_b = mcap / 1e9  # 十億円
        if mcap_b >= 5000:
            f1 = 4
        elif mcap_b >= 2000:
            f1 = 3
        elif mcap_b >= 500:
            f1 = 2
        elif mcap_b >= 100:
            f1 = 1
        else:
            f1 = 0
        f_score += f1

        if mcap_b >= 1000:
            f_details.append(f"時価総額: {mcap_b/1000:.1f}兆円 -> {f1}/4点")
        elif mcap_b >= 1:
            f_details.append(f"時価総額: {mcap_b:.0f}B円 -> {f1}/4点")
        else:
            f_details.append(f"時価総額: {mcap_b:.1f}B円 -> {f1}/4点")
    else:
        f_score = 0
        f_details.append("時価総額: データなし -> 0/4点")

    sections.append(ScoreDetail("市場評価", "Market Quality", f_score, 4, f_details))

    return EvidenceReport(
        edinet_code=str(row.get("edinet_code", "")),
        company_name=str(row.get("name", row.get("company_name", ""))),
        industry=str(row.get("industry", "")),
        ticker=str(row.get("ticker", "")),
        sections=sections,
        strengths=strengths[:5],
        concerns=concerns[:5],
    )


def score_all(profiles: pd.DataFrame) -> list[EvidenceReport]:
    """全企業をスコアリングする。"""
    industry_medians = _compute_industry_medians(profiles)
    reports = []
    for _, row in profiles.iterrows():
        report = score_company(row, industry_medians)
        reports.append(report)
    return reports


def reports_to_dataframe(reports: list[EvidenceReport]) -> pd.DataFrame:
    """レポートリストをDataFrameに変換。"""
    rows = []
    for r in reports:
        row = {
            "edinet_code": r.edinet_code,
            "企業名": r.company_name,
            "業種": r.industry,
            "ティッカー": r.ticker,
            "総合スコア": r.score_total,
            "ランク": r.rank,
        }
        for s in r.sections:
            row[s.name] = f"{s.score}/{s.max_score}"
        row["強み"] = " / ".join(r.strengths) if r.strengths else "-"
        row["懸念"] = " / ".join(r.concerns) if r.concerns else "-"
        rows.append(row)
    return pd.DataFrame(rows).sort_values("総合スコア", ascending=False).reset_index(drop=True)


def _compute_industry_medians(profiles: pd.DataFrame) -> pd.DataFrame:
    """業種別の各指標中央値を計算。"""
    agg_dict = {}
    col_map = {
        "forwardPE": "forwardPE_median",
        "priceToBook": "priceToBook_median",
    }
    for src_col, dst_col in col_map.items():
        if src_col in profiles.columns:
            agg_dict[dst_col] = (src_col, "median")
    if agg_dict:
        return profiles.groupby("industry").agg(**agg_dict).reset_index()
    return pd.DataFrame(columns=["industry"])


def _safe_float(val, default=None) -> float | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_int(val, default: int = 0) -> int:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default
