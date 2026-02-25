"""
Technical / Momentum Factor Analysis
Task #4: テクニカル・モメンタム系指標と株価リターンの相関分析
"""
import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

DATA = "/Users/harann/edinet-screener/data"

# ── 1. Load data ──────────────────────────────────────────────
sp = pd.read_csv(f"{DATA}/stock_prices.csv")
hr = pd.read_csv(f"{DATA}/historical_returns.csv")
co = pd.read_csv(f"{DATA}/companies.csv")

print(f"stock_prices: {sp.shape}, columns: {list(sp.columns)}")
print(f"historical_returns: {hr.shape}, columns: {list(hr.columns)}")
print(f"companies: {co.shape}, columns: {list(co.columns)}")

# ── 2. Merge ──────────────────────────────────────────────────
# stock_prices has ticker, historical_returns has ticker => direct join
df = sp.merge(hr, on="ticker", how="inner")
print(f"\nMerged: {df.shape[0]} rows")

# ── 3. Derive technical indicators ───────────────────────────
df["ma50_deviation"] = (df["currentPrice"] - df["fiftyDayAverage"]) / df["fiftyDayAverage"]
df["ma200_deviation"] = (df["currentPrice"] - df["twoHundredDayAverage"]) / df["twoHundredDayAverage"]
df["range_52w_position"] = (df["currentPrice"] - df["fiftyTwoWeekLow"]) / (df["fiftyTwoWeekHigh"] - df["fiftyTwoWeekLow"])
df["ma_crossover"] = df["fiftyDayAverage"] / df["twoHundredDayAverage"]
df["drawdown_from_52w_high"] = (df["currentPrice"] - df["fiftyTwoWeekHigh"]) / df["fiftyTwoWeekHigh"]

print("\n=== Derived Indicators Sample ===")
print(df[["ticker", "ma50_deviation", "ma200_deviation", "range_52w_position",
          "ma_crossover", "drawdown_from_52w_high"]].head(10).to_string())

# ── 4. Define factor universe ────────────────────────────────
# Existing technical + derived
tech_factors = [
    # Existing raw
    "beta",
    "fiftyDayAverage", "twoHundredDayAverage",
    "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
    # Derived
    "ma50_deviation", "ma200_deviation", "range_52w_position",
    "ma_crossover", "drawdown_from_52w_high",
    # Valuation (for combo analysis later)
    "priceToBook", "trailingPE", "forwardPE", "dividendYield",
    "returnOnEquity", "debtToEquity",
]
return_cols = ["return_1y", "return_3y", "return_5y"]

# ── 5. Winsorize at 1%/99% ───────────────────────────────────
for col in tech_factors + return_cols:
    if col in df.columns:
        s = df[col].dropna()
        if len(s) > 0:
            lo, hi = s.quantile(0.01), s.quantile(0.99)
            df[col] = df[col].clip(lo, hi)

# ── 6. Spearman correlation: all factors vs returns ──────────
print("\n" + "="*80)
print("SPEARMAN CORRELATION: Technical Factors vs Future Returns")
print("="*80)

