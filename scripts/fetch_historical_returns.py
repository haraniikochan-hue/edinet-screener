"""
yfinance で全上場企業の過去1年/3年/5年のリターンを取得する。

使い方:
    python scripts/fetch_historical_returns.py
"""

import csv
import time
from pathlib import Path

import yfinance as yf
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
COMPANIES_CSV = DATA_DIR / "companies.csv"
OUTPUT_CSV = DATA_DIR / "historical_returns.csv"

BATCH_SIZE = 50
SLEEP_BETWEEN_BATCHES = 0.5


def load_tickers() -> list[str]:
    """companies.csv からティッカーリストを作成"""
    tickers = []
    with open(COMPANIES_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sec_code = row.get("sec_code", "").strip()
            if sec_code and len(sec_code) >= 4:
                tickers.append(sec_code[:4] + ".T")
    return tickers


def fetch_returns_batch(tickers: list[str]) -> list[dict]:
    """バッチで1年/3年/5年リターンを計算"""
    results = []

    for period, label in [("1y", "return_1y"), ("3y", "return_3y"), ("5y", "return_5y")]:
        try:
            data = yf.download(
                tickers, period=period, interval="1mo",
                auto_adjust=True, progress=False, threads=True,
            )
            if data.empty:
                continue

            close = data["Close"] if "Close" in data.columns else data
            if isinstance(close, pd.Series):
                # Single ticker case
                close = close.to_frame(tickers[0])

            for t in tickers:
                if t in close.columns:
                    series = close[t].dropna()
                    if len(series) >= 2:
                        ret = (series.iloc[-1] / series.iloc[0]) - 1
                        # Find existing or create new entry
                        existing = [r for r in results if r["ticker"] == t]
                        if existing:
                            existing[0][label] = ret
                        else:
                            results.append({"ticker": t, label: ret})
        except Exception as e:
            print(f"  Error fetching {period}: {e}")

    return results


def main():
    tickers = load_tickers()
    print(f"Total tickers: {len(tickers)}")

    all_results: dict[str, dict] = {}

    # Fetch each period separately for reliability
    for period, label in [("1y", "return_1y"), ("3y", "return_3y"), ("5y", "return_5y")]:
        print(f"\n=== Fetching {period} returns ===")
        total_batches = (len(tickers) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(tickers), BATCH_SIZE):
            batch = tickers[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1

            if batch_num % 10 == 1:
                print(f"  [{batch_num}/{total_batches}] Processing...")

            try:
                data = yf.download(
                    batch, period=period, interval="1mo",
                    auto_adjust=True, progress=False, threads=True,
                )
                if data.empty:
                    continue

                close = data["Close"] if "Close" in data.columns else data
                if isinstance(close, pd.Series):
                    close = close.to_frame(batch[0])

                for t in batch:
                    if t in close.columns:
                        series = close[t].dropna()
                        if len(series) >= 2:
                            ret = float((series.iloc[-1] / series.iloc[0]) - 1)
                            if t not in all_results:
                                all_results[t] = {"ticker": t}
                            all_results[t][label] = ret
            except Exception as e:
                print(f"  Batch error: {e}")

            if i + BATCH_SIZE < len(tickers):
                time.sleep(SLEEP_BETWEEN_BATCHES)

        count = sum(1 for r in all_results.values() if label in r)
        print(f"  {label}: {count} tickers fetched")

    # Write CSV
    rows = list(all_results.values())
    print(f"\nWriting {len(rows)} records to {OUTPUT_CSV}")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticker", "return_1y", "return_3y", "return_5y"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print("Done!")


if __name__ == "__main__":
    main()
