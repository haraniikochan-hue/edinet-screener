# Physical AI infrastructure bottlenecks and "stranded compute": indicators to watch (as of 26 Oct 2026)

Scope: power and grid interconnection, data center construction, power equipment, stranded-compute signals, policy and permitting, key projects. Each indicator lists what it measures, where to find it, how often it updates, free or paid, the latest level found (with date), and what reading means "worsening" or "easing".
Conventions: "(secondary)" means the figure comes from a tracker, aggregator or law-firm summary, not the primary publisher. "(URL from general knowledge; not fetched this session)" marks a canonical data URL I did not open in this session. Fetch-tool summaries of long filings, such as Nvidia's 10-Q, are marked where the exact figure should be re-checked.

Context (the trigger for this research):
- On 25 Oct 2026 Musk wrote on X: "I think we're going to see a lot of stranded compute in partially complete data centers", and "the constraint on deployment of superintelligence is more in power and cooling and infrastructure than it is in chips." He also said "debt markets have almost entirely shut off access to money", that "the 200+ neoclouds are going to see guppy-level death and consolidation", and that the debt is "primarily callable debt for GPU purchases that will arrive in Q1 and Q2." SpaceX has secured $40B of debt for GPU purchases, mainly for chips arriving in H1 2027. SpaceX Q3 capex was $19.6B and its Q4 capex guidance is $35–40B. — [Stocktwits, 25 Oct 2026](https://stocktwits.com/news-articles/markets/equity/spcx-musk-40b-gpu-deal-warns-neoclouds-dan-ives-game-of-thrones-war/cZUdlckRBUs)
- Chamath (X, ~25 Oct 2026): "As someone with a portfolio of energized land assets…". He says neoclouds are "disorganized and poorly capitalized", hyperscalers "take 3 months to do an NDA and want 18mo escrow periods", and there are delays in the existing pipeline "that will catch people off guard in 2027". He also wrote "2027 will be a turbulent year because it will clear out a bunch of wrong/bad bets", and flagged Texas mineral-rights hurdles, overloaded utilities, public opposition, and grid connections that will demand more upfront capital. — [Chamath on X](https://x.com/chamath/status/2114389987563381004); [Stocktwits](https://stocktwits.com/news-articles/markets/equity/spcx-musk-40b-gpu-deal-warns-neoclouds-dan-ives-game-of-thrones-war/cZUdlckRBUs); [Digg summary](https://digg.com/ai/f5sbesjj)

---

## Q1. Grid and power indicators (ERCOT, PJM, MISO/SPP, LBNL, FERC, utility tariffs and IRPs, EIA)

### Takeaway
Large-load requests far exceed what has been studied or energized. ERCOT has roughly 410–474 GW of large-load requests, but only about 9 GW is approved to energize, and in March about 70% of requests had no studies submitted. PJM's 2028/29 capacity auction cleared at the $325/MW-day cap and came up 6.8 GW short. Utilities are adopting take-or-pay large-load tariffs (25 states approved, 8 pending) that weed out speculative "squatter" requests. The best signals of energization are the gap between "requested" and "approved to energize / observed energized" load, the share of requests carrying signed agreements and collateral, and capacity prices.

### Cited Findings

**1. ERCOT Large Load Interconnection (LLI) queue and status reports**
- What it measures: MW of large loads (≥75 MW) requesting interconnection, broken down by stage: no studies submitted → under ERCOT review → planning studies approved → approved to energize → observed energized. The board deck also reports quarterly intake.
- Where: ERCOT Board/TAC "Interconnection and Grid Analysis Update" decks, for example [Apr 2026 deck](https://www.ercot.com/files/docs/2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf) and [May 2026 deck](https://www.ercot.com/files/docs/2026/05/24/8-Interconnection-and-Grid-Analysis-Update.pdf); ERCOT [Trending Topics on batch connection, 18 Jun 2026](https://www.ercot.com/files/docs/2026/06/18/ERCOT-Trending-Topic-New-Batch-Connection-Process-for-Large-Electricity-Users.pdf). Free trackers: [Corley Energy](https://www.corleyenergy.com/ercot-large-load-queue.html) (refreshed monthly), [interconnectionqueue.org](https://interconnectionqueue.org/iso/ercot), [DC Hub](https://dchub.cloud/grid/ercot). Free; updated monthly or quarterly.
- Levels:
  - About 410 GW after 198 new requests in Q1 2026; about 87% are data centers. — [RTO Insider](https://www.rtoinsider.com/129421-ercot-large-load-requests-soar-again/)
  - Stage breakdown as of 26 Mar 2026: 410,618 MW total; 293,651 MW (71.5%) with no studies submitted; 86,605 MW under ERCOT review; 21,343 MW planning studies approved; 3,241 MW approved to energize but not operational; 5,778 MW observed energized. Quarterly intake was 63, 76 and 48 GW in 2025 quarters, then 198 GW in Q1 2026. — [Corley Energy (secondary, citing ERCOT Senate testimony 1 Apr 2026)](https://www.corleyenergy.com/ercot-large-load-queue.html)
  - June 2026 board update: about 438 GW of large-load requests, alongside about 452 GW of generation requests. A ~474 GW figure (data as of June 2026, from a 29 Jul 2026 Senate presentation) and 9,456 MW "approved to energize" (Aug 2026 operational overview) both come from a secondary summary. — [DC Hub (secondary)](https://dchub.cloud/grid/ercot); search summary of ERCOT material
- Process change: ERCOT is moving to batch studies. "Batch Zero" began in July 2026. — [ERCOT Trending Topics, 18 Jun 2026](https://www.ercot.com/files/docs/2026/06/18/ERCOT-Trending-Topic-New-Batch-Connection-Process-for-Large-Electricity-Users.pdf)
- Worsening: the total queue keeps rising while "approved to energize" and "observed energized" stay flat; a large stock of "approved to energize but not operational" MW, meaning the building or equipment is not ready, which is a direct stranded-compute precursor; Batch Zero slipping or being cut back.
- Easing: the queue shrinks because speculative requests withdraw after fees and collateral are imposed, while the "planning studies approved" and "energized" shares rise.

**2. Texas PUCT SB 6 rules (Projects 58480/58481 etc.)**
- What it measures: cost and commitment barriers for large loads, and curtailment exposure.
- Levels:
  - SB 6 applies to loads of ≥75 MW at a single site; the PUCT can lower that threshold. Large loads interconnected after 31 Dec 2025 must install equipment that lets ERCOT curtail them directly during firm load-shed events. The co-located net-metering rule was adopted 26 Mar 2026. Transmission cost allocation rules are due by 31 Dec 2026. — [GT Law / NatLawReview](https://www.gtlaw.com/en/insights/2026/3/texas-senate-bill-6-update-what-data-centers-large-load-customers-should-know-about-proposed-interconnection-standards); [White & Case](https://www.whitecase.com/insight-alert/puct-affirms-curtailment-authority-over-co-located-data-centers-first-net-metering)
  - The interconnection-standards rule (16 TAC §25.194, Project 58481) was adopted around 18–20 Sep 2026 and took effect 8 Oct 2026. Reportedly it was softened from the March draft: a flat $100,000 study fee and no per-MW interconnection charge. — [Texas Power Cost (secondary; page did not render on fetch)](https://www.texaspowercost.com/news/puct-large-load-interconnection-rules-adopted-2026.php); [NFM Consulting](https://nfmconsulting.com/knowledge/texas-sb6-large-load-ercot-data-center-compliance/)
- Worsening: stricter financial-security requirements, or curtailment events actually being called on data centers. Easing: a softer final rule (the reported Sep 2026 outcome) and clear cost-allocation rules by end-2026.

**3. PJM capacity auction (Base Residual Auction) and load forecast**
- What it measures: the price and adequacy of capacity, i.e. whether new load can be served reliably. Where: [PJM Inside Lines](https://insidelines.pjm.com/pjm-capacity-auction-procures-138318-mw-of-generation-resources-as-work-continues-to-address-growing-electricity-demand/); PJM RPM page (https://www.pjm.com/markets-and-operations/rpm, URL from general knowledge; not fetched this session); [PJM load forecast documents](https://www.pjm.com/-/media/DotCom/planning/res-adeq/load-forecast/2026-load-forecast-accuracy-report.pdf). Free. The auction runs annually; the load forecast is published each January, with mid-year adjustments.
- Levels:
  - The 2028/29 BRA (results July 2026) procured 138,318 MW, 6,831 MW short of the reliability requirement. It cleared at the $325/MW-day cap in all zones and added only 525 MW UCAP of new generation and uprates. One analysis puts the uncapped price at about $554.72/MW-day. — [PJM Inside Lines](https://insidelines.pjm.com/pjm-capacity-auction-procures-138318-mw-of-generation-resources-as-work-continues-to-address-growing-electricity-demand/); [NRG special market update](https://www.nrg.com/content/dam/nrg/web/en/multimedia/documents/insights/white-papers-and-webinars/pjm-bra-results-july2026.pdf); [Syso Technologies](https://www.sysotechnologies.com/2026/07/16/pjm-2028-2029-bra-results/)
  - One figure attributes about $6.3B of the $16.4B in capacity charges to data centers. Sources state this share differently, so check the IMM report. — search summary of [Data Center Knowledge](https://www.datacenterknowledge.com/energy-power-supply/pjm-s-power-shortfall-puts-data-center-growth-in-focus) and others
  - PJM proposed a backstop central procurement to fill the 6.8 GW gap, running Sep–Oct 2026, with results expected in December 2026. — [Distroforge](https://distroforge.com/blog/pjm-capacity-auction-results-backstop-procurement/); search summary
  - 2026 load forecast: large-load adjustments grow by 35.1 GW from 2026 to 2031. Utility requests compiled by the Maryland OPC imply about 60 GW of 2030 growth versus about 33 GW in the 2025 forecast. The PJM Board has asked for proposals to serve 32 GW of growth by 2030. — [Modo Energy](https://modoenergy.com/research/en/pjm-load-forecast-data-centers-2046); [MD OPC letter](https://www.pjm.com/-/media/DotCom/about-pjm/who-we-are/public-disclosures/2025/20251015-md-office-of-peoples-counsel-re-large-load-adjustments-for-the-2026-load-forecast.pdf); [RTO Insider tag](https://www.rtoinsider.com/tag/large-load-adjustments-llas)
- Worsening: the next BRA clears at the cap again with a larger shortfall; the December backstop procurement fails to attract supply; PJM imposes "bring your own generation" or curtailable-service mandates on new data centers. Easing: prices clear below the cap; new-generation MW rise; the forecast's large-load adjustments are revised down because tariffs or collateral flush out duplicate requests.

**4. MISO and SPP large-load processes**
- Levels:
  - MISO reports an "unprecedented surge" in large-load requests, mainly from data centers, and uses ERAS (Expedited Resource Addition Study) and EPR to speed approvals. — [MISO Large Load Workshop, 30 Jan 2026](https://cdn.misoenergy.org/20260130%20Large%20Load%20Workshop%20Presentation738349.pdf)
  - In July 2026 MISO said it will create a dedicated expedited study process for large loads, outside the regular queue, as the ERAS fast lane winds down. — [RTO Insider](https://www.rtoinsider.com/136995-miso-to-design-dedicated-queue-process-for-large-loads-and-devoted-generation/)
  - MISO's reliability proposal defines large loads as >50 MW and "computational loads" as large loads with ≥25 MW of IT equipment. — [Utility Dive](https://www.utilitydive.com/news/large-load-reliability-requirements-miso-ferc/829278/)
  - SPP's High Impact Large Load (HILL) process was accepted by FERC on 14 Jan 2026. Its Conditional HILL service, accepted 5 Jun 2026, requires real-time telemetry and gives SPP a remote-disconnect capability. — [McGuireWoods](https://www.mcguirewoods.com/client-resources/alerts/2026/6/ferc-issues-section-206-show-cause-orders-directing-all-six-rtos-isos-to-justify-or-reform-large-load-integration-rules/); [Secondwatt (secondary)](https://secondwatt.com/resources/ferc-rm26-4-data-center-interconnection-standards-2026)
- Watch: MISO's large-load queue design filings, and how much SPP Conditional HILL service is actually curtailed. "Conditional" or "curtailable" service means a site can be energized but not run at full load, which is partial stranding.

**5. FERC large-load interconnection (Docket RM26-4 and the Section 206 show-cause dockets)**
- Levels:
  - DOE's Section 403 directive (Oct 2025) asked FERC for final action by 30 Apr 2026. The ANOPR proposed a national 20 MW threshold with standardized deposits, cost responsibility and timelines; commenters proposed thresholds from 30 to 300 MW. — [Akin Gump](https://www.akingump.com/en/insights/blogs/speaking-energy/doe-directs-ferc-to-initiate-large-load-interconnection-rulemaking); [hData](https://blog.hdata.com/2026-ferc-rulemaking-large-loads)
  - On 16 Apr 2026 FERC said it would act by end-June. — [Holland & Knight](https://www.hklaw.com/en/insights/publications/2026/04/ferc-to-act-on-large-load-interconnection-docket-in-june)
  - On 18 Jun 2026 FERC issued show-cause orders to all six RTOs/ISOs under FPA §206 instead of a final rule. MISO's response was reportedly due 17 Aug 2026 (docket EL26-70). — [McGuireWoods](https://www.mcguirewoods.com/client-resources/alerts/2026/6/ferc-issues-section-206-show-cause-orders-directing-all-six-rtos-isos-to-justify-or-reform-large-load-integration-rules/); [Avanza Energy](https://avanzaenergy.substack.com/p/the-60-day-clock-ferc-just-forced)
  - As of these sources, no final rule had been issued. — [Build.inc](https://build.inc/insights/ferc-rm26-4-data-center-interconnection-developers)
- Where: FERC eLibrary (https://elibrary.ferc.gov, URL from general knowledge; not fetched this session). Free; event-driven.
- Worsening: FERC accepts RTO rules that require large up-front deposits or collateral, the "flush the squatters" mechanism Chamath describes. These are bad for thinly capitalized developers, although they make the queue more realistic. Easing: standardized, fast study timelines and clear treatment of co-location and behind-the-meter supply.

**6. LBNL "Queued Up" (generation interconnection queues; this covers supply, not load)**
- Where: [LBNL Queued Up](https://emp.lbl.gov/queues); [2026 edition](https://emp.lbl.gov/publications/queued-2026-edition-characteristics). Free, with a CC BY 4.0 data file. Annual (published around May; a webinar on 16 Jul 2026).
- Level (end-2025): 2,061 GW of generation and storage actively queued, down about 10% year on year from a peak near 2,600 GW at end-2023. Gas rose 86% to 253 GW; solar (773 GW), storage (749 GW) and wind (220 GW) each fell 16–19%. Only 13% of 2000–2020 requests had reached commercial operation by end-2025, and 75% were withdrawn. The median time from interconnection request to commercial operation exceeded 5 years for projects built in 2025. — [LBNL news](https://emp.lbl.gov/news/backlog-power-plants-seeking-transmission-grid-connection-eased-somewhat-2025-amidst)
- Worsening: completion rates fall further and the median time to commercial operation lengthens. A growing gas queue is a sign of demand pull rather than easing, because turbines are sold out (see Q1b). Easing: higher completion rates and shorter durations.

**7. Utility large-load tariffs and contracted pipelines (AEP Ohio, Dominion, Georgia Power, etc.)**
- EEI "Large Load Projects and Tariffs (October 2026)", updated 9 Oct 2026: publicly announced projects total more than $1.14T and more than 72 GW of connected load. 25 states have approved at least one large-load tariff and 8 more have tariffs pending. Common terms are minimum contract terms, exit fees, minimum billing demand and collateral. — [EEI PDF](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs). Free; periodic updates.
- AEP Ohio (PUCO 24-0508-EL-ATA, approved Jul 2025): data centers above 25 MW must pay for at least 85% of contracted capacity for up to 12 years. The PUCO update of 12 Feb 2026 shows 17,861 MW of contracted data center load (12,219 MW signed before the tariff plus 5,642 MW signed under it), compared with roughly 30 GW of initial interest. The load forecast was cut by 6,521 MW, which AEP attributes to the tariff, and the Ohio Manufacturers' Association is challenging the tariff in court. — [EEI](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs); [DataPowerDemand](https://www.datapowerdemand.com/market/ohio); [New Project Media](https://newprojectmedia.com/policy-aep-ohio-touts-right-sized-load-as-data-center-pipeline-shrinks-further-under-new-tariff/); [Tri-City Local News](https://tricitylocalnews.com/data-centers-in-ohio/)
- AEP's systemwide contracted capacity was 63 GW in May 2026, about 90% data centers, mostly in its Texas and Ohio subsidiaries. — [DCD](https://www.datacenterdynamics.com/en/news/aep-sees/)
- Dominion (Virginia SCC PUR-2025-00058, approved Nov 2025): minimum demand charges and contract terms for loads ≥25 MW, plus a new GS-5 rate class for loads ≥25 MW with a load factor ≥75%. — [EEI](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs)
- Georgia Power (GPSC 44280): minimum billing and longer contract terms for loads ≥100 MW, with exit-cost recovery. — [EEI](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs)
- AEP Ohio is contracting 100 MW of onsite fuel cells for two customers so they can start operating while the grid expands. This is a "bridge power" indicator. — [EEI](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs)
- Worsening: contracted MW stall while "interest" MW collapse; utilities raise collateral or minimum-take terms; exit fees start being triggered, meaning customers walk away from capacity they reserved. Easing: contracted MW convert to energized MW on schedule. Quarterly utility earnings calls (AEP, Dominion, Southern, Entergy, Oncor/Sempra, Xcel) disclose contracted and in-service large-load MW.

**8. EIA data (demand actually showing up)**
- Where: EIA Electric Power Monthly (https://www.eia.gov/electricity/monthly/), EIA-860M monthly generator inventory of planned, delayed and retired units (https://www.eia.gov/electricity/data/eia860m/), EIA STEO (https://www.eia.gov/outlooks/steo/), and the EIA-930 hourly grid monitor. All URLs from general knowledge; not fetched this session. Free; monthly or hourly.
- Use: growth in commercial-sector and state-level retail sales (Virginia, Texas, Georgia, Ohio) shows whether load is actually being energized. EIA-860M planned in-service dates for gas and battery units near data center clusters show slippage.
- Level: not retrieved this session (gap).

### Q1b. Power equipment: gas turbines and transformers (needed for behind-the-meter and bridge power)

**9. GE Vernova gas backlog and slot reservations**
- Where: [GE Vernova 2Q26 press release (8-K)](https://www.sec.gov/Archives/edgar/data/1996810/000199681026000147/gevpressrelease2q26.htm); [1Q26](https://www.sec.gov/Archives/edgar/data/0001996810/000199681026000063/gevpressrelease1q26.htm). Free; quarterly.
- Level (2Q26, 22 Jul 2026): gas backlog plus slot-reservation agreements (SRAs) rose from 100 GW to 116 GW. That is 53 GW of firm backlog and 63 GW of SRAs. In the quarter it signed 18 GW of SRAs and 2 GW of orders, converted 10 GW of SRAs to orders, and shipped 3 GW. Year-end 2026 target is ≥125 GW, raised from ≥110 GW in 1Q26. Reservations are being booked 4–5 years out, and customers are about 80% utilities and 20% data centers. — [GEV 2Q26](https://www.sec.gov/Archives/edgar/data/1996810/000199681026000147/gevpressrelease2q26.htm); [Utility Dive](https://www.utilitydive.com/news/ge-vernova-gas-turbine-backlog-climbs-to-116-gw/826039/)
- Worsening: SRAs pile up faster than shipments (3 GW shipped per quarter against about 20 GW signed), and delivery slots move further out. A sharp drop in SRA-to-order conversion, or SRA cancellations, would instead signal that demand is fading, i.e. stranded projects.

**10. Siemens Energy and Mitsubishi Heavy Industries**
- Siemens Energy's gas turbine backlog was 69 GW as of 30 Jun 2026 after 15 GW of orders in the quarter. It shipped 6 GW that quarter, expects 15–16 GW of deliveries this year, and its CFO cites lead times of 3+ years. — [Utility Dive](https://www.utilitydive.com/news/siemens-gas-turbine-backlog-nears-70-gw-as-company-expands-manufacturing/827390/)
- MHI: one source reports a roughly 35 GW large-frame backlog with the order book full through 2030 and contracts for 2031–34 deliveries. EPRI, via Utility Dive in Sep 2025, put lead times at up to 7 years. — [Severenergo (secondary)](https://severenergo.com/en/gas-turbine-slots-sold-out/); [Medium (secondary)](https://medium.com/@Elongated_musk/gas-turbines-are-the-only-near-term-answer-oems-are-sold-out-through-2029-da185356c328)
- Cadence: quarterly. Siemens Energy's fiscal Q4 comes around mid-November and MHI's interim results around early November (typical cadence; not verified).

**11. Transformer and switchgear lead times**
- Wood Mackenzie Q2 2025 survey: power transformers took 128 weeks and generator step-up (GSU) units 144 weeks. A Reuters report from July 2026, cited secondhand, says GSU lead times exceeded 160 weeks in Q1 2026, against 143 weeks in 2024. WoodMac models a 30% supply shortfall for power transformers and 10% for distribution transformers in 2025–26. A 210-week figure circulates but is unconfirmed. — [Industrial Sage](https://www.industrialsage.com/power-transformer-lead-times-us-grid-shortage/); [Distroforge](https://distroforge.com/blog/transformer-procurement-2026/); [BADGER lead-time index](https://usevawn.com/resources/electrical-equipment-lead-times/); [Digg/Reuters relay](https://digg.com/ai/f5sbesjj)
- Where: Wood Mackenzie (paid); NEMA and supplier lead-time indices (mixed); earnings calls of Hitachi Energy, Siemens Energy Grid, Eaton, Schneider, Hubbell and Vertiv. Watch backlog, book-to-bill and quoted lead times.
- Worsening: GSU or substation transformer lead times move above 160 weeks. Easing: quoted lead times fall and the US capacity additions announced in 2024–26 come online.

### Inferences
- The cleanest stranded-compute precursor in grid data is the "approved to energize but not operational" bucket together with the gap between "approved to energize" and "observed energized/peak consumption" in ERCOT. Stalled site readiness shows up there before it shows up anywhere else.
- Large-load tariffs (85% take-or-pay for up to 12 years in AEP Ohio; GS-5 in Dominion; ≥100 MW rules in Georgia) are the "larger early capital commitments to flush out squatters" Chamath describes. The AEP Ohio queue fell from about 30 GW of interest to 5.6 GW signed under the tariff. Expect the same pattern in ERCOT after SB 6 and in FERC-driven RTO reforms: reported queues will shrink. That is a cleansing, not easing, signal unless energized MW rise.
- Capacity price stuck at the PJM cap plus sold-out turbines plus GSU lead times above 160 weeks means bridge and behind-the-meter solutions are also constrained. Projects counting on onsite gas for 2027 should be checked against turbine delivery slots.

### Gaps
- ERCOT's own monthly "Large Load Interconnection Status" spreadsheet was not opened; the ~474 GW and 9,456 MW figures are secondary.
- PJM's final 2026 load forecast figure for 2030 large load, and the IMM's data center cost share, were not verified from primary documents.
- GE Vernova Q3 2026 results (likely released around 21–22 Oct 2026) did not appear in search results. Check https://www.gevernova.com/investors.
- Wood Mackenzie's 2026 transformer report was not accessed directly.
- No current EIA data levels were pulled.
- The outcomes of the FERC show-cause responses were not found.

---

## Q2. Data center construction and market indicators (Census, CBRE/JLL/Cushman, Epoch AI, SemiAnalysis, Sightline, Data Center Watch, ConstructConnect)

### Takeaway
Building spending and leasing are at records: Census data center construction ran at an $85B annual rate in Aug 2026 (+73% y/y), CBRE vacancy is 1.4% and JLL counts 66 GW under construction, 95% precommitted. At the same time, delay and cancellation trackers show 30–50% of 2026-scheduled US capacity slipping, and local opposition blocked or delayed $68B of projects in Q2 2026. The useful signal is the divergence between capital spent (Census, capex) and capacity actually energized (Epoch AI and satellite trackers; Sightline slippage).

### Cited Findings

**12. US Census Bureau Construction Spending (C30), "Data center" category**
- What it measures: monthly value put in place for private data center construction at a seasonally adjusted annual rate. It covers buildings only and excludes racks and servers.
- Where: https://www.census.gov/construction/c30/c30index.html (URL from general knowledge; not fetched this session). Free; monthly, released around the 1st business day of the month with a two-month lag.
- Level: Aug 2026 (released 1 Oct 2026) was a record $85B SAAR, +7.5% m/m and +73% y/y. Total construction was $2.203T SAAR. ABC's "149%" figure is an annualized growth rate since March, not a cumulative increase. — [Construction Dive](https://www.constructiondive.com/news/data-center-construction-spending-august/831954/); [Yahoo Finance](https://finance.yahoo.com/technology/articles/data-center-construction-spending-hits-120000927.html); [ENR](https://www.enr.com/articles/63746-data-center-construction-spending-accelerates-at-149-annualized-pace); [Census on X](https://x.com/uscensusbureau/status/2105666294783656353)
- Worsening, for stranded compute: spending keeps accelerating while energization trackers lag, which means shells are being built without power. A sudden m/m decline would mean a capex pullback or cancellations. Easing: spending flattens while the energized MW tracked by Epoch and ERCOT catch up.

**13. ConstructConnect data center starts**
- August 2026 data center construction starts were $22.3B, the second highest on record. — [ConstructConnect](https://news.constructconnect.com/august-2026-data-center-report-construction-starts-total-22.3-billion-second-highest-on-record). Monthly. The headline is free; detail is paid.

**14. CBRE North America Data Center Trends (semiannual)**
- Where: [CBRE H1 2026](https://www.cbre.com/insights/books/north-america-data-center-trends-h1-2026). Free; semiannual, with H1 published around Aug–Sep and H2 around Feb–Mar. It covers primary colocation and wholesale markets only.
- Levels (H1 2026): vacancy 1.4%, a record low (1.6% a year earlier); supply 10,903 MW (+33.7%); under construction a record 7,481 MW (+24.8%; prior peak 6,350 MW in H2 2024); 80.4% of under-construction capacity preleased (74.3% a year earlier); net absorption 1,456 MW (+11.7%); less than 1,500 MW of future capacity unclaimed, about 6 months of absorption. Atlanta's under-construction capacity (2,882 MW, +52.3%) passed Northern Virginia's for the first time. NoVA inventory is 4,496.5 MW with vacancy of about 0.2%. — [Data Center Frontier](https://www.datacenterfrontier.com/site-selection/news/55401462/cbre-record-data-center-construction-fails-to-ease-capacity-crunch); [Exchange](https://exchange.construction/news/cbre-north-america-data-center-h1-2026-vacancy-record-construction/)
- Worsening, for stranded compute: under-construction MW keep rising but deliveries to inventory slip (under construction grows faster than supply); preleasing falls below about 75%, meaning speculative shells; vacancy rises in frontier markets.

**15. JLL North America Data Center Report (semiannual)**
- Where: [JLL Midyear 2026](https://www.jll.com/en-us/insights/market-dynamics/north-america-data-centers); [press release](https://www.jll.com/en-us/newsroom/data-center-demand-exceeds-expectations-in-h1-2026). Free; semiannual.
- Levels (Midyear 2026, released around 11 Aug 2026): 66 GW under construction in North America, 95% precommitted. 77% of that is in frontier markets, with Texas at 26 GW, more than double Virginia. H1 2026 absorption was 25 GW, double a year earlier. Vacancy has been about 1% for three straight years. Most tenants signing now are contracting for 2028 delivery. JLL expects more than $700B of debt financing through 2028. In its survey, 79% of Americans support US AI leadership but only 14% support a data center in their own community. — [DCD](https://www.datacenterdynamics.com/en/whitepapers/north-america-data-center-report-midyear-2026/); [JLL newsroom](https://www.jll.com/en-us/newsroom/data-center-demand-exceeds-expectations-in-h1-2026)
- Discrepancy: CBRE counts about 7.5 GW under construction and JLL about 66 GW. The difference is methodology: CBRE covers primary colocation markets, while JLL includes self-build and frontier hyperscale campuses. The two series should not be mixed.
- Cushman & Wakefield's data center reports were not retrieved this session (gap).

**16. Sightline Climate data center tracker (as relayed by Bloomberg)**
- Level (spring 2026; exact date unverified): 30–50% of US data center capacity planned for 2026 is delayed or at risk of cancellation. About 12 GW was expected online in 2026 with only about one-third under active construction. Other coverage cites a 16 GW pipeline with about 5 GW under construction. Causes cited are shortages of transformers, switchgear and batteries, plus grid constraints. — [Yahoo/Tom's Hardware](https://finance.yahoo.com/sectors/technology/articles/half-planned-us-data-center-150928890.html); [Futurism](https://futurism.com/science-energy/data-centers-construction-supply); [X relay](https://x.com/WithRitesh/status/2042293751008432183)
- Where: Sightline Climate (mostly paid; Bloomberg coverage is paywalled). Frequency is uncertain.
- Worsening: the slipped share rises for the 2027 cohort, the cohort Chamath is warning about. Easing: the share of 2027 capacity under active construction rises.

**17. Data Center Watch (local opposition)**
- Where: [datacenterwatch.org/report](https://www.datacenterwatch.org/report). Free; quarterly.
- Levels: Q2 2026 (Apr–Jun): at least 45 projects worth about $68B blocked or delayed, more than half of the large-scale projects newly proposed that quarter, down from Q1. Q1 2026: at least 75 projects worth about $130B, a record quarter. There are 843 local opposition groups across 49 states (833 at end-March). Moratoria are increasingly passed before any proposal arrives, for example Harpersville, AL. — [Tom's Hardware](https://www.tomshardware.com/tech-industry/data-centers/local-opposition-blocked-usd68-billion-worth-of-data-center-projects-in-the-second-quarter-of-2026-data-center-investments-reportedly-still-on-track-to-hit-usd32-trillion-by-2050); [Bloomberg, 21 Sep 2026](https://www.bloomberg.com/news/articles/2026-09-21/new-data-centers-worth-68-billion-disrupted-in-us-data-show); [Trending Topics](https://www.trendingtopics.eu/us-data-center-opposition-q2-2026/)
- Caveat: Data Center Watch itself says attributing delays solely to opposition oversimplifies the picture, and delayed projects are not necessarily lost.
- Worsening: the number of groups and the blocked-$ figure rise again in Q3 2026 (next report around Dec 2026, timing unverified), and opposition spreads to the states that are currently "safe": TX, LA and MS.

**18. Epoch AI Frontier Data Centers directory (satellite-based)**
- Where: https://epoch.ai/data/ai-data-centers (directory); [ranking by power](https://epoch.ai/graphs/largest-ai-data-centers-by-power-capacity); per-site pages such as [Colossus 2](https://epoch.ai/data/ai-data-centers/directory/colossus-2) and [Fairwater Atlanta](https://epoch.ai/data/ai-data-centers/directory/microsoft-fairwater-atlanta). Free, with periodic per-site updates.
- Method: satellite and drone imagery, a cooling-equipment power model (chiller and condenser counts), turbine-based power calculations, and company disclosures. — [Epoch Colossus 2 page](https://epoch.ai/data/ai-data-centers/directory/colossus-2)
- Levels (current IT power): Colossus 2 about 946 MW, Anthropic-Amazon New Carlisle about 910 MW, Fairwater Atlanta about 636 MW. — [Epoch ranking](https://epoch.ai/graphs/largest-ai-data-centers-by-power-capacity)
- Use: compare Epoch's "current IT power" with announced or contracted GW and with chip shipments. A widening gap between chips delivered and estimated energized IT power is the most direct public proxy for stranded compute.

**19. SemiAnalysis Datacenter Industry Model**
- A paid institutional model tracking datacenter capacity by site, quarter by quarter, using satellite imagery, permits and utility filings. Example free coverage: [Colossus 2 article](https://newsletter.semianalysis.com/p/xais-colossus-2-first-gigawatt-datacenter). Pricing and update cadence were not verified (gap).

### Inferences
- Record Census spending plus record JLL absorption plus 30–50% Sightline slippage is consistent with Musk's "partially complete data centers": capital goes in before power. The best composite to watch is Census data center SAAR (capital in) versus Epoch and ERCOT energized MW (capacity out) versus Taiwan ODM rack shipments (chips in).
- JLL's note that new contracts are mostly for 2028 delivery means 2027 deliveries are already fixed. Any slippage in that cohort lands directly on chips shipped in H1 2027, including SpaceX's GPU orders.

### Gaps
- Cushman & Wakefield, Synergy Research and Uptime Institute 2026 figures were not retrieved.
- The Sightline report's exact date and primary text were not accessed.
- SemiAnalysis model figures are paywalled.

---

## Q3. Stranded-compute signals (idle GPUs, ODM and Nvidia inventory and shipments, cancellations, delays)

### Takeaway
Stranded compute is now documented. AWS has staged about $5B of GB300 racks in warehouses because sites lack power, with about $3B more per month projected (Business Insider, Oct 2026). Microsoft exited Nscale's 23,040-GPU Loughton project after the UK grid said power would not arrive until the early-to-mid 2030s (Oct 2026). Upstream, Nvidia's inventory and receivables are rising sharply and Taiwan ODM revenue is still growing 38–87% y/y, so hardware flow is not slowing. The gap between hardware shipped and power energized is the metric to track.

### Cited Findings

**20. Direct reports of idle or warehoused GPUs ("dark GPUs")**
- AWS: internal August emails expected about $5B of Nvidia GB300 racks under an "Early Rack Receipt" process, then about $3B more per month "for the foreseeable future". Some sites had room for racks but not power. One team lacked "a clear forecasted path" to move incoming racks into data centers. Amazon's capex plan is $220B this year; free cash flow for the 12 months to 30 Jun was −$7.6B. — [American Bazaar citing Business Insider, 23 Oct 2026](https://americanbazaaronline.com/2026/10/23/amazons-5-billion-nvidia-ai-servers-sit-idle-in-warehouses-amid-data-center-power-shortages-490651/); [GuruFocus](https://www.gurufocus.com/news/9133467/amazons-ai-hardware-strategy-faces-power-shortages-impacting-gpu-deployment)
- Amazon says staging hardware early is standard practice when supply is uncertain. The $3B/month figure is a projection. — search summary of the coverage above
- Supply-chain framing: [Logistics Viewpoints, 21 Oct 2026, "AI's Stranded Capital Problem: When Hardware Arrives Before the Power"](http://logisticsviewpoints.com/2026/10/21/ais-stranded-capital-problem-when-hardware-arrives-before-the-power/) (not fetched).
- Where to monitor: Business Insider, The Information, Bloomberg and Reuters (paid); hyperscaler 10-Qs (search for "early receipt", "staging", "property and equipment not yet placed in service", "construction in progress"). Hyperscaler construction-in-progress and assets not yet placed in service, compared with placed-in-service PP&E, are a free quarterly proxy. The disclosure terms differ by company and were not checked this session.

**21. Cancelled or exited projects because of power**
- Microsoft–Nscale, Loughton (UK): Microsoft terminated the contract on about 18 Oct 2026 after UK Power Networks said adequate power would not be available until the early-to-mid 2030s. The site was a 50 MW (up to 90 MW) campus with 23,040 GB300 GPUs planned for Azure. Nscale says its other Microsoft contracts are unaffected. — [Data Center Knowledge, 19 Oct 2026](https://www.datacenterknowledge.com/build-design/microsoft-exits-nscale-data-center-deal-over-uk-power-delays); [InvestorPlace](https://investorplace.com/hypergrowthinvesting/2026/10/microsofts-23040-chip-data-center-stalled-on-a-power-problem/)
- Nscale's IPO filing (Sep 2026, data as of 31 Aug 2026) shows $103.4B of total contract value against $2.6B active. Microsoft agreements are worth up to $43.8B through Dec 2033 and Anthropic agreements up to $44.6B. Nscale had not secured binding financing for the Anthropic GPUs. — [Data Center Knowledge](https://www.datacenterknowledge.com/build-design/microsoft-exits-nscale-data-center-deal-over-uk-power-delays). A secondary claim of about 25,000 active GPUs against 461,000 active and contracted is unverified. — search summary
- NextDC M3 (Melbourne): grid-upgrade delays push its next supply increase to FY2028. — search summary (primary not fetched)
- A mid-2026 TD Cowen note, relayed secondhand, says Microsoft cancelled or paused several hundred MW of leases, mostly international. Claims that Stargate's Texas expansion "quietly stalled" come from an aggregator and are unconfirmed. — [Tech-Insider (secondary)](https://tech-insider.org/us-ai-data-center-delays-cancellations-7gw-capacity-crisis-2026/); [BigGo (secondary)](https://finance.biggo.com/news/f1de4930a3163d2b)
- Precedent (2025): CoreWeave cut FY2025 revenue guidance and its year-end power target (from "over 900 MW" to 850 MW) because a third-party developer, widely believed to be Core Scientific, was behind schedule. Backlog was $55.6B with 2.9 GW contracted, and no single developer accounts for more than 20% of contracted power. — [CNBC, Nov 2025](https://www.cnbc.com/2025/11/11/coreweave-stock-core-scientific-delays.html); [DCD](https://www.datacenterdynamics.com/en/news/coreweave-q3-earnings-show-revenue-backlog-doubled-to-556bn/). I found no evidence of a similar CoreWeave guidance cut in 2026.
- Worsening: more anchor tenants exit over power dates; neoclouds or hyperscalers re-baseline "active MW" targets; contracts are re-dated, the CoreWeave 2025 pattern; GPU-backed lenders pull back. Musk says debt markets have "almost entirely shut off".

**22. Nvidia balance sheet (10-Q/10-K)**
- Where: SEC EDGAR, [Q2 FY2027 10-Q, quarter ended 26 Jul 2026](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000075/nvda-20260726.htm). Free; quarterly. The next filing (Q3 FY2027) is expected around late Nov 2026 (typical cadence).
- Levels (fetch-tool extraction; verify exact numbers in the filing):
  - Inventory $31.58B, up from $21.40B on 25 Jan 2026 (+47%).
  - Supply and capacity commitments about $279B; total future commitments about $366B.
  - Accrued excess inventory purchase obligations $2.14B, down from $2.74B.
  - Accounts receivable $63.06B, up from $38.47B; five direct customers account for 70% of receivables.
  - Q2 revenue $96.22B, so DSO is about 60 days (my calculation).
  - Provisions for inventory and excess purchase obligations were $985M in Q2 and $2.1B in H1; gross margin was 75.0%.
  - The filing reportedly describes SB Energy-related guarantees of up to $105B across nine construction phases. Unverified; check the filing. — [Nvidia 10-Q](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000075/nvda-20260726.htm)
- Worsening: DSO and receivables rise faster than revenue, meaning customers are slow to pay for hardware they cannot deploy; inventory provisions rise; customers ask to defer shipments; Nvidia's cloud-service "buyback" agreements grow (about $29B in cloud service agreements plus about $36B in AI cloud agreements per the same extraction, to verify). Easing: DSO stable and provisions falling.

**23. Taiwan ODM and EMS monthly revenue (Foxconn/Hon Hai 2317, Quanta 2382, Wistron 3231, Wiwynn 6669, Inventec 2356, Gigabyte 2376)**
- Where: MOPS (https://mops.twse.com.tw, URL from general knowledge; not fetched this session), where companies post monthly sales by the 10th of the following month, plus company IR pages. Free; monthly.
- Levels (Sep 2026):
  - Foxconn: record revenue of T$1.16T (about $36.5B), +38% y/y. It expects further AI expansion through year-end; full Q3 results are due 12 Nov 2026. — [Quartz](https://qz.com/foxconn-third-quarter-revenue-ai-demand-100526); [Yahoo](https://finance.yahoo.com/technology/ai/articles/foxconn-q3-2026-earnings-beat-132808287.html)
  - Quanta NT$325.3B (+77% y/y) and Wistron NT$380.8B (+87% y/y), from a single tracker. Unverified; check MOPS. — [Stackpath tracker](https://stackpath.ie/global/taiwan-ai-supply-chain-monthly)
  - Foxconn AI servers passed half of revenue for the first time (Aug 2026). — [secondary](https://salamsanat.ir/en/blog/6904/foxconn-ai-server-revenue-record-august-2026/)
- Use: ODM rack revenue is "chips in". Continued high growth while energization lags (Q1 and Q2 indicators) means more rack inventory sits at customer sites or in warehouses. A sudden m/m drop, or ODM commentary about customers "pushing out" rack pull-ins, is the first sign that stranding is feeding back into orders.
- Other hardware OEMs: Supermicro, Dell (ISG AI server backlog) and HPE report quarterly. Watch inventory, backlog, "shipments deferred at customer request", and DSO. None of these were retrieved this session (gap).

**24. GPU rental prices and neocloud utilization**
- The relayed Musk post says GPU rental prices are rising despite power shortages. — [Sam Badawi on X (secondary)](https://x.com/Sam_Badawi/status/2114228636060688635)
- Inference: rising rental prices alongside idle warehoused GPUs is the signature of a physical (power) bottleneck rather than a demand shortfall. If rental prices fall while racks sit idle, that would instead point to over-ordering. Sources for rental prices (e.g., SemiAnalysis or GPU price indices) were not retrieved this session (gap).

### Inferences
- Near-term stranded compute is concentrated where hardware is ordered against power dates that are uncertain: AWS early rack receipt, neoclouds with large contracted-versus-active gaps (Nscale $103.4B vs $2.6B), and GPU purchases arriving in H1 2027 financed with callable debt (SpaceX and others). The Musk and Chamath warnings fit that profile.
- The quarterly checklist: (a) hyperscaler construction in progress and assets not yet placed in service; (b) Nvidia receivables and DSO and inventory provisions; (c) the ODM revenue trend; (d) the energized-MW trackers (Epoch, ERCOT). Divergence between (c) and (d) is the stranded-compute gauge.

### Gaps
- No hyperscaler 10-Q line items were pulled for this session.
- Supermicro, Dell and HPE inventory and backlog levels were not retrieved.
- Nscale's GPU counts are secondary.
- No primary source confirms a 2026 Microsoft lease-cancellation total.
- No reliable public dataset counts warehoused GPUs.

---

## Q4. Policy and permitting (state moratoria, Texas actions, local pushback, federal, water)

### Takeaway
Policy risk escalated sharply in Q3 2026. New York imposed a one-year environmental-permitting moratorium on data centers above 50 MW (EO 62, 14 Jul 2026). Texas Governor Abbott ordered TCEQ on 21 Sep 2026 to pause data center permits until an ERCOT/TWDB grid and water audit is done (expected around mid-Dec 2026). The pause reportedly also covers off-grid, behind-the-meter projects. East Texas water litigation and PUCT records fights add legal uncertainty in exactly the region Chamath flagged.

### Cited Findings

**25. Texas, the most important item for 2027 deliveries**
- On 21 Sep 2026 Abbott directed TCEQ to halt data center permits until ERCOT and the Texas Water Development Board finish their audit. TCEQ says applications can be submitted but "will not advance through the review process". — [Governor's office](https://gov.texas.gov/news/post/governor-abbott-directs-tceq-to-halt-data-center-permits); [Texas Tribune, 21 Sep 2026](https://www.texastribune.org/2026/09/21/texas-data-center-moratorium-water-energy/); [Houston Public Media](https://www.houstonpublicmedia.org/articles/news/energy-environment/2026/09/21/562389/gov-abbott-orders-tceq-to-pause-environmental-permits-for-ai-crytocurrency-data-centers-until-audit-is-complete/)
- Scope: the pause reportedly applies to all data center projects, including "islanded" behind-the-meter facilities. TCEQ told FracTracker it paused "all air and water permits and authorizations related to the construction or development of infrastructure directly supporting data centers". Law firms disagree on exactly how far it reaches. Bracewell expects the audit around mid-Dec 2026, and ERCOT said it intends to finish by December 2026. A 14 Sep 2026 directive told TWDB to enforce data center water-use reporting. — [Foley](https://www.foley.com/insights/publications/2026/09/texas-governor-abbott-directs-tceq-to-freeze-all-data-center-permits-in-a-whole-of-government-action/); [Bracewell](https://www.bracewell.com/resources/governor-abbott-orders-tceq-to-pause-all-permit-issuance-for-data-center-projects/); [B&D Law](https://www.bdlaw.com/publications/texas-pauses-all-environmental-permitting-for-data-centers/); [Global ELR, Oct 2026](https://www.globalelr.com/2026/10/texas-pauses-certain-data-center-approvals-amid-grid-water-and-community-concerns/)
- TCEQ is being scrutinized for alleged non-compliance with the directive. — [Texas Scorecard](https://texasscorecard.com/state/tceq-scrutinized-for-alleged-noncompliance-with-abbott-data-center-directive/)
- On 6 Oct 2026 the PUCT sued the Attorney General's office to block release of data center location records. — [Texas Tribune](https://www.texastribune.org/2026/10/06/texas-data-center-lawsuit-paxton-water/); [Route Fifty](https://www.route-fifty.com/infrastructure/2026/10/texas-agency-sues-stop-release-data-center-records-it-says-could-aid-terrorists/416460/)
- East Texas water litigation (July 2026): Kyle Bass's companies sued the Neches & Trinity Valleys Groundwater Conservation District in federal court to lift its moratorium on large-scale water extraction. — [Texas Tribune, 8 Jul 2026](https://www.texastribune.org/2026/07/08/east-texas-lawsuit-groundwater-rights-bass/); [Texas Standard](https://texasstandard.org/stories/east-texas-lawsuit-water-rights-kyle-bass/)
- Mineral rights: Texas's accommodation doctrine governs conflicts between surface uses and the mineral estate. A Texas court ruling in a solar case held that contract language did not displace the doctrine, which is relevant to data center sites on severed-mineral land. — [Davis Graham](https://davisgraham.com/news-events/texas-court-addresses-conflict-between-solar-and-mineral-development/). A forum thread (low reliability) shows Leon County mineral owners debating data centers and new gas plants near Lake Limestone. — [Mineral Rights Forum](https://www.mineralrightsforum.com/t/data-centers-in-east-tx/85655)
- Worsening: the audit is delayed beyond December; TCEQ's air-permit pause blocks onsite turbines, the bridge-power route for 2027 sites; the legislature, which convenes Jan 2027, codifies limits; more water-district moratoria. Easing: the audit finishes in December and permits resume with conditions.

**26. New York and other states**
- The New York legislature passed a one-year moratorium on new large data centers of ≥20 MW (Senate 44–16, Assembly 102–39, 4 Jun 2026). Governor Hochul instead issued EO 62 on 14 Jul 2026: a one-year moratorium on discretionary environmental permitting for data centers above 50 MW, in effect until the Department of Public Service finalizes a GEIS. — [Davis Polk](https://www.davispolk.com/insights/client-update/new-york-state-enacts-data-center-moratorium); [DLA Piper](https://www.dlapiper.com/en-us/insights/publications/2026/07/new-york-state-legislature-passes-first-in-the-nation-data-center-moratorium); [Rockefeller Institute](https://rockinst.org/blog/pushing-back-on-the-cloud-the-first-statewide-moratorium/)
- Maine's legislature passed a moratorium that Governor Mills vetoed on 24 Apr 2026. Bills have been introduced in OK, VA, PA, SC, SD, VT and WI; none confirmed passed. — [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/using-temporary-pauses-to-develop-permanent-regulation); [Rockefeller Institute update](https://www.rockinst.org/blog/updates-on-the-cloud-more-moratoriums-on-data-centers/)
- About 30 statehouses have introduced or adopted data center siting or utility rules. — [Trending Topics (secondary)](https://www.trendingtopics.eu/us-data-center-opposition-q2-2026/)
- Public opinion: a 2026 Gallup survey, cited secondhand, found 7 in 10 Americans would oppose an AI data center locally. JLL found only 14% support a data center in their own community. — [Forbes Council post](https://forbes.com/councils/forbesbusinesscouncil/2026/10/20/the-data-center-paradox-why-community-opposition-is-now-a-business-constraint); [JLL](https://www.jll.com/en-us/webinars/midyear-2026-data-center-report)
- Where to track: Rockefeller Institute blog, law-firm alerts, Data Center Watch, NCSL bill trackers. Free; event-driven.

**27. Federal**
- FERC RM26-4 and the §206 show-cause proceedings: see indicator #5.
- In the Colossus 2 turbine case, DOJ filed on 15 Jun 2026 arguing that restricting the turbines could threaten national security. That signals federal support for behind-the-meter generation. — [Colossus search summary; Tech-Insider (secondary)](https://tech-insider.org/xai-colossus-2-naacp-lawsuit-illegal-gas-turbines-memphis-2026/)
- I found no comprehensive 2026 list of federal permitting actions (gap).

### Inferences
- The Texas permit pause hits the state with the largest share of 2027 builds (JLL: Texas has 26 GW under construction). If it covers air permits for onsite turbines, behind-the-meter bridge power, the main workaround for ERCOT queue delays, is also blocked. This is the most direct mechanism for Chamath's "pipeline delays that catch people off guard in 2027".
- The local-opposition count of 843 groups and pre-emptive moratoria mean projects without entitlements are increasingly speculative. Fully entitled, energized sites ("energized land", which Chamath owns) gain scarcity value, and his commentary should be read with that interest in mind.

### Gaps
- The precise scope of the TCEQ pause (air versus water versus all permits) has no official TCEQ guidance yet.
- I found no specific 2026 litigation in which mineral owners challenged a data center site, and no source explaining what Chamath meant by "East Texas legal risk". The groundwater moratorium litigation is a candidate but unconfirmed.
- Water and cooling constraint datasets (e.g., state water-use reporting) were not retrieved.

---

## Q5. Key projects and milestones to watch

### Takeaway
Use Epoch AI's satellite-based "current versus projected IT power", permits and court dockets, and company disclosures to track milestones. Colossus 2 is about 946 MW of an estimated 1,531 MW and projected complete around Feb 2027, so its turbines and permits are critical for the H1 2027 chip arrivals. Stargate Abilene is partly live; Milam County is not energized. Fairwater Atlanta is about 636 MW. Meta Hyperion's first power is expected around 2027. Chamath's Arizona site still needs an APS utility agreement.

### Cited Findings

**28. SpaceX/xAI Colossus 2 (Memphis, TN, with power in Southaven, MS)**
- Epoch AI (updated 30 Jul 2026; imagery from 15 Jun 2026): operational, about 946 MW current IT power, about 1,531 MW projected by about 25 Feb 2027. Compute is about 1.11M H100-equivalent, projected about 1.82M (B200/B300). Estimated cost is $35.8B now and $58.0B projected. Cooling: 217 air-cooled chillers and 144 condensers. Milestones: first cluster around Oct 2025 (about 239 MW); Building 3 completion projected Feb 2027. Power comes from gas turbines in Mississippi plus a battery facility. — [Epoch AI](https://epoch.ai/data/ai-data-centers/directory/colossus-2)
- Mississippi issued a PSD permit in March 2026 for a permanent plant of about 1.2 GW (41 turbines), with temporary units to be phased out by mid-2027. At least 27 permanent turbines were under construction as of July (MDEQ). A July 2026 report says 59 turbines were installed without federal permits. The NAACP and SELC sued on 14 Apr 2026, and DOJ filed on 15 Jun 2026. — [Global Energy Monitor](https://www.gem.wiki/Colossus_2_power_station); [Technology.org](https://www.technology.org/2026/07/15/xai-59-unpermitted-gas-turbines-southaven-colossus-2/); [SELC](https://www.selc.org/news/inside-memphis-fight-against-xai/); [Tech-Insider](https://tech-insider.org/xai-colossus-2-naacp-lawsuit-illegal-gas-turbines-memphis-2026/)
- Milestones to watch: permanent turbines commissioned (MDEQ records); court rulings on the turbines; Building 3 completion around Feb 2027; MLGW/TVA grid supply; GPU arrivals in H1 2027 (financed by $40B of debt) matched against energized MW.

**29. OpenAI Stargate: Abilene (Crusoe/Oracle) and Milam County (SB Energy)**
- Abilene is about 1.2 GW planned across 8 buildings. Trackers disagree on progress: 4 of 8 buildings energized (Epoch, earlier); "partially operational, Oracle 42% delivered" (tracker, 29 Aug 2026); 6 of 8 delivered (an Oct 2026 guide). — [Epoch Substack](https://epochai.substack.com/p/openai-stargate-where-the-us-sites); [stargate.how](https://stargate.how/news/current-status-us-stargate-data-centers); [Nameplate Data](https://nameplatereport.substack.com/p/which-stargates-are-real); [compute.institute](https://compute.institute/projects/stargate-abilene)
- Milam County: OpenAI has signed a 1.2 GW lease. Epoch shows 0 GW current capacity with completion projected for Q4 2028; no energization was confirmed as of Oct 2026. — [Silicon Report](https://www.siliconreport.com/datacenters/facility/stargate-milam-county); [Epoch Substack](https://epochai.substack.com/p/openai-stargate-where-the-us-sites)
- Abilene's utility is AEP Texas (the Lancium Clean Campus). — [EEI](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs)
- Watch: the remaining Abilene buildings energized; whether the Texas TCEQ pause affects Stargate's Texas sites; Oracle's RPO and capex commentary.

**30. Microsoft Fairwater (Atlanta; Wisconsin)**
- Fairwater Atlanta: Epoch estimates about 636 MW of IT power, with buildings 3 and 4 operational as of June 2026. An alternative estimate puts energized AI load at about 500 MW in mid-2026. Microsoft has not published a figure. — [Epoch](https://epoch.ai/data/ai-data-centers/directory/microsoft-fairwater-atlanta); [MTS (secondary)](https://drops.mts.now/ai-capex/wiki/sites/gigawatt-site-inventory/); [Compute Atlas](https://computeatlas.net/blog/deep-dive-microsoft-fairwater)

**31. Meta Hyperion (Richland Parish, LA)**
- Not yet operating. Planned for up to 5 GW, with about 2 GW by 2030 and full build-out around 2032. It will be powered by new Entergy gas plants. MTS gives a first-power date of 2027. — [ctaio.dev](https://ctaio.dev/en/ai-infrastructure/largest-ai-data-centers/); [MTS](https://drops.mts.now/ai-capex/wiki/sites/gigawatt-site-inventory/)
- Watch: Entergy Louisiana gas plant milestones (LPSC dockets), and whether first power arrives in 2027.

**32. Anthropic–Amazon New Carlisle (IN)**
- About 910 MW of current IT power, per Epoch. — [Epoch ranking](https://epoch.ai/graphs/largest-ai-data-centers-by-power-capacity)

**33. CoreWeave and Core Scientific; neoclouds**
- See indicator #21 for the 2025 precedent. CoreWeave's 2026 quarters reportedly met or beat guidance. Watch active MW against contracted MW (2.9 GW contracted as of Q3 2025). — [DCD](https://www.datacenterdynamics.com/en/news/coreweave-q3-earnings-show-revenue-backlog-doubled-to-556bn/); search summary

**34. Chamath-linked Arizona site (Buckeye, former Hassayampa Ranch)**
- Arizona Land Consulting bought about 2,000 acres west of Phoenix for a potential 1.5 GW campus, about $25B at full build-out. The next step is an agreement with Arizona Public Service. The plan is to resell entitled, power-accessible land to a builder or tech company. Chamath (27 Jan 2026): "This is the 1 GW data center we are building in AZ". I found no confirmation that the site is energized. — [DCD](https://www.datacenterdynamics.com/en/news/arizona-land-consulting-buys-land-for-potential-15gw-data-center/); [Chamath on X](https://x.com/chamath/status/2016299274259345816?lang=en); [Arizona Land Consulting](https://www.arizonalandconsulting.com/media/wiyr0tne9l3l1k1hk68xjbkha11rww)
- In an Aug 2026 post, Chamath says "LPS (Land Power Shell) is still the most obvious and fastest path to cash on cash returns". — [Chamath on X](https://x.com/chamath/status/2083463694931902561?lang=en)
- Watch: APS service agreement, Arizona Corporation Commission large-load tariff dockets (the EEI list includes an ACC docket), and entitlement milestones.

**35. Other large pipelines listed by EEI (Oct 2026)**
- SB Energy, Piketon, OH: a $33B project with up to 10 GW of generation; SB Energy pays $4.2B for transmission. Hut 8, Corpus Christi: $17B, 1 GW. Nebius, Birmingham: 300 MW. AES Ohio/AWS: ramping from 65 MW to 480 MW within a year, then 1,500 MW in 2031. — [EEI](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs)

### Inferences
- The projects most exposed to "chips before power" in H1 2027 are those whose energization depends on onsite gas (Colossus 2, Hyperion, Texas islanded sites), because turbine slots are sold out and Texas has paused air permits. Grid-connected sites in ERCOT depend on Batch Zero and SB 6 outcomes.
- A monthly dashboard should include: Epoch site pages (current versus projected IT MW), ERCOT LLI status, Census data center SAAR, Taiwan ODM revenue (by the 10th of each month), Data Center Watch (quarterly), GEV, Siemens Energy and MHI backlog (quarterly), PJM backstop results (Dec 2026), the Texas TCEQ/ERCOT audit (around mid-Dec 2026), Nvidia's Q3 FY27 10-Q (around late Nov 2026), and Foxconn Q3 results (12 Nov 2026).

### Gaps
- Abilene building counts conflict across trackers; there is no primary Crusoe or Oracle statement for Oct 2026.
- Microsoft Fairwater Wisconsin's status was not retrieved.
- No 2026 status update was found for Chamath's AZ site, and no site with an "East Texas" connection was identified.
- Stargate Michigan, New Mexico and Ohio sites and Crusoe's Wyoming site were not covered.