results = []
for fac in tech_factors:
    if fac not in df.columns:
        continue
    for ret in return_cols:
        sub = df[[fac, ret]].dropna()
        if len(sub) < 30:
            continue
        rho, pval = stats.spearmanr(sub[fac], sub[ret])
        results.append({
            "factor": fac,
            "return_horizon": ret,
            "spearman_rho": round(rho, 4),
            "p_value": round(pval, 6),
            "n": len(sub),
            "significant": "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        })

corr_df = pd.DataFrame(results).sort_values("spearman_rho", key=abs, ascending=False)
print(corr_df.to_string(index=False))

# ── 7. Pivot: factors x return horizons ──────────────────────
print("\n" + "="*80)
print("CORRELATION PIVOT (factor x horizon)")
print("="*80)
pivot = corr_df.pivot_table(index="factor", columns="return_horizon", values="spearman_rho")
pivot = pivot.reindex(columns=["return_1y", "return_3y", "return_5y"])
pivot["abs_avg"] = pivot.abs().mean(axis=1)
pivot = pivot.sort_values("abs_avg", ascending=False)
print(pivot.round(4).to_string())

# ── 8. Momentum effect: quintile analysis ────────────────────
print("\n" + "="*80)
print("MOMENTUM QUINTILE ANALYSIS")
print("="*80)

momentum_factors = ["ma50_deviation", "ma200_deviation", "range_52w_position",
                    "ma_crossover", "drawdown_from_52w_high"]

for mf in momentum_factors:
    sub = df[[mf] + return_cols].dropna()
    if len(sub) < 50:
        continue
    sub["quintile"] = pd.qcut(sub[mf], 5, labels=["Q1(low)", "Q2", "Q3", "Q4", "Q5(high)"], duplicates="drop")
    print(f"\n--- {mf} ---")
    qr = sub.groupby("quintile", observed=True)[return_cols].agg(["mean", "median", "count"])
    # Flatten column names
    qr.columns = [f"{r}_{s}" for r, s in qr.columns]
    print(qr.round(4).to_string())
    # Q5-Q1 spread
    for ret in return_cols:
        q5 = sub[sub["quintile"] == "Q5(high)"][ret].mean()
        q1 = sub[sub["quintile"] == "Q1(low)"][ret].mean()
        spread = q5 - q1
        print(f"  {ret} Q5-Q1 spread: {spread:.4f}")

# ── 9. Mean Reversion test ───────────────────────────────────
print("\n" + "="*80)
print("MEAN REVERSION TEST")
print("  If past momentum (positive) leads to negative future returns => mean reversion")
print("  If past momentum (positive) leads to positive future returns => momentum continuation")
print("="*80)

for mf in ["ma50_deviation", "ma200_deviation", "drawdown_from_52w_high"]:
    sub = df[[mf] + return_cols].dropna()
    if len(sub) < 50:
        continue
    # Split into extreme groups
    lo_thresh = sub[mf].quantile(0.2)
    hi_thresh = sub[mf].quantile(0.8)
    losers = sub[sub[mf] <= lo_thresh]
    winners = sub[sub[mf] >= hi_thresh]
    print(f"\n--- {mf} ---")
    for ret in return_cols:
        w_ret = winners[ret].mean()
        l_ret = losers[ret].mean()
        print(f"  {ret}: Winners(top20%)={w_ret:.4f}, Losers(bottom20%)={l_ret:.4f}, "
              f"Diff={w_ret-l_ret:.4f} => {'MOMENTUM' if w_ret > l_ret else 'MEAN REVERSION'}")

# ── 10. Beta quintile analysis ────────────────────────────────
print("\n" + "="*80)
print("BETA QUINTILE ANALYSIS (Low Beta Anomaly Test)")
print("="*80)

beta_sub = df[["beta"] + return_cols].dropna()
print(f"N with beta: {len(beta_sub)}")
if len(beta_sub) >= 50:
    beta_sub["quintile"] = pd.qcut(beta_sub["beta"], 5, labels=["Q1(low)", "Q2", "Q3", "Q4", "Q5(high)"], duplicates="drop")
    qr = beta_sub.groupby("quintile", observed=True)[return_cols].agg(["mean", "median", "count"])
    qr.columns = [f"{r}_{s}" for r, s in qr.columns]
    print(qr.round(4).to_string())
    for ret in return_cols:
        q5 = beta_sub[beta_sub["quintile"] == "Q5(high)"][ret].mean()
        q1 = beta_sub[beta_sub["quintile"] == "Q1(low)"][ret].mean()
        print(f"  {ret} Q5-Q1 spread: {q5-q1:.4f} => {'HIGH beta wins' if q5 > q1 else 'LOW BETA ANOMALY confirmed'}")

# ── 11. Value x Momentum combo ────────────────────────────────
print("\n" + "="*80)
print("VALUE x MOMENTUM COMBINATION STRATEGY")
print("="*80)

# Value: low PBR | low forwardPE
# Momentum: high ma50_deviation | high range_52w_position

for val_fac, val_label, val_ascending in [
    ("priceToBook", "Low PBR", True),
    ("forwardPE", "Low Forward PE", True),
]:
    for mom_fac, mom_label in [
        ("ma50_deviation", "High MA50 Dev"),
        ("range_52w_position", "High 52W Range Pos"),
        ("ma_crossover", "MA Crossover > 1"),
    ]:
        sub = df[[val_fac, mom_fac] + return_cols].dropna()
        if len(sub) < 100:
            continue
        # Terciles
        val_lo = sub[val_fac].quantile(0.33)
        val_hi = sub[val_fac].quantile(0.67)
        mom_lo = sub[mom_fac].quantile(0.33)
        mom_hi = sub[mom_fac].quantile(0.67)

        if val_ascending:
            value_stocks = sub[sub[val_fac] <= val_lo]
            growth_stocks = sub[sub[val_fac] >= val_hi]
        else:
            value_stocks = sub[sub[val_fac] >= val_hi]
            growth_stocks = sub[sub[val_fac] <= val_lo]

        momentum_up = sub[sub[mom_fac] >= mom_hi]

        # Combo: value AND momentum
        combo = sub[(sub[val_fac] <= val_lo) & (sub[mom_fac] >= mom_hi)] if val_ascending \
            else sub[(sub[val_fac] >= val_hi) & (sub[mom_fac] >= mom_hi)]

        # Anti-combo: expensive AND weak momentum
        anti_combo = sub[(sub[val_fac] >= val_hi) & (sub[mom_fac] <= mom_lo)] if val_ascending \
            else sub[(sub[val_fac] <= val_lo) & (sub[mom_fac] <= mom_lo)]

        if len(combo) < 10 or len(anti_combo) < 10:
            continue

        print(f"\n--- {val_label} x {mom_label} ---")
        print(f"  Combo (value+momentum): N={len(combo)}")
        print(f"  Anti-combo (expensive+weak): N={len(anti_combo)}")
        print(f"  Universe: N={len(sub)}")
        for ret in return_cols:
            c_mean = combo[ret].mean()
            ac_mean = anti_combo[ret].mean()
            u_mean = sub[ret].mean()
            print(f"  {ret}: Combo={c_mean:.4f}, Anti={ac_mean:.4f}, Universe={u_mean:.4f}, "
                  f"Combo-Anti={c_mean-ac_mean:.4f}")

# ── 12. Top factors summary ──────────────────────────────────
print("\n" + "="*80)
print("TOP 10 FACTOR-RETURN PAIRS BY |SPEARMAN rho|")
print("="*80)
top10 = corr_df.head(10)
for _, row in top10.iterrows():
    print(f"  {row['factor']:30s} vs {row['return_horizon']:12s}: "
          f"rho={row['spearman_rho']:+.4f}  p={row['p_value']:.6f} {row['significant']}  N={row['n']}")

print("\n=== ANALYSIS COMPLETE ===")
