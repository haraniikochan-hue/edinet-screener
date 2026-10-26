# ネオクラウド／AIインフラの信用ストレスと資金調達環境：監視指標カタログ（2026年10月26日時点）

調査日: 2026-10-26。表記ルール:
- ★ = 筆者の推論で、閾値に出典はない。
- 〔TK〕 = 筆者の学習知識（2025年〜2026年6月まで）で、このセッションでは再検証していない。
- 「二次情報」 = アグリゲーター、Substack、AI生成風のまとめサイト経由。一次報道（Bloomberg/Reuters/CNBC/FT）では未確認。

CNBC、Morningstar、Gartner、TheStreet、Benzinga の本文はいずれも WebFetch で 403 となり、取得できなかった。これらの数値は検索結果の要約に基づくため、一次確認が望ましい。

---

## Q1. 債券／CDS：どの銘柄が主要なゲージで、個人投資家はどこで価格を見られるか

### Takeaway
最も感度が高いゲージは CoreWeave（CRWV）の無担保シニア債（2030/2031/2032年償還、クーポン8.5〜9.75%、合計約$10.0B）と、5年CDSである。

- 10月中旬の水準: CDS は1,195bp（10/15日中、過去最高）から約1,082bp（10/19）、債券利回りは約15〜15.8%、一部の債券は78〜79セントで、すでに「ディストレス」水準にある。
- 他社との比較: Nebius、IREN、Cipher は転換社債中心で、満期は2029年以降である。このため、短期的に信用ストレスを測るには CRWV 債と、Applied Digital、TeraWulf、Cipher のプロジェクト担保債（2030年償還）の方が有効である。
- 個人投資家の情報源: 債券価格は FINRA TRACE（無料）で見られる。CDS には無料のリアルタイムソースがなく、報道経由で追うしかない。

### Cited Findings

#### 1) CoreWeave の債券・CDS（最重要）

