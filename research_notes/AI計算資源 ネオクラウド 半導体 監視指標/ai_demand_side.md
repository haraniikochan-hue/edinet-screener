# AI計算資源の「需要側」監視指標カタログ（2026年10月26日時点）

調査範囲: ハイパースケーラーのcapex・クラウド売上・受注残、AIラボの売上と計算資源コミットメント、リースや契約のシグナル、利用量、フロンティアモデルの停滞判定、セルサイドのコンセンサス。
注意: 2026年の数値は二次報道（集約サイト・ブログ）由来のものが多い。一次ソース（SEC/IR）で確認できたものは【一次】と記した。WebFetchの要約で読んだページは、要約モデルの誤読もあり得る。重要な数値は決算資料原本で再確認すること。

---

## Q1. ハイパースケーラー指標（capex、capex/クラウド売上比、FCF、クラウド成長率、RPO/受注残、容量制約発言、Q3決算日）

### Takeaway
2026年Q2〜Q3の実績は、クラウド成長が加速している（AWS +37%、Azure +43%、Google Cloud +82%、OCI +121%）。受注残も積み上がっており（MSFT $678B、Google Cloud $514B、ORCL $664B）、容量制約の発言も続いている。一方で、Meta・Alphabet・Oracleは四半期FCFがマイナスに転じた。最大の注目点は、10/28（MSFT・GOOGL）と10/29（AMZN）の決算で出る2027年capexの方向感、Azureが会社ガイダンス44〜45%（cc）を達成するか、そして受注残の四半期増加額が保たれるかの3つ。

### Cited Findings

