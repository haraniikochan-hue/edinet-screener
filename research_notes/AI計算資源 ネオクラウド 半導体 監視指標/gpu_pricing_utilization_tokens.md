# GPU compute pricing, utilization, secondhand GPU values, and AI token pricing/volume: indicator catalogue (as of 26 Oct 2026)

Research date: 2026-10-26. Live pulls (OpenRouter API, Vast.ai API) were taken 2026-10-26 ~06:05 UTC. Dated values are labelled. "Signal" thresholds in the Inferences sections are this researcher's judgement, not provider statements.

---

## 1. GPU rental price indices and exchange-traded / derivative products

### Takeaway
At least five daily-or-faster public GPU rental benchmarks exist (Silicon Data, Ornn OCPI, SemiAnalysis, getdeploying, plus live marketplace order books). All show H100/H200/B200 rents rising sharply into late Oct 2026, but levels differ a lot by method (B200: ~$6.60 Silicon Data vs ~$9.70 Ornn). Exchange futures (CME/Silicon Data, ICE/Ornn) are still awaiting regulatory clearance as of ~21 Oct 2026. Kalshi event contracts and CME-distributed (non-tradable) forward curves already exist.

### Cited Findings

**A. Silicon Data "Silicon Index" (SDH100RT, SDA100RT, SDB200RT, plus H200 / B300 / MI300X / RAM / LLM Token indices)**
- Index family listed on the site: H100 (Neocloud & Hyperscaler, ticker SDH100RT), A100 (SDA100RT), B200 (SDB200RT), plus daily H200, B300, MI300X indices, a RAM (GDDR6) index and a daily "LLM Token Index". The site says they are "distributed on the Bloomberg and Refinitiv" and offers "up to 8 years of historical data". No GB200 index is listed. — [Silicon Data home](https://www.silicondata.com/)
- SDH100RT (Neo-Cloud) = **$2.89/GPU-hr as of 25 Oct 2026**, +6.2% over 7 days. Daily, from neocloud providers and marketplaces, standardized for specs, terms, platform and location. Stated coverage: 95% of neocloud GPU providers and 100% of major hyperscalers. Hyperscaler readings are published separately. Caveat: the same page's FAQ says "$2.53", which conflicts (probably a stale FAQ). Paid portal with a 7-day trial; free tier not clearly stated. — [Silicon Data H100 index page](https://www.silicondata.com/products/silicon-index/h100)
- SDB200RT = **$6.60/GPU-hr as of 25 Oct 2026**, +12.4% over 7 days (FAQ on the same page says $5.45, which conflicts). — [Silicon Data B200 index page](https://www.silicondata.com/products/silicon-index/b200)
- B200 history from Silicon Data's own blog: June 2026 range $5.26–5.45; July $5.62–6.01; August $5.58–5.69 (month-end $5.62); 7 Sep 2026 $5.69. H100 neocloud: $2.75 (27 Jul), **$2.63 (7 Sep 2026)**. B200/H100 ratio ~2.2x. August annualized volatility 7.1% (lowest month of 2026). — [Silicon Data blog, B200 Aug 2026 update](https://www.silicondata.com/blog/b200-rental-price-august-2026-update)
- Secondary coverage: SDH100RT $2.88 on 24 Oct 2026 vs $2.00 on 9 Dec 2025 (+44%). Intermediate readings reported as ~$2.20 (Jan), $2.47 (Apr), $2.76 (end-May). Not verified on Silicon Data's own page beyond the 25 Oct $2.89. — [FourWeekMBA](https://fourweekmba.com/ai-nvidia-h100-rent-hits-2-88-an-hour-up-44-since-december/) (403 on fetch; values from search snippet); [Uvik ($2.81 on 7 Oct 2026)](https://uvik.net/blog/gpu-price-index/)
- Silicon Data also sells 36-month forward curves (launched 20 Apr 2026, recalculated each business day) and an "Implied Forward Curve" product. — [Silicon Data forward curve blog](https://www.silicondata.com/blog/the-gpu-forward-curve-pricing-the-curve-not-just-the-spot); [CryptoBriefing](https://cryptobriefing.com/cme-group-gpu-rental-forward-curve-pricing/)
- Pricing/data-download pages: [Silicon Data pricing](https://www.silicondata.com/pricing), [index datasets](https://www.silicondata.com/products/index-datasets)

**B. Ornn Compute Price Index (OCPI)**
- Settled **25 Oct 2026** (USD/GPU-hr): **H100 SXM $3.03** (+0.3% 1D, +6.3% 1M; Bloomberg ORNNH100); **H200 $6.30** (+1.6% 1D, **+24.0% 1M**); **B200 $9.70** (+1.4% 1D, **+20.6% 1M**; Bloomberg ORNNB200); A100 SXM4 $1.09 (+6.9% 1M); RTX PRO 6000 $1.53 (+0.7% 1M). It is a "volume-weighted, winsorized average" of *transacted* rental prices and settles once per trading day at 4:00 PM ET. Free without an account: latest value plus 3 months of daily history for these 5 GPUs, and 4 "token labs". Paid: full history, hourly data, forward curves, Token Price Index, Memory Index, Coding Activity Index, neocloud map, datacenter sites. B300 is not listed. — [Ornn data page](https://data.ornn.com/)
- OCPI H100 was reported at $2.92 on 1 Oct 2026 (+3.2% over 30 days). — via [search summary of akash.network / coloprice pages](https://akash.network/the-bid/h100-rental-price-2026-cost-per-hour/) (secondary)
- Ornn and a16z data reportedly show 2026 YTD rental gains of H200 +160%, B200 +120%, H100 +35%. — [X trending summary](https://x.com/i/trending/2114155255403274436) (secondary, unverified)
- A July 2026 article said "H100s were trading near $1.70/hr". That conflicts with the OCPI ~$2.9–3.0 level in Oct and the SDH100RT $2.75 on 27 Jul. Likely stale or a misquote; treat as unreliable. — [AI Weekly](https://aiweekly.co/alerts/kalshi-launches-gpu-compute-forward-curves-for-ai-hedging)
- Ornn raised $33M led by a16z (June 2026 report). — [AI Weekly](https://aiweekly.co/alerts/ornn-raises-33m-led-by-a16z-to-build-gpu-compute-futures-market)

**C. SemiAnalysis GPU Rental Price Index (H100 1-year contract index + hourly composite)**
- Launched 2 Apr 2026. H100 **1-year contract** pricing went from a low of **$1.70/hr (Oct 2025) to $2.35/hr (Mar 2026)**, about +40%. It broke $2 in late Jan 2026. Based on a monthly survey of 100+ market participants, validated against transactions. It reports the 25th–75th percentile, tracks 3-month to 5-year tenors for H100/H200/B200/B300/GB200/GB300/MI300/MI325/MI355, and the full term structure is for institutional subscribers. — [SemiAnalysis, "The Great GPU Shortage" (2 Apr 2026)](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity)
- Public dashboard: H100 composite $2.82. The detailed table shows $2.80 (Mar 2026) and $2.83 (Feb 2026). B200 $3.68 (Apr 2026). H200/B300/GB300 show "—". Hourly computation. Hyperscalers are weighted above marketplaces and neoclouds. H100 blends in contract-survey data. Bloomberg ticker **SAH100SC**. The public page appeared stale (latest Apr 2026). Full data via sales@semianalysis.com. — [gpu-index.semianalysis.com](https://gpu-index.semianalysis.com/)
- A secondary site says SemiAnalysis's April 2026 1-year range was ~$2.10–2.70 and on-demand ~$2.82 (not verified). — [coloprice](https://coloprice.com/guides/h100-rental-prices/)

**D. getdeploying.com GPU Price Trends (scraped on-demand list prices)**
- Week of **19 Oct 2026**: H100 on-demand median **$3.71/GPU-hr across 40 providers**, **+9% over 4 weeks, +21% YoY**. Medians by segment: H100 GPU-clouds $4.50 vs hyperscalers $7.89 (+75%); H200 $5.40 vs $10.85; **B200 $8.50 vs $14.24**; A100 $2.00 vs $3.67; RTX PRO 6000 $2.15 vs $4.50. Breadth: 11 of 25 models up that week; over the year 17 of 21 up, 4 down. Old-GPU moves: V100 +36% week-on-week, RTX 3090 +30%. **Reserved discount vs on-demand (median): 1 month −8%, 6 months −13%, 1 year −28%, 3 years −49%.** Spot ≈ 53% of on-demand (H100 54%, H200 50%, A100 65%). Methodology: per-provider median, then the median across providers. 88 providers, 103 models, 57,828 weekly observations since Jul 2024. Scraped up to every 15 minutes. Weekly dataset free on page; API for daily and per-provider data. — [getdeploying GPU price trends](https://getdeploying.com/gpu-price-trends)

**E. Live marketplaces / list-price pages (primary "free float" order books)**
- **Vast.ai live API snapshot (26 Oct 2026 ~06:05 UTC, rentable on-demand offers; $/GPU-hr from dph_total, which includes storage/bandwidth add-ons)**: H100 SXM **15 offers / 36 GPUs total**, min $1.93, median $3.75, max $9.67. H100 NVL 7 offers / 12 GPUs, median $2.80. H200 5 offers / 27 GPUs, median $5.37. **B200 16 offers / 56 GPUs, median $10.13**, min $6.49. — researcher pull from `https://console.vast.ai/api/v0/bundles/` (public endpoint, free; [Vast.ai pricing](https://vast.ai/pricing))
- SF Compute (sfcompute.com): the homepage shows a resale model ("sell back their idle compute") with illustrative "Reserved price $3.00/gpu/hr" and "Realized price $4.29/gpu/hr". No public per-GPU index was found, and it is unclear whether these are live numbers. — [SF Compute](https://sfcompute.com/)
- Compute Exchange (Carmen Li is CEO of both Silicon Data and Compute Exchange) launched a secondary marketplace for used data-center GPUs. — [Blockspace](https://blockspace.media/insight/compute-exchange-launches-used-gpu-marketplace/) (403 on fetch; search snippet); [Pitch the PM podcast ep.55](https://pitchthepm.substack.com/p/ep-55-token-prices-dropping-on-model)
- RunPod / Lambda / CoreWeave public on-demand pages exist (runpod.io/pricing, lambda.ai/pricing, coreweave.com/pricing) but were **not fetched in this session**, so current levels are unverified. getdeploying aggregates them.

**F. Exchange-traded / derivative products (status as of late Oct 2026)**
- **CME Group / Silicon Data**: partnership announced 12 May 2026. On 11 Aug 2026 CME said "Silicon Data H100 Rental Index Futures" and "B200 Rental Index Futures" would launch **5 Oct 2026, pending regulatory review**. — [CME press release 12 May 2026](https://www.cmegroup.com/media-room/press-releases/2026/5/12/cme_group_and_silicondatapartnertolaunchfirstcomputefutures.html); [CME/PRNewswire 11 Aug 2026](https://www.prnewswire.com/news-releases/cme-group-and-silicon-data-to-launch-compute-futures-on-october-5-to-unlock-new-way-to-hedge-ai-risks-302848593.html)
- Contract codes **GPU1 (H100) / GPU2 (B200)**, each **730 GPU-hours, cash-settled**. On 15 Oct 2026 CME began distributing *non-tradable* Silicon Data forward-curve data via CME market data feeds. — [CryptoBriefing](https://cryptobriefing.com/cme-group-gpu-rental-forward-curve-pricing/); [TokenPost "Oct. 15 effective date"](https://www.tokenpost.com/news/business/33069)
- The **5 Oct launch slipped**. The CME calendar reportedly lists **9 Nov 2026** as first trade, "pending review", and regulators had not cleared it as of 21 Oct. This is a single, less-established source. — [RuntimeWire](https://runtimewire.com/article/silicon-data-cme-compute-futures-november-2026); a CME Q3 2026 write-up also says it is still awaiting review — [Criptolog](https://www.criptolog.com/finance/cme-groups-record-q3-2026-lifts-volume-revenue-and-product-plans/)
- **ICE / Ornn**: announced 19 May 2026. USD cash-settled GPU compute futures referencing OCPI, pending regulatory approval, with no timeline given. — [ICE IR](https://ir.theice.com/press/news-details/2026/ICE-and-Ornn-to-Launch-GPU-Compute-Futures-Contracts/default.aspx)
- **Kalshi** (CFTC-regulated event contracts) has H100 weekly and monthly price markets settled on Ornn, e.g. ticker family KXH100MON. Forward curves for B200/H200/A100 launched 14 Jul 2026. Liquidity is thin: ~$1K of 24h volume on some strikes per a tracker. — [Kalshi KXH100MON](https://kalshi.com/markets/kxh100mon/h100-monthly-price/kxh100mon-26mar31); [AI Weekly](https://aiweekly.co/alerts/kalshi-launches-gpu-compute-forward-curves-for-ai-hedging); [simplefunctions tracker](https://simplefunctions.dev/answer/h100ms)
- **Architect Financial Technologies (AX)**: perpetual futures on GPU and RAM prices with Ornn, announced Jan 2026, pending approval. Ornn says the first cleared-price compute swap was executed Dec 2025. — [PRNewswire](https://www.prnewswire.com/news-releases/architect-financial-technologies-partners-with-compute-index-provider-ornn-to-launch-exchange-traded-futures-on-gpu-and-ram-prices-302666613.html)

### Inferences
- **Index divergence is itself a signal.** On 25 Oct 2026 B200 reads $6.60 (Silicon Data, standardized observations), $8.50 (getdeploying GPU-cloud on-demand median), $9.70 (Ornn, transacted spot) and ~$10.13 (Vast.ai median ask). The transacted/marketplace measures (Ornn, Vast) run 45–55% above Silicon Data. That fits a very thin "free float" where marginal prints clear far above broad list/observed rates. Watch for the **Ornn–Silicon Data gap closing from above** (marginal spot falling toward broad rates) as an early glut sign.
- Momentum: Ornn H200/B200 +20–24% in one month and Silicon Data B200 +12% in 7 days are accelerations, not plateaus. Silicon Data H100 fell from $2.75 (late Jul) to $2.63 (7 Sep) before re-accelerating to $2.89 (25 Oct). Check whether that dip coincided with new capacity coming online.
- Suggested signal map (judgement):

| Indicator | Tightness continues | Glut / stranded compute / forced liquidation |
|---|---|---|
| SDH100RT / OCPI H100 | Holds ≥$2.8–3.0 and makes new highs; A100/V100 also rise | Sustained fall below ~$2.35 (the Mar-2026 1-yr contract level), then below $2.00 (Dec-2025 level) |
| OCPI/SD B200 | ≥$6–10 with positive 1M change | 1M change turns negative across H100/H200/B200 at once; B200/H100 ratio compresses <~1.8x |
| getdeploying breadth | Majority of models up week-over-week; YoY >+15% | Majority down for 4+ consecutive weeks; hyperscaler premium widens (neoclouds cutting faster) |
| Spot/OD ratio (getdeploying) | Rises above ~60% | Falls well below ~50% (interruptible capacity being dumped) |
| Vast.ai rentable offer counts | Dozens of H100/B200 GPUs (as on 26 Oct) | Multi-fold jump in listed H100/B200 GPUs with falling medians |
| CME GPU1/GPU2, Kalshi, Silicon Data forward curve | Curve flat or in contango; futures ≥ spot | Steep backwardation (12M forward >15–20% below spot); open interest skewed to short hedges by neoclouds |

### Gaps
- Could not read Silicon Data H200 / B300 / MI300X current values. B300 index level unknown (not on Ornn either).
- No GB200/GB300 NVL72 rental index found publicly. SemiAnalysis tracks it but behind a paywall.
- SemiAnalysis public dashboard appears stale (Apr 2026). No verified Sep/Oct 2026 1-year contract value.
- CME first-trade date (9 Nov) rests on one source. CFTC status not independently confirmed.
- RunPod / Lambda / CoreWeave list prices not fetched this session.
- The SF Compute figures may be illustrative.

---

## 2. Spot vs term (1–3 year reserved) pricing; spot–term spread

### Takeaway
Term pricing is mostly disclosed through survey indices (SemiAnalysis), Silicon Data forward/term curves, aggregator reserved-discount data (getdeploying), and anecdotes from earnings calls. Neocloud filings disclose backlog, not $/GPU-hr. Evidence shows most capacity is under multi-year commitments (CoreWeave: 98% of revenue from committed contracts). The B200 curve was backwardated in Sep–Oct 2026 (forward below spot), which conflicts with a reported "contango" characterization.

### Cited Findings
- **Silicon Data B200 term/forward (7 Sep 2026)**: spot $5.69. Term rates 3M $5.73 / 6M $5.64 / 12M $5.39. Implied forwards 3M $5.68 / 6M $5.41 / **12M $5.03 (~12% below spot)**. Silicon Data calls the curve **backwardated**. — [Silicon Data blog](https://www.silicondata.com/blog/b200-rental-price-august-2026-update)
- Mid-Oct 2026: both the H100 and B200 Silicon Data curves were reportedly in backwardation (spot H100 $2.53–2.81, B200 $5.45–6.01). — [CryptoBriefing](https://cryptobriefing.com/cme-group-gpu-rental-forward-curve-pricing/)
- **Conflict**: Silicon Data CEO Carmen Li is quoted saying the curve went from downward-sloping last year to **contango** this year, so longer contracts no longer carry a discount ("priced to rise for 36 months"). — [FourWeekMBA](https://fourweekmba.com/ai-nvidia-gpu-rents-are-now-priced-to-rise-for-36-months/) (secondary; article date not verified); [Pitch the PM ep.55](https://pitchthepm.substack.com/p/ep-55-token-prices-dropping-on-model)
- Silicon Data's own forward-curve blog reportedly shows B200 spot ~$5.62 vs 36-month term ~$5.17 (~8% backwardation), with the forward crossing back above term at the long end. — [Silicon Data forward-curve blog](https://www.silicondata.com/blog/the-gpu-forward-curve-pricing-the-curve-not-just-the-spot) (via search summary)
- **SemiAnalysis (Apr 2026)**: H100 1-yr contract $1.70 → $2.35 (Oct 2025 → Mar 2026). Some H100 contracts are renewing at the same rate as 2–3 years ago and being extended to 2028. AI labs take 4–5-year, 50–100 MW offtakes; AI-natives mostly 1–3-year tenors, some 4+ years with >20% prepayment. Hyperscalers backstop neocloud deals and resell to labs. AWS p6-b200 spot reportedly bid ~$14/hr/GPU. Most rental volume is transacted in the contract market, not on-demand. — [SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity)
- **getdeploying reserved discounts (week of 19 Oct 2026)**: 1Y −28%, 3Y −49% vs on-demand median. — [getdeploying](https://getdeploying.com/gpu-price-trends)
- **SpaceX (xAI parent) Q3 call, ~20 Oct 2026**: Musk said older H100s are renting for more than when new. Contracts are short-term at roughly spot rates, and renewals come in at higher $/W. SpaceX could rent compute "several times over". New deployments pay back in <1 year (CFO). Power, cooling and infrastructure, not chips, are the binding constraint. — [Yahoo Finance/Stocktwits, 20 Oct 2026](https://finance.yahoo.com/markets/stocks/articles/crwv-nbis-nvda-jump-overnight-023720804.html)
- ARK's Brett Winton: renewals on the same chips are rising year over year. — [same](https://finance.yahoo.com/markets/stocks/articles/crwv-nbis-nvda-jump-overnight-023720804.html)
- **CoreWeave 10-Q (Q2 2026, period end 30 Jun 2026)**: RPO **$103.7B**. ~41% to be recognized within 24 months, 39% in months 25–48, the rest in 49–78. **~98% of revenue from customer commitments**. Customer A 36% of Q2 revenue (71% a year earlier), B 26%, C 10%. Total debt ≈ $35.1B (recourse $31.4B + non-recourse $3.7B). DDTL 1.0–5.0 facilities (GPU-backed delayed-draw term loans); DDTL 5.5 added Aug 2026. — [SEC EDGAR CoreWeave 10-Q](https://www.sec.gov/Archives/edgar/data/0001769628/000176962826000366/crwv-20260630.htm)
- **Nvidia FQ2 FY2027 call (26 Aug 2026)**: Nvidia introduced a neocloud **revenue-sharing structure**. It provides a **take-or-pay commitment on a portion of a facility's capacity** (minimum revenue guarantee for lenders) and shares revenue above the floor. Neoclouds are expected to exit 2026 with **8 GW installed vs ~3 GW at end-2025**. — [Nvidia transcript PDF](https://s201.q4cdn.com/141608511/files/content_files/TRANSCRIPT_-NVIDIA-Corp-NVDA-US-Q2-2027-Earnings-Call-26-August-2026-5_00-PM-ET.pdf)

### Inferences
- **Spot–term spread as the core "free float" gauge.** Spot/on-demand above 1-yr term (backwardation) means marginal buyers pay up for immediacy while most capacity is locked. That is consistent with the thin-float thesis: spot reflects marginal scarcity, not aggregate demand. A **flip to spot < term** (or the 12M forward discount widening past ~15–20%) would be the cleanest early glut signal, because holders of committed capacity (labs or hyperscalers sub-letting) would start dumping excess into spot.
- The CoreWeave mix (98% committed, RPO $103.7B, 41% due within 24 months) shows that neocloud revenue is insensitive to spot near-term. Spot collapse would hurt mainly uncontracted capacity and new builds financed against expected rates, and would show up first in renewal pricing and new-contract tenor and prepayment terms.
- Nvidia's take-or-pay backstop for neocloud capacity is a form of vendor demand support. Its growth is a late-cycle warning sign: demand is being underwritten by the supplier.
- Watch list: SemiAnalysis monthly 1-yr index (paid); Silicon Data 3/6/12/36M term curves via CME feed (from 15 Oct); renewal-rate commentary on neocloud calls (CoreWeave, Nebius, IREN, SpaceX/xAI); RPO growth vs capex; prepayment % and tenor.

### Gaps
- No public 3-year H100/B200/GB300 term $/GPU-hr from a primary source. Bernstein, Morgan Stanley and broker term-lease reports were not found in open sources.
- The Silicon Data CEO's "contango" quote vs published backwardated curves is unresolved. It may depend on date and tenor; reconcile with the CME-distributed curve.
- The CoreWeave Q3 2026 10-Q is not yet available (Q3 results expected ~Nov 2026). Nebius disclosures were not checked.

---

## 3. Secondhand/used GPU and server prices; GPU collateral; depreciation/useful-life assumptions

### Takeaway
There is no authoritative transaction-based used-GPU price index. Published used H100 estimates range from ~$6K to $35K per card, mostly from brokers and vendors. No GPU-backed loan foreclosure or auction had been publicly recorded as of 17 Oct 2026. Depreciation lives are 6 years at CoreWeave and hyperscalers vs ~4 years at Nebius (2025 data). Credit markets, not rental prices, are now the stress channel: CoreWeave CDS >1,000 bp and bond yields ~15% in mid-Oct 2026.

### Cited Findings
**Used GPU prices (all secondary, conflicting)**
- CloudZero: used H100 ~$25–35K (new ~$31K). Mercatus (Jun 2026): $22.5–25.5K for 18–30-month-old cards. ServerBuyback "GPU Resale Value Index" (Jun 2026): $15–28K, ~75–85% retention over 24 months. ClusterBid: $15–19K in Q2 2026. IntuitionLabs: $6–22K. One April 2026 analysis: "H100 secondhand $12–18K (down from $40K)". — [CloudZero](https://www.cloudzero.com/blog/h100-gpu-cost/); [Mercatus](https://www.mercatus-ai.com/blog/h100-resale-value); [ServerBuyback index](https://serverbuyback.com/resources/gpu-resale-value-index/); [ClusterBid](https://clusterbid.com/blog/secondary-gpu-market-2026-used-h100-prices-resale-value-trading-volume); [IntuitionLabs](https://intuitionlabs.ai/articles/data-center-gpu-pricing-2026); [siliconanalysts](https://siliconanalysts.com/analysis/nvidia-gpu-prices-double-as-ai-demand-overwhelms-supply-chain)
- Compute Exchange's used-GPU marketplace: used equipment can sell 40–60% below MSRP. — [Blockspace (search snippet)](https://blockspace.media/insight/compute-exchange-launches-used-gpu-marketplace/)
- Hashrate Index (Luxor/Blockspace) has an "AI hardware price benchmark" (could not fetch; 403). — [Blockspace](https://blockspace.media/insight/hashrate-index-ai-hardware-price-benchmark/)
- 8×H100 server ~$285K (Mercatus). — [Mercatus](https://www.mercatus-ai.com/blog/h100-server-price)

**Collateral / distress record**
- AM Compute "GPU risk" tracker (updated **17 Oct 2026**): **no public record of a GPU-backed loan being foreclosed and its GPUs auctioned as of Oct 2026**. Character.AI filed Ch.11 on 12 Oct 2026 (a compute buyer, not a neocloud). Mining-era (2022–24) equipment-lender recoveries ranged from 37% (Bitfarms/BlockFi) to ~65% (Core Scientific/NYDIG) to 80–100% (others). Precedents: Aug 2024 H100 short-term rents fell from >$8 to $1–2. After the Sep 2022 Ethereum Merge, RTX 3080 resale fell from $1,783 to $638. 1979 Itel/IBM 4300 lease collapse. — [AM Compute defaults](https://www.amcompute.com/gpu-risk/defaults); [AM Compute risk ranking](https://www.amcompute.com/gpu-risk)
- Genesis Cloud reportedly in formal liquidation since Aug 2025 but still selling capacity (vendor blog, unverified). — [Spheron](https://www.spheron.network/blog/genesis-cloud-pricing-2026-eu-h100-cost/)
- Lambda closed a $1B syndicated senior secured facility (May 2026). — via [AM Compute/search summary](https://www.amcompute.com/gpu-risk) (secondary)
- A headline reports that Nvidia is asking insurers to cover GPU residual-value (resale) risk. Not verified. — [letsdatascience](https://letsdatascience.com/blog/nvidia-asking-insurers-cover-what-happens-if-gpus-dont-resell)

**Credit-market stress (Oct 2026)**
- CoreWeave 5-yr CDS rose above **1,140 bp** at one point and later sat near **1,038 bp** (CNBC 15 Oct 2026). The 2032 notes yielded ~14.8% (CNBC 14 Oct). The 9.75% 2031 bond hit a record **15.76%** yield. The stock is ~70% below its all-time high. — [CNBC 15 Oct](https://www.cnbc.com/2026/10/15/coreweave-credit-default-swaps-hit-distress-levels-as-investors-sour-on-ai-debt.html); [CNBC 14 Oct](https://www.cnbc.com/2026/10/14/coreweave-stock-bond-yields-ai-debt.html); [Benzinga](https://www.benzinga.com/markets/bonds/26/10/62541064/coreweave-debt-stress-mounts-bond-yield-hits-record-as-stock-suffers-44-billion-wipeout) (fetch 403; values via search summary)
- CoreWeave >$51B debt and obligations (CNBC). ~$640M quarterly interest vs ~$128M operating income; $10.6B due by end-2027; S&P B+ (24/7 Wall St). The claim that ~80% is GPU-backed at ~9% comes from a single outlet (Startup Fortune). The selloff spread to NBIS and IREN. — [24/7 Wall St](https://247wallst.com/investing/2026/10/22/the-neocloud-bloodbath-nbis-iren-and-crwv-selloff-continues/); [Startup Fortune](https://startupfortune.com/ai-neocloud-stocks-sink-as-coreweave-debt-fears-spread-to-equities/)
- Janus Henderson PM holding CoreWeave debt calls it "a bump in the road". — [CNBC 20 Oct](https://www.cnbc.com/2026/10/20/coreweave-debt-janus-henderson-lloyd.html)
- Musk (X, 25 Oct 2026): "a lot of stranded compute in partially complete data centers". Debt markets have shut off neoclouds without non-AI revenue. 200+ neoclouds face "guppy-level death" and consolidation. SpaceX closed $40B of GPU debt (investment-grade). Chamath (X, 25 Oct 2026): neoclouds are "disorganized and poorly capitalized". There will be more "partially stranded compute and compute sitting in inventory in 2027" than forecast, and 2027 will be "turbulent". He gave no data; he writes as an owner of "energized land assets". — [TrendingTopics](https://www.trendingtopics.eu/musk-neoclouds-die-off-spacex-40-billion-debt/); [Wccftech](https://wccftech.com/elon-musk-goes-ballistic-on-ai-neoclouds-says-they-will-see-guppy-level-death-as-spacex-raises-40-billion-for-gpus/); [Chamath on X](https://x.com/chamath/status/2114389987563381004)

**Depreciation / useful life**
- CoreWeave FY2025 10-K: technology equipment over **6 years** (changed from 5 on 1 Jan 2023). Q2 2026 D&A on PP&E $1.4B (six months $2.5B). Gross technology equipment $33.8B, CIP $11.9B, net PP&E $46.7B. No asset impairments reported. — [CoreWeave 10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/0001769628/000176962826000366/crwv-20260630.htm); [Cape Fear Advisors](https://capefearadvisors.substack.com/p/the-second-contract) ("six-year GPU depreciation, no salvage")
- Nebius depreciates GPUs over ~4 years (2025 commentary, not re-verified for 2026). Hyperscalers normalized on ~6 years by 2023. — [Bizety (Sep 2025)](https://bizety.com/2025/09/23/gpu-depreciation-coreweave-vs-nebius/); [gpuinsights](https://gpuinsights.net/server-useful-life-gpu-depreciation-2026/); [SiliconANGLE (Nov 2025)](https://siliconangle.com/2025/11/22/resetting-gpu-depreciation-ai-factories-bend-dont-break-useful-life-assumptions/)

### Inferences
- The 2026 rent rebound (H100 renting above its new-card economics per Musk) has *supported* used values and collateral marks. That makes collateral value pro-cyclical with spot. A spot collapse would hit loan-to-value on DDTL-style facilities at the same moment refinancing is hardest. This is the mechanism behind the "forced selling → rental collapse" loop.
- Today's stress is in **funding** (CDS, yields, equity), not in **utilization or price**. Rents are rising while neocloud credit sells off. "Stranded compute" (Musk) refers to unfinished data centers and financing, a supply-side failure, not a lack of demand. A demand-side glut would need rental indices to roll over too.
- Signal map (judgement):

| Indicator | Tightness | Glut / forced liquidation |
|---|---|---|
| Used H100 card price (broker quotes, ServerBuyback index, Compute Exchange) | ≥~$20K and stable | <~$12–15K, or a widening bid-ask / failed auctions |
| GPU-loan foreclosures (AM Compute tracker) | None | First public GPU foreclosure or auction; lender-run sales |
| CoreWeave 5y CDS / 2031 bond yield | Back below ~600 bp / <10% | Sustained >1,000 bp, missed covenant or DDTL waiver, distressed exchange |
| Depreciation policy changes | Lives unchanged or lengthened | Useful-life shortening or impairments in 10-Q/10-K (CoreWeave, Nebius, IREN, hyperscalers) |
| Neocloud equity (CRWV, NBIS, IREN) vs rental indices | Move together | Equity and credit keep falling while rents also start falling (confirmation) |

### Gaps
- No transaction-level used-GPU index with a verifiable methodology. All used prices come from broker or vendor blogs.
- CoreWeave Q3 2026 figures not yet available. CDS levels differ by outlet (1,038–1,140 bp). Bloomberg/Reuters primary data not accessed.
- Nebius / IREN / Lambda 2026 depreciation policies not verified from filings.
- Nvidia residual-value insurance story not verified.

---

## 4. GPU utilization / idle capacity / availability and lead times

### Takeaway
There is no public, high-frequency measure of fleet-wide utilization. Proxies are vendor statements ("fully utilized"), SemiAnalysis surveys, marketplace availability counts, and spot-vs-OD price ratios. Workload-level utilization (Cast AI 5%) is a different concept from rental occupancy. Nvidia says supply remains a bottleneck through FY2028 (to ~Jan 2028). Vera Rubin production shipments began Aug 2026.

### Cited Findings
- **Nvidia (26 Aug 2026)**: "NVIDIA Compute is fully utilized across every cloud we serve". FY2028 revenue growth of ~70% guided as a "supply-constrained outlook". Supply is a bottleneck "at least through the end of fiscal year 2028". Vera Rubin production shipments began Aug 2026, ~20% of DC revenue expected in Q3 FY27. Q3 FY27 revenue guide $108B ±2%. Inventory rose to **$32B**. **DSO rose to 60 days** due to "extended payment terms for large purchases by certain investment-grade customers". Top-5 hyperscaler capex ~$800B (2026) and $1.3T (2027). Cloud backlog >$2T. — [Nvidia transcript PDF](https://s201.q4cdn.com/141608511/files/content_files/TRANSCRIPT_-NVIDIA-Corp-NVDA-US-Q2-2027-Earnings-Call-26-August-2026-5_00-PM-ET.pdf)
- **SemiAnalysis (Apr 2026)**: on-demand "sold out across all GPU types". About half of providers were fully sold out of 64-GPU H100/H200 configurations. Little Hopper is coming off contract. Blackwell lead times ran into Jun–Jul 2026, with capacity through Aug–Sep 2026 booked. The author calls **utilization the best high-frequency demand indicator** for on-demand (on-demand list prices are sticky). — [SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity)
- **SemiAnalysis ClusterMAX 3.0** (23 Sep 2026): rates 77 GPU clouds, based on 200+ user interviews. Paywalled. Useful for which neoclouds are weakest (most likely to fail or dump capacity). — [SemiAnalysis ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- **Cast AI (21 Apr 2026)**: average GPU utilization of **5%** across analyzed (non-optimized) Kubernetes clusters. This is a vendor report with thin methodology, and it measures in-cluster compute use, not whether rented GPUs are leased. — [Cast AI press release](https://cast.ai/press-release/2026-state-of-kubernetes-optimization-report/)
- **Vast.ai availability (26 Oct 2026)**: only 36 H100 SXM, 27 H200 and 56 B200 GPUs listed rentable on-demand. — researcher API pull ([Vast.ai](https://vast.ai/pricing))
- getdeploying: spot ≈ 53% of on-demand across 16 models (H100 54%). — [getdeploying](https://getdeploying.com/gpu-price-trends)
- Lead times (secondary, conflicting): B300 lead times reportedly fell from 36 to 18 weeks; DGX B300 shipping at 8–12 weeks; one source claims H100 lead times of 6–12 weeks. — [Civo](https://www.civo.com/blog/vera-rubin-vs-b300-wait-or-deploy-now); [Barrack.ai](https://blog.barrack.ai/nvidia-rubin-vs-blackwell-rent-now-or-wait/) (vendor blogs)
- A Vera Rubin delay (thermal lid, HBM4 qualification) was reportedly resolved, with 1.7–1.8M units still projected. — [Memeburn](https://memeburn.com/nvidia-vera-rubin-delay-explained/) (secondary)
- Jensen Huang (22 Oct 2026) sees no memory glut through 2029. — [CNBC](https://www.cnbc.com/2026/10/22/jensen-huang-nvidia-memory-selloff-shortage.html)
- SpaceX: binding constraints are power, cooling and infrastructure. Compute capacity was 1.7 GW at end-Sep, with 2.5–3 GW targeted by year-end and ≥13 GW by end-2027; 200K GB300/month coming online. — [Yahoo/Stocktwits](https://finance.yahoo.com/markets/stocks/articles/crwv-nbis-nvda-jump-overnight-023720804.html)

### Inferences
- "Stranded compute" risk will likely show up first as **delivered-but-not-energized GPUs**: inventory build at OEMs and neoclouds, Nvidia DSO and inventory, CIP balances at neoclouds (CoreWeave CIP $11.9B). Rental prices are a lagging signal for this.
- Supply waves to watch: neocloud installed base ~3 GW → 8 GW in 2026 (Nvidia); Vera Rubin ramp through Q4 2026–2027; SpaceX 13 GW. If token-demand growth (Section 5) decelerates while these waves land, spot should break first on older generations (H100/A100). A100 and V100 still rising (getdeploying, Ornn A100 +6.9% 1M) currently says the opposite.
- Signal map (judgement):

| Indicator | Tightness | Glut |
|---|---|---|
| Nvidia "fully utilized"/"supply-constrained" language; lead times | Maintained; guides beat | Dropped; lead times collapse to stock; DSO/inventory keep rising with vendor financing |
| Marketplace availability (Vast, SF Compute, getdeploying spot share) | Low counts, spot ≥50% of OD | Counts multiply; spot <40% of OD |
| Neocloud CIP vs energized MW | CIP converts quickly | CIP and inventory pile up; delays like CoreWeave's Nov-2025 third-party DC delay recur |
| Older-gen (A100/V100) rents | Rising | Falling first |

### Gaps
- No public fleet-occupancy statistic (share of installed GPUs leased) was found for any provider.
- Nvidia Q3 FY27 results date and B300 lead times not verified from primary sources.
- Vast.ai API counts are a point-in-time snapshot. No history was collected; the API may cap results.

---

## 5. Token pricing and volume; inference-provider economics

### Takeaway
Token volume on OpenRouter grew ~34x YoY to ~168T tokens/week (week of 5 Oct 2026), with open-weight models ~72% of tokens. Open-model token prices are extremely dispersed across 40–50 hosts. Frontier closed-model list prices were cut ~20% (Opus 5.5) in Sep 2026 while GPU rents rose 20–45%. That supports Deedy Das's "compute up, tokens down" framing, but inference-provider margins are the squeezed variable.

### Cited Findings
**Volume**
- OpenRouter Open/Closed rankings: week beginning 20 Oct 2025, open-weight 1.27T + closed 3.60T = **4.87T tokens/week**. Week beginning **5 Oct 2026, open 120.95T + closed 46.70T = 167.65T/week** (~34x). Closed-weight share fell from 74% to 28%. Monthly growth Aug–Sep 2026 ~44–73% (closed 73%/52%, open 45%/44%). Model-level: DeepSeek V4.1 Flash 40.97T (week of 5 Oct), GPT-6 Luna 7.08T, Claude Opus 5.5 5.02T. Ramp data (5–11 Oct): Anthropic 58.9% of token volume and 60.1% of spend among connected businesses. — [Global Advisors (17 Oct 2026, citing OpenRouter and Ramp)](https://globaladvisors.biz/2026/10/17/fast-fact-closed-weight-ai-usage-on-openrouter-rose-13-fold-as-its-share-of-tokens-fell/)
- OpenRouter CEO chart: 132.6T agentic tokens vs ~17T human in the week ending 5 Oct 2026. — [RuntimeWire](https://runtimewire.com/article/openrouter-agentic-usage-132-trillion-weekly-tokens)
- OpenRouter rankings page: "Usage data through Oct 25, 2026". Weekly top models and open/closed share charts. Free. Data API documented. — [openrouter.ai/rankings](https://openrouter.ai/rankings)
- Fireworks AI: >40T tokens/day; ~50% gross margin (secondary). — [valueaddvc](https://valueaddvc.com/blog/fireworks-ai-valuation-2026-17-5b-series-d-and-the-1b-arr-inference-business)

**Prices (OpenRouter public API `/api/v1/models`, pulled 26 Oct 2026; USD per 1M tokens input/output, default listing)**
- Closed: Claude Opus 5.5 $4/$20 (Opus 5 $5/$25). Claude Sonnet 5.5 $2/$10. GPT-6 Sol $2/$10. GPT-6.1 Sol $2/$10. GPT-6 Astra $10/$50. GPT-6 Luna $0.10/$0.50. Gemini 4 Argon $2/$10. Batch variants are ~50% off. — researcher pull from [OpenRouter models API](https://openrouter.ai/api/v1/models)
- Open-weight: Kimi K3.1 Pro (released 23 Oct 2026) $2/$10 (Moonshot only). DeepSeek V4.1 Flash-1017 $0.15/$0.60. DeepSeek V4.1 Flash $0.02/$1.00 (cheapest host). DeepSeek V4 Pro-0813 $0.66/$1.98. GLM-5.3 $0.07/$1.40 (cheapest). GLM-5.3 Prime $2.80/$8.80. Qwen3.8 Max $2/$6. Qwen3.8 Max Prime $4/$12. MiniMax M3.1 Flash $0.15/$0.60. — [OpenRouter models API](https://openrouter.ai/api/v1/models)
- **Per-host dispersion (OpenRouter `/models/{id}/endpoints`, 26 Oct 2026)**. **DeepSeek V4.1 Flash: ~41 endpoints, output $0.18–$2.40/M**: DeepInfra $0.336–0.63, CoreWeave $0.65, Fireworks $0.84–1.80, Together/Nebius/Crusoe/Google/Baseten/Modal $1.20, Baseten up to $2.40. **GLM-5.3: ~49 endpoints, output $1.40–$8.80/M**: DeepInfra $2.50, Fireworks $3.08–6.60, Together/Baseten/Nebius/Crusoe/Z.AI (first party) $4.40, Amazon Bedrock $5.28. — [OpenRouter endpoints API](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash/endpoints)
- Anthropic Opus 5.5 at $4/$20 is a ~20% cut vs Opus 5 (released ~22 Sep 2026, same day OpenAI cut GPT-6 prices). Cache reads $0.20 vs $0.50. — [AI Weekly](https://aiweekly.co/alerts/openai-anthropic-slash-prices-as-gpt-6-and-opus-55-ship); [usagepricing](https://www.usagepricing.com/blueprint/activity/anthropic-2026-10-05-opus-5-5-price-cut)
- RunInfra (24 providers): the same weights vary 3.2x in output price by provider, and utilization matters more than provider choice. — [RunInfra](https://runinfra.ai/news/inference-cost-truth)

**Quality-adjusted price trackers**
- Artificial Analysis: Intelligence Index v4.3.2 (Opus 5.5 57.6; Sonnet 5.5 56.0; **Kimi K3.1 Pro 55.1, top open-weight**; Qwen3.8 Max 53.4; GPT-6 Astra 52.7; Gemini 4 Argon 52.6). Tracks cost per task, tokens/s, and provider leaderboards for price, latency and accuracy. Free web; API available. — [Artificial Analysis](https://artificialanalysis.ai/); [providers leaderboard](https://artificialanalysis.ai/leaderboards/providers)
- Epoch AI: the price to reach a fixed capability falls 9x–900x per year depending on benchmark (e.g. ~40x/yr for GPT-4-level GPQA). A Sep 2026 Epoch report ("The plunging price of thought") reportedly estimates −47% per quarter (~13x/yr) at fixed performance since 2023 (secondary, unverified). — [Epoch AI data insight](https://epoch.ai/data-insights/llm-inference-price-trends); [Pillitteri (secondary)](https://pasqualepillitteri.it/en/news/21044/epoch-ai-ai-prices-fall-47-percent-quarter)
- Token price indices: Silicon Data "LLM Token Index" (daily, blended) — [Silicon Data](https://www.silicondata.com/). Ornn "Token Price Index" (paid) and 4 free "token labs" — [Ornn](https://data.ornn.com/)

**Inference-provider revenue / arbitrage**
- Deedy Das (Menlo Ventures, X, 25 Oct 2026): a "barrage of inference providers" reaching $1M/month quickly. Even at $8/GPU-hr for on-demand B300s, many open models can earn >$10–20/GPU-hr at ~100 tok/s per user. Arbitrage depends on each chip/model throughput curve. (Quoted via secondary write-up; post not directly verified.) — [FourWeekMBA](https://fourweekmba.com/ai-deepseek-says-a-gpu-hour-earns-38-while-rent-runs-near-8/); [Strange VC](https://thereview.strangevc.com/p/the-brief-everyones-backup-business); [Brandon Carl on X](https://x.com/brandonjcarl/status/2114205902773395763)
- Headline (unverified): "DeepSeek says a GPU-hour earns $38 while rent runs near $8". — [FourWeekMBA](https://fourweekmba.com/ai-deepseek-says-a-gpu-hour-earns-38-while-rent-runs-near-8/)
- Counter-view: inference resellers "rent GPUs… slap a 40%+ margin" and may not last (dax, X). IOSF/Hyperbolic: resellers are short product and long input with no hedge. — [dax on X](https://x.com/thdxr/status/2092679229481623757); [IOSF](https://x.com/IOSFVC/status/2112212202858156506)
- **Fireworks AI**: >$1B ARR (company, Jul 2026); Sacra estimate $800M (May 2026) vs ~$305M (end-2025); $1.505B Series D at $17.5B post (Jul 2026). **Together AI**: reportedly nearing $1B annualized (early 2026). **Baseten**: $300M Series E at $5B (Jan 2026), revenue undisclosed. — [Sacra](https://sacra.com/research/fireworks-ai/); [Quartz](https://qz.com/fireworks-ai-series-d-fundraise-valuation-open-source-071626); [Metavert](https://metavert.io/together-ai-vs-fireworks-ai)
- Dan Niles cites "slowing OpenAI and Anthropic revenue growth" (opinion). — [Yahoo/Stocktwits](https://finance.yahoo.com/markets/stocks/articles/crwv-nbis-nvda-jump-overnight-023720804.html)

### Inferences
- **Break-even formula** for the arbitrage: required aggregate output throughput per GPU (tokens/s) = GPU $/hr ÷ (blended $/M tokens × 0.0036). Example: B200 at $8.50/hr (getdeploying GPU-cloud median) serving DeepSeek V4.1 Flash at $1.20/M output needs ~1,970 output tok/s per GPU. At $0.60/M it needs ~3,900 tok/s (ignores input-token revenue and cache economics). A rise in GPU rent or a cut in token price directly raises the throughput needed. Watch **cheapest-host price on OpenRouter vs Ornn/Silicon Data GPU index** as a margin-compression gauge.
- Thesis mapping: rising token *volume* (34x YoY, ~45–50%/month) is the demand engine behind spot tightness. The key glut lead indicator is **deceleration of OpenRouter weekly token growth** (e.g. monthly growth falling under ~10–15%) while new GPU capacity (8 GW neocloud, Vera Rubin) lands. A second is **token price wars in open models** (cheapest-host output prices falling while GPU rents fall too), signalling idle capacity being monetized at marginal cost.
- Signal map (judgement):

| Indicator | Tightness (compute up, tokens down holds) | Glut |
|---|---|---|
| OpenRouter weekly tokens | MoM growth ≥30%; new records weekly | Growth stalls or declines for several weeks |
| Open-model price dispersion (OpenRouter endpoints) | Wide; premium hosts hold price | Collapse to the floor across hosts; many new hosts undercut (idle-GPU dumping) |
| Inference-provider ARR / GM (Fireworks ~50%) | ARR growth with stable GM | GM compression, layoffs, down-rounds, or provider exits |
| Frontier list-price cuts | Modest (~20%) cuts paired with volume growth | Deep cuts plus slowing lab revenue (Niles) |

### Gaps
- OpenRouter covers only routed traffic (not first-party API or apps). Weekly totals after 5 Oct 2026 were not extracted.
- Artificial Analysis blended $/M price for open vs closed models over time was not extracted (JS charts).
- Baseten, DeepInfra and Together 2026 revenue not verified. The Deedy Das post and "DeepSeek $38/GPU-hr" claim were not verified at the primary source.
- Silicon Data LLM Token Index and Ornn Token Price Index levels are paywalled or unseen.

---

## 6. What analysts use as leading indicators of a compute glut

### Takeaway
No Bernstein or Morgan Stanley glut framework was found in open sources. The publicly visible analyst toolkit is SemiAnalysis (contract index, utilization and sell-out surveys, ClusterMAX), index providers (Silicon Data forward curves, Ornn), Epoch AI (price/compute trends), and credit-market signals. Current reads (Oct 2026) are mixed: price and utilization data are tight, credit is distressed.

### Cited Findings
- SemiAnalysis: utilization (not posted price) is the best high-frequency on-demand indicator. Contract-market pricing is where volume transacts. Checkpoints are the GB300 ramp and the extent of the silicon shortage. A more mature server market may not repeat 2023–24 OEM-margin excess. — [SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity)
- Silicon Data: forward-curve shape (contango vs backwardation) as a consensus view of future rents (Li quote). — [Silicon Data forward-curve blog](https://www.silicondata.com/blog/the-gpu-forward-curve-pricing-the-curve-not-just-the-spot); [FourWeekMBA](https://fourweekmba.com/ai-nvidia-gpu-rents-are-now-priced-to-rise-for-36-months/)
- The Aug 2024 precedent: H100 short-term rents fell from >$8 to $1–2 when supply caught up. The Oct 2025 trough was $1.70 (1-yr contract). — [AM Compute](https://www.amcompute.com/gpu-risk/defaults); [SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity)
- Gene Munster calls oversupply fears "off base" (SpaceX SI segment $7.6B Q3 revenue). ARK's Winton cites rising renewals. — [Yahoo/Stocktwits](https://finance.yahoo.com/markets/stocks/articles/crwv-nbis-nvda-jump-overnight-023720804.html)
- Bearish voices: Musk and Chamath (stranded compute, neocloud die-off). Credit analysts quoted by CNBC say the market rejects AI debt without operating-cash-flow support. — [CNBC](https://www.cnbc.com/2026/10/15/coreweave-credit-default-swaps-hit-distress-levels-as-investors-sour-on-ai-debt.html); [TrendingTopics](https://www.trendingtopics.eu/musk-neoclouds-die-off-spacex-40-billion-debt/)
- Microsoft lease walkaways (TD Cowen, Feb 2025) and CoreWeave's Nov 2025 guidance cut from a third-party DC delay are cited as earlier stress events. — [AM Compute](https://www.amcompute.com/gpu-risk/defaults)
- Nvidia vendor-support indicators: take-or-pay neocloud backstops, DSO 60 days with extended terms, inventory $32B. — [Nvidia transcript](https://s201.q4cdn.com/141608511/files/content_files/TRANSCRIPT_-NVIDIA-Corp-NVDA-US-Q2-2027-Earnings-Call-26-August-2026-5_00-PM-ET.pdf)

### Inferences
- A practical dashboard (frequency): **daily** — Ornn OCPI (free), Silicon Data SDH100RT/SDB200RT (index pages), Vast.ai offer counts (free API), CoreWeave CDS and bond yields (Bloomberg/TRACE); **weekly** — getdeploying medians, breadth and spot/OD ratio, OpenRouter token volume and open-model host prices; **monthly** — SemiAnalysis 1-yr contract index, Silicon Data term/forward curves (CME feed), used-GPU broker quotes; **quarterly** — CoreWeave/Nebius RPO, CIP, D&A and useful-life notes, Nvidia DSO/inventory/"supply-constrained" language, Fireworks/Together ARR, Nvidia take-or-pay exposure; **event-driven** — first GPU-loan foreclosure (AM Compute tracker), CME GPU1/GPU2 launch and open interest, Kalshi forward-curve pricing.
- **The most discriminating combined signal** for the "thin free float masks a coming glut" thesis is the sequence: (1) neocloud credit stress (already present) → (2) older-gen (A100/H100) rents and used-card prices roll over → (3) spot falls below 1-yr term (curve flips to steep backwardation) → (4) open-model token prices collapse to the floor across hosts → (5) first forced GPU sale or foreclosure. As of 26 Oct 2026 only step (1) is observed. Rents (steps 2–3) are still rising, including old-gen.

### Gaps
- No Bernstein, Morgan Stanley or other sell-side compute-glut indicator framework was found in open sources (likely paywalled).
- No Epoch AI data hub series specifically on GPU rental prices or utilization was verified. Epoch covers price per capability and hardware trends.
- The Information / Bloomberg paywalled reporting on neocloud contract terms was not accessed.
