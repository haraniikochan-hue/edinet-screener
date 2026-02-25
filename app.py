"""
EDINET 銘柄スクリーニングツール — Streamlit アプリ

機能:
  1. 企業診断レポート（エビデンスベーススコアリング + 業種比較 + 競合比較）
  2. マルチファクタースクリーナー
  3. ランキング一覧
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# lib を import パスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.evidence_scorer import EvidenceReport, reports_to_dataframe, score_all, score_company
from lib.data_loader import (
    build_company_profiles,
    get_company_timeseries,
    get_industry_benchmark,
    get_industry_percentile,
    get_peer_companies,
    load_companies,
    load_stock_prices,
)

# ─────────────────────────────────────
# ページ設定
# ─────────────────────────────────────
st.set_page_config(
    page_title="EDINET 銘柄スクリーナー",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────
# Apple-like カスタム CSS
# ─────────────────────────────────────
_CUSTOM_CSS = """
<style>
/* --- Global --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display',
                 'Segoe UI', Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}

/* Main container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* --- Sidebar --- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fafafa 0%, #f5f5f7 100%);
    border-right: 1px solid #e5e5e7;
}
section[data-testid="stSidebar"] .stRadio > label {
    font-weight: 500;
}

/* --- Metric cards --- */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e5e7;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
    transition: box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
[data-testid="stMetric"] label {
    font-size: 0.75rem;
    font-weight: 500;
    color: #86868b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1d1d1f;
}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem;
}

/* --- Dataframes / tables --- */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e5e5e7;
}

/* --- Expander --- */
.streamlit-expanderHeader {
    font-weight: 500;
    color: #1d1d1f;
    background: #fafafa;
    border-radius: 12px;
}

/* --- Divider --- */
hr {
    border: none;
    border-top: 1px solid #e5e5e7;
    margin: 2rem 0;
}

/* --- Section headers --- */
.section-header {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1d1d1f;
    margin-bottom: 1rem;
    letter-spacing: -0.01em;
}

.section-sub {
    font-size: 0.85rem;
    color: #86868b;
    margin-top: -0.8rem;
    margin-bottom: 1.2rem;
}

