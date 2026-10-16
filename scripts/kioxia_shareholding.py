"""
キオクシア (285A) の大量保有・変更報告書を EDINET から取得し、
「最近60日間の取得又は処分の状況」表を日次 CSV に変換する。

EDINET API (v2) は Subscription-Key が必要なため、書類 PDF の公開 URL
(disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/<docID>.pdf) から直接取得する。
PDF のテキスト抽出には PyMuPDF を使う (pip install pymupdf)。

出力:
    data/kioxia/holder_reports.csv       報告書ごとの保有者・保有数・保有割合
    data/kioxia/holder_transactions.csv  60日表の明細 (重複除去済み)

使い方:
    python scripts/kioxia_shareholding.py
    python scripts/kioxia_shareholding.py --extra S100XXXX S100YYYY   # 書類IDを追加
"""

import argparse
import csv
import re
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "kioxia"
PDF_DIR = OUT_DIR / "edinet_pdf"
PDF_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{doc_id}.pdf"

# 2026-10-16 時点で確認できた 285A 関連の報告書
# (M&A Online の発行体別一覧と松井証券ニュースから収集)
DOC_IDS = [
    # 東芝 2024-2025
    "S100V026",  # 大量保有報告書 (IPO時)
    "S100V3TO",  # No.1  グリーンシュー
    "S100WR99",  # No.4  2025-09-17
    "S100WWHQ",  # No.11 2025-10-15
    "S100WWX0",  # No.12 2025-10-17
    # 2026
    "S100XMGC", "S100XMQN", "S100XMQO", "S100XP4U", "S100XP8J",
    "S100XRA1", "S100XRA5", "S100XRN8", "S100XRX4", "S100XSU6",
    "S100XTX4", "S100XUMF", "S100XXID", "S100XZBP", "S100Y02O",
    "S100Y0X5", "S100Y4QG", "S100Y63W", "S100Y7LV", "S100Y88M",
    "S100YBT0", "S100YS0I", "S100YVH4", "S100Z25L", "S100Z6ZB",
]

# 株式分割 (1:3) の権利落ち日。この日以降の約定は分割後株数で記載されている
SPLIT_EX_DATE = "2026-09-29"
SPLIT_RATIO = 3

DATE_RE = r"(?:令和\s*\d+|\d{4})\s*年\s*\d+\s*月\s*\d+\s*日"
# テキストは NFKC 正規化後 (全角括弧・数字は半角) を前提にする
TX_RE = re.compile(
    rf"({DATE_RE})\s*株券\(普通株\s*式\)?\s*([\d,]+)\s*([\d.]+)\s*(市場内|市場外)\s*(処分|取得)"
    # 単価はカンマか小数点を含むものに限定 (次行の「2026年」を拾わないため)
    r"\s*(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+)?"
)


def to_iso_date(s: str) -> str:
    s = re.sub(r"\s", "", s)
    m = re.match(r"(令和)?(\d+)年(\d+)月(\d+)日", s)
    year = int(m.group(2))
    if m.group(1):
        year += 2018
    return f"{year:04d}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"


