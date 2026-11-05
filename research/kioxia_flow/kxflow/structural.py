"""信用買い方の構造モデル（建値ビンテージ × 保証金率クラス × 追証の3経路 × 執行制約）.

1日の流れ（価格は始値 O・終値 C・前日終値 prev、出来高 V、張り付きフラグ lock）:
  A. 寄付: 期日到来の売り（強制決済キュー、一部売却キュー）を執行。張り付き日は執行率 lock_exec のみ、残りは翌日へ
  B. 日中: 自主的な手仕舞い  v_j = b0 + b1·dn·(1 + κ·(loss_j − loss̄)) + b2·up·(1 + β_be·1[建値±band])
           新規の信用買い（ナンピン） N = V·(n0 + n1·dn·余力比 + n2·up)
  C. 大引け: 維持率 = me_{j,k} − loss_j < maint → 追証。入金（確率 qc·余力比）／一部売却（qs + 入金不能分×η）／強制（残り）
  D. 余力 D を更新（新規建ての保証金、入金額を控除）

すべて numpy でパラメータ本数 Ps 分を同時に計算する。価格は Ps 本の経路でも共通でもよい。
"""
from __future__ import annotations

import numpy as np

from .config import P

THETA_BOUNDS = dict(
    w30=(0.0, 0.6), w50=(0.0, 0.6),
    qc=(0.0, 0.95), qs=(0.0, 0.6),
    b0=(0.0, 0.03), b1=(0.0, 0.8), b2=(0.0, 0.8),
    kappa=(-2.0, 4.0), bbe=(0.0, 4.0),
    n0=(0.0, 0.06), n1=(0.0, 0.8), n2=(0.0, 0.3),
    lD0=(10.0, 12.7),
)
THETA_NAMES = dict(
    w30="保証金30%(フルレバ)比率", w50="保証金50%比率", qc="追証→入金で解消する確率", qs="追証→一部売却で解消する確率",
    b0="平常の自主決済/日", b1="下落率あたりの投げ", b2="上昇率あたりの手仕舞い",
    kappa="投げの含み損集中度(κ: +で深い損ほど投げる)", bbe="建値回復時の『やれやれ売り』倍率",
    n0="平常の新規買い/出来高", n1="下落率あたりのナンピン", n2="上昇率あたりの追随買い",
    lD0="log10(買い方の追加資金余力・円)",
)


def normalize_theta(th: dict) -> dict:
    th = {k: np.asarray(v, float).copy() for k, v in th.items()}
    s = th["w30"] + th["w50"]
    over = s > 0.95
    th["w30"][over] *= 0.95 / s[over]
    th["w50"][over] *= 0.95 / s[over]
    s2 = th["qc"] + th["qs"]
    over2 = s2 > 0.98
    th["qc"][over2] *= 0.98 / s2[over2]
    th["qs"][over2] *= 0.98 / s2[over2]
    return th


