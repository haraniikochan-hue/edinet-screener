"""構造モデルの推定（クロスエントロピー探索 → 擬似尤度の重み付きアンサンブル）、履歴の実行、検証."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import P
from .structural import THETA_BOUNDS, MarginModel, normalize_theta, run_days

TAU_S, TAU_A = 0.02, 0.01   # 観測ノイズの目安（株数・平均建値の相対誤差）


def sample_theta(rng, n, center=None, scale=0.0):
    th = {}
    for k, (lo, hi) in THETA_BOUNDS.items():
        if center is None:
            th[k] = rng.uniform(lo, hi, n)
        else:
            th[k] = np.clip(rng.choice(center[k], n) + rng.normal(0, (hi - lo) * scale, n), lo, hi)
    return normalize_theta(th)


def take(th, idx):
    return {k: v[idx] for k, v in th.items()}


def history_frame(px: pd.DataFrame, mg: pd.DataFrame, through=None) -> tuple[pd.DataFrame, float]:
    """mg の初日の翌営業日から through（既定: px の最終日）までの価格行と、初日の終値."""
    d0 = mg.date.iloc[0]
    days = px[px.date > d0]
    if through is not None:
        days = days[days.date <= through]
    prev0 = float(px.loc[px.date == d0, "close"].iloc[0])
    return days.reset_index(drop=True), prev0


def simulate_history(theta, px, mg, through=None, n_extra=0):
    days, prev0 = history_frame(px, mg, through)
    model = MarginModel(theta, float(mg.buy_shares.iloc[0]), float(mg.buy_amount.iloc[0]), prev0, len(days) + n_extra)
    out = run_days(model, days, prev0)
    out["dates"] = list(days.date)
    return model, out


def loss_fn(out, days, mg):
    """観測のある日だけで損失（相対誤差を τ で標準化した二乗和）."""
    obs = mg.set_index("date")
    idx = [i for i, d in enumerate(days) if d in obs.index]
    S_obs = obs.loc[[days[i] for i in idx], "buy_shares"].values
    A_obs = obs.loc[[days[i] for i in idx], "buy_amount"].values
    S = out["S"][:, idx]
    avg = out["A"][:, idx] / np.maximum(S, 1)
    eS = (S - S_obs) / S_obs
    eA = (avg - A_obs / S_obs) / (A_obs / S_obs)
    return ((eS / TAU_S) ** 2).sum(1) + ((eA / TAU_A) ** 2).sum(1), eS, eA


def calibrate(px, mg, rng, n_samples=None, n_rounds=None, elite=None, top_k=None, through=None):
    n = n_samples or P["n_samples"]
    R = n_rounds or P["n_rounds"]
    E = elite or P["elite"]
    K = top_k or P["top_k"]
    through = through or mg.date.max()
    th = sample_theta(rng, n)
    best = None
    scales = [None] + list(np.linspace(0.10, 0.02, R - 1))
    for sc in scales:
        if sc is not None:
            th = sample_theta(rng, n, center=best, scale=sc)
        _, out = simulate_history(th, px, mg, through=through)
        lo, _, _ = loss_fn(out, out["dates"], mg)
        order = np.argsort(lo)
        best = take(th, order[:E])
        best_loss = lo[order[:E]]
    ens = take(best, np.arange(K))
    ens_loss = best_loss[:K]
    # 擬似尤度の重み：温度は有効サンプル数 ≈ K/3 になるように選ぶ
    w = _tempered_weights(ens_loss, target_ess=K / 3)
    _, fit = simulate_history(ens, px, mg, through=through)
    lo, eS, eA = loss_fn(fit, fit["dates"], mg)
    diag = dict(loss_best=float(ens_loss[0]), loss_med=float(np.median(ens_loss)),
                rmse_S=float(np.sqrt(np.mean(eS[0] ** 2))), rmse_A=float(np.sqrt(np.mean(eA[0] ** 2))),
                rmse_S_ens=float(np.sqrt(np.mean((np.average(fit["S"], 0, w) / 1 - 0) ** 0 * 0 + 0))),  # placeholder
                dates=fit["dates"])
    # アンサンブル加重中央値のフィット誤差
    obs = mg.set_index("date")
    idx = [i for i, d in enumerate(fit["dates"]) if d in obs.index]
    S_obs = obs.loc[[fit["dates"][i] for i in idx], "buy_shares"].values
    Sw = np.average(fit["S"][:, idx], axis=0, weights=w)
    diag["rmse_S_ens"] = float(np.sqrt(np.mean(((Sw - S_obs) / S_obs) ** 2)))
    diag["fit_S"] = Sw
    diag["fit_avg"] = np.average(fit["A"][:, idx] / fit["S"][:, idx], axis=0, weights=w)
    diag["obs_S"] = S_obs
    diag["obs_avg"] = obs.loc[[fit["dates"][i] for i in idx], "buy_amount"].values / S_obs
    diag["obs_dates"] = [fit["dates"][i] for i in idx]
    return ens, w, diag


def _tempered_weights(loss, target_ess):
    loss = np.asarray(loss) - loss.min()
    lo_T, hi_T = 1e-3, 1e6
    for _ in range(60):
        T = np.sqrt(lo_T * hi_T)
        w = np.exp(-0.5 * loss / T)
        w /= w.sum()
        ess = 1 / np.sum(w ** 2)
        if ess < target_ess:
            lo_T = T
        else:
            hi_T = T
    return w


def weighted_quantile(x, w, qs):
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    cw /= cw[-1]
    return np.interp(qs, cw, x[o])


def param_summary(ens, w):
    rows = []
    for k in THETA_BOUNDS:
        q = weighted_quantile(ens[k], w, [0.5, 0.25, 0.75])
        rows.append(dict(param=k, med=q[0], q25=q[1], q75=q[2], lo=THETA_BOUNDS[k][0], hi=THETA_BOUNDS[k][1]))
    return pd.DataFrame(rows)


def param_corr(ens, w):
    keys = list(THETA_BOUNDS)
    X = np.stack([ens[k] for k in keys], 1)
    mu = np.average(X, 0, w)
    Xc = (X - mu) * np.sqrt(w)[:, None]
    C = Xc.T @ Xc
    sd = np.sqrt(np.diag(C))
    corr = C / np.outer(sd, sd)
    return pd.DataFrame(corr, index=keys, columns=keys)


def walk_forward(px, mg, n_test=8, seed=11, **kw):
    """1日先のアウトオブサンプル検証：d-1 までの観測で推定し、d の残高を予測（最終観測にアンカー）."""
    rows = []
    for k in range(n_test, 0, -1):
        mg_tr = mg.iloc[:-k].reset_index(drop=True)
        target = mg.iloc[-k]
        rng = np.random.default_rng(seed)
        ens, w, _ = calibrate(px, mg_tr, rng, through=mg_tr.date.max(), **kw)
        _, out = simulate_history(ens, px, mg_tr, through=target.date)
        dates = out["dates"]
        i_last = dates.index(mg_tr.date.iloc[-1])
        i_tgt = dates.index(target.date)
        S = out["S"][:, i_tgt] + (mg_tr.buy_shares.iloc[-1] - out["S"][:, i_last])
        q = weighted_quantile(S, w, [0.1, 0.5, 0.9])
        naive = mg_tr.buy_shares.iloc[-1]
        r = float(np.log(px.loc[px.date == target.date, "close"].iloc[0] / px.loc[px.date == mg_tr.date.iloc[-1], "close"].iloc[0]))
        rows.append(dict(date=target.date, actual=target.buy_shares, pred=q[1], lo=q[0], hi=q[2], naive=naive, ret=r))
    return pd.DataFrame(rows)
