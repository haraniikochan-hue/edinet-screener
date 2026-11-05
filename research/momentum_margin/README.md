# momentum_margin — モメンタム銘柄の底局面における信用需給の横断分析

- `universe.csv` … 44銘柄（電線・電力、半導体、AI/DC/重電、防衛、話題株、キオクシア）
- `fetch_kabutan.py` … 株探から週次・日次の信用残を取得 → `data/margin_weekly_all.csv`, `data/margin_daily_all.csv`
- `fetch_prices.py` … yfinance から日足と分割イベント → `data/prices_all.csv`, `data/splits_all.csv`
- `analyze.py` … 局所底・急落イベントの検出と信用需給の文脈（`data/events_bottoms.csv`, `data/events_crash.csv`）
- `analyze2.py` … −10%日後の条件付きリターン（`data/events_m10.csv`）、今回局面の横断（`data/current_cross.csv`）、キオクシア級の類似事例、反発の停止位置、混雑度
- `analyze3.py` … マクロ急落日（2025/4 等）を除いた頑健性、キオクシアの週次参照価格
- `report.md` … 結果のまとめ

更新: `python3 fetch_kabutan.py && python3 fetch_prices.py && python3 analyze.py && python3 analyze2.py && python3 analyze3.py`（このディレクトリで実行）。
