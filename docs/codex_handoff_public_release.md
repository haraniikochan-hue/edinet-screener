# Codex 引き継ぎ: EDINET スクリーナー 公開準備

**作成日**: 2026-02-25
**作成者**: Claude Code (Opus)
**目的**: GitHub 公開に向けた残作業の整理

---

## 1. プロジェクト現状

### 概要
EDINET 開示企業（日本上場 約3,848社）の財務データを **6軸30点** でスコアリングし、
Streamlit で企業診断・スクリーニング・ランキングを提供するWebアプリ。

スコアリングの特徴: 配点は「良い企業の条件」ではなく、**実際の株価リターンとの相関分析**（Spearman順位相関、p<0.001）に基づいて設計。ROE水準やEPS成長年数（相関ほぼゼロ）は除外し、配当安定性・ROEの安定性・時価総額など実際にリターンと相関が高い指標で評価。

### 技術スタック
- Python 3.10+
- Streamlit（Webアプリ）
- Pandas / NumPy（データ処理）
- Plotly（チャート）
- yfinance / yahooquery（市場データ取得）
- SciPy（統計分析）

### ディレクトリ構造
```
edinet-screener/
├── app.py                    # Streamlit メインアプリ（1,003行）
├── lib/
│   ├── data_loader.py        # データ読み込み・企業プロファイル構築（386行）
│   ├── evidence_scorer.py    # スコアリングエンジン 6軸30点（453行）
│   └── buffett_scorer.py     # 旧スコアリング（未使用、参考用）
├── scripts/                  # データ取得・分析スクリプト（16本、8,117行）
│   ├── fetch_stock_prices.py        # yfinance で株価・PER・PBR 取得
│   ├── fetch_historical_returns.py  # yfinance で 1/3/5年リターン取得
│   ├── fetch_yf_sectors.py          # yahooquery で sector/industry 取得
│   ├── analyze_factor_correlations.py  # 相関分析
│   ├── unified_factor_gate.py       # ファクター検証ゲート
│   └── ...（研究用分析スクリプト多数）
├── data/                     # CSV データ（16MB、29ファイル）
│   ├── companies.csv         # 企業マスタ（3,848社）
│   ├── financials_all.csv    # 財務諸表 6年分（19,226行）
│   ├── ratios_all.csv        # 財務比率 6年分（19,226行）
│   ├── stock_prices.csv      # yfinance 市場データ（3,745社）
│   ├── historical_returns.csv # 過去リターン（3,745社）
│   ├── yf_sectors.csv        # yahooquery 業種（3,735社 × 127業種）
│   ├── factor_correlations.csv
│   └── ...（ランキング CSV 等）
└── docs/
    ├── handoff_20260225.md                # 詳細引き継ぎ書
    └── codex_handoff_public_release.md    # 本書
```

---

## 2. 直前の変更（2026-02-25、未コミット）

### 競合マッチング修正 + データ品質改善

**問題**: NEC の競合に日立/富士通/NRI が出ず、全く無関係な食品企業が出ていた。
EDINET の `industry` は33カテゴリしかなく（NEC = "電気機器" にソニー/パナソニック/キーエンスも含まれる）、
財務類似度だけのマッチングでは業種が合わない。

**解決**: yahooquery の `industry_yf`（127カテゴリ）を主キーにマッチング。

#### 変更ファイル

**`lib/data_loader.py`** — 4箇所変更:
1. `build_company_profiles()`: `data/yf_sectors.csv` を merge して `industry_yf`, `sector` カラム追加
2. `get_industry_benchmark()`: `industry_col` パラメータ追加（デフォルト `"industry"`）
3. `get_industry_percentile()`: 同上
4. `get_peer_companies()`: 全面書き換え
   - industry_yf → sector → EDINET industry の段階的フォールバック
   - 時価総額レンジ 0.05x〜20x（同業種内なので広め）
   - 時価総額距離（log スケール）も類似度に加味

**`app.py`** — 3箇所変更:
1. `_render_report()`: industry_yf 優先でベンチマーク/ピア計算、hero ヘッダーに EDINET + YF 両業種表示
2. `_render_industry_comparison()`: `industry_col` パラメータ追加
3. `get_industry_percentile()` 呼び出し: `industry_col` を伝播

#### 検証済み結果
```
NEC industry_yf: Information Technology Services
IT Services companies: 161社
forwardPE median: 14.23x（修正前の「0.8」問題は解消）
Peers: 富士通, 大塚商会, TIS, 野村総合研究所, 日鉄ソリューションズ
```

---

## 3. 公開に向けて必要な作業

### 必須（公開ブロッカー）

| # | タスク | 詳細 |
|---|--------|------|
| 1 | **`.gitignore` 作成** | `__pycache__/`, `*.pyc`, `.env`, `data/fetch_progress.json` を除外 |
| 2 | **`requirements.txt` 作成** | `streamlit`, `pandas`, `numpy`, `plotly`, `yfinance`, `yahooquery`, `scipy` |
| 3 | **`README.md` 作成** | プロジェクト概要、スクリーンショット、セットアップ手順、使い方 |
| 4 | **LICENSE 選択** | MIT が無難 |
| 5 | **data/ の扱い決定** | 16MB の CSV を含めるか、`.gitignore` して取得スクリプトのみにするか（下記参照） |
| 6 | **初回コミット + GitHub リポジトリ作成** | 現在コミット0件 |

