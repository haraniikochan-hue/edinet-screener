"""共通パラメータ・営業日・値幅制限."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
REPORTS = BASE / "reports"

P = dict(
    # --- 株式数（分割後）
    shares_total=1_644_045_264,
    treasury=48_400_000,            # 自己株（8月取得 16.13M株×3）
    toshiba_shares=172_007_400,     # 東芝 10.46%（10/27時点）
    skhynix_pct=0.14,               # SKハイニックス（ベイン系ビークル経由、概算）
    # --- 信用・追証の制度仮定
    maint=0.20,                     # 最低維持率（証券会社により20〜30%）
    cure_buffer=0.05,               # 解消後の維持率は maint+buffer まで戻すと仮定
    lag_forced=3,                   # 追証発生→強制決済執行（翌々営業日15:30期限→その翌営業日寄付）
    lag_cure=1,                     # 追証発生→一部売却による解消の執行
    classes=(0.30, 0.50, 1.00),     # 新規建て時の保証金率クラス
    legacy_split=((0.79, 0.30), (0.94, 0.40), (1.29, 0.30)),  # 初期建玉の建値分散（平均比, 比率）
    eta_nocash=0.5,                 # 現金入金できない人のうち一部売却で解消する比率（残りは強制）
    lock_exec=0.25,                 # ストップ安張り付き日の売り注文の執行率（比例配分）
    be_band=0.03,                   # 建値±3%を「やれやれ売り」ゾーンとみなす
    # --- 市場インパクト（平方根則）
    impact_Y=0.7,
    # --- 現物ホルダーの入れ替わり
    turnover_alpha=0.5,             # 出来高のうち実質的な保有者入れ替わり比率（0.4〜0.8で感応度）
    be_sell_cash=0.10,              # 現物保有者が建値回復時に手放す比率（仮定）
    be_sell_margin=0.35,            # 信用の同（ラダー表示用。シミュレーションでは beta_be で推定）
    # --- 大口
    topix_ffw_step=0.175,
    passive_share=(0.15, 0.20, 0.25),
    toshiba_participation=(0.016, 0.025, 0.078, 0.153),  # 平常ペース(1.2M株/日≈1.6%)と10/23〜27の観測参加率
    # --- ボラ
    ewma_lambda=None,               # None=尤度最大化で推定
    resid_window=250,               # 標準化残差のブートストラップ窓
    # --- 推定・MC
    n_samples=10000, n_rounds=4, elite=300, top_k=100, seed=7,
    mc_paths=20000, horizon=5,
)

JP_HOLIDAYS = {dt.date(2026, 11, 23), dt.date(2026, 12, 31), dt.date(2027, 1, 1), dt.date(2027, 1, 2),
               dt.date(2027, 1, 11), dt.date(2027, 2, 11), dt.date(2027, 2, 23), dt.date(2027, 3, 22)}


def is_bday(d: dt.date) -> bool:
    return d.weekday() < 5 and d not in JP_HOLIDAYS


def next_bdays(d: dt.date, n: int) -> list[dt.date]:
    out, cur = [], d
    while len(out) < n:
        cur += dt.timedelta(days=1)
        if is_bday(cur):
            out.append(cur)
    return out


def bdays_between(a: dt.date, b: dt.date) -> int:
    n, cur = 0, a
    while cur < b:
        cur += dt.timedelta(days=1)
        if is_bday(cur):
            n += 1
    return n


_LIMIT_TABLE = [(100, 30), (200, 50), (500, 80), (700, 100), (1000, 150), (1500, 300), (2000, 400),
                (3000, 500), (5000, 700), (7000, 1000), (10000, 1500), (15000, 3000), (20000, 4000),
                (30000, 5000), (50000, 7000), (70000, 10000), (100000, 15000), (150000, 30000)]


def price_limit(base: float) -> float:
    """東証の制限値幅（基準値段=前日終値）."""
    for hi, lim in _LIMIT_TABLE:
        if base < hi:
            return lim
    return 50000


def price_limit_vec(base):
    import numpy as np
    base = np.asarray(base, dtype=float)
    out = np.full(base.shape, 50000.0)
    for hi, lim in reversed(_LIMIT_TABLE):
        out[base < hi] = lim
    return out
