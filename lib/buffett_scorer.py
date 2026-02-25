"""
バフェット型スコアリングエンジン（7軸・30点満点）

A. 経済的堀 (Economic Moat)       — 10点
B. 利益の予測可能性               — 7点
C. 財務の保守性                   — 5点
D. フリーキャッシュフロー          — 4点
E. 成長性                         — 4点
F. 割安度                         — 2点 (bonus-like)
G. 株主還元の一貫性               — 3点 (bonus-like) => 合計調整で30点扱い

実際の満点合計 = 35 → 30点スケールに正規化して出力する。
※ 内部では raw_score (0-35) で計算し、最終出力で 0-30 に変換。
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ScoreDetail:
    """各軸のスコア詳細"""
    name: str
    name_en: str
    score: int
    max_score: int
    details: list[str] = field(default_factory=list)

    @property
    def pct(self) -> float:
        return self.score / self.max_score if self.max_score > 0 else 0.0


@dataclass
class BuffettReport:
    """1企業のバフェットスコアレポート"""
    edinet_code: str
    company_name: str
    industry: str
    ticker: str
    sections: list[ScoreDetail]
    strengths: list[str]
    concerns: list[str]

    @property
    def raw_total(self) -> int:
        return sum(s.score for s in self.sections)

    @property
    def raw_max(self) -> int:
        return sum(s.max_score for s in self.sections)

    @property
    def score_30(self) -> float:
        """30点満点に正規化"""
        return round(self.raw_total / self.raw_max * 30, 1) if self.raw_max > 0 else 0.0

    @property
    def rank(self) -> str:
        s = self.score_30
        if s >= 25:
            return "S"
        elif s >= 20:
            return "A"
        elif s >= 15:
            return "B"
        elif s >= 10:
            return "C"
        else:
            return "D"


def score_company(row: pd.Series, industry_medians: pd.DataFrame | None = None) -> BuffettReport:
    """1企業の行データからバフェットスコアを計算する。"""
    sections = []
    strengths = []
    concerns = []

    # === A. 経済的堀 (0-10) ===
    a_score = 0
    a_details = []

    # A1: ROE一貫性 (0-3)
    roe_above_10 = _safe_int(row.get("roe_above_10_count"), 0)
    n_years = _safe_int(row.get("n_years"), 0)
    if roe_above_10 >= 6:
        a1 = 3
    elif roe_above_10 >= 5:
        a1 = 2
    elif roe_above_10 >= 4:
        a1 = 1
    else:
        a1 = 0
    a_score += a1
    a_details.append(f"ROE>10%: {roe_above_10}/{n_years}年 → {a1}/3点")
    if a1 == 3:
        a_details.append(f"  💡 {n_years}年中{roe_above_10}年でROE10%超を維持。株主資本を効率的に活用し続けており、持続的な競争優位性（経済的堀）の存在を示唆")
        strengths.append(f"ROE {n_years}年連続10%超")
    elif a1 >= 1:
        a_details.append(f"  💡 {n_years}年中{roe_above_10}年でROE10%超。一定の資本効率はあるが、毎年安定して高ROEを維持できておらず堀の強さには疑問が残る")
    else:
        a_details.append(f"  💡 {n_years}年中{roe_above_10}年しかROE10%を超えておらず、持続的な競争優位性があるとは判断しにくい。業界構造や競争環境の影響の可能性")
        concerns.append("ROEが10%を下回る年が多い")

    # A2: ROE水準 (0-3)
    roe_mean = _safe_float(row.get("roe_mean"))
    if roe_mean is not None:
        roe_mean_pct = roe_mean * 100 if roe_mean < 1 else roe_mean
        if roe_mean_pct >= 20:
            a2 = 3
        elif roe_mean_pct >= 15:
            a2 = 2
        elif roe_mean_pct >= 10:
            a2 = 1
        else:
            a2 = 0
        a_details.append(f"ROE平均: {roe_mean_pct:.1f}% → {a2}/3点")
        if a2 == 3:
            a_details.append(f"  💡 平均ROE {roe_mean_pct:.1f}%は卓越した水準。ブランド力・特許・ネットワーク効果など強い堀を持つ企業に典型的")
            strengths.append(f"ROE平均 {roe_mean_pct:.1f}%（高水準）")
        elif a2 == 2:
            a_details.append(f"  💡 平均ROE {roe_mean_pct:.1f}%は優良企業の水準。効率的な資本運用だが、バフェットが好む20%超にはやや届かない")
            strengths.append(f"ROE平均 {roe_mean_pct:.1f}%（高水準）")
        elif a2 == 1:
            a_details.append(f"  💡 平均ROE {roe_mean_pct:.1f}%は日本企業の平均（8-9%）を上回るが、強い堀があるとは言いにくい水準")
        else:
            a_details.append(f"  💡 平均ROE {roe_mean_pct:.1f}%は日本企業平均並みかそれ以下。資本効率の改善余地が大きい")
    else:
        a2 = 0
        a_details.append("ROE平均: データなし → 0/3点")
        a_details.append("  💡 ROEデータが取得できず評価不能。開示が不十分な可能性")
    a_score += a2

    # A3: 営業利益率の安定性 (0-2)
    om_cv = _safe_float(row.get("om_cv"))
    if om_cv is not None:
        if om_cv < 0.15:
            a3 = 2
        elif om_cv < 0.30:
            a3 = 1
        else:
            a3 = 0
        a_details.append(f"営業利益率CV: {om_cv:.2f} → {a3}/2点")
        if a3 == 2:
            a_details.append(f"  💡 変動係数{om_cv:.2f}は非常に安定。景気変動やコスト上昇に左右されにくい価格決定力を持つ事業構造")
        elif a3 == 1:
            a_details.append(f"  💡 変動係数{om_cv:.2f}はやや変動あり。利益率は概ね安定しているが、外部環境の変化で振れることがある")
        else:
            a_details.append(f"  💡 変動係数{om_cv:.2f}は利益率の振れが大きい。景気循環型ビジネスや競争激化による値下げ圧力が影響している可能性")
            concerns.append(f"営業利益率のブレが大きい(CV={om_cv:.2f})")
    else:
        a3 = 0
        a_details.append("営業利益率CV: データなし → 0/2点")
        a_details.append("  💡 営業利益率の時系列データが不足しており安定性を評価できない")
    a_score += a3

    # A4: 営業利益率水準 — 業種内相対評価 (0-2)
    om_mean = _safe_float(row.get("om_mean"))
    ind_om_med = None
    if industry_medians is not None and row.get("industry"):
        med_row = industry_medians[industry_medians["industry"] == row["industry"]]
        if len(med_row) > 0:
            ind_om_med = _safe_float(med_row.iloc[0].get("om_mean_median"))

    if om_mean is not None:
        om_mean_pct = om_mean * 100 if abs(om_mean) < 1 else om_mean
        if ind_om_med is not None:
            ind_om_pct = ind_om_med * 100 if abs(ind_om_med) < 1 else ind_om_med
            om_ratio = om_mean_pct / ind_om_pct if ind_om_pct > 0 else 0
            if om_ratio >= 1.5:
                a4 = 2  # 業種中央値の1.5倍以上
            elif om_ratio >= 1.0:
                a4 = 1  # 業種中央値以上
            else:
                a4 = 0
            a_details.append(f"営業利益率平均: {om_mean_pct:.1f}% (業種中央値: {ind_om_pct:.1f}%, 比率: {om_ratio:.2f}) → {a4}/2点")
            if om_ratio >= 1.5:
                a_details.append(f"  💡 業種中央値の{om_ratio:.1f}倍と大幅に上回る。同業他社にない差別化要因（ブランド・技術・規模の経済）を示唆")
            elif om_ratio >= 1.0:
                a_details.append(f"  💡 業種中央値を上回るが突出はしていない。競争力はあるが圧倒的な価格支配力とまでは言えない")
            else:
                a_details.append(f"  💡 業種中央値を下回っており、同業他社と比較して収益性で劣後。コスト構造や競争環境に課題がある可能性")
        else:
            # フォールバック: 絶対基準
            if om_mean_pct >= 15:
                a4 = 2
            elif om_mean_pct >= 10:
                a4 = 1
            else:
                a4 = 0
            a_details.append(f"営業利益率平均: {om_mean_pct:.1f}% (業種中央値なし) → {a4}/2点")
            if om_mean_pct >= 15:
                a_details.append(f"  💡 営業利益率{om_mean_pct:.1f}%は高水準。本業での稼ぐ力が強い")
            elif om_mean_pct >= 10:
                a_details.append(f"  💡 営業利益率{om_mean_pct:.1f}%は平均的。本業の収益力は標準水準")
            else:
                a_details.append(f"  💡 営業利益率{om_mean_pct:.1f}%は低水準。薄利多売型か、競争圧力が強い事業構造の可能性")
    else:
        a4 = 0
        a_details.append("営業利益率平均: データなし → 0/2点")
        a_details.append("  💡 営業利益率データが取得できず評価不能")
    a_score += a4

    sections.append(ScoreDetail("経済的堀", "Economic Moat", a_score, 10, a_details))

    # === B. 利益の予測可能性 (0-7) ===
    b_score = 0
    b_details = []

    # B1: EPS連続増加 (0-3)
    eps_inc = _safe_int(row.get("eps_increase_years"), 0)
    if eps_inc >= 5:
        b1 = 3
    elif eps_inc >= 4:
        b1 = 2
    elif eps_inc >= 3:
        b1 = 1
    else:
        b1 = 0
    b_score += b1
    b_details.append(f"EPS増加年数: {eps_inc}年 → {b1}/3点")
    if b1 == 3:
        b_details.append(f"  💡 {eps_inc}年連続でEPS増加。利益成長の予測可能性が高く、バフェットが最も重視する「将来利益が読める企業」の条件を満たす")
        strengths.append(f"EPS {eps_inc}年連続増加")
    elif b1 >= 1:
        b_details.append(f"  💡 {eps_inc}年のEPS増加はある程度の利益トレンドを示すが、一貫した右肩上がりとは言い切れない")
    else:
        b_details.append(f"  💡 EPS増加が{eps_inc}年のみで利益の方向性が不安定。事業環境や競争構造の変化に利益が左右されやすい")

    # B2: 赤字なし (0/2)
    has_loss = row.get("has_loss", True)
    b2 = 0 if has_loss else 2
    b_score += b2
    b_details.append(f"赤字年あり: {'あり' if has_loss else 'なし'} → {b2}/2点")
    if has_loss:
        b_details.append("  💡 過去に赤字を計上した年がある。一時的な特殊要因か構造的な問題かの見極めが必要。バフェットは赤字歴のある企業を敬遠する傾向")
        concerns.append("過去に赤字年あり")
    else:
        b_details.append(f"  💡 過去{n_years}年間赤字なし。不況期でも黒字を維持できる事業の底堅さを示す")

    # B3: 利益の質 - アクルーアル比率 (0-2)
    accrual = _safe_float(row.get("accrual_ratio"))
    if accrual is not None:
        if accrual < -0.05:
            b3 = 2
        elif accrual < 0.05:
            b3 = 1
        else:
            b3 = 0
        b_details.append(f"アクルーアル比率: {accrual:.3f} → {b3}/2点")
        if b3 == 2:
            b_details.append(f"  💡 アクルーアル比率{accrual:.3f}（負値）= 営業CFが純利益を上回る。利益がキャッシュに裏付けられた「質の高い利益」")
            strengths.append("キャッシュ裏付けの強い利益")
        elif b3 == 1:
            b_details.append(f"  💡 アクルーアル比率{accrual:.3f}は標準的な範囲。利益とキャッシュフローに大きな乖離はない")
        else:
            b_details.append(f"  💡 アクルーアル比率{accrual:.3f}（正値・大）= 利益の多くが売掛金や棚卸資産など会計上の数字。キャッシュ裏付けが弱く利益の質に懸念")
            concerns.append(f"利益の質に懸念(アクルーアル={accrual:.3f})")
    else:
        b3 = 0
        b_details.append("アクルーアル比率: データなし → 0/2点")
        b_details.append("  💡 営業CF・純利益・総資産のいずれかが欠損しており利益の質を評価できない")
    b_score += b3

    sections.append(ScoreDetail("利益の予測可能性", "Earnings Predictability", b_score, 7, b_details))

    # === C. 財務の保守性 (0-5) ===
    c_score = 0
    c_details = []

    # C1: 自己資本比率 — 業種内相対評価 (0-2)
    eq_ratio = _safe_float(row.get("equity_ratio"))
    if eq_ratio is None:
        eq_ratio = _safe_float(row.get("equity_ratio_official"))

    ind_eq_med = None
    if industry_medians is not None and row.get("industry"):
        med_row = industry_medians[industry_medians["industry"] == row["industry"]]
        if len(med_row) > 0:
            ind_eq_med = _safe_float(med_row.iloc[0].get("equity_ratio_median"))

    if eq_ratio is not None:
        eq_pct = eq_ratio * 100 if eq_ratio < 1 else eq_ratio
        if ind_eq_med is not None:
            ind_eq_pct = ind_eq_med * 100 if ind_eq_med < 1 else ind_eq_med
            eq_ratio_vs = eq_pct / ind_eq_pct if ind_eq_pct > 0 else 0
            if eq_ratio_vs >= 1.3:
                c1 = 2  # 業種中央値の1.3倍以上
            elif eq_ratio_vs >= 1.0:
                c1 = 1  # 業種中央値以上
            else:
                c1 = 0
            c_details.append(f"自己資本比率: {eq_pct:.1f}% (業種中央値: {ind_eq_pct:.1f}%, 比率: {eq_ratio_vs:.2f}) → {c1}/2点")
            if eq_ratio_vs >= 1.3:
                c_details.append(f"  💡 同業種の中央値{ind_eq_pct:.0f}%に対し{eq_pct:.0f}%と大幅に上回る。財務基盤が堅固で不況への耐性が高い")
                strengths.append(f"自己資本比率 {eq_pct:.0f}%（業種内上位）")
            elif eq_ratio_vs >= 1.0:
                c_details.append(f"  💡 業種中央値を上回っており財務は健全だが、突出して保守的というほどではない")
            else:
                c_details.append(f"  💡 業種中央値を下回っており、同業他社と比べて借入依存度が高い。金利上昇時のリスクに注意")
                if eq_ratio_vs < 0.7:
                    concerns.append(f"自己資本比率が業種内で低い({eq_pct:.0f}%, 中央値{ind_eq_pct:.0f}%)")
        else:
            if eq_pct >= 60:
                c1 = 2
            elif eq_pct >= 40:
                c1 = 1
            else:
                c1 = 0
            c_details.append(f"自己資本比率: {eq_pct:.1f}% (業種中央値なし) → {c1}/2点")
            if eq_pct >= 60:
                c_details.append(f"  💡 自己資本比率{eq_pct:.0f}%は堅実な財務体質。外部資金への依存度が低く経営の安定性が高い")
                strengths.append(f"自己資本比率 {eq_pct:.0f}%（堅実）")
            elif eq_pct >= 40:
                c_details.append(f"  💡 自己資本比率{eq_pct:.0f}%は標準的な水準。大きな懸念はないが余裕があるとも言いにくい")
            else:
                c_details.append(f"  💡 自己資本比率{eq_pct:.0f}%は低め。借入金への依存が大きく、業績悪化時に財務が脆弱になるリスク")
    else:
        c1 = 0
        c_details.append("自己資本比率: データなし → 0/2点")
        c_details.append("  💡 自己資本比率データが取得できず財務健全性を評価できない")
    c_score += c1

    # C2: D/Eレシオ — 業種内相対評価 (0-2)
    de_ratio = _safe_float(row.get("debtToEquity"))
    ind_de_med = None
    if industry_medians is not None and row.get("industry"):
        med_row = industry_medians[industry_medians["industry"] == row["industry"]]
        if len(med_row) > 0:
            ind_de_med = _safe_float(med_row.iloc[0].get("debtToEquity_median"))

    if de_ratio is not None:
        de_val = de_ratio / 100 if de_ratio > 5 else de_ratio
        if ind_de_med is not None:
            ind_de_val = ind_de_med / 100 if ind_de_med > 5 else ind_de_med
            if ind_de_val > 0:
                de_ratio_vs = de_val / ind_de_val
                if de_ratio_vs < 0.5:
                    c2 = 2  # 業種中央値の半分以下の負債
                elif de_ratio_vs < 0.8:
                    c2 = 1  # 業種中央値より20%以上低い
                else:
                    c2 = 0
                c_details.append(f"D/Eレシオ: {de_val:.2f} (業種中央値: {ind_de_val:.2f}, 比率: {de_ratio_vs:.2f}) → {c2}/2点")
                if de_ratio_vs < 0.5:
                    c_details.append(f"  💡 D/E{de_val:.2f}は業種中央値{ind_de_val:.2f}の半分以下。負債に頼らず事業を回せる強い収益力の証")
                elif de_ratio_vs < 0.8:
                    c_details.append(f"  💡 D/E{de_val:.2f}は業種中央値より低く、財務レバレッジは控えめ。バフェット好みの保守的な資本構成")
                else:
                    c_details.append(f"  💡 D/E{de_val:.2f}は業種中央値並みかそれ以上。借入金が多く、金利負担や返済リスクに注意が必要")
                if de_ratio_vs > 2.0:
                    concerns.append(f"負債が業種内で多い(D/E={de_val:.2f}, 中央値{ind_de_val:.2f})")
            else:
                c2 = 2 if de_val < 0.3 else (1 if de_val < 0.8 else 0)
                c_details.append(f"D/Eレシオ: {de_val:.2f} (業種中央値=0) → {c2}/2点")
                c_details.append(f"  💡 D/E{de_val:.2f}{'は低水準で実質無借金に近い' if de_val < 0.3 else 'は標準的な負債水準' if de_val < 0.8 else 'は高めの負債水準'}")
        else:
            c2 = 2 if de_val < 0.3 else (1 if de_val < 0.8 else 0)
            c_details.append(f"D/Eレシオ: {de_val:.2f} (業種中央値なし) → {c2}/2点")
            c_details.append(f"  💡 D/E{de_val:.2f}{'は低水準で実質無借金に近い' if de_val < 0.3 else 'は標準的な負債水準' if de_val < 0.8 else 'は高めの負債水準。利益で返済をカバーできるかの確認が必要'}")
    else:
        c2 = 0
        c_details.append("D/Eレシオ: データなし → 0/2点")
        c_details.append("  💡 D/Eレシオデータが取得できず負債状況を評価できない")
    c_score += c2

    # C3: 自己資本比率改善 (0-1)
    eq_improving = row.get("equity_ratio_improving", False)
    c3 = 1 if eq_improving else 0
    c_score += c3
    c_details.append(f"自己資本比率改善: {'改善' if eq_improving else '悪化/横ばい'} → {c3}/1点")
    if eq_improving:
        c_details.append("  💡 自己資本比率が改善傾向にあり、利益蓄積で財務体質が着実に強化されている")
    else:
        c_details.append("  💡 自己資本比率が横ばいまたは悪化。借入増加や利益減少により財務体質の改善が進んでいない")

    sections.append(ScoreDetail("財務の保守性", "Conservative Financing", c_score, 5, c_details))

    # === D. フリーキャッシュフロー (0-4) ===
    d_score = 0
    d_details = []

    # D1: FCF黒字年数 (0-3)
    fcf_pos = _safe_int(row.get("fcf_positive_years"), 0)
    if fcf_pos >= 6:
        d1 = 3
    elif fcf_pos >= 5:
        d1 = 2
    elif fcf_pos >= 4:
        d1 = 1
    else:
        d1 = 0
    d_score += d1
    d_details.append(f"FCF黒字年数: {fcf_pos}年 → {d1}/3点")
    if d1 == 3:
        d_details.append(f"  💡 {fcf_pos}年連続でFCF黒字。営業活動で稼いだキャッシュが設備投資を上回り続けており、株主還元・成長投資に充てる余力が十分")
        strengths.append(f"FCF {fcf_pos}年連続黒字")
    elif d1 >= 1:
        d_details.append(f"  💡 {fcf_pos}年のFCF黒字はある程度のキャッシュ創出力を示すが、毎年安定黒字とは言えない。設備投資の波や事業サイクルの影響")
    else:
        d_details.append(f"  💡 FCF黒字が{fcf_pos}年のみで不安定。大型設備投資が続いているか、本業のキャッシュ創出力に課題がある可能性")
        if fcf_pos < 3:
            concerns.append("FCFが不安定")

    # D2: FCF成長 (0-1)
    fcf_growing = row.get("fcf_growing", False)
    d2 = 1 if fcf_growing else 0
    d_score += d2
    d_details.append(f"FCF成長: {'成長' if fcf_growing else '減少/横ばい'} → {d2}/1点")
    if fcf_growing:
        d_details.append("  💡 FCFが成長傾向にあり、事業規模拡大とともにキャッシュ創出力も向上。バフェットの言う「オーナー利益」が増えている状態")
    else:
        d_details.append("  💡 FCFが伸びていない。売上成長に見合ったキャッシュ創出ができていないか、投資フェーズで一時的にFCFが圧迫されている可能性")

    sections.append(ScoreDetail("フリーキャッシュフロー", "Owner Earnings", d_score, 4, d_details))

    # === E. 成長性 (0-4) ===
    e_score = 0
    e_details = []

    # E1: EPS CAGR 5年 (0-2)
    eps_cagr_5y = _safe_float(row.get("eps_cagr_5y"))
    if eps_cagr_5y is not None:
        eps_cagr_pct = eps_cagr_5y * 100 if abs(eps_cagr_5y) < 5 else eps_cagr_5y
        if eps_cagr_pct >= 15:
            e1 = 2
        elif eps_cagr_pct >= 7:
            e1 = 1
        else:
            e1 = 0
        e_details.append(f"EPS CAGR 5年: {eps_cagr_pct:.1f}% → {e1}/2点")
        if eps_cagr_pct >= 15:
            e_details.append(f"  💡 5年間で年平均{eps_cagr_pct:.1f}%の利益成長は優秀。事業拡大と利益率改善が両立した高成長企業")
            strengths.append(f"EPS年平均成長率 {eps_cagr_pct:.1f}%")
        elif eps_cagr_pct >= 7:
            e_details.append(f"  💡 年平均{eps_cagr_pct:.1f}%の利益成長は堅調。市場平均を上回るペースで利益が拡大している")
        elif eps_cagr_pct >= 0:
            e_details.append(f"  💡 年平均{eps_cagr_pct:.1f}%の成長はインフレ率程度。実質的な利益成長は限定的")
        else:
            e_details.append(f"  💡 EPS CAGRが{eps_cagr_pct:.1f}%とマイナス成長。利益が縮小傾向にあり構造的な問題の可能性")
    else:
        e1 = 0
        e_details.append("EPS CAGR 5年: データなし → 0/2点")
        e_details.append("  💡 5年分のEPSデータが不足しており成長率を計算できない")
    e_score += e1

    # E2: 売上CAGR 5年 (0-1)
    rev_cagr = _safe_float(row.get("revenue_cagr_5y"))
    if rev_cagr is not None:
        rev_cagr_pct = rev_cagr * 100 if abs(rev_cagr) < 5 else rev_cagr
        if rev_cagr_pct >= 5:
            e2 = 1
        else:
            e2 = 0
        e_details.append(f"売上CAGR 5年: {rev_cagr_pct:.1f}% → {e2}/1点")
        if rev_cagr_pct >= 5:
            e_details.append(f"  💡 年平均{rev_cagr_pct:.1f}%の売上成長は市場拡大または市場シェア獲得を反映。トップラインの成長が利益成長の土台になる")
        elif rev_cagr_pct >= 0:
            e_details.append(f"  💡 売上成長率{rev_cagr_pct:.1f}%は緩やか。成熟市場で安定しているとも、成長余地が限られるとも解釈できる")
        else:
            e_details.append(f"  💡 売上が縮小傾向（{rev_cagr_pct:.1f}%）。市場縮小や競争力低下の兆候であり長期保有には注意が必要")
    else:
        e2 = 0
        e_details.append("売上CAGR 5年: データなし → 0/1点")
        e_details.append("  💡 5年分の売上データが不足しており成長率を計算できない")
    e_score += e2

    # E3: BPS成長 (0-1)
    bps_inc = _safe_int(row.get("bps_increase_years"), 0)
    e3 = 1 if bps_inc >= 4 else 0
    e_score += e3
    e_details.append(f"BPS増加年数: {bps_inc}年 → {e3}/1点")
    if bps_inc >= 4:
        e_details.append(f"  💡 BPS（1株純資産）が{bps_inc}年増加。内部留保の蓄積で企業の本源的価値が着実に成長している")
    else:
        e_details.append(f"  💡 BPS増加が{bps_inc}年のみ。利益蓄積のペースが遅いか、大型投資・減損・自社株買いの影響の可能性")

    sections.append(ScoreDetail("成長性", "Growth", e_score, 4, e_details))

    # === F. 割安度 (0-3) — 業種内相対評価 ===
    f_score = 0
    f_details = []

    per = _safe_float(row.get("trailingPE")) or _safe_float(row.get("per"))
    pbr = _safe_float(row.get("priceToBook"))
    industry = row.get("industry", "")

    # 業種別中央値を取得
    ind_per_med = None
    ind_pbr_med = None
    if industry_medians is not None and industry:
        med_row = industry_medians[industry_medians["industry"] == industry]
        if len(med_row) > 0:
            ind_per_med = _safe_float(med_row.iloc[0].get("trailingPE_median"))
            ind_pbr_med = _safe_float(med_row.iloc[0].get("priceToBook_median"))

    # F1: PER — 業種中央値との比較 (0-1)
    if per is not None and per > 0:
        if ind_per_med and ind_per_med > 0:
            per_ratio = per / ind_per_med
            if per_ratio < 0.8:
                f1 = 1  # 業種中央値より20%以上割安
            else:
                f1 = 0
            f_details.append(
                f"PER: {per:.1f} (業種中央値: {ind_per_med:.1f}, 比率: {per_ratio:.2f}) → {f1}/1点"
            )
            if per_ratio < 0.8:
                f_details.append(f"  💡 PER{per:.1f}倍は業種中央値{ind_per_med:.1f}倍の{per_ratio:.0%}水準。市場が利益の持続性を過小評価しているか、何らかの懸念が織り込まれている可能性")
            elif per_ratio <= 1.2:
                f_details.append(f"  💡 PER{per:.1f}倍は業種中央値並み。市場は同業他社と同程度の成長・リスクを見込んでおり、特段の割安感はない")
            else:
                f_details.append(f"  💡 PER{per:.1f}倍は業種中央値の{per_ratio:.0%}で割高寄り。高い成長期待が織り込まれており、期待を下回ると株価下落リスクが高い")
        else:
            f1 = 1 if per < 16 else 0
            f_details.append(f"PER: {per:.1f} (業種中央値なし, 全体基準<16) → {f1}/1点")
            if per < 16:
                f_details.append(f"  💡 PER{per:.1f}倍は市場平均（約16倍）を下回り相対的に割安")
            else:
                f_details.append(f"  💡 PER{per:.1f}倍は市場平均並みかそれ以上で割安感は乏しい")
    else:
        f1 = 0
        f_details.append("PER: データなし → 0/1点")
        f_details.append("  💡 PERデータが取得できず割安度を判断できない。赤字企業の場合PERは算出不可")
    f_score += f1

    # F2: PEG — 成長対比の割安度 (0-1)
    if per is not None and per > 0 and eps_cagr_5y is not None:
        growth_rate = eps_cagr_5y * 100 if abs(eps_cagr_5y) < 5 else eps_cagr_5y
        if growth_rate > 0:
            peg = per / growth_rate
            f2 = 1 if peg < 2 else 0
            f_details.append(f"PEG: {peg:.2f} (PER {per:.1f} ÷ EPS成長率 {growth_rate:.1f}%) → {f2}/1点")
            if peg < 1:
                f_details.append(f"  💡 PEG{peg:.2f}は1未満で成長率対比で非常に割安。高成長が株価に十分反映されていない状態")
            elif peg < 2:
                f_details.append(f"  💡 PEG{peg:.2f}は適正〜割安圏。利益成長のペースに対して株価は妥当な範囲")
            else:
                f_details.append(f"  💡 PEG{peg:.2f}は成長率に対して株価が高い。将来の成長鈍化リスクを考慮する必要がある")
        else:
            f2 = 0
            f_details.append("PEG: EPS成長率≤0 → 0/1点")
            f_details.append("  💡 EPS成長率がゼロ以下のためPEGを計算できない。成長なき状態では割安度をPEGで測る意味がない")
    else:
        f2 = 0
        f_details.append("PEG: データ不足 → 0/1点")
        f_details.append("  💡 PERまたはEPS成長率データが不足しておりPEGを計算できない")
    f_score += f2

    # F3: PBR — 業種中央値との比較 (0-1)
    if pbr is not None and pbr > 0:
        if ind_pbr_med and ind_pbr_med > 0:
            pbr_ratio = pbr / ind_pbr_med
            if pbr_ratio < 0.8:
                f3 = 1  # 業種中央値より20%以上割安
            else:
                f3 = 0
            f_details.append(
                f"PBR: {pbr:.2f} (業種中央値: {ind_pbr_med:.2f}, 比率: {pbr_ratio:.2f}) → {f3}/1点"
            )
            if pbr_ratio < 0.8:
                f_details.append(f"  💡 PBR{pbr:.2f}倍は業種中央値{ind_pbr_med:.2f}倍を大幅に下回る。純資産対比で割安だが、成長期待の低さや隠れたリスクが反映されている可能性も")
            elif pbr_ratio <= 1.5:
                f_details.append(f"  💡 PBR{pbr:.2f}倍は業種中央値並み。純資産対比では標準的な評価水準")
            else:
                f_details.append(f"  💡 PBR{pbr:.2f}倍は業種中央値の{pbr_ratio:.1f}倍で割高。ブランド価値や無形資産を市場が高く評価しているか、過熱気味の可能性")
            if pbr_ratio > 3.0:
                concerns.append(f"PBRが業種中央値の{pbr_ratio:.1f}倍（割高）")
        else:
            f3 = 1 if pbr < 1.5 else 0
            f_details.append(f"PBR: {pbr:.2f} (業種中央値なし, 全体基準<1.5) → {f3}/1点")
            if pbr < 1.0:
                f_details.append(f"  💡 PBR{pbr:.2f}倍は1倍割れ。理論上、解散価値を下回る株価であり割安だが、市場が将来の業績悪化を見込んでいる可能性も")
            elif pbr < 1.5:
                f_details.append(f"  💡 PBR{pbr:.2f}倍はやや割安水準。純資産に対して大きなプレミアムは乗っていない")
            else:
                f_details.append(f"  💡 PBR{pbr:.2f}倍は純資産対比で割高。高い収益力やブランド価値への期待が株価に反映されている")
    else:
        f3 = 0
        f_details.append("PBR: データなし → 0/1点")
        f_details.append("  💡 PBRデータが取得できず純資産対比の割安度を判断できない")
    f_score += f3

    sections.append(ScoreDetail("割安度", "Margin of Safety", f_score, 3, f_details))

    # === G. 株主還元の一貫性 (0-2) ===
    g_score = 0
    g_details = []

    # G1: 連続配当 (0-1)
    dps_pos = _safe_int(row.get("dps_positive_years"), 0)
    g1 = 1 if dps_pos >= n_years and n_years >= 4 else 0
    g_score += g1
    g_details.append(f"連続配当: {dps_pos}/{n_years}年 → {g1}/1点")
    if g1 == 1:
        g_details.append(f"  💡 {dps_pos}年連続で配当を実施。安定したキャッシュフローに基づく株主還元姿勢があり、経営陣が利益を株主と共有する意思を示している")
        strengths.append(f"配当 {dps_pos}年連続")
    else:
        if dps_pos == 0:
            g_details.append("  💡 配当実績なし。成長投資に資金を振り向けるグロース企業か、配当に回す余力がない企業かの見極めが必要")
        else:
            g_details.append(f"  💡 配当実績は{dps_pos}/{n_years}年。途中で無配の年があり、業績悪化時に配当を維持する体力に不安が残る")

    # G2: 増配傾向 (0-1)
    dps_inc = _safe_int(row.get("dps_increase_years"), 0)
    g2 = 1 if dps_inc >= 3 else 0
    g_score += g2
    g_details.append(f"増配年数: {dps_inc}年 → {g2}/1点")
    if dps_inc >= 4:
        g_details.append(f"  💡 {dps_inc}年連続増配は利益成長と株主還元強化の両立を示す。経営陣が将来の業績に自信を持っている証拠")
        strengths.append(f"{dps_inc}年増配")
    elif dps_inc >= 3:
        g_details.append(f"  💡 {dps_inc}年の増配は株主還元の姿勢を示すが、長期連続増配の実績としてはまだ十分とは言えない")
    else:
        g_details.append(f"  💡 増配実績が{dps_inc}年のみ。配当は横ばいか減配の年があり、利益成長に見合った還元強化が進んでいない")

    sections.append(ScoreDetail("株主還元", "Shareholder Returns", g_score, 2, g_details))

    return BuffettReport(
        edinet_code=str(row.get("edinet_code", "")),
        company_name=str(row.get("name", row.get("company_name", ""))),
        industry=str(row.get("industry", "")),
        ticker=str(row.get("ticker", "")),
        sections=sections,
        strengths=strengths[:5],
        concerns=concerns[:5],
    )


def score_all(profiles: pd.DataFrame) -> list[BuffettReport]:
    """全企業をスコアリングする。"""
    # 業種別中央値を計算
    industry_medians = _compute_industry_medians(profiles)

    reports = []
    for _, row in profiles.iterrows():
        report = score_company(row, industry_medians)
        reports.append(report)
    return reports


def reports_to_dataframe(reports: list[BuffettReport]) -> pd.DataFrame:
    """レポートリストをDataFrameに変換（一覧表示用）。"""
    rows = []
    for r in reports:
        row = {
            "edinet_code": r.edinet_code,
            "企業名": r.company_name,
            "業種": r.industry,
            "ティッカー": r.ticker,
            "総合スコア": r.score_30,
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
        "trailingPE": "trailingPE_median",
        "priceToBook": "priceToBook_median",
        "om_mean": "om_mean_median",
        "equity_ratio": "equity_ratio_median",
        "debtToEquity": "debtToEquity_median",
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
