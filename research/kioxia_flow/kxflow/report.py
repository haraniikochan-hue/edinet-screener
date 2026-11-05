"""レポート組み立て（短期トレード向け、Markdown）."""
from __future__ import annotations

import datetime as dt
import math

import numpy as np
import pandas as pd

from .calib import param_corr, param_summary, weighted_quantile
from .config import P, next_bdays, price_limit
from .structural import THETA_NAMES


def M(x):
    return f"{x / 1e6:,.2f}M"


def pct(x, d=1):
    return f"{x * 100:+.{d}f}%"


def lpct(x, d=1):
    """対数リターン → 単純リターン表示."""
    return f"{(math.exp(x) - 1) * 100:+.{d}f}%"


def q(a, p, w=None):
    return weighted_quantile(np.asarray(a), w, [p / 100])[0] if w is not None else float(np.percentile(a, p))


class Report:
    def __init__(self):
        self.L = []

    def w(self, s=""):
        self.L.append(s)

    def table(self, header, rows):
        self.w("| " + " | ".join(header) + " |")
        self.w("|" + "---|" * len(header))
        for r in rows:
            self.w("| " + " | ".join(str(x) for x in r) + " |")
        self.w("")

    def text(self):
        return "\n".join(self.L)


def build(ctx: dict) -> str:
    R = Report()
    px, asof, last, now = ctx["px"], ctx["asof"], ctx["last"], ctx["now"]
    eng, gm, es, cond = ctx["eng"], ctx["gm"], ctx["es"], ctx["cond"]
    coh, pain, bots, sim, ws = ctx["coh"], ctx["pain"], ctx["bots"], ctx["sim"], ctx["ws"]
    ens, w, diag, model, hist = ctx["ens"], ctx["w"], ctx["diag"], ctx["model"], ctx["hist"]
    mcs, tt, imb, pas, adv = ctx["mc"], ctx["tt"], ctx["imb"], ctx["passive"], ctx["adv"]
    mg, ev = ctx["mg"], ctx["ev"]
    lim = price_limit(last.close)
    nd = next_bdays(asof, 5)
    S_last = float(mg.buy_shares.iloc[-1])

    R.w(f"# キオクシア(285A) 短期需給・ホルダー行動モデル v2 — 基準日 {asof}")
    R.w(f"- 終値 {last.close:,.0f}円（{lpct(last.ret)}） / 参考現在値 **{now:,.0f}円**（終値比 {pct(now / last.close - 1)}）"
        f" / 翌営業日 {nd[0]:%m/%d} の制限値幅 ±{lim:,.0f}円 → ストップ安 **{last.close - lim:,.0f}** ・ストップ高 {last.close + lim:,.0f}")
    R.w(f"- 条件付きボラ（EWMA, λ={eng.lam:.2f}）: 翌日 σ **{eng.sigma_next:.1%}**（窓 {math.sqrt(eng.var_g_next):.1%} / 日中 {math.sqrt(eng.var_i_next):.1%}）"
        f" / ADV21 {M(adv)}株 / 生成 {dt.datetime.now():%Y-%m-%d %H:%M}")
    up = ev[(ev.date.dt.date > asof) & (ev.date.dt.date <= nd[-1])]
    if len(up):
        R.w("- 直近5営業日のイベント: " + " / ".join(f"{r.date:%m/%d} {r.event}" for r in up.itertuples()))
    pe = ctx["peer_last"]
    R.w(f"- 直前の米国セッション（{pe.get('note', '')}）: " + ", ".join(f"{k} {lpct(v['ret'])}" for k, v in pe["ret"].items())
        + f" → 窓モデルの予測 {lpct(ctx['gap_pred'])}（残差σ {gm['gap_resid_sd']:.1%}）; 参考現在値は {pct(now / last.close - 1)}（窓σの {abs(math.log(now / last.close)) / math.sqrt(eng.var_g_next):.1f}倍）")
    R.w("")

    # ---------------------------------------------------------------- 1. next day
    R.w(f"## 1. 翌営業日（{nd[0]:%m/%d}）の見通し — 統合MC（{ctx['n_paths']:,}本）")
    base = mcs["normal"]
    O, C, LK, F = base["O"], base["C"], base["LK"], base["F"]
    R.table(["", "p10", "p25", "p50", "p75", "p90"],
            [["寄付"] + [f"{q(O[:, 0], p):,.0f}" for p in (10, 25, 50, 75, 90)],
             ["大引け"] + [f"{q(C[:, 0], p):,.0f}" for p in (10, 25, 50, 75, 90)],
             ["日中（寄→引）"] + [lpct(q(np.log(C[:, 0] / O[:, 0]), p)) for p in (10, 25, 50, 75, 90)]])
    R.w(f"- ストップ安張り付きで引ける確率 **{LK[:, 0].mean():.0%}**（寄付で張り付き {(O[:, 0] <= last.close - lim + 0.5).mean():.0%}）"
        f" / 日中が陽線の確率 {(C[:, 0] > O[:, 0]).mean():.0%}")
    R.w(f"- 寄付の予定売り: 強制決済 {M(imb['forced'])} ＋ 一部売却 {M(imb['cure'])} ＋ 東芝（平常） {M(imb['toshiba'])} ＝ {M(imb['total'])}"
        f" vs 寄付の典型出来高 {M(imb['open_vol'])}（ADVの12%仮定）→ **インバランス {imb['ratio']:.0%}**")
    lad = ctx["ladder"]
    R.w("- 終値ごとに新たに追証になる株数（現在の建玉構成から）: " + ", ".join(f"{p:,}円→{M(v)}" for p, v in lad))
    R.w(f"- 日次フロー（中央値）: 強制 {M(np.median(F['forced'][:, 0]))}・一部売却 {M(np.median(F['cure'][:, 0]))}・自主決済 {M(np.median(F['volc'][:, 0]))}"
        f"・新規買い {M(np.median(F['new'][:, 0]))}・東芝(平均) {M(base['TOSH'][:, 0].mean())} / 当日の追証発生 {M(np.median(F['trig'][:, 0]))}"
        f" / 信用買い残 {M(np.median(F['S'][:, 0]) + ctx['anchor'])} / 余力残 {np.median(F['D'][:, 0]):.0%}")
    R.w(f"- 追証の時間割: {nd[0]:%m/%d}の追証 → 一部売却は{nd[1]:%m/%d}寄付・強制決済は{nd[3]:%m/%d}寄付（11/5分はそれぞれ {nd[0]:%m/%d}・{nd[2]:%m/%d}）。寄付の売りが膨らむのは **{nd[2]:%m/%d}〜{nd[3]:%m/%d}**")
    R.w("")

    # ---------------------------------------------------------------- 2. 1-5 days
    R.w("## 2. 1〜5営業日の経路と戦術")
    hp = ctx["hits"]
    R.table(["営業日", "↑9,300", "↑10,000", "↑10,700", "↓7,500", "↓7,000", "↓6,324"],
            [[r["h"], f"{r['up9300']:.0%}", f"{r['up10000']:.0%}", f"{r['up10700']:.0%}", f"{r['dn7500']:.0%}", f"{r['dn7000']:.0%}", f"{r['dn6324']:.0%}"] for r in hp])
    R.w("日次（中央値 [p10–p90]）:")
    rows = []
    for t in range(C.shape[1]):
        rows.append([f"{nd[t]:%m/%d}", f"{q(O[:, t], 50):,.0f}", f"{q(C[:, t], 50):,.0f} [{q(C[:, t], 10):,.0f}–{q(C[:, t], 90):,.0f}]",
                     f"{LK[:, t].mean():.0%}", M(np.median(F["forced"][:, t] + F["cure"][:, t])), M(np.median(F["volc"][:, t])),
                     M(np.median(F["new"][:, t])), M(base["TOSH"][:, t].mean()), M(np.median(F["S"][:, t]) + ctx["anchor"]), f"{np.median(F['D'][:, t]):.0%}"])
    R.table(["日付", "寄付", "大引け", "張付", "強制+一部売却", "自主決済", "新規買い", "東芝(平均)", "信用買い残", "余力"], rows)
    R.w("**エントリー時期別の期待値（day5 大引けで手仕舞い、東芝=平常）**")
    R.table(["エントリー", "想定価格(中央値)", "平均", "中央値", "勝率", "p10", "p90"],
            [[r["entry"], f"{r['entry_med']:,.0f}", lpct(r["mean"]), lpct(r["med"]), f"{r['p_win']:.0%}", lpct(r["p10"]), lpct(r["p90"])] for r in ctx["entry"]])
    R.w("**戦術別（東芝=平常）** — RR = (勝ち平均×勝率)/(負け平均×負率)")
    rows = []
    for k, v in ctx["tactics"].items():
        if v.get("n", 0) >= 50:
            rows.append([k, f"{v['n']:,}", lpct(v["mean"]), lpct(v["med"]), f"{v['p_win']:.0%}", lpct(v["p5"]), lpct(v["p95"]), f"{v['rr']:.2f}"])
        else:
            rows.append([k, f"{v.get('n', 0)}", "—", "—", "—", "—", "—", "—"])
    R.table(["戦術", "n", "平均", "中央値", "勝率", "p5", "p95", "RR"], rows)
    R.w("**感応度（day3 大引けの中央値 / ↓7,000到達確率(5日) / ↑9,300(5日)）**")
    rows = []
    for lab, key in (("東芝なし", "none"), ("東芝=平常", "normal"), ("東芝=集中売り(毎日6〜15%)", "burst"), ("インパクトなし（純粋な外生ショック）", "noimp"), ("無条件ブートストラップ", "uncond")):
        m = mcs.get(key)
        if m is None:
            continue
        Cm, Om = m["C"], m["O"]
        mx = np.maximum(Cm.max(1), Om.max(1)); mn = np.minimum(Cm.min(1), Om.min(1))
        rows.append([lab, f"{np.median(Cm[:, 2]):,.0f}", f"{(mn <= 7000).mean():.0%}", f"{(mx >= 9300).mean():.0%}", f"{m['LK'][:, 0].mean():.0%}"])
    R.table(["シナリオ", "day3終値 中央値", "↓7,000", "↑9,300", "初日張付"], rows)

    # ---------------------------------------------------------------- 3. holders
    R.w("## 3. ホルダーの苦痛と行動")
    R.w(f"- 回転率減衰モデル（α={P['turnover_alpha']}）の参照価格（能動的な浮動株の平均取得コスト） RP = **{coh['rp'][-1]:,.0f}円** → 参考現在値はその {pct(now / coh['rp'][-1] - 1)}"
        f"（Grinblatt–Han の CGO=(P−RP)/P では {pct((now - coh['rp'][-1]) / now)}）、能動的浮動株の含み損比率 {coh['underwater'][-1]:.0%}")
    pr = pain.iloc[-1]
    R.w(f"- 苦痛指数 {pr.pain:+.2f}（全履歴のパーセンタイル **{pr.pain_pct:.0%}**）: 構成 CGO {pr.cgo:+.0%}, 5日 {pct(pr.ret5)}, 20日 {pct(pr.ret20)}, 高値から {pct(pr['dd'])}")
    pb = pain.set_index("date").loc[bots.date]
    R.w("- 過去の局所底（前後10日の最安値→10日以内に+15%）での同指数: " + ", ".join(f"{d:%y/%m/%d} {v:+.2f}" for d, v in zip(pb.index, pb.pain)))
    bf = sim["bottoms_feat"]
    R.w(f"- 底値の特徴（中央値）: 5日 {pct(bf.ret5.median())}, 出来高/ADV {bf.vol.median():.2f}, 終値位置 {bf.pos.median():.0%}, CGO {bf.cgo.median():+.0%}"
        f" ← **安値引け（終値位置が低い）が普通で、出来高のピークは必須でない**。反転は翌日の窓上げで確認される形が多い")
    R.w(f"- kNN 底値類似度（特徴: 5日・20日リターン、出来高/ADV、終値位置、CGO、含み損比率; k=25）: 近傍のうち底±2日だった比率 **{sim['share']:.0%}**"
        f"（ベースレート {sim['base']:.0%}、リフト {sim['lift']:.1f}倍）; 最近傍 {', '.join(str(d)[:10] for d in sim['nn_dates'][:5])}")
    R.w(f"- 週次の信用買い残の弾力性（{ws['n']}週）: Δlog(買い残) = {ws['alpha']:+.3f} {ws['beta']:+.2f}×週次リターン（R² {ws['r2']:.2f}）; **直近8週は {ws['beta8']:+.2f}**"
        f" → 過去より{abs(ws['beta8'] / ws['beta']):.1f}倍強い逆張り（下落ほど買い増す）")
    if len(ws["around"]):
        R.w("- 過去の底の前3週／後3週の信用買い残の変化: " + ", ".join(f"{r.bottom:%y/%m/%d} {pct(r.pre3w, 0)}/{pct(r.post3w, 0)}" for r in ws["around"].itertuples())
            + " → **底の前に買い残が減る法則はない**（9回中4回は増えながら底打ち）")
    R.w("")
    # vintage table of margin longs
    vs, vc = model.vintage_table()
    R.w("**信用買い残の建値分布（構造モデル、加重平均）と参考現在値での損益**")
    rows = []
    edges = [(0, 10000), (10000, 12000), (12000, 14000), (14000, 16000), (16000, 19000), (19000, 99999)]
    for lo, hi in edges:
        m = (vc >= lo) & (vc < hi)
        sh = np.average((vs * m).sum(1), weights=w)
        if sh < 1e4:
            continue
        cst = np.average(((vs * vc * m).sum(1)) / np.maximum((vs * m).sum(1), 1), weights=w)
        rows.append([f"{lo:,}–{hi:,}" if hi < 99999 else f"{lo:,}+", M(sh), f"{sh / np.average(vs.sum(1), weights=w):.0%}", f"{cst:,.0f}", pct(now / cst - 1, 0)])
    R.table(["建値帯", "株数", "比率", "平均建値", "損益"], rows)
    sl = ctx["ladder_supply"]
    if len(sl):
        R.w("**戻り売りラダー（建値±3%到達時の供給: 信用35%・現物10%が手放すと仮定）**")
        R.table(["価格帯", "信用", "現物", "合計", "ADV比", "1日で吸収時のインパクト"],
                [[f"{r.lo:,}–{r.hi:,}", M(r.margin), M(r.cash), M(r.total), f"{r.adv_days:.2f}日", pct(-r.impact)] for r in sl.itertuples()])

    # ---------------------------------------------------------------- 4. structural
    R.w("## 4. 構造モデル（信用買い方）の推定")
    R.w(f"- 観測 {len(diag['obs_dates'])}日の信用買い残（株数・平均建値）に適合。最良 loss {diag['loss_best']:.0f}（中央値 {diag['loss_med']:.0f}）、"
        f"株数 RMSE {diag['rmse_S']:.1%}（アンサンブル加重 {diag['rmse_S_ens']:.1%}）、平均建値 RMSE {diag['rmse_A']:.1%}。有効サンプル数 {1 / np.sum(w ** 2):.0f}/{len(w)}")
    ps = param_summary(ens, w)
    R.table(["パラメータ", "中央値", "25–75%", "探索範囲"],
            [[THETA_NAMES[r.param], f"{r.med:.3f}", f"{r.q25:.3f}–{r.q75:.3f}", f"{r.lo}–{r.hi}"] for r in ps.itertuples()])
    D0 = 10 ** ens["lD0"]
    R.w(f"- 買い方の追加資金余力（初期）: {weighted_quantile(D0, w, [0.5])[0] / 1e8:,.0f}億円 [{weighted_quantile(D0, w, [0.25])[0] / 1e8:,.0f}–{weighted_quantile(D0, w, [0.75])[0] / 1e8:,.0f}]"
        f" → 現在の残り **{np.average(hist['D'][:, -1], weights=w):.0%}**")
    cr = param_corr(ens, w)
    pairs = sorted([(a, b, cr.loc[a, b]) for i, a in enumerate(cr.index) for b in cr.columns[i + 1:] if abs(cr.loc[a, b]) > 0.4], key=lambda x: -abs(x[2]))
    R.w("- 識別性（アンサンブル内の相関 |ρ|>0.4）: " + (", ".join(f"{a}×{b} {v:+.2f}" for a, b, v in pairs[:8]) if pairs else "なし")
        + " ← 相関の強い組は個別には決まらない（合計の挙動のみ識別）")
    R.w("**日次フロー分解（加重中央値、直近8日）**")
    rows = []
    for i in range(max(0, len(hist["dates"]) - 8), len(hist["dates"])):
        d = hist["dates"][i]
        f = {k: weighted_quantile(hist[k][:, i], w, [0.5])[0] for k in ("forced", "cure", "volc", "new", "trig", "S", "D")}
        obs = mg[mg.date == d]
        so = f"{obs.buy_shares.iloc[0] / 1e6:.2f}M" if len(obs) else "（未公表）"
        rows.append([f"{d:%m/%d}", f"{px.loc[px.date == d, 'close'].iloc[0]:,.0f}", M(f["forced"]), M(f["cure"]), M(f["volc"]), M(f["new"]), M(f["trig"]), M(f["S"]), so, f"{f['D']:.0%}"])
    R.table(["日付", "終値", "強制", "一部売却", "自主決済", "新規買い", "追証発生", "モデル残高", "実績", "余力"], rows)
    for d, s_med, s_lo, s_hi, a_med in ctx["pred_rows"]:
        R.w(f"- **{d:%m/%d}分の信用買い残（未公表）の予測: {M(s_med)}株 [{M(s_lo)}–{M(s_hi)}]（前回比 {pct(s_med / S_last - 1)}）、平均建値 {a_med:,.0f}円**"
            f" — 下限割れ＝ナンピン停止・投げ優勢、上限超え＝買い下がり継続")
    if ctx.get("bt") is not None:
        bt = ctx["bt"]
        R.w("**ウォークフォワード検証（1日先、アウトオブサンプル）**")
        R.table(["日付", "当日リターン", "実績", "予測 [10–90%]", "誤差", "横ばい予測の誤差"],
                [[f"{r.date:%m/%d}", pct(r.ret), M(r.actual), f"{M(r.pred)} [{M(r.lo)}–{M(r.hi)}]", pct(r.pred / r.actual - 1), pct(r.naive / r.actual - 1)] for r in bt.itertuples()])
        mae, mae_n = np.mean(np.abs(bt.pred / bt.actual - 1)), np.mean(np.abs(bt.naive / bt.actual - 1))
        cov = np.mean((bt.actual >= bt.lo) & (bt.actual <= bt.hi))
        hit = np.mean(np.sign(bt.pred - bt.naive) == np.sign(bt.actual - bt.naive))
        R.w(f"- MAE モデル {mae:.1%} / 横ばい {mae_n:.1%}、増減方向の的中 {hit:.0%}、80%区間のカバー率 {cov:.0%}\n")

    # ---------------------------------------------------------------- 5. empirical references
    R.w("## 5. 実績に基づく参照分布（Kioxia の全履歴 " + f"{len(px)}日）")
    rows = []
    for k, lab in (("day_le_m10", "日次 ≤ −10%"), ("day_le_m15", "日次 ≤ −15%"), ("two_day_le_m20", "2日で ≤ −20%"), ("lock_dn", "ストップ安張り付き"), ("touch_dn_not_lock", "ストップ安タッチ（張り付かず）")):
        e = es.get(k)
        if e is None or len(e) == 0:
            rows.append([lab, 0, "—", "—", "—", "—", "—", "—", "—"])
            continue
        rows.append([lab, len(e), pct(e.gap1.median()), pct(e.intra1.median()), f"{pct(e.c1.median())} ({(e.c1 > 0).mean():.0%})",
                     pct(e.c3.median()), pct(e.c5.median()), pct(e.max5.median()), pct(e.min5.median())])
    R.table(["イベント", "n", "翌日の窓", "翌日の日中", "翌日終値(勝率)", "3日後", "5日後", "5日内の最大上昇", "5日内の最大下落"], rows)
    g, gu = es["gapdown5_intra"], es["gapup5_intra"]
    R.w(f"- 窓 ≤ −5% で寄った日（n={len(g)}）の日中: 中央値 {pct(g.intra.median())}、陽線 {(g.intra > 0).mean():.0%} / 窓 ≥ +5%（n={len(gu)}）: 中央値 {pct(gu.intra.median())}、陽線 {(gu.intra > 0).mean():.0%}")
    R.w("- 条件付きブートストラップの参照（直近250日、分位ビン）: " + " / ".join(
        f"前日{['最弱', '弱', '中', '強', '最強'][r['bin']]}→窓 {lpct(r['gap_med'])}({r['gap_pos']:.0%})" for r in cond))
    R.w("- 窓の分位→日中: " + " / ".join(f"窓{['最弱', '弱', '中', '強', '最強'][r['bin']]}→{lpct(r['intra_med'])}({r['intra_pos']:.0%})" for r in cond))
    b = gm["gap_coef"]
    R.w(f"- 窓モデル（直近{gm['n']}日）: 窓 = {b[0]:+.3f} + {b[1]:.2f}×SOX(前夜) + {b[2]:.2f}×MU(前夜)、R² {gm['gap_r2']:.2f}")
    rb = gm["ret_coef"]
    rr = gm["ret_resid"]
    R.w(f"- 日次リターンのピアβ: {rb[1]:.2f}×SOX(前夜) + {rb[2]:.2f}×SKハイニックス(同日); **βで説明できない固有リターンの累計: 5日 {lpct(rr.tail(5).sum())}、10日 {lpct(rr.tail(10).sum())}、20日 {lpct(rr.tail(20).sum())}**"
        " → 需給（信用整理・東芝・NAND見通し）主導の下落")
    R.w("")

    # ---------------------------------------------------------------- 6. large holders
    R.w("## 6. 大口フロー")
    R.w(f"- 東芝: 最新報告 {tt['last_pct']:.2f}%（{tt['last_date']}計算、{M(tt['shares'])}株）。次の1%減の報告には {M(tt['threshold'])}株の追加売却が必要。観測された参加率 {', '.join(f'{x:.1%}' for x in tt['part_obs'])}")
    R.table(["参加率の仮定", "計算日以降の推定売却", "到達日", "報告期限", "状態"],
            [[f"{r.rate:.1%}", M(r.sold), r.cross or "—", r.due or "—", r.status] for r in tt["rows"].itertuples()])
    R.w("  → 売り続けていれば**次の変更報告はいつ出てもおかしくない**（10/2〜27は1日0.3M株の平常ペースと、TOPIX第1段階に合わせた10/27〜29の集中売りの二段構え。次の流動性イベントは11/27）")
    jp = ctx["hold"][ctx["hold"].kind == "short_report"].sort_values("calc_date").tail(1)
    if len(jp):
        r = jp.iloc[0]
        R.w(f"- 大量空売り報告: {r.entity} {r.pct:.2f}%（{M(r.shares)}株, {r.calc_date:%m/%d}）= ADVの{r.shares / adv:.2f}日分。逆日歩なし・日証金貸株残 ほぼゼロ → 踏み上げの燃料はこれだけ")
    R.w("- TOPIX浮動株比率 第2段階（11/27大引け、適用11/30）: " + " / ".join(f"保有率{r.share:.0%}→{M(r.shares)}株(ADV{r.adv_days:.2f}日, 信用買い残の{r.x_margin:.1f}倍, +{r.impact:.1%})" for r in pas.itertuples()))
    R.w("")

    # ---------------------------------------------------------------- 7. decision
    R.w("## 7. 判断")
    for line in ctx["judgement"]:
        R.w(f"- {line}")
    R.w("")
    R.w("**チェックリスト（自動評価）**")
    R.table(["条件", "状態", "値"], ctx["checklist"])

    if ctx.get("log_rows"):
        R.w("## 8. 過去予測の検証")
        for line in ctx["log_rows"]:
            R.w(f"- {line}")
        R.w("")
    R.w("---")
    R.w("*モデル推計であり投資助言ではない。主な仮定は README 参照（追証ライン20%・強制決済は3営業日後の寄付・張り付き日の執行率25%・平方根インパクト係数 Y〜U(0.3,0.9)・機械的フローと東芝売りの平常水準からの超過分にのみ適用・東芝は平常/集中の2レジーム）。*")
    return R.text()
