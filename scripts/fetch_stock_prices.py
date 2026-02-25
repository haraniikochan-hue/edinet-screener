"""
yfinance で全上場企業の株価データ（時価総額・PBR・配当利回り等）を取得する。

使い方:
    python scripts/fetch_stock_prices.py
    python scripts/fetch_stock_prices.py --resume   # 途中から再開
"""

import argparse
import csv
import json
import time
from pathlib import Path

import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
COMPANIES_CSV = DATA_DIR / "companies.csv"
OUTPUT_CSV = DATA_DIR / "stock_prices.csv"
PROGRESS_FILE = DATA_DIR / "fetch_progress.json"

# 取得するフィールド（yfinance info dict のキー）
FIELDS = [
    "currentPrice",
    "marketCap",
    "priceToBook",       # PBR
    "dividendYield",     # 配当利回り（小数, e.g. 0.03 = 3%）
    "trailingPE",        # PER（実績）
    "forwardPE",         # PER（予想）
    "bookValue",         # BPS
    "totalRevenue",      # 売上高（直近）
    "returnOnEquity",    # ROE
    "debtToEquity",      # D/E ratio
    "freeCashflow",      # FCF
    "fiftyTwoWeekHigh",
    "fiftyTwoWeekLow",
    "fiftyDayAverage",
    "twoHundredDayAverage",
    "beta",
]

BATCH_SIZE = 20  # yfinance に同時リクエストする銘柄数
SLEEP_BETWEEN_BATCHES = 1.0  # バッチ間のスリープ（秒）


def load_companies() -> list[dict]:
    """companies.csv を読み込み、sec_code → yfinance ティッカーに変換"""
    companies = []
    with open(COMPANIES_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sec_code = row.get("sec_code", "").strip()
            if not sec_code or len(sec_code) < 4:
                continue
            ticker = sec_code[:4] + ".T"
            companies.append({
                "edinet_code": row["edinet_code"],
                "name": row["name"],
                "sec_code": sec_code,
                "ticker": ticker,
                "industry": row.get("industry", ""),
            })
    return companies


def load_progress() -> set[str]:
    """取得済みティッカーのセットを返す"""
    if not PROGRESS_FILE.exists():
        return set()
    data = json.loads(PROGRESS_FILE.read_text())
    return set(data.get("completed", []))


def save_progress(completed: set[str]) -> None:
    PROGRESS_FILE.write_text(json.dumps({"completed": sorted(completed)}, ensure_ascii=False))


def fetch_batch(tickers: list[str]) -> dict[str, dict]:
    """複数ティッカーを一括取得"""
    results = {}
    try:
        ticker_str = " ".join(tickers)
        data = yf.Tickers(ticker_str)
        for t in tickers:
            try:
                info = data.tickers[t].info
                if info and info.get("regularMarketPrice") or info.get("currentPrice"):
                    row = {}
                    for field in FIELDS:
                        row[field] = info.get(field)
                    # currentPrice のフォールバック
                    if row["currentPrice"] is None:
                        row["currentPrice"] = info.get("regularMarketPrice")
                    results[t] = row
                else:
                    results[t] = None  # データなし
            except Exception:
                results[t] = None
    except Exception as e:
        print(f"  batch error: {e}")
        for t in tickers:
            results[t] = None
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", help="途中から再開")
    args = parser.parse_args()

    companies = load_companies()
    print(f"企業数: {len(companies)}")

    # ticker → company info のマップ
    ticker_map: dict[str, dict] = {}
    for c in companies:
        ticker_map[c["ticker"]] = c

    completed = load_progress() if args.resume else set()
    if completed:
        print(f"取得済み: {len(completed)} 社 → 残りから再開")

    # 未取得のティッカーリスト
    remaining = [c["ticker"] for c in companies if c["ticker"] not in completed]
    print(f"取得対象: {len(remaining)} 社")

    # 出力CSVの準備
    header = ["edinet_code", "name", "sec_code", "ticker", "industry"] + FIELDS
    write_header = not (args.resume and OUTPUT_CSV.exists())

    with open(OUTPUT_CSV, "a" if args.resume else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if write_header:
            writer.writeheader()

        total_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE
        success_count = len(completed)
        fail_count = 0

        for i in range(0, len(remaining), BATCH_SIZE):
            batch = remaining[i : i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            print(f"[{batch_num}/{total_batches}] 取得中: {batch[0]} ~ {batch[-1]} ...", end=" ")

            results = fetch_batch(batch)

            for ticker, data in results.items():
                comp = ticker_map[ticker]
                if data:
                    row = {
                        "edinet_code": comp["edinet_code"],
                        "name": comp["name"],
                        "sec_code": comp["sec_code"],
                        "ticker": ticker,
                        "industry": comp["industry"],
                    }
                    row.update(data)
                    writer.writerow(row)
                    success_count += 1
                else:
                    fail_count += 1

                completed.add(ticker)

            f.flush()
            print(f"OK ({success_count} 成功 / {fail_count} 失敗)")

            # 50バッチごとにプログレス保存
            if batch_num % 50 == 0:
                save_progress(completed)

            if i + BATCH_SIZE < len(remaining):
                time.sleep(SLEEP_BETWEEN_BATCHES)

    save_progress(completed)
    print(f"\n完了: {OUTPUT_CSV}")
    print(f"  成功: {success_count} 社")
    print(f"  失敗: {fail_count} 社")


if __name__ == "__main__":
    main()