### 推奨（公開品質向上）

| # | タスク | 詳細 |
|---|--------|------|
| 7 | **EDINET データ取得スクリプト** | `companies.csv`, `financials_all.csv`, `ratios_all.csv` の生成スクリプトがリポジトリ外。公開するなら取得手順が必要 |
| 8 | **`scripts/` の整理** | 研究用スクリプト16本のうち、公開に必要なのは `fetch_stock_prices.py`, `fetch_historical_returns.py`, `fetch_yf_sectors.py`, `analyze_factor_correlations.py` 程度。残りは `scripts/research/` に分離するか除外 |
| 9 | **buffett_scorer.py の扱い** | 未使用。参考として残すか削除するか |
| 10 | **テスト追加** | ユニットテストが一切ない |
| 11 | **型ヒント整備** | `app.py` のヘルパー関数に型ヒントがない箇所あり |
| 12 | **Streamlit Cloud デプロイ設定** | `.streamlit/config.toml` 等 |

### data/ の扱いについて

**選択肢 A: data/ を含めて公開**
- メリット: `git clone` → `streamlit run app.py` で即動く
- デメリット: 16MB のCSV。企業固有データの著作権/利用規約リスク
- 注意: EDINET データ自体は公開情報だが、yfinance データは Yahoo の利用規約に注意

**選択肢 B: data/ は `.gitignore`、取得スクリプトのみ公開**
- メリット: リポジトリが軽い、著作権リスク回避
- デメリット: セットアップに1-2時間のデータ取得が必要
- 必要: `scripts/setup_data.py` のような一括取得スクリプトの作成

---

## 4. スコアリングモデルの要点（README用素材）

### 6軸30点の配点
| 軸 | 配点 | 主要ファクター | 根拠 |
|----|------|---------------|------|
| A. 利益力 | 7pt | 純利益率, EPS加速度, 赤字年 | IC=+0.123 (eps_momentum) |
| B. 株主還元力 | 7pt | 連続増配年数, 配当CAGR | IC=+0.220 (consec_div_increase) |
| C. 企業価値蓄積 | 4pt | BPS増加年数, 利益率改善 | IC=+0.103 (bps_increase_years) |
| D. バリュエーション | 4pt | 予想PER(バンド型), PBR, 配当利回り | Gate 6/6 (forwardPE) |
| E. 財務健全性 | 4pt | ROE標準偏差, FCF黒字年数 | IC=-0.224 (roe_std, 2位) |
| F. 市場評価 | 4pt | 時価総額 | 5y_r=+0.483 (最強ファクター) |

### バックテスト実績
- Spearman rho = +0.294 (p < 1e-73)
- Q5-Q1 スプレッド = +16.6%
- S > A > B > C > D 完全単調

### 重要な発見
- **ROE 水準** は株価リターンと **相関ゼロ** (r = -0.005)
- **ROE の安定性**（標準偏差）は **強い負の相関** (r = -0.224)
- **EPS 成長年数** も **相関ゼロ** (r = +0.010)
- **配当の安定性** が最も強い正のシグナル

---

## 5. 主要関数 API

```python
# lib/data_loader.py
build_company_profiles() -> pd.DataFrame
  # 全CSV統合。industry_yf (127カテゴリ), sector も含む

get_industry_benchmark(industry, profiles, industry_col="industry") -> dict
  # 業種内の主要指標中央値

get_industry_percentile(value, col, industry, profiles, industry_col="industry") -> float|None
  # 業種内パーセンタイル (0-100)

get_peer_companies(edinet_code, industry, profiles, n=5, industry_col="industry") -> pd.DataFrame
  # 同業種 + 財務類似度でピア企業を検索
  # industry_yf → sector → EDINET industry の3段フォールバック

get_company_timeseries(edinet_code) -> tuple[pd.DataFrame, pd.DataFrame]
  # 1社の時系列 (financials, ratios)

# lib/evidence_scorer.py
score_company(row, industry_medians) -> EvidenceReport  # 1社スコアリング
score_all(profiles) -> list[EvidenceReport]             # 全社スコアリング
reports_to_dataframe(reports) -> pd.DataFrame           # DF変換
```

---

## 6. 実行方法

```bash
# アプリ起動
cd /Users/harann/edinet-screener
streamlit run app.py
# → http://localhost:8501

# データ更新
python scripts/fetch_stock_prices.py       # 株価データ（1-2時間）
python scripts/fetch_historical_returns.py # リターンデータ（1-2時間）
python scripts/fetch_yf_sectors.py         # 業種データ（数分）
python scripts/analyze_factor_correlations.py  # 相関分析（5-10分）
```

---

## 7. 既知の課題

| 項目 | 状態 | 説明 |
|------|------|------|
| EDINET 取得自動化 | 未実装 | `companies.csv`, `financials_all.csv`, `ratios_all.csv` の生成スクリプトがリポジトリ外 |
| `stock_prices.csv` の forwardPE | データソース問題 | NEC の forwardPE=5.26 等、yfinance 側の値が実態と乖離するケースあり |
| yfinance レート制限 | 要対策 | `fetch_historical_returns.py` で RateLimitError 多発 |
| テスト | なし | ユニットテスト未作成 |
| Streamlit キャッシュ | TTL 3600秒 | データ更新後はプロセス再起動が必要 |

---

*以上。詳細な引き継ぎ書は `docs/handoff_20260225.md` を参照。*