def fetch_pdf(doc_id: str) -> Path:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    path = PDF_DIR / f"{doc_id}.pdf"
    if path.exists() and path.stat().st_size > 0:
        return path
    req = urllib.request.Request(PDF_URL.format(doc_id=doc_id), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        path.write_bytes(resp.read())
    time.sleep(0.5)
    return path


def pdf_text(path: Path) -> str:
    import pymupdf

    with pymupdf.open(path) as doc:
        text = "\n".join(page.get_text() for page in doc)
    return unicodedata.normalize("NFKC", text)


def _first(pattern: str, text: str) -> str:
    m = re.search(pattern, text, re.S)
    return m.group(1).strip() if m else ""


def parse_report(doc_id: str, text: str) -> tuple[list[dict], list[dict]]:
    flat = re.sub(r"\s+", " ", text)
    # ページヘッダ/フッタ (「EDINET提出書類 <提出者>(Exxxxx) 変更報告書 4/13」) を除去
    flat = re.sub(r"EDINET提出書類 .+?\(E\d{5}\) (?:変更報告書|大量保有報告書) \d+/\d+ ?", "", flat)
    header = {
        "doc_id": doc_id,
        "doc_type": _first(r"【提出書類】\s*(.+?)\s*【根拠条文】", flat),
        "obligation_date": to_iso_date(_first(rf"【報告義務発生日】\s*({DATE_RE})", flat)),
        "submit_date": to_iso_date(_first(rf"【提出日】\s*({DATE_RE})", flat)),
        "reason": _first(r"【変更報告書提出事由】\s*(.+?)\s*(?:EDINET|第1)", flat),
    }

    reports, txs = [], []
    # 提出者ごとのセクションに分割 (連名提出では複数)
    sections = re.split(r"[1-9]【提出者\(大量保有者\)/\d+】", flat)[1:]
    for sec in sections:
        holder = _first(r"氏名又は名称\s*(.+?)\s*住所又は本店所在地", sec)
        shares = _first(r"保有株券等の数\(総数\)\s*\(.+?\)\s*[A-Z]*\s*([\d,]+)", sec)
        ratio = _first(r"上記提出者の株券等保有割合\(%\)\s*\(.*?×100\)\s*([\d.]+)", sec)
        prev = _first(r"直前の報告書に記載された\s*株券等保有割合\(%\)\s*([\d.]+)", sec)
        denom = _first(r"発行済株式等総数\(株・口\)\s*\(.+?\)\s*[A-Z]*\s*([\d,]+)", sec)
        reports.append({
            **header,
            "holder": holder,
            "shares": shares.replace(",", ""),
            "ratio_pct": ratio,
            "prev_ratio_pct": prev,
            "shares_outstanding": denom.replace(",", ""),
        })
        table = sec.split("最近60日間の取得又は処分の状況", 1)
        if len(table) < 2:
            continue
        body = table[1].split("【当該株券等に関する担保契約等重要な契約】", 1)[0]
        for m in TX_RE.finditer(body):
            txs.append({
                "holder": holder,
                "trade_date": to_iso_date(m.group(1)),
                "qty": int(m.group(2).replace(",", "")),
                "pct": m.group(3),
                "venue": m.group(4),
                "side": m.group(5),
                "price": (m.group(6) or "").replace(",", ""),
                "source_doc": doc_id,
            })
    return reports, txs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra", nargs="*", default=[], help="追加の書類ID")
    args = parser.parse_args()

    all_reports, all_txs = [], []
    for doc_id in DOC_IDS + args.extra:
        text = pdf_text(fetch_pdf(doc_id))
        if "285A" not in text:
            print(f"skip {doc_id}: 285A の報告書ではない")
            continue
        reports, txs = parse_report(doc_id, text)
        all_reports += reports
        all_txs += txs
        print(f"{doc_id}: {len(reports)} holder(s), {len(txs)} tx rows")

    # 60日表は報告書間で重複するので明細単位で一意化 (最初に出た書類を残す)
    seen, unique = set(), []
    for tx in sorted(all_txs, key=lambda r: (r["holder"], r["trade_date"])):
        key = (tx["holder"], tx["trade_date"], tx["qty"], tx["venue"], tx["side"], tx["price"])
        if key in seen:
            continue
        seen.add(key)
        # 分割後株数に揃えた数量 (株価データも分割調整済みのため)
        tx["qty_split_adj"] = tx["qty"] if tx["trade_date"] >= SPLIT_EX_DATE else tx["qty"] * SPLIT_RATIO
        unique.append(tx)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "holder_reports.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_reports[0].keys()))
        w.writeheader()
        w.writerows(sorted(all_reports, key=lambda r: (r["obligation_date"], r["holder"])))
    with open(OUT_DIR / "holder_transactions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(unique[0].keys()))
        w.writeheader()
        w.writerows(unique)
    print(f"reports={len(all_reports)} transactions={len(unique)} -> {OUT_DIR}")


if __name__ == "__main__":
    main()
