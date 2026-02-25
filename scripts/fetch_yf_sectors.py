"""yahooquery から全銘柄の sector/industry を一括取得して CSV に保存する。

Usage:
    python scripts/fetch_yf_sectors.py

Output:
    data/yf_sectors.csv (ticker, sector, industry_yf)
"""

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT = DATA_DIR / "yf_sectors.csv"


def main():
    from yahooquery import Ticker

    sp = pd.read_csv(DATA_DIR / "stock_prices.csv")
    tickers = sp["ticker"].dropna().unique().tolist()
    print(f"Fetching sector/industry for {len(tickers)} tickers via yahooquery...")

    # Resume from existing partial results
    done = set()
    results = []
    if OUTPUT.exists():
        existing = pd.read_csv(OUTPUT)
        # Only keep rows with valid sector data
        valid = existing[existing["sector"].notna() & (existing["sector"] != "")]
        done = set(valid["ticker"].tolist())
        results = valid.to_dict("records")
        print(f"  Resuming: {len(done)} already fetched with valid data")

    remaining = [t for t in tickers if t not in done]
    print(f"  Remaining: {len(remaining)}")

    batch_size = 50
    for i in range(0, len(remaining), batch_size):
        batch = remaining[i:i + batch_size]
        try:
            t = Ticker(batch, asynchronous=True)
            profiles = t.asset_profile
            for ticker in batch:
                info = profiles.get(ticker, {})
                if isinstance(info, dict):
                    results.append({
                        "ticker": ticker,
                        "sector": info.get("sector", ""),
                        "industry_yf": info.get("industry", ""),
                    })
                else:
                    results.append({"ticker": ticker, "sector": "", "industry_yf": ""})
        except Exception as e:
            print(f"  Error at batch {i}: {e}")
            for ticker in batch:
                results.append({"ticker": ticker, "sector": "", "industry_yf": ""})

        # Save progress every batch
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT, index=False)
        pct = (i + len(batch)) / len(remaining) * 100 if remaining else 100
        filled = df[df["sector"] != ""].shape[0]
        print(f"  {i + len(batch)}/{len(remaining)} ({pct:.0f}%) — {filled} valid")

        time.sleep(0.5)

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT, index=False)
    filled = df[df["industry_yf"] != ""].shape[0]
    print(f"\nDone. {filled}/{len(df)} tickers have industry data.")
    print(f"Unique industries: {df['industry_yf'].nunique()}")
    print(f"Saved to {OUTPUT}")


if __name__ == "__main__":
    main()
