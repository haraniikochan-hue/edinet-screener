#!/usr/bin/env python3
"""キオクシア(285A) 短期需給・ホルダー行動モデル v2 — 実行エントリ.

    python3 research/kioxia_flow/run.py --now 8100                # 参考現在値（気配・PTS・海外デリバ）
    python3 research/kioxia_flow/run.py --now 8100 --log          # 未公表日の信用残予測をログに記録
    python3 research/kioxia_flow/run.py --now 8100 --backtest 8   # 1日先予測のウォークフォワード検証（約1分）
    python3 research/kioxia_flow/run.py --quick                   # 探索を軽くして高速確認
オプション: --peer-sox/--peer-mu 前夜の米国リターン（データにない場合）、--gap-sd-scale 参考現在値の信頼度（0=確定, 1=無情報）
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kxflow import calib, data, flows, holders, mc, report, vol  # noqa: E402
from kxflow.config import DATA, P, REPORTS, next_bdays, price_limit  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", type=float, default=None)
    ap.add_argument("--gap-sd-scale", type=float, default=0.5)
    ap.add_argument("--peer-sox", type=float, default=None)
    ap.add_argument("--peer-mu", type=float, default=None)
    ap.add_argument("--paths", type=int, default=P["mc_paths"])
    ap.add_argument("--horizon", type=int, default=P["horizon"])
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--backtest", type=int, default=0)
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--seed", type=int, default=P["seed"])
    a = ap.parse_args()

    D = data.load_all()
    px, mg, hold, ev, peers = D["px"], D["mg"], D["hold"], D["ev"], D["peers"]
    rng = np.random.default_rng(a.seed)
    asof = px.date.max().date()
    last = px.iloc[-1]
    adv = float(px.volume.iloc[-21:].mean())
    h = a.horizon

    # --- returns engine / peers
    eng = vol.ReturnEngine(px)
    al = data.align_peers(px, peers)
    gm = vol.fit_gap_model(px, al)
    pl = data.latest_peer_session(peers)
    sox = a.peer_sox if a.peer_sox is not None else pl.get("SOX", {}).get("ret", 0.0)
    mu = a.peer_mu if a.peer_mu is not None else pl.get("MU", {}).get("ret", 0.0)
    gap_pred = float(gm["gap_coef"] @ np.array([1.0, sox, mu]))
    peer_note = "暫定: 当日セッション未確定の可能性" if (pl.get("SOX", {}).get("date") == asof) else ""
    peer_last = dict(ret={k: dict(ret=v["ret"]) for k, v in pl.items()}, note=peer_note)
    if a.now is not None:
        now = a.now
        gap_shift, gap_scale = math.log(now / last.close), a.gap_sd_scale
    else:
        now = float(last.close * math.exp(gap_pred))
        gap_shift, gap_scale = gap_pred, 1.0
    es = vol.event_study(px)
    cond = eng.conditional_table()
    bots = vol.local_bottoms(px)
    ws = vol.weekly_margin_stats(D["mgw"], bots)

    # --- holders
    coh = holders.cohort_history(px)
    pain = holders.pain_index(px, coh)
    sim = holders.bottom_similarity(px, pain, bots)

    # --- structural calibration + history
    kw = dict(n_samples=3000, n_rounds=3, elite=200, top_k=100) if a.quick else {}
    ens, w, diag = calib.calibrate(px, mg, rng, **kw)
    model, hist = calib.simulate_history(ens, px, mg, n_extra=h + 1)
    i_last = hist["dates"].index(mg.date.iloc[-1])
    S_last = float(mg.buy_shares.iloc[-1])
    anchor = float(np.average(S_last - hist["S"][:, i_last], weights=w))
    pred_rows = []
    tau_obs = 0.015   # 1日先のモデル誤差（ウォークフォワードのMAE≈0.9〜1.3%から。区間の過信を補正）
    for i in range(i_last + 1, len(hist["dates"])):
        S = (hist["S"][:, i] + (S_last - hist["S"][:, i_last])) * (1 + rng.normal(0, tau_obs * math.sqrt(i - i_last), len(w)))
        avg = hist["A"][:, i] / hist["S"][:, i] * (float(mg.buy_amount.iloc[-1]) / S_last) / (hist["A"][:, i_last] / hist["S"][:, i_last])
        qs = calib.weighted_quantile(S, w, [0.1, 0.5, 0.9])
        pred_rows.append((hist["dates"][i], qs[1], qs[0], qs[2], calib.weighted_quantile(avg, w, [0.5])[0]))
    ladder_prices = sorted({int(last.close - price_limit(last.close)), int(round(now)), 8800, int(last.close), 7000, 6324}, reverse=True)
    lad = [(p, float(np.average(x, weights=w))) for p, x in zip(ladder_prices, model.margin_call_ladder(ladder_prices))]
    vs, vc = model.vintage_table()
    ladder_supply = holders.supply_ladder(now, coh, vs, vc, w, adv, eng.sigma_next)

    # --- flows
    tt = flows.toshiba_timing(px, hold, adv)
    qf, qc = model.due_tomorrow()
    imb = flows.opening_imbalance(qf, qc, w, adv, toshiba_rate=0.016)
    pas = flows.passive_demand(adv, now, S_last, eng.sigma_next)
    mech_base = float(np.average(np.median(hist["forced"][:, :i_last + 1] + hist["cure"][:, :i_last + 1], axis=1), weights=w))
    tosh_base = 1.2e6    # 10/2〜27の平均ペース（直近250日の価格変動に織り込み済みとみなす）

    # --- joint MC (scenarios)
    vb = mc.volume_coef(px)
    zprev0 = float(last.ret / eng.sigma_next)
    mcs = {}
    common = dict(n_paths=a.paths, h=h, p_last=float(last.close), adv=adv, vol_b=vb, gap_shift0=gap_shift,
                  gap_sd_scale0=gap_scale, mech_base=mech_base, tosh_base=tosh_base, z_prev0=zprev0)
    for key, kws in (("normal", dict(toshiba="normal")), ("none", dict(toshiba="none")), ("burst", dict(toshiba="burst")),
                     ("noimp", dict(toshiba="normal", impact_on=False)), ("uncond", dict(toshiba="normal", conditional=False))):
        mcs[key] = mc.joint_mc(model, w, eng, np.random.default_rng(a.seed + 1), **common, **kws)
    base = mcs["normal"]
    hits = mc.hit_probs(base["C"], base["O"], [9300, 10000, 10700], [7500, 7000, 6324], horizons=tuple(x for x in (1, 3, 5) if x <= h))
    entry = mc.entry_curve(base["O"], base["C"])
    tac = mc.tactics(base["O"], base["C"], base["LK"], base["F"], S_last - anchor, float(last.close))

    # --- backtest (optional)
    bt = calib.walk_forward(px, mg, a.backtest, **kw) if a.backtest else None

    # --- judgement & checklist
    nd = next_bdays(asof, h)
    C1, O1, LK1 = base["C"][:, 0], base["O"][:, 0], base["LK"][:, 0]
    ec = {r["entry"]: r for r in entry}
    best_entry = max(entry, key=lambda r: r["mean"])
    j = []
    j.append(f"翌営業日の寄付は中央値 {np.median(O1):,.0f}円、大引け {np.median(C1):,.0f}円。張り付き確率 {LK1.mean():.0%}。寄付の売りインバランスは典型出来高の {imb['ratio']:.0%}")
    il = tac.get("寄付で買い→当日大引けで売り（日中ロング; 張り付き時は翌日寄付で売り）", {})
    if il.get("n"):
        j.append(f"唯一プラス期待値が出る戦術は『寄付で買って当日に売る』（平均 {(math.exp(il['mean']) - 1) * 100:+.1f}%、勝率 {il['p_win']:.0%}、RR {il['rr']:.2f}）。理由は張り付き寄付（{(O1 <= last.close - price_limit(last.close) + 0.5).mean():.0%}）では当日の下値が制度上ゼロなこと。ただし張り付いて引けると売れずに翌日へ持ち越す（{LK1.mean():.0%}）")
    j.append(f"エントリー時期別の期待値（day{h}大引け手仕舞い）: 最良は『{best_entry['entry']}』平均 {best_entry['mean'] * 100:+.1f}%（勝率 {best_entry['p_win']:.0%}）。"
             f"day1寄付 {ec[f'day1 寄付']['mean'] * 100:+.1f}% / day1大引け {ec['day1 大引け']['mean'] * 100:+.1f}% / day2大引け {ec.get('day2 大引け', {}).get('mean', float('nan')) * 100:+.1f}%")
    j.append(f"底値類似度のリフト {sim['lift']:.1f}倍、苦痛指数は全履歴の {pain.pain_pct.iloc[-1]:.0%} 分位。過去の底は安値引け→翌日の窓上げで確認されるのが典型")
    j.append(f"信用買い方の余力は推定 {np.average(hist['D'][:, -1], weights=w):.0%} 残り。直近8週の逆張り弾力性は過去の {abs(ws['beta8'] / ws['beta']):.1f}倍で、買い下がりがまだ強い")
    due_future = [d for d in tt["rows"].due.dropna() if d >= asof]
    normal_row = tt["rows"].iloc[0]
    j.append(f"東芝: 10月下旬の参加率が続いていれば次の変更報告は既に提出期限内（{'〜'.join(str(x) for x in (min(due_future), max(due_future))) if due_future else '期限超過＝売りを止めた可能性'}）。"
             f"平常ペース（参加率{normal_row.rate:.1%}）なら {normal_row.status}。集中売りシナリオでは day3 中央値 {np.median(mcs['burst']['C'][:, 2]):,.0f}円（平常 {np.median(base['C'][:, 2]):,.0f}円、東芝なし {np.median(mcs['none']['C'][:, 2]):,.0f}円）")
    checklist = [
        ["信用買い残が予測区間の下限を下回る（ナンピン停止）", "次回公表で判定", f"{pred_rows[0][0]:%m/%d}分 下限 {pred_rows[0][2] / 1e6:.2f}M / 中央値 {pred_rows[0][1] / 1e6:.2f}M" if pred_rows else "—"],
        ["日証金差引残がピーク比 −10%", _jsf_status(D["jsf"]), ""],
        [f"{nd[0]:%m/%d}の安値引け後、{nd[1]:%m/%d}が窓上げで寄り、{nd[0]:%m/%d}終値の上で引ける（過去の底の典型）", f"{nd[1]:%m/%d}に判定", f"P(窓上げ) {(base['O'][:, 1] > C1).mean():.0%} / P(窓上げ維持) {((base['O'][:, 1] > C1) & (base['C'][:, 1] > C1)).mean():.0%}"],
        ["ストップ安に張り付かない", "翌営業日に判定", f"P(張付) {LK1.mean():.0%}"],
        ["米半導体（MU/SNDK/SOX）の下げ止まり（前夜）", "未達" if (sox < -0.02 or mu < -0.05) else "達成", f"SOX {(math.exp(sox) - 1) * 100:+.1f}% MU {(math.exp(mu) - 1) * 100:+.1f}%"],
        ["東芝の新しい変更報告が出ていない", "要確認（EDINET）", ""],
    ]

    # --- prediction log
    logp = DATA / "predictions_log.csv"
    lg = pd.read_csv(logp, dtype=str) if logp.exists() else pd.DataFrame(columns=["made_on", "target_date", "metric", "predicted_median", "predicted_low", "predicted_high", "actual", "note"])
    actual = {(d.date().isoformat(), "buy_shares"): s for d, s in zip(mg.date, mg.buy_shares)}
    actual.update({(d.date().isoformat(), "avg_cost"): A / S for d, S, A in zip(mg.date, mg.buy_shares, mg.buy_amount)})
    actual.update({(d.date().isoformat(), "close"): c for d, c in zip(px.date, px.close)})
    log_rows = []
    if len(lg):
        lg["actual"] = [f"{actual[(t, m)]:.0f}" if (t, m) in actual else (ac if isinstance(ac, str) else "") for t, m, ac in zip(lg.target_date, lg.metric, lg.actual)]
        for r in lg.itertuples():
            if r.actual:
                err = float(r.actual) / float(r.predicted_median) - 1
                inside = float(r.predicted_low) <= float(r.actual) <= float(r.predicted_high)
                log_rows.append(f"{r.made_on}→{r.target_date} {r.metric}: 予測 {float(r.predicted_median):,.0f} [{float(r.predicted_low):,.0f}–{float(r.predicted_high):,.0f}] / 実績 {float(r.actual):,.0f}（誤差 {err:+.1%}、区間内 {'○' if inside else '×'}）")
    if a.log:
        rows = []
        for d, s_med, s_lo, s_hi, a_med in pred_rows:
            rows.append(dict(made_on=dt.date.today().isoformat(), target_date=d.date().isoformat(), metric="buy_shares", predicted_median=f"{s_med:.0f}", predicted_low=f"{s_lo:.0f}", predicted_high=f"{s_hi:.0f}", actual="", note=f"v2 asof {asof} now {now:.0f}"))
        for t in range(h):
            rows.append(dict(made_on=dt.date.today().isoformat(), target_date=nd[t].isoformat(), metric="close", predicted_median=f"{np.median(base['C'][:, t]):.0f}", predicted_low=f"{np.percentile(base['C'][:, t], 10):.0f}", predicted_high=f"{np.percentile(base['C'][:, t], 90):.0f}", actual="", note=f"v2 asof {asof} now {now:.0f}"))
        lg = pd.concat([lg, pd.DataFrame(rows)], ignore_index=True).drop_duplicates(subset=["made_on", "target_date", "metric"], keep="last")
    if len(lg):
        lg.to_csv(logp, index=False)

    ctx = dict(px=px, asof=asof, last=last, now=now, eng=eng, gm=gm, es=es, cond=cond, coh=coh, pain=pain, bots=bots, sim=sim, ws=ws,
               ens=ens, w=w, diag=diag, model=model, hist=hist, mc=mcs, tt=tt, imb=imb, passive=pas, adv=adv, mg=mg, ev=ev, hold=hold,
               peer_last=peer_last, gap_pred=gap_pred, n_paths=a.paths, ladder=lad, ladder_supply=ladder_supply, anchor=anchor,
               hits=hits, entry=entry, tactics=tac, pred_rows=pred_rows, bt=bt, judgement=j, checklist=checklist, log_rows=log_rows)
    text = report.build(ctx)
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / f"{asof}.md").write_text(text, encoding="utf-8")
    print(text)


def _jsf_status(jsf):
    j = jsf.dropna(subset=["net_loan_minus_lend"])
    if len(j) < 2:
        return "データ不足"
    peak = j.net_loan_minus_lend.max()
    cur = j.net_loan_minus_lend.iloc[-1]
    return f"{'達成' if cur <= 0.9 * peak else '未達'}（ピーク比 {cur / peak - 1:+.1%}、目安 {peak * 0.9 / 1e6:.2f}M）"


if __name__ == "__main__":
    main()