#### 決算カレンダー（2026年10月下旬〜2027年初）
- SpaceX Q3: 10/20（済）。Meta Q3: 10/21（済） — [Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/10/20/spacex-spcx-q3-2026-earnings-call-transcript/); [Meta 8-K Ex.99.1](https://www.sec.gov/Archives/edgar/data/0001326801/000162828026066700/meta-09302026xexhibit991.htm)
- Microsoft FY27 Q1: 2026/10/28（水）引け後、電話会議は5:30pm ET — [Tradingpedia](https://www.tradingpedia.com/2026/10/23/microsoft-faces-high-bar-as-investors-await-q1-earnings/); [Manifold](https://manifold.markets/Terminator2/what-yearoveryear-azure-growth-will)。一方で10/27と書くプレビューもあり、日付が食い違っている — [GO Markets](https://www.gomarkets.com/en/articles/us-earnings-q3-2026-big-tech-ai-roi)。IRページで要確認: https://www.microsoft.com/en-us/investor
- Alphabet Q3: 10/28（水）引け後 — [Top1Markets preview](https://www.top1markets.com/news/alphabet-q3-2026-earnings-preview-cloud-capex)
- Amazon Q3: 10/29 — [Investing.com/Reuters](https://www.investing.com/news/stock-market-news/amazon-cloud-capacity-sold-out-through-2027-ceo-jassy-says-4970506)（検索要約による。会社IRで要確認）
- CoreWeave Q3: 11/9〜10と推定（会社未確認） — [TipRanks](https://www.tipranks.com/news/coreweave-crwv-is-about-to-report-q3-earnings-heres-what-to-expect); [nextearningsdate](https://nextearningsdate.com/coreweave.html)
- Nvidia FY27 Q3: 11/18（水）と推定（未確認）。会社ガイダンスは売上$108B±2% — [Webull](https://www.webull.com/blog/304-Nvidia-Q2-FY2027-Earnings-Beats-Revenue-EPS-Estimates-Guides-Q3-to-108B); [days.to](https://days.to/nvidia-earnings)
- Oracle FY27 Q1は9/10に発表済み。10月に投資家説明会、次はQ2決算 — [Oracle Q1 FY27 search summary / erp.today](https://erp.today/oracle-q1-fy27-results-664b-backlog-ai-contracts/)

#### Microsoft
- FY26 Q4（6月期、7/29発表）: capexは$35.8B、FY26通期は$115.9B。Azureは+43%（予想は約40%）、Microsoft Cloudは$59.3B（+27%）。受注残は$627Bから$678Bへ、四半期で+$51B — [Digital Applied scorecard](https://www.digitalapplied.com/blog/ai-capex-scorecard-earnings-week-july-2026)
- capexガイダンスは、暦年2026が約$175B（第三者のまとめ）、FY27 Q1が$50B超。FY27通期は前年比増とのみ示し、金額はない。巷の「$255〜260B」は決算前のアナリスト予想で、会社ガイダンスではない — [Digital Applied](https://www.digitalapplied.com/blog/ai-capex-scorecard-earnings-week-july-2026)
- 会計変更あり。建物の耐用年数を15年から25年に延ばし、一部リースを再分類した。これで2026暦年の報告capexが約$15B小さく見える。他社比較では要調整 — [Digital Applied](https://www.digitalapplied.com/blog/ai-capex-scorecard-earnings-week-july-2026)
- FY27 Q1のAzureガイダンスは約45%（cc）で、44〜45%とする報道もある。経営陣は「容量制約が続いている」「上期にAzure成長は加速する」と発言。売上ガイダンスは$89.85〜90.95B、コンセンサスはEPS $4.73、売上$90.65B — [Tradingpedia](https://www.tradingpedia.com/2026/10/23/microsoft-faces-high-bar-as-investors-await-q1-earnings/); [Coinotag](https://en.coinotag.com/microsoft-msft-guides-azure-growth-44-to-45-wednesday-report)
- 予想段階ではMicrosoftが「今後1年でFCFがマイナスにならない唯一のハイパースケーラー」とされる — [TradingView/Seeking Alpha](https://www.tradingview.com/news/seekingalpha:5b2f48ec7094b:0-microsoft-is-the-only-hyperscaler-not-forecast-to-dip-into-negative-fcf-in-the-next-year/)

#### Alphabet
- Q2 2026（7/22発表）: Google Cloudの売上は$24.8B（+82%）、営業利益は$8.8B（利益率35.6%、前年20.7%）。クラウド受注残は$514B（Q1比+$50B超）で、約半分が24か月以内に売上化する見込み — [Top1Markets](https://www.top1markets.com/news/alphabet-q3-2026-earnings-preview-cloud-capex)
- Q2のcapexは$44.9B（前年$22.5B）、上期は$80.6B。2026年capexガイダンスは$180〜190Bから$195〜205Bに上方修正（下期は約$119B、1四半期あたり約$60Bを示唆）。CFOは2027年に「さらに意味のある増加（meaningful step-up）」と再確認したが、金額はない — [Top1Markets](https://www.top1markets.com/news/alphabet-q3-2026-earnings-preview-cloud-capex)
- Q2のFCFは-$5.9Bで、2004年IPO以来初のマイナス。営業CFは$39.1B — [Digital Applied](https://www.digitalapplied.com/blog/ai-capex-scorecard-earnings-week-july-2026)。Q3のFCFを-$15〜20Bとみる筆者推定もある（ガイダンスではない） — [Top1Markets](https://www.top1markets.com/news/alphabet-q3-2026-earnings-preview-cloud-capex)
- Q3のコンセンサスは売上約$127.5B（前年$102.3B）、EPS約$2.94 — [Top1Markets](https://www.top1markets.com/news/alphabet-q3-2026-earnings-preview-cloud-capex)

#### Amazon/AWS
- Q2 2026（7/30発表）: AWSの売上は$42.2B（+37%、18四半期ぶりの高成長、予想は約31%）。営業利益は$16.6B（利益率39.4%）。直近12か月のcapexは$173.0B（ファイナンスリース差引後）で、通期ガイダンスは出していない — [Digital Applied](https://www.digitalapplied.com/blog/ai-capex-scorecard-earnings-week-july-2026)
- 2026年の投資額を$220Bとする報道あり（二次） — [shattered.io](https://shattered.io/aws-capacity-largely-sold-out-2027-jassy-220b-2026/)
- Jassyの発言。7/30の決算説明会で「2026年の需要すべてに応えるだけの容量はなく、2027年も同様」。その後a16zのポッドキャストで「2027年までほぼ売り切れ、2028年分もかなりの部分がコミット済み」。ただしオンデマンドとBedrock向けには常に一定の枠を残すとも述べた。「2028年まで売り切れ」という見出し（The Information）は発言より強い表現との指摘がある — [Investing.com/Reuters](https://www.investing.com/news/stock-market-news/amazon-cloud-capacity-sold-out-through-2027-ceo-jassy-says-4970506); [The Information](https://www.theinformation.com/briefings/aws-sold-capacity-2028-jassy-says); [explainx検証記事](https://explainx.ai/blog/aws-capacity-sold-out-2026-2027-2028-jassy-good-chunk-claimed-vs-verified-2026)
- AWSの受注残$496B（Q2）は二次ソースのみで未検証 — [explainx](https://explainx.ai/blog/aws-capacity-sold-out-2026-2027-2028-jassy-good-chunk-claimed-vs-verified-2026)

#### Meta
- 【一次】Q3 2026（9月期）: 売上$64.60B（+26%）、営業CF $32.79B、capex（ファイナンスリース含む）$34.91B、FCF -$2.12B。2026年capexは$130〜145Bから$135〜145Bに絞り込み。2027年はcapexも費用も数値を示さず、「積極投資を継続、予算は策定中」。長期負債は$80.92B（2025年末$58.74B）。人員は前年比-15% — [Meta 8-K Ex.99.1 (SEC)](https://www.sec.gov/Archives/edgar/data/0001326801/000162828026066700/meta-09302026xexhibit991.htm)
- Q2のFCFは$784M（前年$8.5Bから約-91%） — [Digital Applied](https://www.digitalapplied.com/blog/ai-capex-scorecard-earnings-week-july-2026)
- CFOのSusan Liは「来年の予算と容量計画はまだかなり初期段階」と述べた — [Fool transcript (Meta Q3)](https://www.fool.com/earnings/call-transcripts/2026/10/21/meta-meta-q3-2026-earnings-call-transcript/)（検索要約経由）。「2027年capexの具体的見通しは現時点で示さない」という引用は前四半期（7月）の発言の可能性が高い — [Yahoo](https://finance.yahoo.com/markets/article/one-line-from-metas-earnings-call-that-ensured-the-stock-will-likely-stay-dead-money-134542007.html)
- 米4社（MSFT・GOOGL・AMZN・META）の2026年capex見通しの合計は約$730B（CNBC、検索要約経由） — [CNBC](https://www.cnbc.com/2026/10/21/meta-earnings-q3-2026-live-updates.html)

#### Oracle（OCI）
- FY27 Q1（8月期、9/10発表）: 売上$19.3B（+30%）、OCIは$7.4B（+121%、前四半期は+93%）。RPOは$664B（前年比+$209B、6月の$638Bから+$26B）。約半分が36か月以内に売上化する見込み。新規契約の多くは前払いか顧客持ち込みハードで、Oracle側の追加資本は小さいと説明。FY27売上ガイダンスは$90B以上（+34%超）に上方修正 — [erp.today](https://erp.today/oracle-q1-fy27-results-664b-backlog-ai-contracts/); [Bitget](https://www.bitget.com/news/detail/12560605823020)
- capexは約$28Bで売上を上回った。FCFは-$5.0B〜-$5.4B（ソースで差あり）。Q4末以降、850MW・30万GPU超のAI容量を顧客に引き渡した — [erp.today](https://erp.today/oracle-q1-fy27-results-664b-backlog-ai-contracts/); [howtheymake.money](https://howtheymake.money/en/blog/orcl-q1-fy2027-capex-overtook-revenue)

### Inferences
- capex/クラウド売上比（上記数値からの概算）。Alphabetは四半期capex $44.9BをCloud売上$24.8Bで割って約1.8倍。Oracleは$28Bを総売上$19.3Bで割って約1.45倍、OCI単体比では約3.8倍。AWSはTTM capex $173BをQ2売上の年率換算（約$169B）で割って約1.0倍。MicrosoftはQ4 capex $35.8BをMicrosoft Cloud $59.3Bで割って約0.6倍（会計変更で約$15B過小）。この比率が上がり続ける一方でクラウド成長が鈍れば、ROI悪化のシグナルになる。
- 受注残の四半期増加額の目安は、MSFT +$51B、GOOGL +$50B、ORCL +$26B（Oracleは前年比+$209Bなので、四半期増は明らかに鈍化した）。弱気の閾値: 2四半期連続で増加額が半減する（例: GOOGL/MSFTで+$25B未満）、またはRPOの「24〜36か月以内に売上化」の比率が下がる。
- 成長率の閾値:
  - Azure: ガイダンス約45%（cc）から1pt以上下振れ、または次四半期ガイダンスが40%未満なら減速。
  - AWS: 30%を割れば減速。ただし直前の+37%は予想の+31%を大きく上回っていた。
  - Google Cloud: 82%から50%台へ急低下すれば要注意。
  - OCI: 3桁成長からの鈍化はOpenAI向け容量の立ち上がり時期に左右されるため、RPOと合わせて見る。
- 2027年capexの判定材料は、10月末の決算（MSFTのFY27レンジ、GOOGLの「step-up」の大きさ、AMZNの2027年言及）と、2027年1〜2月のQ4決算で示される通年ガイダンス（Meta・Alphabet・Amazonは例年Q4決算で翌年capexを出すと理解しているが、本調査では未検証）。強気は「前年比+40%以上」。弱気は「横ばいまたは減少」、または「容量制約が解消した」という発言。
- 容量制約の発言（Jassy、MSFTの「capacity constrained」）が消えることが、需要減速のいちばん早い定性シグナルになる。

### Gaps
- Amazon Q3の正式な日付と時刻、AWS受注残の一次ソース値、AmazonとMicrosoftの四半期FCFは一次ソースで確認できなかった。
- Microsoftの「受注残$678B」が商業RPO全体なのか、何に対する数値なのかの定義は未確認。
- 2026年Q3の各社コンセンサス（Azure/AWS/GCPの成長率、capex）の一次データ（Visible Alpha、FactSet）にはアクセスできなかった。
- Oracle FY27 Q2の決算日は未確認（例年12月中旬だが検証していない）。

---

## Q2. AIラボ指標（Anthropic S-1、OpenAI、xAI/SpaceXAI、Meta、IPO日程）

### Takeaway
Anthropicの売上は急増している（H1 2026 $16.3B、Q3単独$16.8B、前四半期比+45%）。ただし計算資源コミットメントは$518Bから最大$750Bに膨らみ、その約80%は解約不能と報じられる。S-1では「ハイパースケーラーが競合と見なし、容量を削減・値上げ・終了し得る」とリスクを開示した。このため、売上成長率とコミットメントの比率、粗利率、上位顧客への集中度が需要の持続性を測る核心指標になる。OpenAIは年換算売上約$50B（9月末）、コミットメントは$1.4T超（名目）で、2026年前半に月次の売上目標を未達だったと報じられた。

### Cited Findings

#### Anthropic
- 2026/6/1に秘密裏にS-1ドラフトを提出。9/28にReutersがS-1を報じたが、記事時点ではEDGARに未掲載。2025年売上は約$4.59B。コミットメントは計$518Bで、内訳はGoogle約$111.1B、Amazon $110B、Microsoft $31.4B、Broadcom $161.2B（4社計約$413.7B、残り約$104Bは記事中で帰属不明）。約80%が拘束的かつ解約不能。2025年売上1ドルあたり約$113のコミットメント。261ページ中約80ページがリスク要因 — [Yahoo Finance (2026/9/29)](https://finance.yahoo.com/technology/ai/articles/anthropic-1-518-billion-commitment-165731037.html)
- WSJによるドラフトS-1の精査（Dealroom 10/21付、10/23更新）:
  - 売上: H1 2026が$16.3B（前年同期$1.1B）。Q3 2026は$16.8B（Q2比+45%）で、これは別の投資家向け連絡による数値。
  - 損益: H1の純損失は$80.7Bで、うち約$72Bは資金調達で発行した金融商品に関わる非現金費用。
  - 計算資源: H1のコンピュート・インフラ支出は約$9B（2025年通年は$7.3B）。コミットメントは今後数年で最大$750B（交渉中の案件を含む）。
  - リスク要因: 上位2顧客で売上の約20%。AWS・Google・Microsoftが同社を競合と見なしつつあり、十分な計算資源を得られない恐れがある。容量は「curtailed, repriced, or terminated（削減・値上げ・終了）」され得る。
  - IPO: 最短で2026年11月上場、評価額は約$2Tと報道。
  — [Dealroom](https://dealroom.co/news/164610-anthropics-draft-s-1-reveals-16-3b-revenue-80-7b-loss-and-up-to-750b-com/); [Yahoo/WSJ](https://finance.yahoo.com/technology/ai/articles/anthropic-revenue-hits-16-3-201707100.html)
- コミットメントは$600B超に達し、さらに約$150Bを交渉中で、合計$750Bになり得るとの報道 — [ZeroHedge](https://www.zerohedge.com/ai/807-billion-red-ink-and-600-billion-tab-inside-anthropics-updated-ipo-prospectus)（二次）
- 粗利率は未確定。推計は約44%（Yahoo）、約50%で2028年に77%へ改善（Futurum、投資家向け予測）、2025年見通しを約40%に下方修正（Direxion）と幅がある。推論マージン70%超という推計は会社開示ではない。2026年5月時点のラン・レートは約$47Bと報道 — [Yahoo](https://finance.yahoo.com/markets/stocks/articles/anthropics-gross-margin-most-important-070500338.html); [Futurum](https://futurumgroup.com/insights/anthropic-files-for-ipo-looking-to-beat-openai-to-the-punch/); [Direxion](https://www.direxion.com/xchange/from-claude-to-the-stock-market-anthropics-ipo-filing-explained); [Digital Applied](https://www.digitalapplied.com/blog/anthropic-ipo-filing-2026-claude-stack-analysis)
- 公開版S-1のEDGAR掲載は確認できない（10/3時点のトラッカーで未掲載）。SEC規則では、公開S-1はロードショー開始の15日以上前に提出が必要 — [Leverage Shares tracker](https://leverageshares.com/us/anthropic-ipo-tracker/); [decodethefuture](https://decodethefuture.org/en/anthropic-s1-ipo-filing-explained/)
- 監視すべき開示はEDGARのフルテキスト検索（https://efts.sec.gov/LATEST/search-index?q=Anthropic 、またはhttps://www.sec.gov/edgar/search/ ）で拾う。S-1/A改訂のたびに更新される項目は、売上、粗利率、契約上の義務（contractual obligations）表、上位顧客比率、リスク要因の文言変更。

#### OpenAI
- FTが報じた投資家資料によると、年換算売上は2026年9月末で$50B弱。以前の約$70Bという報道は、Anthropic方式で比較した数値とされる — [AI Magazine](https://aimagazine.com/news/openais-billion-users-us-852bn-valuation-and-stargate)
- WSJによると、2026年前半に月次の売上目標を複数回未達で、市場参入戦略を全面的に見直した — [tech-insider](https://tech-insider.org/openai-revenue-miss-friar-altman-stargate-2026/)（WSJ二次）
- 複数年の計算資源・データセンターのコミットメントは名目$1.4T超（推計）。Altmanは「現状で賄える額を大きく超える」と発言したと報じられる。Stargateの看板は$500B・10GW（2025年1月）、実働プログラムは$400B超・約7GW（2026年5月時点）。最大の個別契約はOracleとの5年$300B（2027〜2032） — [presenc.ai tracker](https://presenc.ai/research/openai-compute-commitments-tracker-2026); [tech-insider](https://tech-insider.org/openai-revenue-miss-friar-altman-stargate-2026/)
- 評価額$1.4T超の調達を、Anthropic上場前に進めていると報道 — [Dealroom](https://dealroom.co/news/164610-anthropics-draft-s-1-reveals-16-3b-revenue-80-7b-loss-and-up-to-750b-com/)

#### SpaceX / SpaceXAI（xAI統合後）
- Q3 2026（10/20）:
  - 全社: 売上$14.6B（+161%）、純利益$4.4B、capex $19.6B。Q4 capexガイダンスは$35〜40B、2027年Q1売上ガイダンスは$33〜37B、受注残は$63B。
  - Super Intelligenceセグメント: 売上$7.6B（前年$813M。Cursor買収分$608Mを含む）。名目計算容量1.7GW、四半期末までに2.5〜3GWが目標。新規導入は現行価格で1年未満で回収するとの説明。
  — [Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/10/20/spacex-spcx-q3-2026-earnings-call-transcript/); [BigGo](https://finance.biggo.com/news/US_SPCX_2026-10-20)
- Muskの発言（トランスクリプト要約経由）:
  - 「超知能向け計算資源は不足し、その不足は長く続く」。
  - 短期契約・スポット的価格を好む。計算資源の約半分を自社用、半分を賃貸に回す。
  - 来年末までに13GWを下回れば驚く。
  - 2027年末のARR目標は$500B〜$1T。
  — [Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/10/20/spacex-spcx-q3-2026-earnings-call-transcript/); [BigGo](https://finance.biggo.com/news/US_SPCX_2026-10-20)
- 依頼文にある「過剰容量論は『ridiculous』」という引用は、検索とトランスクリプト要約のどちらでも確認できなかった（未検証）。なおFoolのページにはプロンプトインジェクション的な文言が含まれていたため、要約内容も念のため原本で確認すること。

#### Meta（自社需要）
- 2026年capexは$135〜145B、2027年は未提示（Q1のMeta欄参照）。FortuneはCFOが「企業（corporate America）を新たなAI顧客として見ている」と報じた（見出しのみで、内容は未読） — [Fortune](https://fortune.com/2026/10/22/metas-cfo-susan-li-has-a-new-ai-customer-in-mind-corporate-america/)

### Inferences
- Anthropicの「コミットメント/年換算売上」比率。Q3の$16.8B×4で約$67Bとすると、$518Bで約7.7倍、$750Bで約11倍。2025年売上基準の113倍から大きく下がっており、売上成長がコミットメントに追いついているかを示す主指標になる。
  - 強気: 四半期の前期比成長が+20%超を維持し、比率が低下を続ける。
  - 弱気: 前期比成長が+10%未満に鈍化する一方で、コミットメントが増え続ける。
- 粗利率は推論の単価と効率を映す。S-1/Aで粗利率が40%台から改善すれば、価格競争（オープンモデル圧力）に耐えている証拠になる。下落すれば、loracleの言う「価格下落圧力」を裏付ける。
- 「ハイパースケーラーが十分に供給しない」というリスク開示は、需要不足ではなく供給不足（需要超過）を示す。同時に、AnthropicがSpaceXのような短期・解約可能な賃貸に頼る理由でもあり、需要が減れば最初に切られるのはこの部分になる。
- OpenAIは「年換算約$50B」と「コミットメント$1.4T超」の乖離が大きく、月次目標の未達報道もある。弱気シナリオの最大の火種はOpenAIの資金調達と契約履行（Oracle RPOの大半はOpenAI関連と一般に理解されているが、本調査では未検証）。

### Gaps
- 公開S-1（EDGAR）の原文、監査済みの粗利率、遊休容量リスクの記述、SpaceX契約の開示有無は確認できなかった。
- OpenAIの一次の売上開示はない（非上場）。IPO日程も未確認。
- SpaceXのIPO関連（S-1/A）で、Anthropic・Google契約の解約条項がどう開示されているかは未確認（S-1/Aへのリンクは存在する: https://www.sec.gov/Archives/edgar/data/0001181412/000162828026039276/spaceexplorationtechnologi.htm ）。

---

## Q3. リース・契約シグナル（新規の大型契約、GPU時間単価、解約条項、キャンセル）

### Takeaway
2026年の大型賃貸契約（Google→SpaceXが月$920M、Anthropic→Colossus 1が月$1.25B）は、Googleほどの企業ですら「つなぎ」の外部容量を必要とする需要超過の証拠である。同時に、どちらも解約可能な条項を持つ。Google契約では、2026/12/31以降は90日前通知でどちらも解約できる。最短で2027年4月頃から解約が効力を持ち得るため、2027年上期は「90日解約の行使があるか」が需要減速の最も直接的な観測点になる。

### Cited Findings
- Google–SpaceX契約:
  - 規模と期間: 約110,000基のNvidia GPU（CPUやメモリ等を含む）を月$920Mで、2026年10月〜2029年6月。9月までは減額料金で段階的に立ち上げ。
  - 解約: 2026/12/31以降、両者とも90日前通知で解約できる。9/30までにGPUが納入されない場合、Googleは1か月の猶予後に即時解約するか、数量と料金を減らせる。
  - 位置づけと開示: GoogleはGemini Enterprise需要に対する「短期のつなぎ」と説明。SECのFWP（free writing prospectus）で開示された。
  — [TechCrunch (2026/6/5)](https://techcrunch.com/2026/06/05/google-will-pay-spacex-920m-per-month-for-compute/)
- Anthropic–SpaceX（Colossus 1）: 22万基超のNvidia GPU、300MW超の全容量を2029年まで月$1.25Bで借りる。TechCrunchはGoogle契約に「Anthropic契約と同様の解約条項」があると記述（Anthropic側の具体的条件は記事中にない）。Muskは「人類に害をなす行為」があれば容量を取り戻す権利を留保していると発言 — [TechCrunch](https://techcrunch.com/2026/06/05/google-will-pay-spacex-920m-per-month-for-compute/); [Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/musks-spacex-has-rented-out-access-to-its-supercomputers-220-000-nvidia-gpus-and-300-megawatts-of-ai-compute-power-to-rival-anthropic-musk-says-no-one-set-off-my-evil-detector-antrhropic-also-interested-in-orbital-data-centers)
- SpaceXがColossus 1を賃貸に回したのは、Grok訓練への統合がうまくいかなかったためとの報道 — [The Next Web](https://thenextweb.com/news/spacex-colossus-1-technical-problems-rented-anthropic)
- 「Colossus 1の容量はxAI拠点全体の11%に上限」とする報道（見出しのみ） — [ActuIA](https://www.actuia.com/en/news/anthropic-rents-colossus-1-for-125-billionmonth-on-an-xai-park-capped-at-11-capacity/)
- Oracleの新規契約の多くは前払いか顧客持ち込みハード — [erp.today](https://erp.today/oracle-q1-fy27-results-664b-backlog-ai-contracts/)
- キャンセルの前例: 2025年2月、TD Cowenのチャネルチェックで、Microsoftが数百MWの米国リースを破棄し、SOQ（statement of qualifications）からリースへの転換も遅らせていると判明。後続レポートでは約6か月で米国と欧州の2GW超から撤退したと推定したが、データセンター需要全体は前年比で増加し、Google・Metaが埋め戻したとしている。2026年について同種のTD Cowenレポートは見つからなかった — [Bloomberg](https://www.bloomberg.com/news/articles/2025-02-24/microsoft-cancels-leases-for-ai-data-centers-analyst-says); [DCD](https://datacenterdynamics.com/en/news/microsoft-cancels-200mw-of-ai-data-center-leases-report); [wccftech](https://wccftech.com/markets-recoil-in-horror-as-trump-imposes-recession-inducing-auto-tariffs-td-cowen-flags-microsofts-more-pervasive-data-center-lease-cancelations//amp/)

### Inferences
- 暗黙のGPU単価（筆者の概算。CPUやメモリ等込みのバンドル価格であり、純粋なGPU単価ではない）:
  - Google契約: $920M÷11万基で月約$8,360/基、730時間で割って約$11.5/GPU時間。
  - Anthropic契約: $1.25B÷22万基で月約$5,680/基、約$7.8/GPU時間（GPU世代の混在が想定され、比較には注意）。
  - 新規契約の単価がこれらを下回っていけば、需給緩和のシグナルになる。
- 90日解約条項の監視:
  - 2027/1/1以降に解約通知が出れば、効力は最短で約4月。開示経路は、SpaceX（上場企業）の8-K・10-Qと、Anthropic S-1/Aの契約義務表。
  - 「解約通知ゼロ・契約延長・新規追加」なら需要は堅調。「解約・減量オプション行使」ならloracleシナリオ（ラボのGPU余剰）の実現。
- 減速の先行シグナル:
  - ハイパースケーラーによる新規リース契約の減少や、SOQからリースへの転換の遅れ（TD Cowen型のチャネルチェック）。
  - データセンター開発業者・ネオクラウドの決算で、「契約の延期」「前払い比率の低下」が出ること。

### Gaps
- Anthropic–SpaceX契約の具体的な解約条件（90日かどうか）は一次ソースで確認できなかった（依頼文の前提は未検証）。
- 2026年の新規GPU賃貸の市場価格（H100/B200/GB300のスポット・長期価格の時系列）は本調査範囲では未収集（供給側担当の範囲と重なる）。
- 2026年に実際にキャンセルや非更新があった事例は見つからなかった。

---

## Q4. 利用量シグナル（トークン量、OpenRouter、企業導入調査、API価格）

### Takeaway
トークン量は爆発的に増えている（Googleは月3.2京トークン、前年比約7倍）。一方で、Rampは「8〜9月はトークン支出がほぼ横ばいで、量だけが増えた」「導入率はSカーブの頭打ちに近い」と警告している。OpenRouterでは、オープンウェイトモデルが約61〜72%のトークンシェアを持つ。したがって、量の増加（計算需要には強気）と、単価の低下・オープンモデルへの移行（ラボの収益性には弱気）を区別して見る必要がある。

### Cited Findings
- Googleの月間トークン処理量: 2024年5月が9.7兆、2025年5月が480兆、2026年5月（I/O）が3.2京で、前年比約7倍。会社発表で監査はない。Q2決算ではGeminiモデルが毎分220億トークン（6か月で+120%、月約1京相当）と報じられた — [GIGAZINE](https://gigazine.net/gsc_news/en/20260520-google-monthly-tokens-processed/); [Shacknews](https://www.shacknews.com/article/149205/google-3-2-quadrillion-monthly-ai-tokens); [a16z on X](https://x.com/a16z/status/2057854267420283217)
- OpenRouter（https://openrouter.ai/rankings 、週次・月次でリアルタイム更新）: 直近の首位はDeepSeek V4.1 Flash系（週30.8T・18.7T、月124T）、GLM 5.3 Flashは週12.5T・月49.7T。ページ内の表に不整合あり — [OpenRouter rankings](https://openrouter.ai/rankings)（検索要約経由）
- オープンウェイトのシェア: 2026/10/5の週に全トークンの約72%、中国5ラボで60%（二次） — [geotoolbox](https://geotoolbox.ai/blog/chinese-ai-models-compared)。2026年5月時点では中国オープンウェイトが約61%（Xiaomi MiMo約21%、DeepSeek約17.6%） — [Datagravity](https://www.datagravity.dev/p/chinas-open-weight-takeover)。両者は方法論が異なる可能性があり、直接比較はできない。
- Ramp AI Index（2026/10/14公表、9月データ、月次。https://ramp.com/data/ai-index ）:
  - 導入率: 米企業のAI有料利用率は55.9%（+0.62pt）。Anthropic 43.8%（+0.25pt）、OpenAI 40.6%（+1.12pt）、xAI +0.6pt。
  - 支出: 従業員1人あたり支出は前月比+11.7%。上位1%企業は$9,568/人/月で、7月ピーク比-3.1%。10月初めにAI支出は8月ピーク比+1.5%の新高値。OpenAIとAnthropicへの支出の約80%は上位1%企業から。
  - トークン: 8〜9月は支出がほぼ伸びず、量は増加。フロンティアの値下げと効率改善でブレンド単価が低下し、契約交渉力は顧客側にある。
  - 筆者の見立て: 導入はSカーブ上部に近く、成長は利用の深化に依存する。シリーズ名は「Cracks in the AI thesis」の第3回。
  — [Ramp AI Index Oct 2026](https://ramp.com/data/ai-index-oct-2026); [Ramp Sept 2026](https://ramp.com/data/ai-index-sept-2026)
- AnthropicがOpenAIを初めて上回ったのは2026年4月データ（34.4%対32.3%） — [Ramp AI Index Oct 2026検索要約](https://ramp.com/data/ai-index-oct-2026); [VentureBeat](https://venturebeat.com/technology/anthropic-finally-beat-openai-in-business-ai-adoption-but-3-big-threats-could-erase-its-lead)
- 「Opus 5.5が企業支出の34%」という主張はX上のチャート由来で、Rampの本文にはない（未検証） — [explainx](https://explainx.ai/blog/ramp-ai-index-october-2026-opus-5-5-34-percent-spend-claim-adoption-flattening)
- Census BTOS（隔週。https://www.census.gov/data/experimental-data-products/business-trends-and-outlook-survey.html ）:
  - 導入率: 業務機能でAIを使う企業は19.8%（2026/5/3までの期間）。2025年12月〜2026年5月は17〜20%の範囲。従業員250人以上では37%、100〜249人では32%。
  - 6か月以内の導入予定は20〜23%。
  - 2026年AI補足調査（2025年11月〜2026年1月）では18%、雇用加重では32%。
  — [Census Bureau story (2026/5)](https://www.census.gov/library/stories/2026/05/ai-use-businesses.html); [Census CES-WP-26-25](https://www2.census.gov/library/working-papers/2026/adrm/ces/CES-WP-26-25.pdf)
- API価格:
  - OpenAI: 2026年8月にGPT-5.6 Solを3か月限定で20%超値下げ（入力/出力 $5/$30→$4/$20）。Terraも-20%、Lunaは-80%。値下げ終了日を11/21とするソースは1件のみ（未確認）。
  - Anthropic: Claude Fable 5は$10/$50、Opus 5は$5/$25。Sonnet 5の導入価格$2/$10は8/31に終了し、9/1から$3/$15。
  - Google: Gemini 3.7 Flashの導入価格$0.75/$3.75は2026/12/31まで。
  — [The Star/Reuters](https://www.thestar.com.my/tech/tech-news/2026/08/22/openai-cuts-developer-pricing-for-frontier-gpt-56-sol-model-by-more-than-20); [DEV](https://dev.to/truongandev/llm-api-pricing-2026-what-changes-on-september-1-2b97); [techjacksolutions](https://techjacksolutions.com/ai-tools/rankings/frontier-ai-price-war/)

### Inferences
- 量と金額の乖離は計算需要にとって中立から強気（トークン量が増えればGPU時間も増える）だが、ラボの売上と粗利にとっては弱気。loracleの「オープンモデルへのシフト」はOpenRouterのデータとは整合する。ただしOpenRouterは価格に敏感な開発者向けの経路で、企業の直接API利用やAzure/Bedrock/Vertex経由の利用を代表しない。シェア72%を市場全体に一般化するのは誤り（推論）。
- オープンモデル需要も推論GPUを必要とし、ネオクラウドや中国勢の容量で処理される。「ラボのGPUが推論に転用される」こと自体は、GPU総需要の減少を意味しない。
- 閾値:
  - Google: 次回発表（Q3決算10/28、または2027年5月のI/O）で前年比の伸びが3倍未満に鈍化すれば減速。
  - Ramp: 導入率の前月比増が3か月連続で+0.3pt未満、かつ1人あたり支出がマイナスなら減速。
  - Census BTOS: 20%前後で頭打ちが続くと中小企業の普及停滞を示唆するが、雇用加重では大企業が主導している点に注意。
  - API価格: 値下げの頻度と幅が加速し（四半期で-30%超）、かつトークン量の伸びが鈍化すれば、需要の価格弾力性が落ちたことを意味する。

### Gaps
- Microsoftの月間トークン処理量の2026年値は見つからなかった。
- OpenRouterの公式な週次オープンモデルシェアは一次で取得できていない（ランキングページは動的）。
- Census BTOSの最新（2026年9〜10月）の値は見つからなかった。

---

## Q5. フロンティア進歩・停滞の指標（Epoch、METR、LMArena/Artificial Analysis、リリース頻度、訓練規模）

### Takeaway
2026年10月時点の主要指標は「停滞」を示していない。Epoch ECIのトップは約1か月で166から169に上がり、reasoning以降の傾きは年約14ptで、それ以前の約6ptを上回る。METRの時間地平の倍増期間は約3〜4か月に短縮した。一方で、オープンとクローズドの差は能力で約4〜7か月、Artificial Analysis指数で3〜12ptと縮小傾向にある。これはloracleの言う「オープンへの代替圧力」を支持するが、「フロンティアの停滞」を支持するものではない。

### Cited Findings
- Epoch Brief（2026/10/23）:
  - ECIの上位: Claude Opus 5.5 169、GPT-6 Astra 169、GPT-6.1 Sol 168、Gemini 4 Argon 166（10/13公開）、Claude Fable 5.1 166、Gemini 3.8 Flash 157。
  - Cyber ECI: 上位クローズドは171、オープンの首位GLM-5.3は160で、6〜7か月遅れ。
  - SpireClimbでは6か月で勝率が90%超に上昇。「Epochの業務を自動化できるか」テストでは「まだ労働者を置き換えられない」との結論。
  — [Epoch Brief Oct 23 2026](https://epochai.substack.com/p/the-epoch-brief-october-23-2026)
- 以前の更新ではGPT-6 Astraが166で首位、Claude Fable 5.1が164 — [Epoch data insights](https://epoch.ai/data-insights)。ECIのフロンティアはreasoning導入後に年約14pt前進（非reasoning期は約6pt）。2026年1月以降、オープンモデルの遅れは平均約4か月 — [Epoch open-closed gap](https://epoch.ai/data-insights/open-closed-eci-gap); [Epoch capabilities](https://epoch.ai/topics/capabilities)
- 反論: 「再加速」の主張（ECIの傾きが2024年前の年8.3ptから2024年後の15.5ptへ）は本物の再加速ではない、という論評 — [Paul Kedrosky](https://paulkedrosky.com/the-ai-re-acceleration-that-wasnt/)
- METR:
  - TH1.1（2026/1/29）: 2023年以降の倍増期間は131日（TH1では165日）、2024年のみでは89日。
  - 2026年5月のレポートでは2024年以降のフロンティアで約105日とされるが、二次ソース。
  - Claude Mythos Preview（2026年3月測定）の50%時間地平は約17.4時間（95%CIは約8.5〜55時間）。
  — [METR TH1.1](https://metr.org/blog/2026-01-29-time-horizon-1-1/); [AI 2027 tracker](https://ai2027-tracker.com/predictions/metr-doubling/); [agitracker](https://agitracker.io/blog/metr-time-horizons-2026/)
- Artificial Analysis Intelligence Index（https://artificialanalysis.ai/models ）:
  - プロプライエタリ: Claude Opus 5.5が58で首位。
  - オープンウェイト: 首位はMiMo-V2.6-Proの46、DeepSeek V4.1 Flashが45。
  - Kimi K3.1 Proは55で4位。重みが公開されれば（11月初め予定）、オープンとの差は12ptから3ptに縮む。
  - 以前のKimi K3の投稿は「差4pt（Claude Opus 5は61）」としており、指数のバージョン変更とみられる不整合がある。
  - 1年前のオープン最高スコアは22。
  — [AA models](https://artificialanalysis.ai/models); [AA on X (Kimi K3.1 Pro)](https://x.com/ArtificialAnlys/status/2113688083145314416); [AA on X (Kimi K3)](https://x.com/ArtificialAnlys/status/2081926991788626011); [Trending Topics](https://www.trendingtopics.eu/kimi-k3-1-pro-open-weight-model/)
- 訓練規模:
  - 2026年の最大訓練ランを検証済みの数値で示すものは見つからなかった。2025年7月以降のクローズドモデルの推計は公開DBにないとの指摘がある。
  - 二次ソースでは、フロンティアは約10^26.5〜10^27 FLOP（日付不明）。
  - Epochの予測ではオープンのフロンティアモデルの訓練計算量が年約4.7倍。
  - 最大のAIデータセンター（IT電力）の記録は2024年半ば以降、約10か月ごとに倍増。
  — [futuresearch](https://futuresearch.ai/app/p/a/rsi-largest-training-compute); [AI 2027 tracker](https://ai2027-tracker.com/predictions/training-compute/); [Epoch open models](https://epoch.ai/data-insights/open-models-threshold); [Epoch data insights](https://epoch.ai/data-insights)
- リリース頻度（2026年の確認できた例）: GPT-5.4（3月）、GPT-5.5・Claude Mythos Preview（4月）、Gemini 3.8 Flash（9月初め）、Gemini 4 Argon（10/13）、GPT-6 Astra / GPT-6.1 Sol / Claude Opus 5.5 / Fable 5.1（9〜10月にECIへ収載） — [Epoch Brief Oct 23 2026](https://epochai.substack.com/p/the-epoch-brief-october-23-2026)

### Inferences
- 「停滞」の判定基準案。このうち2つ以上が2四半期続けば停滞と判断する。
  1. ECIのフロンティアの年率換算の上昇が6pt未満（reasoning導入前の傾き）。
  2. METRの倍増期間が7か月（約210日）超に戻る。
  3. AA指数のトップ更新が6か月以上止まる。
  4. 主要ラボの新世代モデル（GPT-7、Claude 6、Gemini 5級）の発表が延期され、増分リリースだけになる。
  5. 訓練用クラスタ発注の中止報道。
- 現状はいずれも満たしていない。10月の1か月でECIトップが3pt上がり、新たな上位モデルも相次いでいる。
- 「オープンとの差の縮小」は停滞とは別の軸で、価格競争と収益化の圧力（Ramp「量は増えるが支出横ばい」）とつながる。差がAA指数で3pt未満のまま定着し、オープンモデルのOpenRouterシェアが80%超に上がれば、ラボの価格決定力が失われつつあるサインになる。それでも計算総量の需要は落ちない可能性が高い（推論）。
- 訓練ROIの低下を直接測るのは難しい。代理指標は「訓練capex/推論capexの比率」の会社コメント、ラボ売上の伸び÷計算支出の伸び、粗利率の推移。

### Gaps
- LMArena（旧LMSYS）の2026年10月の数値は取得していない。
- 2026年の最大訓練ラン（FLOP）とラボ別の訓練クラスタ規模は、信頼できる一次数値が見つからなかった。
- METRによるGPT-6系・Claude Opus 5.5の時間地平測定は見つからなかった。

---

## Q6. セルサイド・コンセンサスのcapexトラッカー（Goldman、UBS、BofA、MS等）と改訂の見方

### Takeaway
Goldman（2026年9月下旬）は、上位5社のAI capexを2026年$800B、2027年$1.2T（+54%）、2028年$1.4T（+12%）とし、2027年のコンセンサス$1.1Tを上回る見通しを出した。Morgan Stanley（10/15）は、リース込みで2027年の投資を$1.58Tとし、FCFの赤字はこの年が最大（約$600B）と見る。FCFの見通しには機関ごとに矛盾がある（BofAの赤字拡大説と2027年下期の黒字転換説）。2028年に「+12%」へ急減速するという予想自体が、2027年後半から2028年の「成長率の崖」リスクの所在を示している。

### Cited Findings
- Goldman Sachs（2026年9月下旬、ストラテジストRyan Hammond）:
  - capex見通し: Amazon・Alphabet・Microsoft・Oracle・Metaの5社で2026年$800B、2027年$1.2T（+54%、コンセンサス$1.1T比+$130B）、2028年$1.4T（+12%、コンセンサス比+$100B）。
  - 必要収益: 損益分岐に必要なAI年間売上は約$300B（2026〜2027年平均capexに基づく減価償却費と営業費用の合計）。
  - 資金調達: 2027年のIG債発行は約$400〜420B。
  - 一次レポートは未取得で、二次報道に依拠。2028年$2Tとする記事もあり、不一致がある。
  — [Startup Fortune](https://startupfortune.com/goldman-sachs-says-hyperscalers-will-spend-12-trillion-on-ai-in-2027/); [TradingView/CryptoBriefing](https://www.tradingview.com/news/cryptobriefing:58b8b34cf094b:0-goldman-sachs-projects-1-2t-in-ai-infrastructure-capex-by-2027-as-energy-becomes-key-bottleneck/); [CryptoBriefing](https://cryptobriefing.com/goldman-sachs-hyperscaler-capex-ai-revenue/); [briefs.co](https://www.briefs.co/news/goldman-says-hyperscaler-ai-spend-could-jump-to-1-2-trillion/)
- Morgan Stanley（2026/10/15）: 2027年のAI計算投資は総額約$1.58T（リースファイナンス込み）。ハイパースケーラーとネオクラウドのFCFは2027年が最悪で、キャッシュバーンは約$600Bに迫る — [CryptoBriefing](https://cryptobriefing.com/morgan-stanley-hyperscaler-cash-burn-2027/)
- BofA: ハイパースケーラー合計のFCFを2026年-$64B、2027年-$144B、2028年-$186Bと予想 — [TFTC](https://www.tftc.io/ai-capex-cash-flow-negative-2027-peak-hyperscalers)。一方で「2027年下期にFCFが黒字化する」とするBofA解説もあり、矛盾している — [TradingView/Seeking Alpha](https://www.tradingview.com/news/seekingalpha:5b2f48ec7094b:0-microsoft-is-the-only-hyperscaler-not-forecast-to-dip-into-negative-fcf-in-the-next-year/)
- JPMorgan: ハイパースケーラーのFCFは2027年にマイナスとなり、建設資金の多くを信用市場に頼るとの予想 — [Yahoo Finance](https://finance.yahoo.com/markets/article/2-charts-show-why-wall-street-is-right-to-worry-about-tech-stocks-145612923.html)。ReutersがLSEGのコンセンサスを分析すると、上位5社のcapexは2027年までに合計FCFを上回る。S&Pは、一部が2026〜2027年にFCFマイナスになり得るとみる — [Magica](https://magica.com/news/hyperscaler-ai-capex-free-cash-flow-2027)
- 年初来でハイパースケーラーのcapex予想が66%上方修正されたとする記事あり（見出しのみ） — [note/アセットアライブ](https://note.com/asset_alive/n/ne21b98991643?hl=en)

### Inferences
- コンセンサス改訂の見方（推論）。一次はBloomberg（BEst）、FactSet、LSEG I/B/E/S、Visible Alpha の「capex」と「FCF」の予想。無料で追う場合は、決算直後の主要ブローカーのノート要約（CNBC・Reuters・Yahoo）と、Goldman・MS・BofAの定期的な「hyperscaler capex tracker」更新を見る。
- 判定:
  - 強気: 10月末の決算後、2027年のコンセンサスが$1.1Tから$1.2T（Goldman水準）に近づく。
  - 弱気: 2027年の予想が下方修正されるか、2028年の伸び率予想が1桁に下がる。
- 「2027年+54%、2028年+12%」という形は、2028年に向けた成長率の急減速を織り込んでいる。供給側（半導体、ネオクラウド）にとっての典型的な危険信号は「capexの絶対額が増えていても、前年比の伸び率が鈍る局面」。各社が2027年1〜2月のQ4決算で2027年ガイダンスを出し、2027年10月頃に2028年の方向感を示す時期が要所になる。
- FCFのマイナス化と社債発行の増加（Metaの長期負債は$58.7Bから$80.9Bへ）は、需要減速がなくても資本市場の側からcapexを抑える経路になり得る。社債スプレッドやIG発行額も補助指標にする。

### Gaps
- UBSのcapexとFCFの予想は見つからなかった。
- Goldmanの一次レポート原文、LSEGやVisible Alphaのコンセンサス数値（日付付き）は未取得。
- 10月末の決算前後のコンセンサス改訂幅は、まだ発生していないか未取得。
