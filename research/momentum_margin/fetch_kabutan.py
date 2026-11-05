"""株探の信用残（週次・日次）を取得して data/margin_weekly_all.csv, data/margin_daily_all.csv に保存."""
import re, sys, time, csv
import requests
from lxml import html
import pandas as pd
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept-Language": "ja,en;q=0.8"}
uni = pd.read_csv("universe.csv", dtype=str)
def num(s):
    s = s.replace("株", "").replace(",", "").replace("％", "").replace("%", "").strip()
    if s in ("ー", "-", "", "—"): return None
    try: return float(s)
    except: return None
def parse(url):
    r = requests.get(url, headers=UA, timeout=30)
    if r.status_code != 200: return None
    doc = html.fromstring(r.text)
    for t in doc.xpath("//table"):
        rows = t.xpath(".//tr")
        hdr = [c.text_content().strip() for c in rows[0].xpath("./th|./td")] if rows else []
        if hdr and hdr[0] == "日付":
            out = []
            for rw in rows[1:]:
                cells = [c.text_content().strip() for c in rw.xpath("./th|./td")]
                if len(cells) == len(hdr): out.append(dict(zip(hdr, cells)))
            return out
    return []
wk, dy = [], []
for code, name in zip(uni.code, uni.name):
    for page in range(1, 5):
        rows = parse(f"https://s.kabutan.jp/stocks/{code}/historical_margins/weekly/?page={page}")
        if not rows: break
        for r in rows:
            wk.append(dict(code=code, date=r["日付"], close=num(r["終値"]), ratio=num(r.get("信用倍率", "")), sell=num(r["売り残(株)"]), buy=num(r["買い残(株)"]),
                           vwap=num(r.get("売買単価", "")), volume=num(r.get("売買高(株)", ""))))
        time.sleep(0.4)
        if len(rows) < 30: break
    rows = parse(f"https://s.kabutan.jp/stocks/{code}/historical_margins/daily/")
    for r in rows or []:
        dy.append(dict(code=code, date=r["日付"], close=num(r["終値"]), ratio=num(r.get("信用倍率", "")), sell=num(r["売り残(株)"]), sell_amt=num(r.get("売り残(額)", "")),
                       buy=num(r["買い残(株)"]), buy_amt=num(r.get("買い残(額)", ""))))
    print(code, name, "weekly", sum(1 for x in wk if x["code"] == code), "daily", sum(1 for x in dy if x["code"] == code), file=sys.stderr)
    time.sleep(0.4)
w = pd.DataFrame(wk); w["date"] = pd.to_datetime("20" + w.date, format="%Y/%m/%d"); w.to_csv("data/margin_weekly_all.csv", index=False)
d = pd.DataFrame(dy); d["date"] = pd.to_datetime("2026/" + d.date, format="%Y/%m/%d"); d.to_csv("data/margin_daily_all.csv", index=False)
print("done", len(w), len(d))