class MarginModel:
    """状態を保持し、1日ずつ進める."""

    def __init__(self, theta: dict, S0: float, A0: float, P0: float, n_days_max: int):
        self.th = normalize_theta(theta)
        self.Ps = len(self.th["qc"])
        self.m = np.array(P["classes"], float)
        self.K = len(self.m)
        self.maint, self.buf = P["maint"], P["cure_buffer"]
        self.Lf, self.Lc, self.rho, self.eta = P["lag_forced"], P["lag_cure"], P["lock_exec"], P["eta_nocash"]
        self.band = P["be_band"]
        leg = P["legacy_split"]
        self.NL = len(leg)
        self.NV = self.NL + n_days_max
        Ps, NV, K = self.Ps, self.NV, self.K
        avg0 = A0 / S0
        self.cost = np.zeros((Ps, NV))
        self.sh = np.zeros((Ps, NV, K))
        self.me = np.tile(self.m, (Ps, NV, 1))
        wk = np.stack([self.th["w30"], self.th["w50"], 1 - self.th["w30"] - self.th["w50"]], axis=1)  # (Ps,K)
        self.wk = wk
        self.mbar = (wk * self.m[None, :]).sum(1)  # 新規建ての平均保証金率
        for j, (mult, wl) in enumerate(leg):
            self.cost[:, j] = avg0 * mult
            self.sh[:, j, :] = S0 * wl * wk
            loss0 = 1 - P0 / (avg0 * mult)
            self.me[:, j, :] = np.maximum(self.m[None, :], self.maint + loss0 + self.buf)
        self.pend_f = [np.zeros((Ps, NV, K)) for _ in range(self.Lf)]
        self.pend_c = [np.zeros((Ps, NV, K)) for _ in range(self.Lc)]
        self.D0 = 10 ** self.th["lD0"]
        self.D = self.D0.copy()
        self.t = 0
        self.alive = np.zeros(NV, bool)
        self.alive[: self.NL] = True

    # ------------------------------------------------------------------ helpers
    def _loss(self, C):
        safe = np.where(self.cost > 0, self.cost, 1.0)
        return np.where(self.alive[None, :] & (self.cost > 0), 1 - np.asarray(C, float)[:, None] / safe, 0.0)

    def preview_flows(self, prev, C, V):
        """状態を変えずに、終値 C・出来高 V のときの自主決済株数と新規買い株数を返す（MC の不動点反復用）."""
        th, Ps = self.th, self.Ps
        prev, C, V = (np.broadcast_to(np.asarray(x, float), (Ps,)) for x in (prev, C, V))
        r = np.log(C / prev)
        dn, up = np.maximum(-r, 0.0), np.maximum(r, 0.0)
        loss = self._loss(C)
        shv = self.sh.sum(2)
        loss_bar = (loss * shv).sum(1) / np.maximum(shv.sum(1), 1.0)
        near_be = np.abs(loss) <= self.band
        v = (th["b0"][:, None]
             + th["b1"][:, None] * dn[:, None] * np.clip(1 + th["kappa"][:, None] * (loss - loss_bar[:, None]), 0.0, 5.0)
             + th["b2"][:, None] * up[:, None] * (1 + th["bbe"][:, None] * near_be))
        volc = (shv * np.clip(v, 0.0, 0.8)).sum(1)
        N = V * np.clip(th["n0"] + th["n1"] * dn * self.frac() + th["n2"] * up, 0.0, 0.6)
        return volc, N

    def frac(self):
        return np.clip(self.D / self.D0, 0.0, 1.0)

    def totals(self):
        pend = sum(self.pend_f) + sum(self.pend_c)
        tot = self.sh + pend
        S = tot.sum(axis=(1, 2))
        A = (tot * self.cost[:, :, None]).sum(axis=(1, 2))
        return S, A

    def vintage_table(self):
        """現在の建玉（キュー含む）を建値ごとに（Ps, NV）で返す."""
        pend = sum(self.pend_f) + sum(self.pend_c)
        return (self.sh + pend).sum(2), self.cost.copy()

    # ------------------------------------------------------------------ one day
    def step(self, prev, O, C, V, lock, tp=None):
        """prev/O/C/V/lock: スカラーまたは (Ps,) 配列。戻り値: 当日のフロー（(Ps,) 配列の dict）."""
        th, Ps, K = self.th, self.Ps, self.K
        prev, O, C, V = (np.broadcast_to(np.asarray(x, float), (Ps,)) for x in (prev, O, C, V))
        lock = np.broadcast_to(np.asarray(lock, bool), (Ps,))
        e = np.where(lock, self.rho, 1.0)[:, None, None]
        j = self.NL + self.t
        self.alive[j] = True
        if tp is None:
            tp = (O + 2 * C) / 3
        tp = np.broadcast_to(np.asarray(tp, float), (Ps,))
        self.cost[:, j] = tp

        # --- A. 寄付での執行（キュー）
        due_f = self.pend_f.pop(0)
        ex_f = due_f * e
        self.pend_f.append(np.zeros_like(due_f))
        self.pend_f[0] += due_f - ex_f            # 未執行分は翌日へ
        due_c = self.pend_c.pop(0)
        ex_c = due_c * e
        self.pend_c.append(np.zeros_like(due_c))
        self.pend_c[0] += due_c - ex_c
        forced_exec = ex_f.sum(axis=(1, 2))
        cure_exec = ex_c.sum(axis=(1, 2))

        # --- B. 日中の自主決済・新規買い
        r = np.log(C / prev)
        dn, up = np.maximum(-r, 0.0), np.maximum(r, 0.0)
        loss = self._loss(C)                                                        # (Ps,NV)
        shv = self.sh.sum(2)
        wsum = np.maximum(shv.sum(1), 1.0)
        loss_bar = (loss * shv).sum(1) / wsum
        near_be = np.abs(loss) <= self.band                                          # |C/cost − 1| ≤ band
        v = (th["b0"][:, None]
             + th["b1"][:, None] * dn[:, None] * np.clip(1 + th["kappa"][:, None] * (loss - loss_bar[:, None]), 0.0, 5.0)
             + th["b2"][:, None] * up[:, None] * (1 + th["bbe"][:, None] * near_be))
        v = np.clip(v, 0.0, 0.8)
        volc_sh = self.sh * v[:, :, None]
        self.sh -= volc_sh
        volc = volc_sh.sum(axis=(1, 2))
        fr = self.frac()
        N = V * np.clip(th["n0"] + th["n1"] * dn * fr + th["n2"] * up, 0.0, 0.6)
        self.sh[:, j, :] += N[:, None] * self.wk
        self.me[:, j, :] = self.m[None, :]
        self.D = self.D - N * tp * self.mbar

        # --- C. 大引けの追証判定
        loss = self._loss(C)
        ratio = self.me - loss[:, :, None]
        trig = (ratio < self.maint) & (self.sh > 0)
        T = np.where(trig, self.sh, 0.0)
        trig_sh = T.sum(axis=(1, 2))
        fr = self.frac()
        p_cash = th["qc"] * fr
        p_sell = np.minimum(th["qs"] + th["qc"] * (1 - fr) * self.eta, 0.98 - p_cash)
        p_forced = np.clip(1 - p_cash - p_sell, 0.0, 1.0)
        T_cash = T * p_cash[:, None, None]
        T_sell = T * p_sell[:, None, None]
        T_forced = T * p_forced[:, None, None]
        target = self.maint + self.buf
        need = np.clip(target - ratio, 0.0, None)                                  # 維持率を戻すのに必要な率
        # 入金で解消：全株保持、me を更新、D を消費
        self.D = self.D - (T_cash * need * self.cost[:, :, None]).sum(axis=(1, 2))
        # 一部売却で解消：x = 1 − ratio/target を売却、残りは保持
        x = np.clip(1 - ratio / target, 0.0, 1.0)
        sell_part = T_sell * x
        keep_part = T_sell - sell_part
        self.pend_c[self.Lc - 1] += sell_part
        self.pend_f[self.Lf - 1] += T_forced
        self.sh = self.sh - T_cash - T_sell - T_forced + T_cash + keep_part
        self.me = np.where(trig, target + loss[:, :, None], self.me)
        self.D = np.maximum(self.D, 0.0)

        S, A = self.totals()
        self.t += 1
        return dict(forced=forced_exec, cure=cure_exec, volc=volc, new=N, trig=trig_sh,
                    sell=forced_exec + cure_exec + volc, S=S, A=A, D=self.frac(),
                    queued_f=sum(self.pend_f).sum(axis=(1, 2)), queued_c=sum(self.pend_c).sum(axis=(1, 2)))

    def due_tomorrow(self):
        """翌営業日の寄付で執行予定の売り（強制＋一部売却）."""
        return self.pend_f[0].sum(axis=(1, 2)), self.pend_c[0].sum(axis=(1, 2))

    def margin_call_ladder(self, prices):
        """価格ごとに、その終値で新たに追証になる株数（現在の sh, me に基づく）."""
        out = []
        for p in prices:
            loss = self._loss(np.full(self.Ps, float(p)))
            trig = ((self.me - loss[:, :, None]) < self.maint) & (self.sh > 0)
            out.append(np.where(trig, self.sh, 0.0).sum(axis=(1, 2)))
        return np.array(out)  # (len(prices), Ps)

    def select(self, idx):
        """パス拡張：アンサンブルの index でコピーした新しいモデルを返す."""
        new = MarginModel.__new__(MarginModel)
        new.__dict__.update({k: v for k, v in self.__dict__.items()})
        new.th = {k: v[idx] for k, v in self.th.items()}
        new.Ps = len(idx)
        for k in ("cost", "sh", "me", "wk", "mbar", "D0", "D"):
            setattr(new, k, getattr(self, k)[idx].copy())
        new.pend_f = [a[idx].copy() for a in self.pend_f]
        new.pend_c = [a[idx].copy() for a in self.pend_c]
        new.alive = self.alive.copy()
        return new


def run_days(model: MarginModel, days: "pd.DataFrame", prev0: float):
    """px の行（open, close, volume, lock_dn, tp）を順に与えて走らせ、日次フローの dict(配列 (Ps,T)) を返す."""
    keys = ("forced", "cure", "volc", "new", "trig", "sell", "S", "A", "D", "queued_f", "queued_c")
    out = {k: np.zeros((model.Ps, len(days))) for k in keys}
    prev = prev0
    for i, row in enumerate(days.itertuples()):
        f = model.step(prev, row.open, row.close, row.volume, bool(row.lock_dn), tp=row.tp)
        for k in keys:
            out[k][:, i] = f[k]
        prev = row.close
    return out