**CDS（5年）**
- 10/15 に日中1,195bp で過去最高を付けた。CNBC は1,000bp超をディストレスの目安としている。 — [Motley Fool 10/16](https://www.fool.com/investing/2026/10/16/why-is-coreweave-stock-falling-today/); [BigGo](https://finance.biggo.com/news/7484e05c-561d-43d5-8c9e-95537e5b5688)（1,194.5bp）
- 10/19 は約1,082bp で、前週金曜比約2%低下した。CNBC は1,000bp超を「ディストレス」と表現している。 — [CNBC 10/19](https://www.cnbc.com/2026/10/19/coreweave-oracle-ai-credit-stress.html)
- 約1,115bp（スプレッドが11%超）という数字もある。 — [AI Weekly（Nvidia backstop記事）](https://aiweekly.co/alerts/nvidias-1715b-neocloud-backstop-faces-first-real-market-test)
- 依頼文の「~1,115bp」はこの水準と整合する。

**CDS から逆算した5年デフォルト確率**
- Bloomberg ベースで約60%。 — [CNBC Investing Club 10/16](https://www.cnbc.com/investingclub/2026/10/16/coreweave-credit-default-swaps.html)
- S&P Global データでは約64%。 — [BigGo](https://finance.biggo.com/news/7484e05c-561d-43d5-8c9e-95537e5b5688)

**債券**
- 2031年債の利回りが過去最高の約15.76%に達した。 — [Benzinga](https://www.benzinga.com/markets/bonds/26/10/62541064/coreweave-debt-stress-mounts-bond-yield-hits-record-as-stock-suffers-44-billion-wipeout)
- 9.625% 2032年債は10/19に利回り約14.9%。 — [CNBC 10/19](https://www.cnbc.com/2026/10/19/coreweave-oracle-ai-credit-stress.html)
- 一部の債券は78〜79セントまで下落した。 — [Morningstar](https://www.morningstar.com/bonds/coreweave-data-center-bonds-slide-capex-debt-overhang-concerns)

**格付け**
- S&P は B+（ジャンク）。 — [CNBC 10/14](https://www.cnbc.com/2026/10/14/coreweave-stock-bond-yields-ai-debt.html)

**債券の個別銘柄**
- 「CRWV 9.250% 01Jun2030」（Reg S ISIN USU2069EAA83）のファクトシートがある。 — [Bondsupermart](https://www.bondsupermart.com/bsm/bond-factsheet/USU2069EAA83)
- 〔TK〕2030年債は2025年5月発行の $2B、2031年債は2025年7月発行の $1.75B・9.0% と記憶している（未再検証）。
- 2026年6月発行の9.625% 2032年債は依頼文と CNBC の記述に基づく。

**無担保シニア債の総額（6/30時点）**
- 合計 $10.0B（元本の28.2%）、固定クーポン8.50〜9.75%、2030〜2032年償還。 — [StockTitan 10/15（10/22更新）](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due)

**転換社債（CRWV）**
- 合計 $6.6B。1.75%（2026年4月発行）の2032年債は転換価格約$119.60、2.875%（2026年9月発行）の2033年債は約$97.85。 — [StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due)
- 9/22に $4.2B の2.875% 2033年4月償還債を発行した。 — 同上

#### 2) Nebius（NBIS）：転換社債のみで満期は遠い
- 6/30時点の債務はすべて転換社債で、元本は $10.0B。 — [StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due)
- 6シリーズの満期は2029年6月〜2033年3月で、2028年末までの償還は0%。 — 同上
- 8/24に $5.75B を発行した（0.50% 2030年2月償還は110%償還、4.50% 2034年2月償還は125%償還）。 — 同上
- 現金は $8.0B、6/30時点の担保付債務はゼロ。 — 同上
- 転換社債の公正価値は6/30時点で $20.8B。 — 同上

#### 3) IREN：無担保の転換社債
- 内訳は次のとおり。 — [IREN 10-K FY2026](https://www.sec.gov/Archives/edgar/data/0001878848/000187884826000052/iren-20260630.htm); [IREN press release](https://www.sec.gov/Archives/edgar/data/1878848/000114036126021285/ef20073507_ex99-1.htm); [Blockspace](https://blockspace.media/insight/iren-closes-3-billion-convertible-notes/)
  - 2031年償還 $1B（2025年10月）
  - 2032年償還 $1.15B と2033年6月償還 $1.15B（2025年12月）
  - 1.00% 2033年償還 $3.0B（2026年5月。転換プレミアム32.5%、参照株価$55.15、キャップドコール上限$110.30）
- これらはシニア無担保債務である。 — 同上
- 10/20、IREN の共同CEOが「借入れはない（no-debt）」と市場を安心させる発言をした（見出しベース）。 — [24/7 Wall St. 10/20](https://247wallst.com/investing/2026/10/20/iren-sinks-6-then-recovers-after-co-ceos-no-debt-reassurance-as-neocloud-worries-persist-terawulf-and-applied-digital-rise-3/)

#### 4) Cipher Digital（CIFR、旧 Cipher Mining）
- 10月中旬、$850M のゼロクーポン転換社債を値決めし、既存の転換社債の一部を4,070万株と交換した。 — [24/7 Wall St. 10/13](https://247wallst.com/investing/2026/10/13/cipher-digital-tumbles-14-on-850m-convertible-note-offering-and-share-exchange-applied-digital-drops-5/); [Yahoo/24/7 10/14](https://finance.yahoo.com/markets/stocks/articles/cipher-digital-falls-5-850m-133917862.html)
- 株価は2営業日で約18%下落した。 — 同上
- 建設資金はプロジェクトレベルの担保付債券と親会社レベルの転換社債で調達していると報じられている。 — 同上

#### 5) TeraWulf、Applied Digital、Cipher のプロジェクト担保債
- 〔TK、未再検証〕 TeraWulf は2025年10月、WULF Compute 発行の約$3.2B・7.75%シニア担保債（2030年償還、Google のバックストップ付き）を出した。
- 〔TK、未再検証〕 Cipher は2025年11月、約$1.4B・7.125%シニア担保債（2030年償還）を出した。
- 〔TK、未再検証〕 Applied Digital（APLD ComputeCo）は2025年11月、約$2.35B・9.25%シニア担保債（2030年償還）を出した。
- このセッションの検索では、これら3銘柄の10月の価格・利回りは見つからなかった（Gaps 参照）。
- TeraWulf と Anthropic のケンタッキー案件は20年・約$19Bのリースだが、投資適格の信用補完は「見込み」段階で、署名済みではないとの分析がある（二次情報）。 — [Cycledesk Substack](https://cycledesk.substack.com/p/landlords-and-renters-who-walks-out)

#### 6) Oracle の CDS（AIインフラ信用の「IG側」の代理指標）
- 5年CDSは2026年7月に約203bp で2008年以来の最高、年初は144bp。 — [AI Weekly（Bloomberg 7/20 引用）](https://aiweekly.co/alerts/oracle-nvidia-alphabet-spacex-cds-hit-records-on-ai-debt)
- S&P は Oracle を BBB- に格下げした。FY2026 のフリーキャッシュフローは -$23.7B、総債務は約$130B。 — 同上
- FY2027 に約$40B の追加調達を計画している。 — [letsdatascience（二次情報）](https://letsdatascience.com/news/oracle-credit-risk-nears-18-year-high-as-ai-buildout-raises-financing-pressure)
- 「Oracle CDS が約1,000bp」とする二次記事がある。 — [Wealth Professional](https://www.wealthprofessional.ca/investments/equity-markets/oracles-default-insurance-hits-high-yield-levels-as-ai-debt-mounts/393817)
  - 他の情報源（約200〜300bp）と大きく矛盾し、誤記の可能性が高い。10月の Oracle CDS 水準は未確認。
- 2026年7月時点で、Nvidia の CDS は約79bp、Alphabet と SpaceX の CDS も過去最高を記録した（LSEG データ、FT 引用）。 — [AI Weekly](https://aiweekly.co/alerts/oracle-nvidia-alphabet-spacex-cds-hit-records-on-ai-debt)
- 大手テック銘柄の CDS ネット想定元本は過去最高の $12.5B（2025年Q2比+500%）。Oracle が $6.5B、Amazon と Alphabet が各約$2B。 — 同上

#### 指標カタログ（Q1）

| 指標 | 何を測るか | 入手先 | 頻度 | 無料/有料 | 直近値（日付） | ストレス/回復のシグナル |
|---|---|---|---|---|---|---|
| CRWV 5年CDS | CoreWeave のデフォルトリスク | Bloomberg（`CRWV CDS USD SR 5Y` 系）、S&P Capital IQ、LSEG、ICE。無料では CNBC/Bloomberg の報道経由。週次のポジション量は DTCC TIW の週次 single-name 統計（無料。スプレッド水準は出ない） | 日次 | 有料（報道は無料） | 1,195bp（10/15日中、最高値）→ 1,082bp（10/19）→ 約1,115bp（~10/23） | 1,000bp超 = ディストレス（CNBC）。★1,500bp超、またはアップフロント建て拡大 = リストラ織り込み。★700bp未満で定着 = 回復 |
| CRWV 無担保債 価格・利回り（2030/2031/2032） | 無担保債権者の回収期待 | [FINRA Fixed Income（TRACE）](https://finra-markets.morningstar.com)（銘柄検索で "CoreWeave"）。Bondsupermart、証券会社の債券画面 | 取引ごと（TRACE は即時〜15分遅延で公表） | 無料 | 78〜79セント、利回り約14.9〜15.76%（10月中旬） | ★70セント割れ、または利回り20%超 = 回収率を議論する局面。★90セント超回復 = 正常化。2030年債と2032年債の価格差が縮む（価格が「回収率」に収斂）のは典型的なディストレス |
| CRWV 転換社債（2032 1.75%／2033 2.875%） | 株式オプション性を剥いだ信用評価 | TRACE（144A も公表）、Bloomberg | 取引ごと | 無料/有料 | 未取得 | ★転換価格（$97.85/$119.60）から大きく乖離し債券価格が額面割れ = 「債券フロア」も信用されていない |
| NBIS／IREN／CIFR 転換社債価格 | 満期は遠いが、新規発行の条件（クーポン、償還プレミアム、株式交換）が資金調達余力を示す | TRACE、8-K/6-K の発行条件 | 発行時・随時 | 無料 | NBIS は2034年償還4.50%・125%償還（8月）。CIFR はゼロクーポン $850M＋株式交換（10月） | ★クーポンや償還プレミアムの上昇、転換プレミアム縮小、既存債を株式と交換（希薄化）= 調達が逼迫 |
| WULF／CIFR／APLD のプロジェクト担保債（2030年） | ハイパースケーラー保証付きリース担保債の信用 | TRACE | 取引ごと | 無料 | 未取得 | ★額面割れで利回り10%超 = 保証付きでも敬遠されている。テナントの信用補完（Google 等）の有無が鍵 |
| Oracle 5年CDS | IG側の AI データセンター信用の代理指標 | 報道（Bloomberg/Reuters） | 日次 | 有料 | 約203bp（2026年7月、2008年以来の最高）。10月値は未確認 | ★250bp超 = BBB-→HY 転落リスクの織り込み |
| CDS ネット想定元本（大手テック） | ヘッジ需要の量 | DTCC（週次、無料） | 週次 | 無料 | $12.5B（2026年7月） | 増加 = ヘッジ需要の拡大 |

### Inferences
- **CRWV は「ディストレス」域だが、満期の壁は近くない。** 無担保債の満期は2030年以降であり、2026〜27年の満期（$10.6B）はほぼ GPU 担保プロジェクトローンとベンダーファイナンスである（Q2 参照）。直近の CDS や債券価格は「即時のデフォルト」よりも、2030年代の借換えリスクと劣後（構造的劣後）を織り込んでいると考えられる。
- **IREN の「no-debt」発言は無担保転換社債の存在と矛盾するように見える。** 約$6.45B の転換社債がある（IREN 10-K）。発言は「担保付・アモチ付きの銀行借入れがない」意と思われる（要確認）。
- **注視点は、満期の近い CRWV の DDTL 群と、既存債と同条件での新規発行が可能かどうか。** 転換社債中心の NBIS/IREN/CIFR は満期が遠く、期限の利益喪失リスクは低い。新規転換社債の条件悪化（例: CIFR の株式交換）が「エクイティ市場経由の調達難」のシグナルになる。

### Gaps
- CRWV 各債券の正確なクーポン・CUSIP・10/20以降の価格は、CNBC/Morningstar/Benzinga の本文が取得できず確認できなかった。2031年債のクーポン（9.0%か）も未確認。
- Nebius、IREN、CIFR、WULF、APLD の債券・転換社債の10月の価格・利回りは見つからなかった。
- Nebius、IREN、TeraWulf などの CDS が取引されているかどうかも不明（流動性のある single-name CDS は CRWV、Oracle 等に限られる可能性がある）。
- Oracle の10月の CDS 水準は不明（約1,000bp説は矛盾）。

---

## Q2. GPU 担保ローン、DDTL、データセンター ABS/CMBS、プライベートクレジット、SPV/オフバランス構造

### Takeaway
GPU 担保ローンのスプレッドは2026年中に明確に上昇した。CoreWeave の場合、3月の非遡及ローンは SOFR+2.25%、8月の DDTL 5.5 は SOFR+5.50%。

それでも10月に入っても、市場は条件付きながら開いている。

| 案件 | 時期 | 条件 |
|---|---|---|
| Nebius の364日ブリッジ $3.5B（Citi） | 10/17 | SOFR+2.75%、90日ごとに+25bp でステップアップ |
| Lambda の DDTL 約$1.0B | 10/1 | 6.78% 固定 |
| SpaceX の $40B | 10/25 | 約7.75〜8.3%（クローズ前の報道） |

データセンター ABS のスプレッドは、一般 ABS と逆行して横ばいまたは拡大し、AI 社債の供給に連動するようになった。Meta Hyperion（Beignet SPV）債の価格が、オフバランス構造に対する市場の評価を示すベンチマークになる。

### Cited Findings

#### CoreWeave の債務構造（6/30/2026、10-Q ベース）
StockTitan による整理。 — [StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due)

**総額・流動性**
- 元本 $35.6B（簿価 $35.1B）。
- 現金 $5.5B。流動性は $15.6B（未使用ファシリティ $10.0B、うちリボルバー $2.0B を含む）。

**満期**

| 時期 | 元本 |
|---|---|
| 2026年残り | $4.4B |
| 2027年 | $6.2B |
| 2028年 | $4.4B |
| 2029年 | $2.4B |
| 2030年 | $3.2B |
| 2030年以降 | $14.9B |

- 2027年末までに $10.6B（29.8%）、2028年末までに42.2%が到来する。
- 流動負債に分類された債務は $7.5B（現金の約0.74倍）。

**商品別内訳**
- GPU 担保プロジェクトローン（DDTL を含む）: $13.6B（38.4%）。顧客契約の入金に連動して償還（アモチ）される。
- 無担保シニア債: $10.0B（28.2%）
- 転換社債: $6.6B（18.5%）
- サプライヤーファイナンス: $5.1B（14.4%、実効金利9〜11%）
- Magnetar ローン: $0.2B
- 非遡及債務は $3.7B（約10%）、遡及債務は $31.4B。SPV は $18.2B の非流動資産（主に設備）で担保されている。

**金利負担・感応度**
- Q2 の債務利息は $558M で、売上 $2,575M の21.7%。
- 金利1ポイントの変動で四半期約$30M の影響がある。
- プロジェクトローンの金利は SOFR+2.25%（2026年3月、非遡及）から SOFR+4.50〜5.50%（最新）まで。初期のローンの1本は実効15%。

**リース・コベナンツ**
- 将来のリース支払いは $29.1B（BS 上のリース負債は $16.3B）。未開始の署名済みリースは $35.5B（割引前）。
- 10-Q は、6/30時点でプロジェクトローンの全コベナンツを遵守していたと記載している。

**依頼文の「CoreWeave 債務の約80%が GPU 担保」との比較**
- 上記の内訳では、GPU 担保プロジェクトローンは38.4%で、サプライヤーファイナンス（設備担保と推定）を足しても約53%にとどまる。80%という数字はこのデータと矛盾する。
- 定義（リースや SPV 資産担保を含めるかなど）の違いによる可能性がある。出典の確認が必要。

#### CoreWeave の主な DDTL
- **DDTL 4.0（$8.5B）**: 満期は2032年（ドローは2027年6月まで）。 — [TradingView](https://www.tradingview.com/news/tradingview:49293798ee967:0-coreweave-secures-8-5-billion-delayed-draw-term-loan-to-fund-gpu-infrastructure/)
  - DCD は2027年3月満期と報じており、情報源間で矛盾がある。 — [DCD](https://www.datacenterdynamics.com/en/news/coreweave-secures-85bn-loan-for-gpu-purchases/)
- **DDTL 5.0（$3.1B）**: 2031/11/15満期、ドローは2026年9月まで。「公開市場での GPU 担保ファイナンス」と位置付けられている。 — [StockTitan 8-K](https://www.stocktitan.net/sec-filings/CRWV/8-k-core-weave-inc-reports-material-event-5d847919a3b3.html); [CoreWeave IR](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Closes-3-1-Billion-Loan-Facility-Expanding-Access-to-Public-Markets-for-GPU-Backed-Financing/default.aspx)
- **DDTL 5.5（$2.6B）**: 2031/9/1満期、ドローは2026年12月まで。SOFR+5.50% で、「より広いスプレッド」で締結された。 — [StockTitan 8-K](https://www.stocktitan.net/sec-filings/CRWV/8-k-core-weave-inc-reports-material-event-51aac4a67769.html); [The Energy Mag 8/11](https://www.theenergymag.com/news/2026-08-11/coreweave-ai-2-6-billion-wider-spread)
- エンティティ別の債務整理は CCIR Research にある（未読）。 — [CCIR](https://ccir.io/research/coreweave-debt-by-entity)

#### 10月の「市場はまだ開いている」証拠（反証）
- **Nebius の Citi ブリッジ**
  - $3.5B の364日シニア担保タームローン。SOFR+2.75% から開始し、10/17以降90日ごとに+0.25%（上限3.50%）。 — [Nebius 6-K（SEC）](https://www.sec.gov/Archives/edgar/data/0001513845/000110465926117978/tm2628078d1_6k.htm); [Nebius newsroom](https://nebius.com/newsroom/nebius-secures-3-5-billion-financing-facility-with-citi); [Blockspace](https://blockspace.media/insight/nebius-secures-citi-bridge-loan/)
  - 期限前返済のペナルティはなく、財務コベナンツは最低流動性のみ。満期は2027/10/16。 — 同上
  - ドロー額は非開示。 — [StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due)
  - 署名日は資料によって10/17（6-K）または10/22（プレスリリース日）。 — [TheStreet](https://www.thestreet.com/investing/nebius-citi-bridge-loan-gpu-prices)
- **Nebius の初の担保付ローン**: 7月、約$775M、SOFR+2.50%、2030年10月満期。展開済みの GPU と契約キャッシュフローで担保されている。 — [StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due)
- **Lambda**: 10/1に $1.008B の担保付ディレイドドロー・ファシリティを締結。6.78% 固定で、ドローは GPU の展開に連動する。 — 検索要約（[kingy.ai](https://kingy.ai/blog/neocloud-funding-ai-bubble/); [TheStreet](https://www.thestreet.com/investing/nebius-citi-bridge-loan-gpu-prices)）
  - ある論評は、Nebius の案件は条件付きで満期が短く、Lambda の案件は10月の急落後の調達可能性を示すものではないと指摘している。 — [kingy.ai](https://kingy.ai/blog/neocloud-funding-ai-bubble/)

#### データセンター ABS/CMBS
**スプレッド（Barclays、2026年9月）** — [The Real Deal 9/30](https://therealdeal.com/new-york/2026/09/30/data-center-securities-flash-ai-concerns/); [Yahoo転載](https://finance.yahoo.com/real-estate/articles/data-center-securities-flash-warning-120000014.html)
- ハイパースケーラー ABS は5年国債+150bp（前年比+16bp）。
- ハイパースケーラー社債は SOFR+165bp（前年比+31bp）。
- データセンター ABS は一般の ABS/CMBS との連動が薄れ、AI 関連社債の供給との連動が強まっている。一般 ABS は複数年レンジのタイト端にあるのに対し、DC ABS は横ばいまたは拡大している。

**発行額** — 同上
- DC ABS は2026年 YTD で $11.9B（Barclays）、2025年通年は $15.5B。
- 別の資料は「ABS 発行が最初の8か月で $38.4B」としているが、定義が異なり整合しない。 — [Axis Intelligence](https://axis-intelligence.com/ai-data-center-financing-statistics/)

**その他**
- Morgan Stanley は AI データセンターのクレジットスプレッドがさらに拡大すると予想している（見出し）。8月時点では、社債スプレッドの拡大後に DC ABS が軟化すると予想し、BBB 格を選好していた。 — [Investing.com](https://m.uk.investing.com/news/stock-market-news/morgan-stanley-sees-ai-data-center-credit-spreads-widening-further-93CH-4817296?ampMode=1)
- SEC の適用除外により、データセンター ABS の発行がさらに増えやすくなった（見出しのみ、詳細は未読）。 — [InvestmentNews](https://www.investmentnews.com/alternatives/sec-exemption-clears-path-for-more-data-center-asset-backed-bonds/267767)
- Man Group が「AI ブームを支える誤った価格の債務」という論考を出している（2026年9月、未読）。 — [Man Group](https://www.man.com/insights/views-from-the-floor-2026-9-Sept)

#### プライベートクレジット
- AI データセンター債務の残高は$500B超で、うち約$200Bをプライベートクレジットファンドが保有している（Bloomberg 推計、二次情報経由）。 — [The State of AI](https://www.thestateofai.com/news/ai-data-center-debt-subprime-pension-funds)
- Morgan Stanley は、2028年までに必要な$1.5Tの半分超をプライベートクレジットが供給すると予想している。 — 同上
- Blue Owl の株価は10/23までの1年間で約-43%（二次情報）。 — 検索要約（[thestateofai](https://www.thestateofai.com/news/ai-data-center-debt-subprime-pension-funds)）
- 主な関与例
  - Magnetar: CoreWeave に $0.2B のローン。 — [StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due)
  - Apollo: SpaceX の SPV（Atlas SP）。 — Q7 参照
  - Blue Owl: Meta Hyperion。 — 下記参照

#### Meta Hyperion（Beignet Investor LLC）：オフバランス SPV のベンチマーク
- **構造**: 破産隔離 SPV の Beignet Investor LLC が、144A-for-life のシニア担保・完全償還型（アモチ付き）債券 $27.294B を単一トランシェで発行した。 — [TheValueist on X](https://x.com/TheValueist/status/1984231167290139044); [privatecreditprep](https://privatecreditprep.com/deals/meta-hyperion-27bn-off-balance-sheet)
  - Blue Owl 管理の80:20 JV で、Meta は少数持分兼テナント。Meta は4年ごとにリースの更新を判断できる。 — [The State of AI](https://www.thestateofai.com/news/ai-data-center-debt-subprime-pension-funds)
  - 〔TK〕クーポンは約6.58%、2049年償還。
- **価格・スプレッドは情報源間で矛盾**
  - 10/20に91セントまで下落したとの報道がある（二次情報）。 — [The State of AI](https://www.thestateofai.com/news/ai-data-center-debt-subprime-pension-funds)
  - 約17日前（10月上旬）には94.4セント・利回り約7.2%で、スプレッドは225bpから約195bpへ縮小したとの記述もある（出典の特定は不十分）。
  - 別の検索要約は、国債スプレッドが約230bp（発行時185bp、7月の最大255bp）としている（出典は不明確）。
  - いずれも TRACE での確認が必要。
- **後続案件**: Meta の El Paso 案件の債券は Hyperion 比+40bp で値決めされた（Substack、二次情報）。 — [Electroneconomics](https://electroneconomics.substack.com/p/metas-el-paso-bond-priced-40-basis)

#### 法的リスク
- Quinn Emanuel が「AI データセンター・ファイナンスと訴訟リスク」というクライアントアラートを出している（未読）。 — [Quinn Emanuel PDF](https://www.quinnemanuel.com/media/4dzkfccz/client-alert-ai-data-center-financing-and-litigation-risks.pdf)

#### GPU レンタル価格：強制売却なら最初に崩れる指標だが、10月時点では上昇基調
- **Silicon Data**
  - ネオクラウド H100 指数は10/24に $2.88/GPU時（2025/12/9は $2.00、+44%）。 — [FourWeekMBA](https://fourweekmba.com/ai-nvidia-h100-rent-hits-2-88-an-hour-up-44-since-december/); 検索要約
  - B200 は10/10に $5.93、10/24に $6.45。
- **Ornn OCPI**
  - H100 SXM は10/4の $2.59 から10/24の $3.02 に上昇。ただし10/24当日は-4.7%。 — [Ornn OCPI](https://data.ornn.com/)
  - B200 は10/1の $7.96、10/4の $7.71、10/19の $8.41、10/24の $9.57。 — [Ornn B200](https://data.ornn.com/markets/b200)
- **Nebius** は10/1、オンデマンド H100 価格を $3.85 から $4.50 に引き上げた。 — [Thunder Compute（二次情報）](https://www.thundercompute.com/blog/ai-gpu-rental-market-trends)
- 指数間で水準が異なる（Silicon Data と Ornn）。各指数は自身の時系列でのみ比較すべきである。 — 同上

#### 指標カタログ（Q2）

| 指標 | 何を測るか | 入手先 | 頻度 | 無料/有料 | 直近値 | シグナル |
|---|---|---|---|---|---|---|
| 新規 GPU 担保ローン／DDTL の価格（SOFR+α）・アドバンスレート・テナー | GPU 担保融資市場の開閉 | 8-K Item 1.01/2.03（EDGAR 全文検索 "delayed draw" "GPU"）、プレスリリース、PitchBook LCD（有料） | 案件ごと | 無料（EDGAR）/有料 | CRWV: SOFR+2.25%（3月）→ +5.50%（8月）。NBIS: SOFR+2.50%（7月）/ +2.75%（10月）。Lambda: 6.78% 固定（10/1） | ★SOFR+6%超、テナー短縮（364日ブリッジ化）、アドバンスレート低下、ドロー期限の延長要請 = 逼迫。★新規案件ゼロが4〜6週間続く = 閉鎖 |
| Nebius ブリッジの借換え | ブリッジを恒久資本に置き換えられるか | 6-K/8-K、プレスリリース | 随時 | 無料 | 10/17締結、ステップアップは90日ごと（初回は~2027/1/15頃★） | ★ステップアップ前に HY/転換社債/ABS で借り換えられれば健全。ドローして放置なら逼迫 |
| CRWV DDTL のドロー状況・未使用枠 | 流動性バッファ | 10-Q の Debt 注記 | 四半期 | 無料 | 未使用枠 $10.0B（6/30） | ★未使用枠の急減、ドロー期限（DDTL 5.5 は2026年12月まで）の延長・失効 |
| データセンター ABS スプレッド・発行額 | 証券化市場の受容度 | Barclays/JPM/BofA のリサーチ（有料）、KBRA/S&P の新規格付けリリース（無料）、Finsight（一部無料） | 週次〜案件ごと | 有料中心 | 発行 $11.9B YTD（9月）。ハイパースケーラー ABS は5年国債+150bp | ★一般 ABS との格差拡大、案件延期・規模縮小、BBB トランシェの消化難 |
| Meta Hyperion（Beignet 2049年債）価格 | オフバランス SPV への評価 | TRACE（144A も公表）、Bloomberg | 取引ごと | 無料 | 91セント（10/20、二次情報）。スプレッド約195〜230bp（矛盾あり） | ★90セント割れ、または250bp超 = IG テナント付き SPV でも敬遠。El Paso 等の後続案件の上乗せ（+40bp）の拡大 |
| GPU レンタル価格指数（H100/H200/B200） | GPU の需給。強制売却なら急落するはず | [Ornn OCPI](https://data.ornn.com/)（無料表示あり）、Silicon Data（一部有料）、各社の公開価格 | 日次 | 無料/一部有料 | H100 は $2.88（SD）/ $3.02（Ornn）、B200 は $6.45（SD）/ $9.57（Ornn）（いずれも10/24） | ★1四半期で-20%超、または中古 H100 の売り案件の急増 = 担保価値の毀損と清算の進行。現状は上昇で、清算シグナルなし |
| プライベートクレジット運用会社の株価（OWL、APO、BX、ARES） | 流動性・評判リスク | 株価（無料） | 日次 | 無料 | OWL は1年で約-43%（~10/23、二次情報） | ★償還請求の増加、ゲート（償還制限）発動の報道 |

### Inferences
- **「完全な閉鎖」ではなく、選別と価格の上昇が起きている。** 10月でも Nebius（現金$8B、満期は2029年以降）、Lambda、SpaceX は調達できた。一方、CoreWeave の新規ローンのスプレッドは年初比で約+300bp に拡大した。Musk の「ほぼ全面的に閉鎖」は、少なくとも10月上旬までのデータとは完全には一致しない。
- **Nebius の364日ブリッジは「時間を買う」構造である。** 90日ごとのステップアップは借換えを促す設計であり、2027年初めまでに恒久資本へ借り換えられるかが Nebius の最重要イベントになる★。
- **GPU レンタル価格の上昇は、強制売却の連鎖に反する現時点の最大の反証である。** 担保価値（GPU の時価）が維持されれば、LTV 型の担保ローンでマージンコール的な連鎖は起きにくい。逆に指数が急落に転じれば、最も早い警報になる★。
- **CoreWeave の2026〜27年の満期 $10.6B は大半が顧客契約連動の償還（アモチ）である。** 顧客（Microsoft/OpenAI/Meta）からの入金が続く限り自動的に返済が進む。真のリスクは、顧客契約の解約・減額でアモチの原資が消えることにある（Q4 参照）★。

### Gaps
- Lambda の DDTL の一次資料（プレスリリース本文、貸し手名）は未取得。
- Crusoe、Nscale、Fluidstack、Firmus の10月の資金調達条件は見つからなかった。
- データセンター ABS/CMBS の10月のスプレッド水準（数値）は見つからなかった（Barclays の9月コメントが最新）。
- Meta Hyperion 債の10月の価格は二次情報のみで、TRACE での確認が必要。
- 中古 GPU（H100 等）の売買価格の公開指数は確認できなかった。
- Blackstone、Apollo、Magnetar のネオクラウド向けエクスポージャーの総額は不明。

---

## Q3. 広域クレジット：US HY OAS、テック HY、レバレッジドローン、IG テック発行、BDC、金利

### Takeaway
広域のクレジット市場はまだ平穏で、ストレスは AI インフラに局所化している。

- US HY OAS は3.40%（10/22、FRED）で、52週レンジ（2.60〜3.46%）の上端に近い。
- IG OAS は約82bp（10/8）。CCC OAS は約13.4%（二次情報）と高い。
- ハイパースケーラーの起債は2026年に記録的な規模（7月上旬までに約$194B）となり、7月時点で既発債の大半が発行時より高い利回りで取引されていた。
- 9月16日に FRB が3年ぶりに利上げしたとの記述がある（要確認）。これも資金調達コストを押し上げている。

### Cited Findings
- **US HY OAS**（BAMLH0A0HYM2）
  - 10/22に3.40%、10/21に3.27%、10/20に3.33%。 — [FRED](https://fred.stlouisfed.org/series/BAMLH0A0HYM2); [govspending.org](https://govspending.org/series/BAMLH0A0HYM2/)
  - 過去52週のレンジは2.60%（2026/8/28）〜3.46%（2026/3/30）。 — [Macrotrends](https://www.macrotrends.net/3006/high-yield-spread)
- **CCC OAS** は約1,340bp（前日1,307bp、1週間前1,297bp）。Substack の記述で二次情報。 — [Clint Smith Substack](https://clintsmith.substack.com/p/the-market-looked-healthier-credit)
  - FRED では BAMLH0A3HYC で確認できる（★推奨）。
- **IG OAS**（BAMLC0A0CM）は2026/10/8に82bp。 — [ConvexTrade](https://convextrade.com/metrics/bamlc0a0cm)
- **HY 発行額**は YTD $186.9B（2026年6月末の N-CSRS と推定）で、AI インフラとデータセンター関連のファイナンス急増が支えた。 — [T. Rowe Price OHA N-CSRS](https://www.sec.gov/Archives/edgar/data/0002028436/000202843626000009/ck0002028436-20260630.htm)
- **Apollo Debt Solutions BDC の Q3 2026 8-K**: 2026年前半に生成AI の進展がソフトウェア／テック系サービス企業の急落を引き起こし、その後は AI インフラに必要な巨額資本へ関心が移ったと記載している。 — [Apollo Debt Solutions 8-K](https://www.sec.gov/Archives/edgar/data/0001837532/000119312526427340/d164012d8k.htm)
- **ハイパースケーラーの社債発行**
  - 2025年は5社で計$121B（2020〜24年の平均は年$28B）。BofA の集計。 — [検索要約（Quartz 他）](https://qz.com/tech-hyperscaler-bond-issuance-investment-grade-index-050526)
  - 2026年は7/7までに4社で約$194B（Reuters/LSEG）、8/10までに Microsoft を含む5社で約$220B（BNP）。 — [MLQ.ai](https://mlq.ai/news/hyperscaler-bond-issuance-reaches-about-220-billion-as-ai-financing-costs-rise/); [Yahoo/Reuters](https://finance.yahoo.com/markets/stocks/articles/hyperscaler-debt-binge-pushes-yields-134825104.html)
  - 予測は Goldman が2026年約$250B・2027年$400B、Morgan Stanley が2026年$400B と幅が大きい。 — 同上
  - 2026年発行のハイパースケーラー債91本のうち78本が、7/28時点で発行時より高い利回り（中央値+22bp）で取引されていた。 — [Yahoo/Reuters](https://finance.yahoo.com/markets/stocks/articles/hyperscaler-debt-binge-pushes-yields-134825104.html)
  - 大手テックの IG 社債発行は YTD で過去最高の$182B（7月時点）。 — [AI Weekly](https://aiweekly.co/alerts/oracle-nvidia-alphabet-spacex-cds-hit-records-on-ai-debt)
- **金利**
  - FRB が3年ぶりに利上げした（関連リンクの日付は2026/9/16）。 — [The Real Deal 9/30（WebFetch 要約）](https://therealdeal.com/new-york/2026/09/30/data-center-securities-flash-ai-concerns/)
    - 一次確認していない。利上げ幅や現在の FF レンジは未確認。
  - FRB の Kevin Warsh は、ハイパースケーラーの資金調達が利回り上昇の一因だと発言した。 — 同上
- **テック・ブレッドスとクレジットのダイバージェンス**: 「テックは打撃を受けているが、市場の裾野（ブレッドス）は持ちこたえており、クレジットはまだ崩れを確認していない」という Substack の論評がある。 — [Clint Smith Substack](https://clintsmith.substack.com/p/tech-is-taking-the-hit-breadth-is)

#### 指標カタログ（Q3）

| 指標 | 何を測るか | 入手先 | 頻度 | 無料/有料 | 直近値 | シグナル |
|---|---|---|---|---|---|---|
| ICE BofA US HY OAS（BAMLH0A0HYM2） | HY 全体のリスクプレミアム | [FRED](https://fred.stlouisfed.org/series/BAMLH0A0HYM2) | 日次（1営業日遅れ） | 無料 | 3.40%（10/22） | ★4.0%超 = AI 以外へ波及開始、★5%超 = 広域ストレス、★3.0%未満へ戻る = 局所化継続 |
| CCC OAS（BAMLH0A3HYC） | 低格付け層の調達環境 | FRED | 日次 | 無料 | 約13.4%（二次情報） | ★15%超、または CCC と BB の格差拡大 = 選別の激化 |
| BB／B OAS（BAMLH0A1HYBB／BAMLH0A2HYB） | CRWV（B+）が属する格付け帯 | FRED | 日次 | 無料 | 未取得 | ★CRWV の利回りと B 指数の利回りの格差の拡大 = 銘柄固有のストレス（B 指数の現状値は未取得） |
| IG OAS（BAMLC0A0CM） | IG（ハイパースケーラー）の調達コスト | FRED | 日次 | 無料 | 82bp（10/8） | ★100bp超 = ハイパースケーラーの起債も高コスト化 |
| ICE BofA US テック HY／IG セクター指数 | テック限定のスプレッド | ICE Data Indices（有料）、Bloomberg | 日次 | 有料 | 未取得 | ★全体の OAS とのスプレッド差の拡大 |
| HYG/LQD、JNK、BKLN/SRLN（ローン ETF）の価格・資金流出入 | 流動性・資金フローの代理指標 | ETF の価格（無料）、ETF.com のフロー | 日次 | 無料 | 未取得 | ★BKLN の大幅ディスカウント、連続流出 |
| Morningstar LSTA US レバレッジドローン指数（価格） | ローン市場の値付け | PitchBook LCD（有料）。無料ではニュース経由 | 日次 | 有料 | 未取得 | ★指数価格が95割れ、またはテック・ローンの80割れ比率（ディストレス比率）の上昇 |
| ハイパースケーラー新発債の条件（規模、需要倍率、新発プレミアム） | IG 側の吸収力 | Bloomberg/Reuters/IFR の報道、8-K（FWP/424B2） | 案件ごと | 無料（報道・EDGAR） | 2026 YTD は約$194〜220B（7〜8月） | ★新発プレミアム20bp超、需要倍率3倍割れ、既発債の連鎖的なワイド化 |
| BDC の NAV、非発生債権（non-accrual）、P/NAV | プライベートクレジットのマーク | 各 BDC の10-Q/決算（ARCC、OBDC、BXSL、Apollo Debt Solutions など）、BIZD ETF | 四半期（Q3 は11月上旬〜中旬★） | 無料 | 未取得 | ★NAV の-3%超、non-accrual の上昇、P/NAV が0.8割れ、非上場 BDC の償還請求の増加 |
| FedWatch（FF 先物の織り込み） | 金利パス | [CME FedWatch](https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html) | リアルタイム | 無料 | 未取得（9/16に利上げとの記述あり） | ★追加利上げの織り込み上昇 = 変動金利の DDTL（SOFR 連動）の負担増。CRWV は1pt で四半期約$30M |
| 10年 UST、SOFR 先物 | 長期金利・ベースレート | FRED（DGS10、SOFR） | 日次 | 無料 | 未取得 | 上昇 = 借換えコストの上昇 |

### Inferences
- **現状は「局所的なディストレス」で、HY 全体の OAS は340bp前後にとどまる。** CRWV の CDS は1,000bp超だが、HY 全体の OAS は340bp近辺にある。HY 全体がワイド化し始めれば、ネオクラウドの調達窓口はさらに狭まる★。
- **IG 側の供給過多が中間層の調達を圧迫している可能性がある。** IG 側では、ハイパースケーラーの記録的な起債が既発債の利回りを押し上げている。これが DC ABS や Hyperion 型 SPV 債のスプレッド拡大の主因であり（Barclays の分析）、ネオクラウドのような中間層の調達を圧迫している構図と考えられる★。
- **利上げ局面の確認が必要。** 9月に利上げ局面に入った（要確認）とすれば、変動金利の GPU 担保ローン（SOFR+α）の利払い負担が直接増える。

### Gaps
- 10月のレバレッジドローン指数の価格、テック HY のセクタースプレッド、BDC の Q3 マークは見つからなかった。
- FRB の9月の利上げの事実関係（幅、現行レンジ）は一次確認していない。
- 10月のハイパースケーラー起債の実績（10月単月）は見つからなかった。

---

## Q4. 企業レベルの開示：10-Q/8-K で何を見るか、11月の決算日程

### Takeaway
最重要の開示項目は次の4つである。

- 10-Q の債務満期表と流動負債への分類（CRWV は1年以内に$7.5B）
- コベナンツ遵守の記載
- 継続企業の前提に関する注記
- RPO と顧客集中度（Microsoft/OpenAI/Meta）

これに加えて、8-K の Item 1.02（重要契約の終了）、2.04（期限の利益喪失）、2.06（減損）が、契約解約や GPU の減損を最も早く示すトリガーになる。CoreWeave の Q3 決算は11月10〜16日頃と推定されるが、公式日程は未確認である。

### Cited Findings
- **CRWV の10-Q（Q2 2026）で確認できる項目**: 満期表、流動負債への分類（$7.5B）、コベナンツ遵守の記載、未開始リース（$35.5B）、債務利息の対売上比（21.7%）。 — [StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due)
- **Nebius**: 繰延収益（顧客の前払い）が6/30時点で$6.0B（6か月前は$1.6B）、未開始リースは$12.1B。 — 同上
- **CoreWeave の購入コミットメント**: $45B と主張しており、うち Meta が$14B、OpenAI が$11B（Substack 経由、二次情報）。 — [Cafetech Substack](https://cafetechinenglish.substack.com/p/ais-house-of-cards)
- **SLA のミスマッチ**: ネオクラウドは DC 事業者との契約（電力・冷却）と顧客との契約（GPU の可用性・性能）を別々に結んでいる。顧客へのクレジット（実質的な違約金）が、DC 事業者から回収できる額を上回り得る（数百万ドル単位）。 — [DCD Opinion](https://www.datacenterdynamics.com/en/opinions/the-sla-mismatch-at-the-center-of-the-neocloud-model/)
  - Chamath の「liquidated damages」発言の一次ソースは見つからなかった（Gaps 参照）。
- **Gartner（2026/10/14）**: 2030年までに、コスト圧力と差別化されたビジネスモデルの欠如により、80%超のネオクラウド事業者が独立した事業運営をやめると予測した。また、現在の設備投資ペースが続けば、2030年末までに$3.5T超の AI インフラ投資が減損リスクにさらされるとした。 — [Gartner プレスリリース](https://www.gartner.com/en/newsroom/press-releases/2026-10-14-gartner-says-over-us-dollars-three-and-a-half-trillion-of-artificial-intelligence-infrastructure-spending-could-be-exposed-to-impairment-by-the-end-of-2030); [CRN Asia](https://www.crnasia.com/news/2026/cloud/gartner-80-of-neoclouds-to-lose-independence-by-2030-as-ai)
  - 予測は「独立した事業運営の停止」であり、買収・統合を含む。倒産だけを意味するわけではない。 — 同上
  - Gartner の Will Sommer は「アウトパフォームする者、アンダーパフォームする者、市場から退出せざるを得ない者が出る」と述べた。 — [The Register](https://www.theregister.com/a/5302856)
  - 業界幹部は数百社のうち生き残るのは7〜10社と見ている（The Information 経由、未検証）。 — [FourWeekMBA](https://fourweekmba.com/ai-executives-see-only-7-to-10-neoclouds-surviving-a-shakeout/)
- **決算日程**
  - CoreWeave の Q3 2026 は11/16（月）の17時（米東部時間）と推定されるが、公式には未確認。 — [days.to](https://days.to/coreweave-earnings)
    - 前年は10/27に日程を発表し、11/10（月）に決算を出した。 — [Business Wire 2025](https://www.businesswire.com/news/home/20251027854203/en/CoreWeave-Announces-Date-of-Third-Quarter-2025-Financial-Results)
    - Kalshi 関連市場の取引締切が11/10の16時（米東部時間）であることから、11/10前後の可能性もある。 — [検索要約](https://www.quantisnow.com/earnings/CRWV)
  - Cipher Digital の決算は2026/11/2。 — [Yahoo Finance CIFR](https://finance.yahoo.com/quote/CIFR/)
  - Nebius、IREN、Applied Digital、TeraWulf、Nvidia の Q3 決算日は未確認。Lambda、Crusoe、Nscale は非上場で決算発表はない。
- **8-K の項目番号**（SEC Form 8-K の様式による）: Item 1.01（重要契約の締結＝新規ローン）、1.02（重要契約の終了）、2.03（直接金融債務の発生）、2.04（債務を加速させるトリガー事由＝期限の利益喪失）、2.05（撤退・処分費用）、2.06（重要な減損）、3.01（上場廃止の通知）、5.02（役員の異動）。 — [SEC Form 8-K](https://www.sec.gov/files/form8-k.pdf)

#### 指標カタログ（Q4）

| 開示項目 | 何を見るか | 入手先 | 頻度 | シグナル |
|---|---|---|---|---|
| 10-Q の債務満期表と流動負債への分類 | 12か月以内の返済額と現金の比率 | [EDGAR](https://www.sec.gov/edgar/search/) | 四半期 | ★流動債務／現金が1.0倍超（CRWV は0.74倍） |
| コベナンツ遵守の記載、ウェーバー、修正契約（Amendment） | 財務制限条項への抵触 | 10-Q の Debt 注記、8-K Item 1.01（Amendment） | 四半期・随時 | ★「遵守していた」の文言が消える、または修正やウェーバーの8-K が出る |
| 継続企業の前提（ASC 205-40）、"substantial doubt" | 経営者自身による存続リスクの評価 | 10-Q/10-K、EDGAR 全文検索 | 四半期 | 出現 = 重大なシグナル |
| RPO、受注残、繰延収益 | 将来の売上の確度 | 10-Q の収益認識の注記 | 四半期 | ★RPO の QoQ 減少、繰延収益（前受金）の減少、契約期間の短縮 |
| 顧客集中度（Microsoft、OpenAI、Meta、Google、Anthropic） | 単一顧客への依存 | 10-Q のセグメント／集中リスクの注記 | 四半期 | ★上位顧客の比率上昇、または上位顧客の契約変更 |
| 8-K Item 1.02（重要契約の終了） | 顧客・リース契約の解約 | EDGAR | 随時 | 出現 = 最重要の警報。解約通知の条項（90日など）の行使 |
| 8-K Item 2.04（期限の利益喪失） | デフォルト・クロスデフォルト | EDGAR | 随時 | 出現 = デフォルト |
| 8-K Item 2.06、10-Q の減損・耐用年数の変更 | GPU の減損、減価償却期間の短縮 | EDGAR | 随時・四半期 | ★GPU の耐用年数を6年から短縮する、または減損を計上する = 担保価値の下方修正 |
| 設備投資ガイダンス、電力（MW）稼働計画 | 成長の減速、資金不足 | 決算資料・決算説明会 | 四半期 | ★ガイダンスの下方修正（資金制約による場合）、MW 稼働の延期 |
| 違約金・SLA クレジット、"liquidated damages" の記載 | 納期遅延のペナルティ | 10-Q のリスク要因・偶発債務の注記、契約書の添付（Exhibit 10.x） | 四半期 | ★偶発債務の計上、顧客によるクレジット請求の開示 |
| 未開始リース（CRWV $35.5B、NBIS $12.1B） | 将来の固定費負担 | 10-Q のリース注記 | 四半期 | ★未開始リースの急増（固定費の先積み）または解約 |
| 利息／売上比率（CRWV 21.7%、NBIS 11.6%） | 債務の持続性 | 10-Q | 四半期 | ★25%超へ上昇 |

### Inferences
- **2026〜27年に返済が来る GPU ローンの原資は顧客契約からの入金である。** したがって、顧客契約の解約（8-K Item 1.02）や減額が最も直接的な破綻経路になる★。
- **違約金（liquidated damages）は二方向のリスクである。**
  - ネオクラウドが支払う側: GPU や電力の納期遅延で、顧客への違約金・クレジットが発生する。
  - ネオクラウドが受け取る側: オフテイカーの解約に対する違約金は、ネオクラウドの返済原資になる。
  - DCD の分析では、上流（DC 事業者）から回収できる額が下流（顧客）への支払いを下回るミスマッチがある★。
- **最大のイベントは CRWV の Q3 決算（11月中旬）である。** 次の項目が焦点になる★。
  - DDTL 5.5 のドロー状況
  - 2027年の満期への対応
  - RPO の推移
  - Microsoft/OpenAI 以外への顧客分散
  - 設備投資ガイダンス

### Gaps
- Chamath Palihapitiya の liquidated damages 発言の一次ソース（X 投稿、All-In ポッドキャスト）は検索で見つからなかった。
- Nebius、IREN、Applied Digital、TeraWulf、Nvidia の11月の決算日は未確認。
- CoreWeave の最新 RPO と顧客構成比は今回取得できなかった。
- 依頼文の「~80% GPU 担保」の出典も不明（StockTitan のデータでは38.4%）。

---

## Q5. Nvidia の役割：バックストップ、保証、購入義務、投資の開示場所と変化の追い方

### Takeaway
The Information が Nvidia の開示を分析したところ、7月期までに Nvidia はネオクラウドなどに$170B超を賭けている。内訳は、データセンターを支える保証・その他コミットメントが最大$164.5B、直接投資が$7B超である。

保証には次のようなものがある。

- テナントがリースを履行しない場合に家主へ支払う約束
- 計算資源の購入約束（例: CoreWeave の売れ残り容量を最大$6.3B 買い取る）

開示場所は10-Q の Commitments and Contingencies（購入義務、マルチイヤーのクラウドサービス契約、保証）の注記と MD&A の流動性の項である。次の10-Q（10月期）で総額の増減を追う。

### Cited Findings
- **総額と内訳**: 合計は$170B超。データセンター向けの保証・その他コミットメントが最大$164.5B、ネオクラウドへの直接投資（実行済み・合意済み）が$7B超、チップを購入する企業の株式保有が$99B。数字は7月四半期までの分で、The Information による Nvidia の開示の分析に基づく。 — [The Next Web 10/23](https://thenextweb.com/news/nvidia-170bn-neoclouds-firmus)
  - 合計を$171.5B（直接$7B＋保証・コミットメント$164.5B）とする報道もある。 — [AI Weekly](https://aiweekly.co/alerts/nvidias-1715b-neocloud-backstop-faces-first-real-market-test)
  - 「$99B の株式保有」は時価か簿価か不明で、要確認。
- **保証の中身**: リースのデフォルト時の家主への支払い約束と、計算資源の購入約束。 — 同上
- **CoreWeave**: 出資に加え、他の買い手が見つからない場合に最大$6.3B の計算資源を買い取るコミットメントがある（いわば最後の買い手）。 — [AI Weekly](https://aiweekly.co/alerts/nvidias-1715b-neocloud-backstop-faces-first-real-market-test)
- **数字の見方の違い**
  - ネオクラウド向けのオフバランスのクラウド契約（バックストップ）を$36B とする報道がある。 — [KuCoin News（二次情報）](https://www.kucoin.com/news/flash/nvidia-s-ai-financing-model-faces-pressure-as-neoclouds-struggle)
  - オハイオ州の10GW OpenAI データセンター向けの最大$105B の保証（チップ・土地・電力）は別建てとされている。 — 同上
  - $36B と$164.5B は定義が異なり、直接比較できない。
- **Jensen Huang の発言**: 業界の問題は顧客不足ではなく資本不足だと主張し、CoreWeave に Nvidia のバックストップは不要だと述べた。 — [AI Weekly](https://aiweekly.co/alerts/nvidias-1715b-neocloud-backstop-faces-first-real-market-test); [BigGo](https://finance.biggo.com/news/7484e05c-561d-43d5-8c9e-95537e5b5688)
  - BigGo の記事見出しは「資金調達コストは低下している」というものである。
- **保険の活用**: Nvidia は AI チップローンのバックストップに保険会社を使い、リスクを分散しようとしている。 — [BigGo](https://finance.biggo.com/news/a0ec2737-7685-48bd-937e-90761e9df9c6)
- **GPU 債務バックストップの仕組み**（資本、オフテイク、データセンターの「三位一体」）を SemiAnalysis が解説している。 — [SemiAnalysis](https://newsletter.semianalysis.com/p/nvidia-gpu-debt-backstop-unleashes)
- **Firmus への出資協議**: Nvidia は数億ドル規模の出資を協議中（The Information）。Nvidia はすでに Firmus の投資家である。 — [The Next Web](https://thenextweb.com/news/nvidia-170bn-neoclouds-firmus)
- **過去の開示**: FY2024 Q3 の10-Q には「その他の非在庫購入義務」$13.2B が計上され、うちマルチイヤーのクラウドサービス契約が$11.3B（FY2023 Q3 は$3.60B）。主に R&D と DGX Cloud 向けと説明されていた。 — [NVIDIA 10-Q（FY2024 Q3 Financial Report）](https://www.sec.gov/Archives/edgar/data/1045810/000104581024000316/Financial_Report.xlsx); [NVIDIA 10-Q FY2023](https://www.sec.gov/Archives/edgar/data/1045810/000104581023000227/nvda-20231029.htm)

#### 指標カタログ（Q5）

| 指標 | 入手先 | 頻度 | シグナル |
|---|---|---|---|
| 10-Q の Commitments and Contingencies 注記（購入義務、マルチイヤーのクラウドサービス契約、保証） | EDGAR（NVDA CIK 1045810） | 四半期（次回は FY2027 Q3、10月下旬に期末、11月下旬に発表★） | ★保証・コミットメント総額の QoQ 増加 = 需要の自前での下支えが拡大（ネオクラウドの自立性低下）。★ASC 460 の保証負債・引当金の計上、または損失の認識 = バックストップが実際に発動 |
| 投資の注記（非上場・上場の株式投資、公正価値の変動） | 10-Q | 四半期 | ★ネオクラウド株の評価損 |
| 特定企業の8-K（CRWV など）に記載された Nvidia との契約 | EDGAR 全文検索 "NVIDIA" + "capacity" | 随時 | ★新規のバックストップや容量の買取りの発動 |
| 報道（The Information、FT、Bloomberg）での新規バックストップ・出資（Firmus など） | ニュース | 随時 | ★救済的な出資の増加 = 市場による調達の不全 |
| Nvidia の CDS | 報道（LSEG） | 日次 | 約79bp（2026年7月、過去最高）。★100bp超 |

### Inferences
- **バックストップの拡大は二面的である。** 短期的にはネオクラウドの調達を支えるが、Nvidia の需要が「自己資金で回っている」（循環ファイナンス）ことの証拠にもなる。Gartner の「独立した事業運営の停止」予測は、Nvidia や大手顧客による吸収という形で実現する可能性がある★。
- **追うべきは総額そのものより変化と発動である。** 次の10-Q で保証総額が$164.5B からどう変わるか、また損失計上や容量の買取り実行の記載が出るかが、ネオクラウドの需要の実態を示す★。

### Gaps
- Nvidia の最新10-Q（7月四半期）の該当注記の原文は確認できなかった（The Information の分析経由のみ）。
- $36B／$164.5B／$105B の内訳の整合は未確認。
- Nvidia の次回決算日も未確認。

---

## Q6. 株式市場のシグナル：空売り、インプライドボラティリティ、ETF フロー、IPO パイプライン、ロックアップ、ディストレスイベント

### Takeaway
10月のネオクラウド株の急落（CRWV、NBIS、IREN はいずれも月初来-30%超）と並行して、次のような動きが出た。

- オプション: CRWV の ATM インプライドボラティリティが約97〜103%に達した。
- IPO 市場: Firmus が ASX への上場（IPO）を撤回し、Elice は上場初日に32%下落した。IPO 市場は事実上閉じつつある。
- 直接の「GPU 資産の投げ売り」: 確認できなかった。

### Cited Findings
- **株価**
  - CRWV、NBIS、IREN はいずれも10月に少なくとも30%下落した。 — [AI Weekly](https://aiweekly.co/alerts/nvidias-1715b-neocloud-backstop-faces-first-real-market-test)
  - 10/22の1日だけで CRWV が-10.1%、APLD が-9.0%、IREN が-8.4%、NBIS が-7.2%。 — [検索要約（24/7 Wall St. 系）](https://247wallst.com/investing/2026/10/21/terawulf-jumps-8-as-ceo-says-power-demand-remains-extremely-strong-applied-digital-surges-9-iren-climbs-6/)
  - 10/21の終値は IREN $28.07、WULF $12.94、APLD $21.23、CIFR $9.13。 — [Benzinga](https://www.benzinga.com/trading-ideas/movers/26/10/62509644/gene-munster-points-to-good-news-for-neoclouds-in-spacex-earnings-iren-terawulf-bounce)
  - CoreWeave の時価総額は$44B 消失した（見出し）。 — [Benzinga](https://www.benzinga.com/markets/bonds/26/10/62541064/coreweave-debt-stress-mounts-bond-yield-hits-record-as-stock-suffers-44-billion-wipeout)
  - CoreWeave の株価は6か月で50%下落した。 — [The Next Web](https://thenextweb.com/news/nvidia-170bn-neoclouds-firmus)
- **オプションのインプライドボラティリティ**: 10/21時点で、CRWV の ATM IV は10/23満期が約96.9%、11/13満期が約102.5%。この日の出来高は59.6万枚。 — [Market Chameleon](https://marketchameleon.com/Overview/CRWV/OptionChain/)
  - 8〜9月は IV 70〜80%台で、IV パーセンタイルは低かった。 — [iTiger（Option Witch）](https://www.itiger.com/news/1115583503)
- **空売り比率**: Fintel は浮動株の17.49%、5,460万株、Days to Cover 1.97 としているが、日付は不明。 — [Fintel](https://fintel.io/s/us/crwv)
- **IPO**
  - Firmus は10月上旬に ASX への上場（IPO）を撤回した。 — [DCD](https://datacenterdynamics.com/en/news/neocloud-firmus-cancels-ipo-blames-market-volatility); [Forbes Australia](https://www.forbes.com.au/news/investing/firmus-44-billion-ipo-flop/)
    - 当初は最大$5.5B を約$30B の評価で調達する計画だった（Bloomberg、TNW 経由）。 — [The Next Web](https://thenextweb.com/news/nvidia-170bn-neoclouds-firmus)
    - 別の報道では評価額は約A$44B、価格レンジは A$11 から A$9 に引き下げられた。 — [DCD](https://datacenterdynamics.com/en/news/neocloud-firmus-cancels-ipo-blames-market-volatility); [Cyber Daily](https://www.cyberdaily.au/digital-transformation/14280-the-rundown-firmus-and-its-failed-44bn-asx-ipo)
    - 規模や価格は情報源間で矛盾している。
    - 上場の根拠とされた容量の90%が未建設だったとの指摘がある。 — [Cyber Daily](https://www.cyberdaily.au/digital-transformation/14280-the-rundown-firmus-and-its-failed-44bn-asx-ipo)
    - 撤回後は$2〜3B のプライベートラウンドを模索している（Bloomberg）。 — [BGov](https://news.bgov.com/private-equity/firmus-is-said-to-explore-raising-3-billion-after-shelving-ipo)
  - Elice（韓国）は上場初日に-32%。 — [The Next Web](https://thenextweb.com/news/nvidia-170bn-neoclouds-firmus)

#### 指標カタログ（Q6）

| 指標 | 入手先 | 頻度 | 無料/有料 | 直近値 | シグナル |
|---|---|---|---|---|---|
| 空売り残高（CRWV、NBIS、IREN、CIFR、WULF、APLD） | FINRA/Nasdaq の月2回の空売り残高（無料）、S3 Partners、Ortex（有料、日次推計）、Fintel | 月2回（公式）／日次（推計） | 無料/有料 | CRWV は浮動株の17.49%（日付不明） | ★25%超、またはショートの借株コスト（borrow fee）の急騰 |
| ATM IV、プット・コールのスキュー | Market Chameleon、Barchart、CBOE（無料の表示あり） | 日次 | 無料/一部有料 | CRWV は約97〜103%（10/21） | ★120%超で定着、またはプットスキューの急勾配化。決算前の IV の膨張（11月中旬） |
| 株価と CDS の乖離（エクイティ・クレジットの整合） | 株価（無料）＋CDS（報道） | 日次 | — | 10/19以降、株は反発したが利回りは約15%のまま（CNBC 見出し） | ★株の反発に CDS が追随しない = 債券側の警戒が持続 |
| IPO・二次募集のパイプライン（撤回・延期・値下げ） | SEC EDGAR（S-1/F-1、RW＝取下げ）、ASX の公告、Renaissance Capital、IPOScoop | 随時 | 無料 | Firmus 撤回、Elice -32% | ★Lambda、Crusoe などの上場延期。★ATM（at-the-market）型の増資やディスカウントでの公募増資の増加 |
| ATM 型増資・転換社債と株式交換（希薄化） | 424B5、8-K | 随時 | 無料 | CIFR の株式交換4,070万株 | ★株価下落局面での希薄化型調達の急増 |
| ロックアップ解除 | S-1/424B4 のロックアップ条項、IPO 日からの計算 | 随時 | 無料 | 未取得（CRWV の IPO ロックアップは2025年中に満了済みと推定★） | 解除日前後の売り圧力 |
| ディストレスイベント（デフォルト、リストラ、GPU の売却、Chapter 11） | 8-K Item 2.04/1.03（破産）、PACER、Bloomberg/Reuters | 随時 | 無料/有料 | 確認されたネオクラウドのデフォルトなし（今回の調査範囲） | ★小規模ネオクラウドの Chapter 11、GPU のバルク売却報道、担保の実行 |
| テーマ型 ETF のフロー（AI インフラ／データセンター ETF） | ETF.com、各運用会社のサイト | 日次 | 無料 | 未取得 | ★連続流出 |

### Inferences
- **小規模ネオクラウドの倒産・統合が先行指標になる。** Gartner や Musk の見立て（200社超のネオクラウドが淘汰される）が正しければ、上場大手より先に、非上場の小規模ネオクラウドで倒産・統合・GPU のバルク売却が出るはずである。PACER や業界紙（DCD、The Information）の個別案件の監視が先行指標になる★。
- **GPU の投げ売りはまだ起きていない可能性が高い。** レンタル価格の上昇（Q2）と組み合わせると、10月時点では「株と社債の価格調整」は起きているが、「GPU 資産の投げ売り」には至っていないと推定される★。

### Gaps
- 10月時点の公式の空売り残高（FINRA）、S3 による推計、ETF フロー、ロックアップのカレンダーは取得できなかった。
- ネオクラウドの実際のデフォルト・Chapter 11 の事例は検索では見つからなかった（存在しないとは断定できない）。

---

## Q7. SpaceX 固有：$40B の GPU 債務、社債、格付け、リース条件

### Takeaway
SpaceX（SPCX）は「AI データセンター以外の売上」（Starlink、打ち上げ）と投資適格の格付けを根拠に、$40B の GPU 向け債務を調達した。10/25に Musk が「クローズした」と X に投稿した。

- 構造: SPV（Apollo 系の Atlas SP が管理）でオフバランス化。
- 利回り: 劣後部分が約8.3%、チップ担保部分が約7.75%（クローズ前の報道）。
- 条件の確定状況: 貸し手、最終利回り、スプレッドは未確定・未開示である。

リース面では、S-1 は Anthropic との契約を2029年5月までの月額契約としつつ、どちらの当事者も90日前の通知で解約できると記載している。顧客側の解約権が SpaceX の AI 部門の信用の鍵になる。

### Cited Findings
- **Musk の投稿（10/25、X）**
  - 「債務市場は、AI データセンターから独立した相当の売上を持たない企業に対して、資金へのアクセスをほぼ完全に閉ざした」と述べた。 — [Tesla North](https://teslanorth.com/2026/10/25/spacex-40b-gpu-debt-elon-musk/); [CoinDesk](https://www.coindesk.com/markets/2026/10/26/elon-musk-confirms-usd40-billion-spacex-debt-deal-for-ai-chips-warns-of-neocloud-shakeout); [CNBC 10/26](https://www.cnbc.com/2026/10/26/spacex-closes-40-billion-debt-deal-for-ai-chips-elon-musk-.html)
  - SpaceX は投資適格で、Starlink と打ち上げの売上があると強調した。 — 同上
  - 200社超のネオクラウドが淘汰・統合されると予想した。 — 同上
  - 調達した債務は主に繰上げ償還可能（callable）なもので、GPU は2027年Q1〜Q2に到着予定。 — 同上
- **Reuters の注記**: 「完了」の正確な意味と、投資家が価格に合意したかどうかは不明だとしている。 — [検索要約（Reuters 経由）](https://www.cnbc.com/2026/10/26/spacex-closes-40-billion-debt-deal-for-ai-chips-elon-musk-.html)
- **構造（Bloomberg）**
  - SPV でチップ購入を資金調達し、SpaceX のバランスシートから外して投資適格の格付けを守る。 — [Investing.com（Bloomberg）](https://www.investing.com/news/company-news/spacexs-40bn-ai-debt-deal-faces-hurdles-amid-credit-market-turmoil--bloomberg-4970497)
  - Apollo 系の Atlas SP が SPV を管理する予定。 — 同上
  - 私募債3トランシェで構成し、劣後部分は推定$25〜30B。 — 同上
  - 劣後部分の利回りは当初8%台半ばで協議されていたが、市場の悪化で価格の再交渉に入った。 — 同上
- **価格（Semafor、WebProNews 経由）**: 最下位トランシェが約8.3%、チップ担保部分が約7.75%。 — [WebProNews](https://www.webpronews.com/spacex-40-billion-gpu-debt-closed-musk-credit-markets)
  - Benzinga は「8%超で値決め」と報じた（見出し）。 — [Benzinga](https://www.benzinga.com/markets/tech/26/10/62568125/spacex-pays-up-40-billion-debt-deal-prices-above-8)
- **FT の初期報道（10/7頃）**: 銀行ローン約$10B と投資適格債約$30B の構成で、Apollo が主導し、Pimco も協議に参加していた。 — [BusinessWorld（FT 引用）](https://bworldonline.com/technology/2026/10/07/785188/spacex-seeks-40-billion-financing-led-by-apollo-to-buy-nvidia-chips-ft-reports/)
  - 依頼文の「Goldman/Apollo」のうち、Goldman の関与は今回の情報源では確認できなかった。
  - 依頼文の「$20〜25B の社債」も、報道の劣後$25〜30B と完全には一致しない。
- **SpaceX の CDS・社債**: 2026年7月、SpaceX の CDS は過去最高を付け、30年債のスプレッドは2%ポイント超になったと報じられた（LSEG、FT 引用）。 — [AI Weekly](https://aiweekly.co/alerts/oracle-nvidia-alphabet-spacex-cds-hit-records-on-ai-debt)
  - 格付け会社（Moody's、S&P、Fitch）による SpaceX の具体的な格付けは、今回確認できなかった。
- **Anthropic とのリース**
  - S-1 の記載: 顧客は2029年5月まで月額料金を支払い、2026年5月から容量を減額料金で立ち上げる。どちらの当事者も90日前の通知で解約できる。 — [Yahoo UK](https://uk.finance.yahoo.com/news/elon-musk-says-spacex-only-170549212.html); [TechCrunch 5/28](https://techcrunch.com/2026/05/28/how-long-is-anthropics-lease-with-spacex-opinions-vary/)
  - Musk の説明: 180日のリースで、その後は相互に90日で解約できる。S-1 の「3年契約」という表現と矛盾する。 — 同上
  - その後の報道: Anthropic は2029年までに最大$84.5B を約束しており、約80%が解約不能とされる（非公開の目論見書、Reuters 経由、二次情報）。 — [BigGo](https://finance.biggo.com/news/24d90a7f-d26d-413c-8685-bf4da9cb540d)
    - 90日の解約条項と矛盾し、要確認。
  - Anthropic は SpaceX に月$1.25B を支払っている（見出し）。 — [Yahoo Finance](https://finance.yahoo.com/sectors/technology/articles/why-anthropic-now-paying-biggest-171854528.html)
- **Google**: 6/5に、Colossus の計算容量に月$920M を支払う契約を結んだ。 — [Wikipedia（SpaceXAI／SpaceX IPO）](https://en.wikipedia.org/wiki/Initial_public_offering_of_SpaceX)
  - 「両契約とも2026/12/31以降は90日の解約条項」とする論評があるが、一次ソースは未確認。 — [Milk Road](https://milkroad.com/ideas/why-anthropic-and-google-are-renting-from-spacex/)
- **SpaceX の決算**: Gene Munster は SpaceX の決算に「ネオクラウドにとって良いニュース」があると指摘した。 — [Benzinga](https://www.benzinga.com/trading-ideas/movers/26/10/62509644/gene-munster-points-to-good-news-for-neoclouds-in-spacex-earnings-iren-terawulf-bounce)

#### 指標カタログ（Q7）

| 指標 | 入手先 | 頻度 | シグナル |
|---|---|---|---|
| $40B の最終条件（トランシェ別の利回り・スプレッド、貸し手、コベナンツ、SPV の名称） | SpaceX の8-K（Item 1.01/2.03。SPV がオフバランスでも、保証や契約があれば開示の可能性★）、Bloomberg/FT/Semafor | 随時 | ★劣後トランシェが9%超で確定、または規模の縮小 = IG 発行体でも AI 向けは高コスト |
| SPCX 社債の TRACE 価格・30年債スプレッド | [FINRA TRACE](https://finra-markets.morningstar.com) | 取引ごと | 30年債スプレッドは2pt 超（7月）。★さらなるワイド化 |
| SpaceX の CDS | 報道（LSEG/Bloomberg） | 日次 | 7月に過去最高。★10月の水準は要確認 |
| 格付けアクション（Moody's、S&P、Fitch） | 各社サイト（要登録・無料閲覧可の部分あり） | 随時 | ★見通しをネガティブへ、または SPV の連結判断 |
| 顧客リースの解約権の行使、契約変更（Anthropic、Google） | SpaceX の10-Q/8-K（Item 1.02）、Anthropic 側の開示（同社 IPO 関連の資料がある場合） | 随時 | ★90日解約通知の行使 = SPV のキャッシュフローの毀損 |
| GPU 到着のスケジュール（2027年Q1〜Q2） | 決算説明会 | 四半期 | ★遅延 = callable 債の早期償還や資金の滞留 |

### Inferences
- **SpaceX の調達成功は、10月の調達環境を評価するベンチマークになる。** 「IG・非 AI の売上あり」でも約7.75〜8.3%（SPV の劣後部分）が必要だった。B+ の CoreWeave の新規無担保債が15%前後の利回りを要求される状況とあわせると、AI インフラ向けの資本コストは発行体の非 AI キャッシュフローの有無で二極化していると考えられる★。
- **リースの解約権がネオクラウド全体の構造リスクを象徴している。** S-1 の90日相互解約条項は、ネオクラウド全般のオフテイク契約の解約権・違約金の構造リスクを象徴する。顧客側（Anthropic、Google）が容量を他社へ移す場合、SpaceX の SPV 債権者が最初に影響を受ける★。

### Gaps
- $40B の最終的な貸し手、トランシェ別の確定利回り、SPV の正式名称は確認できなかった（Musk の投稿のみで、SpaceX の公式書類は未確認）。Goldman の関与も同様。
- SpaceX の格付け（具体的なノッチ）、SPCX 社債の銘柄と10月の価格、10月の SpaceX の CDS 水準は見つからなかった。
- Anthropic 契約の解約条件について、S-1（90日）と「約80%解約不能」報道の矛盾は解消できなかった。