/* --- Rank badge --- */
.rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    font-size: 1.25rem;
    font-weight: 700;
    color: white;
}
.rank-S { background: linear-gradient(135deg, #34d399, #059669); }
.rank-A { background: linear-gradient(135deg, #60a5fa, #2563eb); }
.rank-B { background: linear-gradient(135deg, #fbbf24, #d97706); }
.rank-C { background: linear-gradient(135deg, #fb923c, #ea580c); }
.rank-D { background: linear-gradient(135deg, #f87171, #dc2626); }

/* --- Score ring --- */
.score-ring {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 4px solid #e5e5e7;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1d1d1f;
}

/* --- Hero header --- */
.hero-header {
    padding: 1.5rem 0;
}
.hero-name {
    font-size: 2rem;
    font-weight: 700;
    color: #1d1d1f;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.2;
}
.hero-meta {
    font-size: 0.95rem;
    color: #86868b;
    margin-top: 0.25rem;
}

/* --- Comparison table --- */
.comp-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e5e5e7;
    font-size: 0.9rem;
}
.comp-table th {
    background: #fafafa;
    font-weight: 600;
    color: #1d1d1f;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #e5e5e7;
}
.comp-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #f0f0f2;
    color: #1d1d1f;
}
.comp-table tr:last-child td {
    border-bottom: none;
}
.comp-table tr:hover td {
    background: #f5f5f7;
}
.comp-table .self-row td {
    background: #eff6ff;
    font-weight: 600;
}
.comp-table .pctile-good { color: #059669; font-weight: 600; }
.comp-table .pctile-mid { color: #d97706; }
.comp-table .pctile-low { color: #dc2626; }

/* --- Score bar --- */
.score-bar-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}
.score-bar-label {
    width: 120px;
    font-size: 0.85rem;
    font-weight: 500;
    color: #1d1d1f;
}
.score-bar-track {
    flex: 1;
    height: 8px;
    background: #e5e5e7;
    border-radius: 4px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}
.score-bar-value {
    width: 60px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #86868b;
    text-align: right;
}

/* --- Strength / Concern pills --- */
.pill-container { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.pill {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    line-height: 1.4;
}
.pill-green { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.pill-red { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

/* --- Tabs --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #f5f5f7;
    border-radius: 10px;
    padding: 3px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
}

/* --- Text input --- */
.stTextInput input {
    border-radius: 12px;
    border: 1px solid #d1d1d6;
    padding: 12px 16px;
    font-size: 1rem;
}
.stTextInput input:focus {
    border-color: #0071e3;
    box-shadow: 0 0 0 3px rgba(0,113,227,0.15);
}

/* --- Selectbox --- */
.stSelectbox > div > div {
    border-radius: 12px;
}
</style>
"""

st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────
# Plotly テーマ
# ─────────────────────────────────────
_PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, sans-serif", color="#1d1d1f"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="#f0f0f2", zerolinecolor="#e5e5e7"),
    yaxis=dict(gridcolor="#f0f0f2", zerolinecolor="#e5e5e7"),
    margin=dict(l=40, r=20, t=48, b=32),
)

# カラーパレット
_C = {
    "blue": "#0071e3",
    "blue_light": "rgba(0,113,227,0.12)",
    "green": "#34c759",
    "green_dark": "#059669",
    "red": "#ff3b30",
    "orange": "#ff9500",
    "purple": "#af52de",
    "teal": "#5ac8fa",
    "indigo": "#5856d6",
    "pink": "#ff2d55",
    "gray": "#86868b",
    "gray_light": "#e5e5e7",
}


# ─────────────────────────────────────
# フォーマットヘルパー
# ─────────────────────────────────────
def _is_valid_str(val) -> bool:
    """値が有効な文字列かどうか（None, NaN, NA, 空文字列を除外）。"""
    if val is None:
        return False
    s = str(val).strip()
    return s != "" and s.lower() not in ("nan", "none", "<na>")


def _fmt_oku(val) -> str:
    if val is None:
        return "-"
    try:
        if pd.isna(val):
            return "-"
    except (ValueError, TypeError):
        pass
    try:
        v = float(val)
    except (ValueError, TypeError):
        return "-"
    if np.isnan(v):
        return "-"
    if abs(v) >= 1e12:
        return f"{v / 1e12:.2f} 兆円"
    if abs(v) >= 1e8:
        return f"{v / 1e8:.0f} 億円"
    return f"{v / 1e6:.0f} 百万円"


def _fmt_pct(val, digits: int = 1, already_pct: bool = False) -> str:
    if val is None:
        return "-"
    try:
        if pd.isna(val):
            return "-"
    except (ValueError, TypeError):
        pass
    try:
        v = float(val)
    except (ValueError, TypeError):
        return "-"
    if np.isnan(v):
        return "-"
    if not already_pct and abs(v) < 1:
        v *= 100
    return f"{v:.{digits}f}%"


def _fmt_float(val, suffix: str = "", digits: int = 2) -> str:
    if val is None:
        return "-"
    try:
        if pd.isna(val):
            return "-"
    except (ValueError, TypeError):
        pass
    try:
        v = float(val)
    except (ValueError, TypeError):
        return "-"
    if np.isnan(v):
        return "-"
    return f"{v:.{digits}f}{suffix}"


def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (ValueError, TypeError):
        pass
    try:
        f = float(val)
        return None if np.isnan(f) else f
    except (ValueError, TypeError):
        return None


# ─────────────────────────────────────
# Section 1: KPI ダッシュボード
# ─────────────────────────────────────
def _render_kpi_dashboard(row: pd.Series, benchmark: dict) -> None:
    st.markdown('<p class="section-header">Overview</p>', unsafe_allow_html=True)

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        st.metric("時価総額", _fmt_oku(row.get("marketCap")))
    with r1c2:
        st.metric("売上高", _fmt_oku(row.get("revenue")))
    with r1c3:
        st.metric("純利益", _fmt_oku(row.get("net_income")))
    with r1c4:
        roe = _safe_float(row.get("roe"))
        roe_bm = _safe_float(benchmark.get("roe_median"))
        delta = None
        if roe is not None and roe_bm is not None:
            delta = f"{(roe - roe_bm) * 100:+.1f}%pt"
        st.metric("ROE", _fmt_pct(roe), delta=delta)

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        pbr = _safe_float(row.get("priceToBook"))
        pbr_bm = _safe_float(benchmark.get("priceToBook_median"))
        delta = None
        if pbr is not None and pbr_bm is not None:
            delta = f"{pbr - pbr_bm:+.2f}x"
        st.metric("PBR", _fmt_float(pbr, "x"), delta=delta)
    with r2c2:
        dy = _safe_float(row.get("dividendYield"))
        dy_bm = _safe_float(benchmark.get("dividendYield_median"))
        delta = None
        if dy is not None and dy_bm is not None:
            delta = f"{(dy - dy_bm) * 100:+.1f}%pt"
        st.metric("配当利回り", _fmt_pct(dy, 2) if dy is not None else "-", delta=delta)
    with r2c3:
        fpe = _safe_float(row.get("forwardPE"))
        st.metric("予想PER", _fmt_float(fpe, "x", 1) if fpe is not None else "-")
    with r2c4:
        eq = _safe_float(row.get("equity_ratio"))
        eq_bm = _safe_float(benchmark.get("equity_ratio_median"))
        delta = None
        if eq is not None and eq_bm is not None:
            delta = f"{(eq - eq_bm) * 100:+.1f}%pt"
        st.metric("自己資本比率", _fmt_pct(eq), delta=delta)

    # 株価リターン + Beta + 格付
    ret1 = _safe_float(row.get("return_1y"))
    ret3 = _safe_float(row.get("return_3y"))
    beta = _safe_float(row.get("beta"))
    cr = row.get("credit_rating")
    has_cr = _is_valid_str(cr)

    if ret1 is not None or ret3 is not None or beta is not None or has_cr:
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        with r3c1:
            if ret1 is not None:
                st.metric("1年リターン", f"{ret1 * 100:+.1f}%")
        with r3c2:
            if ret3 is not None:
                st.metric("3年リターン", f"{ret3 * 100:+.1f}%")
        with r3c3:
            if beta is not None:
                st.metric("Beta", f"{beta:.2f}")
        with r3c4:
            if has_cr:
                st.metric("信用格付", str(cr))


# ─────────────────────────────────────
# Section 2: 業種内比較（HTML テーブル）
# ─────────────────────────────────────
def _render_industry_comparison(
    row: pd.Series,
    benchmark: dict,
    industry: str,
    all_profiles: pd.DataFrame,
    industry_col: str = "industry",
) -> None:
    n = benchmark.get("company_count", 0)
    st.markdown(f'<p class="section-header">業種内ポジション</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">{industry} — {n}社中の位置づけ</p>', unsafe_allow_html=True)

    metrics = [
        ("ROE", "roe", "roe_median", "ratio"),
        ("営業利益率", "operating_margin", "operating_margin_median", "ratio"),
        ("純利益率", "net_margin", "net_margin_median", "ratio"),
        ("自己資本比率", "equity_ratio", "equity_ratio_median", "ratio"),
        ("配当利回り", "dividendYield", "dividendYield_median", "ratio"),
        ("PBR", "priceToBook", "priceToBook_median", "x"),
        ("予想PER", "forwardPE", "forwardPE_median", "x"),
    ]

    def _fv(val, fmt_type: str) -> str:
        if val is None:
            return "-"
        if fmt_type == "ratio":
            return f"{val * 100:.1f}%" if abs(val) < 1 else f"{val:.1f}%"
        if fmt_type == "pct":
            return f"{val:.1f}%"
        if fmt_type == "x":
            return f"{val:.2f}x"
        return f"{val:.2f}"

    html = '<table class="comp-table"><tr><th>指標</th><th>自社</th><th>業種中央値</th><th>業種内順位</th></tr>'
    for label, col, bm_key, fmt_type in metrics:
        self_val = _safe_float(row.get(col))
        bm_val = _safe_float(benchmark.get(bm_key))
        pctile = get_industry_percentile(
            self_val if self_val is not None else float("nan"),
            col, industry, all_profiles, industry_col=industry_col,
        )
        if pctile is not None:
            rank_num = 100 - pctile
            if rank_num <= 25:
                cls = "pctile-good"
            elif rank_num <= 50:
                cls = "pctile-mid"
            else:
                cls = "pctile-low"
            rank_str = f'<span class="{cls}">上位 {rank_num:.0f}%</span>'
        else:
            rank_str = "-"

        html += f'<tr><td>{label}</td><td><strong>{_fv(self_val, fmt_type)}</strong></td>'
        html += f'<td>{_fv(bm_val, fmt_type)}</td><td>{rank_str}</td></tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────
# Section 3: 主要競合比較（HTML テーブル）
# ─────────────────────────────────────
def _render_peer_comparison(
    peers_df: pd.DataFrame,
    self_row: pd.Series,
    report_map: dict[str, EvidenceReport],
) -> None:
    st.markdown('<p class="section-header">類似企業比較</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">同業種内で事業規模・収益性・財務構造が類似する企業</p>', unsafe_allow_html=True)

    if len(peers_df) == 0:
        st.info("類似する同業種企業が見つかりません")
        return

    rank_bg = {"S": "#34c759", "A": "#0071e3", "B": "#ff9500", "C": "#ff6723", "D": "#ff3b30"}

    def _row_html(r, is_self: bool = False) -> str:
        code = str(r.get("edinet_code", ""))
        name = str(r.get("name", ""))
        rep = report_map.get(code)
        score = f"{rep.score_total:.0f}" if rep else "-"
        rank = rep.rank if rep else "-"
        rc = rank_bg.get(rank, "#86868b")
        rank_html = f'<span style="background:{rc};color:#fff;padding:2px 8px;border-radius:6px;font-size:0.75rem;font-weight:600">{rank}</span>'

        mcap = _safe_float(r.get("marketCap"))
        roe = _safe_float(r.get("roe"))
        om = _safe_float(r.get("operating_margin"))
        dy = _safe_float(r.get("dividendYield"))
        pbr = _safe_float(r.get("priceToBook"))
        ret1 = _safe_float(r.get("return_1y"))

        cls = ' class="self-row"' if is_self else ''
        cells = f'<td><strong>{name}</strong></td>'
        cells += f'<td>{_fmt_oku(mcap)}</td>'
        cells += f'<td>{score}/30</td>'
        cells += f'<td>{rank_html}</td>'
        cells += f'<td>{_fmt_pct(roe)}</td>'
        cells += f'<td>{_fmt_pct(om)}</td>'
        cells += f'<td>{dy * 100:.1f}%</td>' if dy is not None else '<td>-</td>'
        cells += f'<td>{_fmt_float(pbr, "x")}</td>'
        cells += f'<td>{ret1*100:+.1f}%</td>' if ret1 is not None else '<td>-</td>'
        return f'<tr{cls}>{cells}</tr>'

    html = '<table class="comp-table">'
    html += '<tr><th>企業名</th><th>時価総額</th><th>スコア</th><th>ランク</th>'
    html += '<th>ROE</th><th>営業利益率</th><th>配当利回り</th><th>PBR</th><th>1年リターン</th></tr>'
    html += _row_html(self_row, is_self=True)
    for _, peer in peers_df.iterrows():
        html += _row_html(peer)
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────
# Section 4: スコアリング詳細
# ─────────────────────────────────────
def _render_scoring_detail(report: EvidenceReport, benchmark: dict) -> None:
    st.markdown('<p class="section-header">Evidence Score</p>', unsafe_allow_html=True)

    col_chart, col_detail = st.columns([1, 1])

    with col_chart:
        categories = [s.name for s in report.sections]
        values = [s.pct * 100 for s in report.sections]
        values_closed = values + [values[0]]
        categories_closed = categories + [categories[0]]

        fig = go.Figure(data=go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(0, 113, 227, 0.08)",
            line=dict(color=_C["blue"], width=2.5),
            marker=dict(size=7, color=_C["blue"]),
        ))
        fig.update_layout(
            **_PLOTLY_LAYOUT,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True, range=[0, 100], ticksuffix="%",
                    gridcolor="#e5e5e7", linecolor="#e5e5e7",
                    tickfont=dict(size=10, color="#86868b"),
                ),
                angularaxis=dict(
                    gridcolor="#e5e5e7", linecolor="#e5e5e7",
                    tickfont=dict(size=12, color="#1d1d1f", weight=500),
                ),
            ),
            showlegend=False,
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_detail:
        bar_colors = [_C["blue"], _C["green"], _C["purple"], _C["orange"], _C["teal"], _C["indigo"]]
        bars_html = ""
        for i, s in enumerate(report.sections):
            pct = int(s.pct * 100)
            color = bar_colors[i % len(bar_colors)]
            bars_html += f"""
            <div class="score-bar-container">
                <div class="score-bar-label">{s.name}</div>
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:{pct}%;background:{color}"></div>
                </div>
                <div class="score-bar-value">{s.score}/{s.max_score}</div>
            </div>"""
        st.markdown(bars_html, unsafe_allow_html=True)

    # 強み・懸念
    col_s, col_c = st.columns(2)
    with col_s:
        st.markdown('<p class="section-header" style="font-size:1rem">Strengths</p>', unsafe_allow_html=True)
        pills = ""
        for s in report.strengths:
            pills += f'<span class="pill pill-green">{s}</span>'
        if not report.strengths:
            pills = '<span class="pill pill-green">特筆すべき強みなし</span>'
        st.markdown(f'<div class="pill-container">{pills}</div>', unsafe_allow_html=True)

    with col_c:
        st.markdown('<p class="section-header" style="font-size:1rem">Concerns</p>', unsafe_allow_html=True)
        pills = ""
        for c in report.concerns:
            pills += f'<span class="pill pill-red">{c}</span>'
        if not report.concerns:
            pills = '<span class="pill pill-green">特筆すべき懸念なし</span>'
        st.markdown(f'<div class="pill-container">{pills}</div>', unsafe_allow_html=True)

    with st.expander("全スコアリング項目を表示"):
        for s in report.sections:
            st.markdown(f"**{s.name}** ({s.name_en}) — {s.score}/{s.max_score}")
            for d in s.details:
                st.markdown(f"- {d}")
            st.markdown("")


# ─────────────────────────────────────
# Section 5: 時系列チャート
# ─────────────────────────────────────
def _render_timeseries(edinet_code: str) -> None:
    fin_ts, ratios_ts = get_company_timeseries(edinet_code)
    if len(ratios_ts) < 2:
        st.info("時系列データが不足しています")
        return

    def _line(df, col, title, color, pct=False, hlines=None):
        data = df[["fiscal_year", col]].dropna().copy()
        if len(data) == 0:
            return
        data[col] = pd.to_numeric(data[col], errors="coerce")
        y = data[col] * 100 if pct else data[col]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data["fiscal_year"], y=y,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
        ))
        if hlines:
            for yv, c, label in hlines:
                fig.add_hline(y=yv, line_dash="dot", line_color=c, line_width=1,
                              annotation_text=label, annotation_font_color=c, annotation_font_size=10)
        fig.update_layout(**_PLOTLY_LAYOUT, title=dict(text=title, font=dict(size=14, weight=600)), height=280)
        st.plotly_chart(fig, use_container_width=True)

    def _bar(df, col, title, color="#0071e3", scale=1):
        data = df[["fiscal_year", col]].dropna().copy()
        if len(data) == 0:
            return
        data[col] = pd.to_numeric(data[col], errors="coerce")
        y = data[col] / scale
        colors = [_C["green"] if v >= 0 else _C["red"] for v in y]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data["fiscal_year"], y=y,
            marker_color=colors, marker_line_width=0,
        ))
        fig.update_layout(**_PLOTLY_LAYOUT, title=dict(text=title, font=dict(size=14, weight=600)),
                          height=280, bargap=0.3)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-header">Performance History</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if "roe" in ratios_ts.columns:
            _line(ratios_ts, "roe", "ROE (%)", _C["blue"], pct=True,
                  hlines=[(15, _C["green_dark"], "15%"), (10, _C["orange"], "10%")])
    with c2:
        if "eps" in ratios_ts.columns:
            _bar(ratios_ts, "eps", "EPS (円)")

    c3, c4 = st.columns(2)
    with c3:
        if "operating_margin" in ratios_ts.columns:
            _line(ratios_ts, "operating_margin", "営業利益率 (%)", _C["orange"], pct=True)
    with c4:
        if "fcf" in ratios_ts.columns:
            _bar(ratios_ts, "fcf", "FCF (十億円)", scale=1e9)

    c5, c6 = st.columns(2)
    with c5:
        if "revenue" in fin_ts.columns:
            _bar(fin_ts, "revenue", "売上高 (十億円)", scale=1e9)
    with c6:
        if "bps" in ratios_ts.columns:
            _line(ratios_ts, "bps", "BPS (円)", _C["purple"])

    c7, c8 = st.columns(2)
    with c7:
        if "dividend_per_share" in ratios_ts.columns:
            _bar(ratios_ts, "dividend_per_share", "1株配当 (円)")
    with c8:
        if "equity_ratio" in ratios_ts.columns:
            _line(ratios_ts, "equity_ratio", "自己資本比率 (%)", _C["teal"], pct=True)


# ─────────────────────────────────────
# メインレポート描画
# ─────────────────────────────────────
def _render_report(
    report: EvidenceReport,
    all_profiles: pd.DataFrame,
    report_map: dict[str, EvidenceReport],
) -> None:
    rank_cls = f"rank-{report.rank}"

    self_rows = all_profiles[all_profiles["edinet_code"] == report.edinet_code]
    if len(self_rows) == 0:
        st.error("企業データが見つかりません")
        return
    self_row = self_rows.iloc[0]

    # 業種: yahooquery industry_yf (127カテゴリ) を優先、なければ EDINET industry (33カテゴリ)
    industry_yf_raw = self_row.get("industry_yf", "")
    industry_edinet_raw = self_row.get("industry", "")
    industry_yf = str(industry_yf_raw).strip() if _is_valid_str(industry_yf_raw) else ""
    industry_edinet = str(industry_edinet_raw).strip() if _is_valid_str(industry_edinet_raw) else ""
    has_yf = bool(industry_yf)

    if has_yf:
        industry_display = industry_yf
        industry_col = "industry_yf"
        benchmark = get_industry_benchmark(industry_yf, all_profiles, industry_col="industry_yf")
    elif industry_edinet:
        industry_display = industry_edinet
        industry_col = "industry"
        benchmark = get_industry_benchmark(industry_edinet, all_profiles)
    else:
        industry_display = "不明"
        industry_col = "industry"
        benchmark = get_industry_benchmark("", all_profiles)

    # Hero header — EDINET業種 + yahooquery業種 の両方表示
    meta_parts = []
    if industry_edinet:
        meta_parts.append(industry_edinet)
    if has_yf:
        meta_parts.append(industry_yf)
    ticker_str = str(report.ticker) if _is_valid_str(report.ticker) else ""
    if ticker_str:
        meta_parts.append(ticker_str)
    meta_parts.append(f"{report.score_total:.0f}/30 pts")
    meta_str = "  ·  ".join(meta_parts)

    hero = f"""
    <div class="hero-header">
        <div style="display:flex;align-items:center;gap:20px">
            <div class="rank-badge {rank_cls}">{report.rank}</div>
            <div>
                <p class="hero-name">{report.company_name}</p>
                <p class="hero-meta">{meta_str}</p>
            </div>
        </div>
    </div>
    """
    st.markdown(hero, unsafe_allow_html=True)
    st.divider()

    _render_kpi_dashboard(self_row, benchmark)
    st.divider()
    _render_industry_comparison(self_row, benchmark, industry_display, all_profiles, industry_col=industry_col)
    st.divider()

    peers = get_peer_companies(
        report.edinet_code, industry_display, all_profiles, n=5, industry_col=industry_col,
    )
    _render_peer_comparison(peers, self_row, report_map)
    st.divider()

    _render_scoring_detail(report, benchmark)
    st.divider()

    _render_timeseries(report.edinet_code)


# ─────────────────────────────────────
# データキャッシュ
# ─────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="データを読み込んでいます...")
def load_all_data():
    profiles = build_company_profiles()
    reports = score_all(profiles)
    df = reports_to_dataframe(reports)
    return profiles, reports, df


profiles, reports, score_df = load_all_data()
report_map: dict[str, EvidenceReport] = {r.edinet_code: r for r in reports}


# ─────────────────────────────────────
# サイドバー
# ─────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:8px 0 16px 0">
    <p style="font-size:1.25rem;font-weight:700;color:#1d1d1f;margin:0;letter-spacing:-0.02em">
        EDINET Screener
    </p>
    <p style="font-size:0.8rem;color:#86868b;margin:4px 0 0 0">Evidence-based stock analysis</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigate",
    ["企業診断", "スクリーナー", "ランキング"],
    label_visibility="collapsed",
)


# ─────────────────────────────────────
# ページ 1: 企業診断レポート
# ─────────────────────────────────────
if page == "企業診断":
    st.markdown("""
    <div style="padding:0.5rem 0 1.5rem 0">
        <p style="font-size:2rem;font-weight:700;color:#1d1d1f;margin:0;letter-spacing:-0.02em">
            企業診断レポート
        </p>
        <p style="font-size:0.95rem;color:#86868b;margin:4px 0 0 0">
            6軸30点満点のエビデンスベーススコアリングで企業を多角的に診断
        </p>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input("企業名を入力", placeholder="例: トヨタ、信越化学、キーエンス", label_visibility="collapsed")

    if search:
        matches = score_df[score_df["企業名"].str.contains(search, na=False)]
        if len(matches) == 0:
            st.warning("該当する企業が見つかりません")
        else:
            if len(matches) > 1:
                selected_name = st.selectbox(
                    f"{len(matches)} 件の候補", matches["企業名"].tolist()
                )
                selected_row = matches[matches["企業名"] == selected_name].iloc[0]
            else:
                selected_row = matches.iloc[0]

            code = selected_row["edinet_code"]
            report = report_map.get(code)
            if report:
                _render_report(report, profiles, report_map)
            else:
                st.error("レポートデータが見つかりません")


# ─────────────────────────────────────
# ページ 2: スクリーナー
# ─────────────────────────────────────
elif page == "スクリーナー":
    st.markdown("""
    <div style="padding:0.5rem 0 1.5rem 0">
        <p style="font-size:2rem;font-weight:700;color:#1d1d1f;margin:0;letter-spacing:-0.02em">
            マルチファクタースクリーナー
        </p>
    </div>
    """, unsafe_allow_html=True)

    preset = st.selectbox(
        "プリセット",
        ["カスタム", "高スコア (A以上)", "高スコア上位50", "業種別トップ"],
        label_visibility="collapsed",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        min_score = st.slider("最低スコア", 0.0, 30.0, 15.0, 0.5)
        ranks = st.multiselect("ランク", ["S", "A", "B", "C", "D"], default=["S", "A", "B"])
    with col2:
        industries = sorted(v for v in score_df["業種"].dropna().unique() if _is_valid_str(v))
        selected_industries = st.multiselect("業種フィルタ", industries)
    with col3:
        sort_by = st.selectbox("ソート", ["総合スコア", "企業名", "業種"])
        ascending = st.checkbox("昇順", value=False)

    if preset == "高スコア (A以上)":
        min_score = 20.0
        ranks = ["S", "A"]
    elif preset == "高スコア上位50":
        min_score = 0.0
        ranks = ["S", "A", "B", "C", "D"]

    filtered = score_df[
        (score_df["総合スコア"] >= min_score) & (score_df["ランク"].isin(ranks))
    ]
    if selected_industries:
        filtered = filtered[filtered["業種"].isin(selected_industries)]
    filtered = filtered.sort_values(sort_by, ascending=ascending).reset_index(drop=True)

    if preset == "高スコア上位50":
        filtered = filtered.head(50)

    if preset == "業種別トップ":
        filtered = score_df.sort_values("総合スコア", ascending=False).groupby("業種").head(3)
        filtered = filtered.sort_values(["業種", "総合スコア"], ascending=[True, False])

    st.markdown(f'<p style="font-size:0.9rem;color:#86868b;margin-bottom:0.5rem">{len(filtered)} 社がヒット</p>', unsafe_allow_html=True)

    display_cols = ["企業名", "業種", "ティッカー", "総合スコア", "ランク",
                    "利益力", "株主還元力", "企業価値蓄積",
                    "バリュエーション", "財務健全性・安定性", "市場評価",
                    "強み", "懸念"]
    existing_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[existing_cols],
        use_container_width=True,
        height=600,
        column_config={
            "総合スコア": st.column_config.ProgressColumn(
                "総合スコア", min_value=0, max_value=30, format="%.1f",
            ),
        },
    )


# ─────────────────────────────────────
# ページ 3: ランキング
# ─────────────────────────────────────
elif page == "ランキング":
    st.markdown("""
    <div style="padding:0.5rem 0 1.5rem 0">
        <p style="font-size:2rem;font-weight:700;color:#1d1d1f;margin:0;letter-spacing:-0.02em">
            Evidence Score ランキング
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["全体トップ50", "業種別", "分布"])

    with tab1:
        top50 = score_df.head(50)
        st.dataframe(
            top50[["企業名", "業種", "ティッカー", "総合スコア", "ランク", "強み"]],
            use_container_width=True,
            height=600,
            column_config={
                "総合スコア": st.column_config.ProgressColumn(
                    "総合スコア", min_value=0, max_value=30, format="%.1f",
                ),
            },
        )

    with tab2:
        selected_ind = st.selectbox("業種を選択", sorted(v for v in score_df["業種"].dropna().unique() if _is_valid_str(v)))
        ind_df = score_df[score_df["業種"] == selected_ind].head(20)
        st.markdown(f'<p style="font-size:0.9rem;color:#86868b">{selected_ind} — トップ20</p>', unsafe_allow_html=True)
        st.dataframe(
            ind_df[["企業名", "ティッカー", "総合スコア", "ランク",
                     "利益力", "株主還元力", "バリュエーション", "強み"]],
            use_container_width=True,
        )

    with tab3:
        rank_counts = score_df["ランク"].value_counts().sort_index()
        colors_map = {"A": _C["blue"], "B": _C["orange"], "C": _C["red"],
                      "D": _C["gray"], "S": _C["green"]}
        bar_colors = [colors_map.get(r, "#999") for r in rank_counts.index]

        fig = go.Figure(data=[
            go.Bar(
                x=rank_counts.index, y=rank_counts.values,
                marker_color=bar_colors,
                text=rank_counts.values, textposition="auto",
                textfont=dict(weight=600),
                marker_line_width=0,
            )
        ])
        fig.update_layout(**_PLOTLY_LAYOUT, height=400, bargap=0.4,
                          title=dict(text="ランク分布", font=dict(size=16, weight=600)))
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure(data=[
            go.Histogram(x=score_df["総合スコア"], nbinsx=30,
                         marker_color=_C["blue"], marker_line_width=0)
        ])
        fig2.update_layout(**_PLOTLY_LAYOUT, height=400,
                           title=dict(text="スコア分布", font=dict(size=16, weight=600)))
        st.plotly_chart(fig2, use_container_width=True)
