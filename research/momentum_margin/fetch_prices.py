"""yfinance で日足（分割・配当イベントつき）を取得して data/prices_all.csv, data/splits_all.csv に保存."""
import sys, time
import pandas as pd, yfinance as yf
uni = pd.read_csv("universe.csv", dtype=str)
rows, splits = [], []
for code, name in zip(uni.code, uni.name):
    tk = f"{code}.T"
    for attempt in range(3):
        try:
            df = yf.download(tk, start="2024-10-01", end="2026-11-07", auto_adjust=True, actions=True, progress=False, threads=False)
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.dropna(subset=["Close"])
            if len(df) == 0: raise RuntimeError("empty")
            break
        except Exception as e:
            print(tk, "retry", attempt, e, file=sys.stderr); time.sleep(3)
    else:
        continue
    for d, r in df.iterrows():
        rows.append(dict(code=code, date=d.date(), open=r["Open"], high=r["High"], low=r["Low"], close=r["Close"], volume=r["Volume"]))
        if "Stock Splits" in df.columns and r["Stock Splits"] and r["Stock Splits"] > 0:
            splits.append(dict(code=code, date=d.date(), ratio=r["Stock Splits"]))
    print(tk, name, len(df), df.index.min().date(), df.index.max().date(), "splits", [s for s in splits if s["code"] == code], file=sys.stderr)
    time.sleep(0.8)
pd.DataFrame(rows).to_csv("data/prices_all.csv", index=False)
pd.DataFrame(splits).to_csv("data/splits_all.csv", index=False)
print("done", len(rows), "splits", len(splits))
