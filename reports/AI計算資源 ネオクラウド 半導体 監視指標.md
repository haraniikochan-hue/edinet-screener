# 信用が先に割れ、GPU賃料はまだ上がる

2026年10月26日時点のデータでは、AI計算資源市場は二層に割れている。価格と物理の層は逼迫し、信用と株式の層はストレス下にある。H100の取引ベース賃料（Ornn OCPI）は**$3.03/GPU時**、B200は**$9.70**で、B200は1か月に**+20.6%**上がった ([Ornn](https://data.ornn.com/))。OpenRouterの週間トークン量は前年比**約34倍**になり ([Global Advisors](https://globaladvisors.biz/2026/10/17/fast-fact-closed-weight-ai-usage-on-openrouter-rose-13-fold-as-its-share-of-tokens-fell/))、TSMC、SEAJ、韓国輸出も過去最高圏にある。一方でCoreWeaveの5年CDSは日中に**1,195bp**まで上がり、2031年債の利回りは**約15.8%**、ネオクラウド株は10月だけで30%超下げた ([Motley Fool](https://www.fool.com/investing/2026/10/16/why-is-coreweave-stock-falling-today/); [Benzinga](https://www.benzinga.com/markets/bonds/26/10/62541064/coreweave-debt-stress-mounts-bond-yield-hits-record-as-stock-suffers-44-billion-wipeout))。「供給過剰が来る」という見方を検証する5段階のシーケンスを置くと、点灯しているのは第1段階の「ネオクラウドの信用ストレス」だけで、旧世代GPUの賃料も中古価格もまだ崩れていない。Muskの言う「ストランデッド計算資源」は実在する。AWSは電力不足で約$5BのGB300ラックを倉庫に置いている。ただしこれは需要不足ではなく電力不足の症状である。短期的には賃料を支え、電力がつながる2027年に遅れて供給の波として現れる。したがって監視の要点はスポット賃料の水準ではない。見るべきは、薄い「浮動株」に流れ込む供給（出品数、スポット/オンデマンド比、指数間の乖離、先物カーブ）、CoreWeave債とGPU担保ローンの条件、顧客契約の解約権の行使、そしてチップ出荷と通電MWの乖離である。これまでの議論の数字のうち次の二つは訂正が必要で、AnthropicのColossus契約の解約条件はノート上でも未解決である。「CoreWeave債務の約80%がGPU担保」は、10-Qでは**38.4%**（サプライヤーファイナンスを足しても約53%）である。「Nvidiaのネオクラウド・エクスポージャー$170B」は、OpenAI向けのSB Energy保証（最大$105B）を含む、データセンター関連の保証と投資の合計である。

## 5段階の崩壊シーケンスのうち、点灯したのは「信用」の1段だけ

半導体株が下がりGPU賃料が上がる「ねじれ」は矛盾ではない。両者は別のものを測っている。SOXは10月22日に**-6.72%（10,731.98）**と6月以来最悪の下げを記録し、8営業日で**-16%**と2008年10月以来の最長の連続安になった ([Stocktwits](https://stocktwits.com/news-articles/markets/equity/soxx-soxl-smh-plunge-as-chip-stocks-sell-off-amid-supply-chain-concerns/cZxUCbMRBDF); [Crypto Briefing](https://cryptobriefing.com/us-chip-stocks-longest-losing-streak-2008/))。引き金は四つ重なった。

- **金利**: 米9月CPIの上振れで、10月FOMCでの利上げ確率が22%から37%に跳ねた ([Kitco/Reuters](https://www.kitco.com/news/off-the-wire/2026-10-15/us-chip-stocks-set-wipe-out-2-trillion-after-latest-selloff))。
- **AI債務への不安**: CoreWeaveのCDSが1,000bpを超えた。
- **メモリ**: CXMTの新製品と「2029年供給過剰」説で、SK hynixが5営業日で約26%下げた ([KuCoin News](https://www.kucoin.com/news/flash/memory-chip-stocks-drop-amid-china-competition-and-2029-oversupply-fears))。
- **装置**: Lamが供給制約を理由にガイダンスを抑えた ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/lam-research-sinks-9-supply-144450114.html))。

9月FOMCで25bpの利上げ（3.75〜4.00%）があったとの報道もある ([Asia Economy](https://view.asiae.co.kr/en/article/2026100804564226796))。事実なら変動金利のGPU担保ローンに直接効くが、一次資料では未確認である。

一次データは逆の姿を示す。TSMCの9月売上は前年比**+54.6%**で、同社は「需要は供給を上回り、減速は見えない」と述べた ([TSMC](https://pr.tsmc.com/english/news/3343); [Motley Fool](https://www.fool.com/earnings/call-transcripts/2026/10/15/tsmc-tsm-q3-2026-earnings-call-transcript/))。SEAJの9月の日本製装置販売額は**+48.2%**、韓国の10月1〜20日の半導体輸出は**+222.5%**だった ([SEAJ](https://www.seaj.or.jp/statistics/8797579155633.pdf); [Korea Times](https://www.koreatimes.co.kr/economy/20261021/exports-double-in-1st-20-days-of-october-on-robust-chip-shipments))。スポット賃料が映すのは「今日の限界的な希少性」である。半導体株は「明日の買い手が資金を調達できるか」と「価格上昇率の鈍化（二階微分）」を織り込んでいる。株式市場は、データにまだ現れていない2027年のエアポケットを先回りして織り込んでいる。データで確認されるまでは「バリュエーション調整」、一次データが鈍り始めたら「サイクル反転」と区別するのが実務的である。

「スポット市場は浮動株が薄い」という仮説はデータが裏付ける。CoreWeaveの売上の**約98%**は顧客コミットメントに基づき、RPOは**$103.7B**ある ([CoreWeave 10-Q](https://www.sec.gov/Archives/edgar/data/0001769628/000176962826000366/crwv-20260630.htm))。SemiAnalysisも、GPU賃貸の取引量の大半はオンデマンドではなく契約市場で成立すると指摘している ([SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity))。10月26日朝の時点で、Vast.aiに貸出可能と表示されていたH100 SXMは**わずか36基**、B200は56基だった ([Vast.ai](https://vast.ai/pricing))。B200の価格は指数によって大きく違う。Silicon Dataが$6.60、取引ベースのOrnnが$9.70、Vastの中央値が$10.13で、後の二つは45〜55%上に乖離している。H100では両指数の差は5%程度にとどまるため、浮動株が最も薄いのは最新世代（H200/B200）だと読める。

浮動株の薄さは両方向に効く。2024年8月には、H100の短期賃料が$8超から$1〜2へ崩れた前例がある ([AM Compute](https://www.amcompute.com/gpu-risk/defaults))。スポットの上昇は総需要の強さを証明しない。逆に、ラボやネオクラウドがわずかな余剰を放出するだけでもスポットは急落しうる。そしてスポットが崩れれば、GPUの担保価値と借換え条件が同時に悪化する。だから見るべきはスポットの水準ではなく、浮動株への「流入」である。

供給過剰の仮説を時系列で検証するには、次の5段階を順に確認するのが最も識別力が高い。

1. ネオクラウドの信用ストレス
2. 旧世代（A100/H100）の賃料と中古GPU価格の下落
3. スポットが1年契約を下回る（先物カーブが急なバックワーデーションになる）
4. オープンモデルのトークン単価が全ホストで底値に収斂する
5. 初のGPU担保ローンの差押え・強制売却

10月26日時点で点灯しているのは1だけである。OrnnのA100は1か月で**+6.9%**、getdeployingではV100が週次で**+36%**と、旧世代まで上がっている ([Ornn](https://data.ornn.com/); [getdeploying](https://getdeploying.com/gpu-price-trends))。以下では会話で出た仮説をH1〜H5と呼び、各指標表の「仮説」列で対応を示す。

| 記号 | 仮説 | 中核の検証指標 | 2026/10/26時点の読み | 判定 |
|---|---|---|---|---|
| H1 | スポット賃料は総需要を映さない「浮動株」 | 契約売上比率、出品数、指数間乖離、スポット/期間スプレッド | 契約比率98%、H100 SXMの出品は36基、B200は指数間で45〜55%乖離 | 支持 |
| H2 | フロンティアの停滞→オープンモデルへ需要移行→ラボがGPUを放出 | Epoch ECI、METR、AA指数の差、OpenRouterのシェア、ラボのコミットメントと解約権行使 | ECI首位は1か月で166→169。オープンは72%（OpenRouter）だが、GPU放出の証拠はない | 停滞は不支持、移行は部分支持 |
| H3 | ネオクラウドの信用収縮→GPU担保の強制売却 | CDS、債券、新規ローンのスプレッド、差押え記録、中古価格 | CDS 1,000bp超、利回り15%台。差押え・競売の公開記録はなく、賃料は上昇中 | 第1段階のみ |
| H4 | 物理的なストランデッド計算資源（2027年） | 通電MWとチップ出荷の乖離、ERCOT、許認可、倉庫保管 | AWSが$5B分を保管、Microsoft–Nscaleが撤退、テキサスが許可を停止 | 供給側で進行中 |
| H5 | SpaceX固有のリスクとMuskのポジショントーク | $40Bの確定条件、90日解約権、Colossus 2の通電、CDS | 「完了」の中身が不明確、解約条件の情報が矛盾 | 未解決 |

## 最優先で確認すべき10指標

以下は、上の5段階シーケンスを最も早く、安く検知できる順に並べたものである。警戒ラインは、特記がない限り調査担当者の判断であり、提供元の公式基準ではない。

| 優先 | 指標 | 入手先 | 頻度・費用 | 直近値（日付） | 警戒ライン（筆者判断） | 仮説 |
|---|---|---|---|---|---|---|
| 1 | GPU賃料指数（Ornn OCPI と Silicon Data）とその乖離 | [Ornn](https://data.ornn.com/)、[Silicon Data H100](https://www.silicondata.com/products/silicon-index/h100) | 日次。Ornnは最新値と3か月分が無料、Silicon Dataはポータル有料 | H100 $3.03/$2.89、B200 $9.70/$6.60（10/25） | H100/H200/B200の1か月変化率が同時にマイナス。H100が$2.35、次に$2.00を割る。Ornnと Silicon Dataの差が上から縮む | H1・H3 |
| 2 | 期間構造（12か月フォワードとスポットの差） | [Silicon Data 期間カーブ](https://www.silicondata.com/blog/b200-rental-price-august-2026-update)、CME配信（取引不可）、CME GPU1/GPU2先物（上場後） | 営業日ごと・有料 | B200の12か月フォワードはスポット比-12%（9/7） | 割安幅が15〜20%を超える | H1 |
| 3 | 浮動株への流入（Vast.aiの出品数、スポット/オンデマンド比） | [Vast.ai](https://vast.ai/pricing) 公開API、[getdeploying](https://getdeploying.com/gpu-price-trends) | リアルタイム／週次・無料 | H100 SXM 36基・B200 56基（10/26）、スポットはオンデマンドの約53%（10/19週） | 出品GPU数が数倍に増え、中央値が下がる。スポット/オンデマンド比が40%を割る | H1・H2 |
| 4 | CoreWeaveの5年CDSと2031/2032年債 | CDSは報道経由（Bloomberg等は有料）、債券は[FINRA TRACE](https://finra-markets.morningstar.com)（無料） | 日次／約定ごと | 1,195bp（10/15日中）→約1,115bp（10/23頃）、2031年債15.76% | 1,500bp超、または債券価格が70セント割れ。回復は700bp未満・90セント超 | H3 |
| 5 | GPU担保ローンの新規条件と破綻トリガー（8-K Item 1.02/2.04/2.06、差押え記録） | [EDGAR全文検索](https://www.sec.gov/edgar/search/)、[AM Compute](https://www.amcompute.com/gpu-risk/defaults) | 案件ごと・無料 | CoreWeave DDTL 5.5はSOFR+5.50%（8月）。GPU担保の差押え記録はない（10/17） | SOFR+6%超、テナーの364日化、新規案件ゼロが4〜6週間。初の差押え・競売 | H3 |
| 6 | Nvidia 10-Q（在庫、売掛金/DSO、供給コミットメント、クラウド契約、保証） | [Nvidia 10-Q](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000075/nvda-20260726.htm) | 四半期・無料 | 在庫$31.6B、売掛金$63.1B、DSO約60日、供給コミットメント$279B（7/26） | DSOが60日超へ上昇。クラウド容量の買取コミットメントや評価損が増える | H3・H4・半導体 |
| 7 | ハイパースケーラーの受注残の増加額、2027年capexガイド、「容量制約」発言 | 各社IR・8-K | 四半期 | MSFT +$51B、GOOGL +$50B超（2Q） | 増加額が2四半期連続で半減。2027年capexが横ばい。「容量制約」の発言が消える | H2 |
| 8 | OpenRouterの週間トークン量と、オープンモデルの最安ホスト価格 | [OpenRouter rankings](https://openrouter.ai/rankings)、[endpoints API](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash/endpoints) | 週次／随時・無料 | 167.65T/週（10/5週）。DeepSeek V4.1 Flashの出力価格は$0.18〜2.40/M | GPU供給が到着する中で月次の伸びが10〜15%未満に鈍る。全ホストの価格が底値に収斂 | H2・H1 |
| 9 | 通電ギャップ（衛星推計の通電MW vs 台湾ODMの月次売上、ERCOTの「承認済み未稼働」） | [Epoch AI](https://epoch.ai/data/ai-data-centers/directory/colossus-2)、MOPS、[Corley Energy](https://www.corleyenergy.com/ercot-large-load-queue.html) | 月次・無料 | Colossus 2は946MW（予測1,531MW）、Foxconn 9月+38% | ODM売上が伸び続けるのに通電MWが横ばい | H4・H5 |
| 10 | 日本の半導体データ（SEAJ月次、アドバンテスト/東京エレクトロンの受注、TSMC月次、韓国の1〜20日輸出） | [SEAJ](https://www.seaj.or.jp/statistics/)、[TSMC](https://pr.tsmc.com/english/news/3343)、各社TDnet | 月次／四半期・無料 | SEAJ 6,290億円（9月、+48.2%） | SEAJの3か月移動平均が2〜3か月連続で前月比マイナス。受注が前四半期比で減少 | 半導体 |

順位の考え方は三つある。1〜3は無料・高頻度で、シーケンスの2〜3段目、つまり旧世代の賃料下落とスポットの期間割れを最初に捉えられる。4〜5は第1段階の深まりと第5段階（強制売却）の発生を捉える。6〜10は需要側、物理側、日本株への波及を確認する、四半期・月次の裏付けである。

## スポット賃料は「浮動株」であり、見るべきは水準より流入量

GPU賃料の公開ベンチマークは少なくとも5つあり、方法論が違うため水準は一致しない。各指数は自分自身の時系列でのみ比較すべきである。

**Ornn OCPI**は、取引された賃料を出来高で加重し、外れ値を処理（winsorize）した平均で、毎営業日の米東部時間16時に確定する。10月25日の値は、H100 SXMが**$3.03**（1か月+6.3%）、H200が**$6.30**（同**+24.0%**）、B200が**$9.70**（同+20.6%）、A100が$1.09だった ([Ornn](https://data.ornn.com/))。

**Silicon Data**の指数は、仕様・契約条件・地域を標準化した観測値で、ネオクラウドの95%をカバーし、BloombergとRefinitivにも配信されている。10月25日の値は、SDH100RTが**$2.89**（7日間+6.2%）、SDB200RTが**$6.60**（同+12.4%）だった ([Silicon Data H100](https://www.silicondata.com/products/silicon-index/h100); [Silicon Data B200](https://www.silicondata.com/products/silicon-index/b200))。同じページのFAQには$2.53と$5.45という古い値が残っているので、日付を必ず確認する必要がある。H100は$2.75（7/27）から$2.63（9/7）へいったん下げ、10月に再加速した ([Silicon Data blog](https://www.silicondata.com/blog/b200-rental-price-august-2026-update))。2025年12月9日の$2.00から+44%という数字は二次情報である ([FourWeekMBA](https://fourweekmba.com/ai-nvidia-h100-rent-hits-2-88-an-hour-up-44-since-december/))。

**SemiAnalysis**の1年契約指数は、H100で**$1.70（2025年10月）から$2.35（2026年3月）**へ約40%上がった。ただし公開ダッシュボードは2026年4月から更新されていない ([SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity); [gpu-index](https://gpu-index.semianalysis.com/))。この$2.35と2025年12月の$2.00が、下落局面での節目になる。

期間構造は、浮動株仮説を最もきれいに検証できる指標である。Silicon DataのB200は9月7日時点でスポット$5.69に対し、12か月の暗示フォワードが**$5.03（-12%）**のバックワーデーションだった ([Silicon Data blog](https://www.silicondata.com/blog/b200-rental-price-august-2026-update))。10月中旬もH100・B200ともバックワーデーションと報じられている ([CryptoBriefing](https://cryptobriefing.com/cme-group-gpu-rental-forward-curve-pricing/))。バックワーデーションとは、市場が「今は希少だが、供給が届けば下がる」と見ている状態であり、薄い浮動株と整合する。一方、Silicon DataのCEOは「コンタンゴに転じた」と語ったとされ、これは公表カーブと矛盾していて未解決である ([FourWeekMBA](https://fourweekmba.com/ai-nvidia-gpu-rents-are-now-priced-to-rise-for-36-months/))。

getdeployingのデータでは、オンデマンド価格に対する予約割引は1年で**-28%**、3年で**-49%**、スポットはオンデマンドの約53%だった ([getdeploying](https://getdeploying.com/gpu-price-trends))。

CMEのH100/B200先物（GPU1/GPU2、各730GPU時間、現金決済）は10月5日の上場予定が延期された ([PRNewswire/CME](https://www.prnewswire.com/news-releases/cme-group-and-silicon-data-to-launch-compute-futures-on-october-5-to-unlock-new-way-to-hedge-ai-risks-302848593.html))。11月9日に初取引という情報は単一の情報源によるもので、規制当局の審査待ちである ([RuntimeWire](https://runtimewire.com/article/silicon-data-cme-compute-futures-november-2026))。上場すれば、カーブの形と建玉（売りヘッジの偏り）が最も公開性の高いゲージになる。

供給側で浮動株を最も脅かすのは、ネオクラウドの設置容量の急増である。Nvidiaは、ネオクラウドの設置容量が2025年末の約**3GW**から2026年末に**8GW**へ増えると述べた。同時に、施設容量の一部にテイク・オア・ペイの最低収入保証を付ける収益分配スキームも導入した ([Nvidia決算説明会](https://s201.q4cdn.com/141608511/files/content_files/TRANSCRIPT_-NVIDIA-Corp-NVDA-US-Q2-2027-Earnings-Call-26-August-2026-5_00-PM-ET.pdf))。サプライヤーが需要を下支えする構造は、サイクル後期の警告サインとして読むべきである。

稼働率については、全体の稼働状況を示す公開統計がない。Cast AIの「GPU稼働率5%」はクラスタ内の計算利用率であり、レンタルの稼働（貸出済みかどうか）とは別の概念なので混同しないこと ([Cast AI](https://cast.ai/press-release/2026-state-of-kubernetes-optimization-report/))。

| 指標 | 何を測るか | 入手先 | 頻度・費用 | 直近値（日付） | 逼迫・健全 | 過剰・ストレス | 仮説 |
|---|---|---|---|---|---|---|---|
| Ornn OCPI | 取引ベースの出来高加重GPU時間単価 | [data.ornn.com](https://data.ornn.com/) | 日次（16時ET確定）。最新値と3か月分は無料、全履歴とフォワードは有料 | H100 $3.03、H200 $6.30、B200 $9.70、A100 $1.09（10/25） | 1か月変化率がプラスで、旧世代も上昇 | 全世代の1か月変化率が同時にマイナス、B200/H100比が1.8倍未満 | H1・H3 |
| Silicon Data Silicon Index | 標準化した観測ベースの賃料 | [silicondata.com](https://www.silicondata.com/)、[料金](https://www.silicondata.com/pricing) | 日次・有料（7日間の試用あり）、Bloomberg/Refinitivに配信 | H100 $2.89、B200 $6.60（10/25） | 高値更新 | Ornnとの乖離が上から縮小 | H1 |
| SemiAnalysis 1年契約指数 | H100 1年契約価格（100社超への月次調査） | [SemiAnalysis](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity) | 月次・機関向け有料 | $2.35（2026年3月） | $2.35超を維持 | $2.35割れ、次に$2.00割れ | H1 |
| getdeploying | オンデマンド中央値、予約割引、スポット比、上昇モデル数 | [getdeploying](https://getdeploying.com/gpu-price-trends) | 週次・無料（日次・社別はAPI） | H100 $3.71（4週+9%、前年比+21%）（10/19週） | 過半のモデルが週次で上昇、スポット/オンデマンド比60%超 | 4週連続で過半が下落、比率40%未満、ハイパースケーラーとの価格差が拡大 | H1 |
| Vast.ai 出品API | 実際に借りられるGPU（浮動株そのもの） | [Vast.ai](https://vast.ai/pricing) | リアルタイム・無料 | H100 SXM 36基・中央値$3.75、B200 56基・中央値$10.13（10/26） | 出品が数十基にとどまる | 出品数が数倍に増え、中央値が下落 | H1・H2 |
| フォワード/期間カーブ | 3/6/12/36か月の期間価格 | [Silicon Data](https://www.silicondata.com/blog/the-gpu-forward-curve-pricing-the-curve-not-just-the-spot)、CME市場データ（10/15から配信） | 営業日ごと・有料 | B200 12か月フォワード-12%（9/7） | フラット〜コンタンゴ | 割安幅15〜20%超 | H1 |
| CME・ICE先物、Kalshi | 取引可能な賃料ヘッジ | [CME](https://www.cmegroup.com/media-room/press-releases/2026/5/12/cme_group_and_silicondatapartnertolaunchfirstcomputefutures.html)、[ICE](https://ir.theice.com/press/news-details/2026/ICE-and-Ornn-to-Launch-GPU-Compute-Futures-Contracts/default.aspx)、[Kalshi](https://kalshi.com/markets/kxh100mon/h100-monthly-price/kxh100mon-26mar31) | 上場後は日次。Kalshiは既存だが流動性が薄い | CMEは審査待ち（11/9説は単一情報源）、ICEは時期未定 | 先物がスポット以上 | 期先が急に割安、建玉が売りヘッジに偏る | H1・H3 |
| 中国のGPU賃料 | 中国国内のH100/A100賃料 | [SMM](https://news.metal.com/newscontent/104149446-smm-computing-power-daily-a100-monthly-rental-prices-catch-up-on-october-9-with-short-term-rental-premiums) | 日次・一部無料 | 北西部のH100 1年契約は87,000元/台（8月比約+15%）（10/9〜10） | 長期契約価格が上限を突破 | 低価格在庫が再び現れる | H1 |
| ネオクラウドの契約構成・更新単価 | 契約比率、RPOの期間、更新レート | [CoreWeave 10-Q](https://www.sec.gov/Archives/edgar/data/0001769628/000176962826000366/crwv-20260630.htm)、決算説明会 | 四半期・無料 | 契約比率98%、RPO $103.7B（41%が24か月以内）、顧客Aが売上の36%（6/30） | 更新単価が上昇、前払いが増加 | 更新単価の下落、契約期間の短縮 | H1・H3 |
| Nvidiaの稼働・供給に関する発言 | 「フル稼働」「供給制約」の文言 | [Nvidia決算説明会](https://s201.q4cdn.com/141608511/files/content_files/TRANSCRIPT_-NVIDIA-Corp-NVDA-US-Q2-2027-Earnings-Call-26-August-2026-5_00-PM-ET.pdf) | 四半期・無料 | 「全クラウドでフル稼働」、供給制約はFY2028末まで（8/26） | 文言を維持 | 文言が消える、リードタイムが在庫即納に縮む | H1・H4 |

## ネオクラウド信用はディストレス水準だが、満期の壁は2030年以降にある

### 市場の値付け

CNBCは、CDSが1,000bpを超えた状態を「ディストレス」と呼んでいる。CoreWeaveの5年CDSは10月15日に日中**1,195bp**の最高値を付けた後、**約1,082bp**（10/19）に下がった ([Motley Fool](https://www.fool.com/investing/2026/10/16/why-is-coreweave-stock-falling-today/); [CNBC](https://www.cnbc.com/2026/10/19/coreweave-oracle-ai-credit-stress.html))。そこから逆算した5年デフォルト確率は約60%である ([CNBC Investing Club](https://www.cnbc.com/investingclub/2026/10/16/coreweave-credit-default-swaps.html))。CDSの水準は出典によって1,038〜1,195bpの幅があるので、日付と出典を必ずセットで見る必要がある。債券では、9.75%の2031年債が過去最高の約**15.76%**の利回りを付け、一部の銘柄は**78〜79セント**まで下げた ([Benzinga](https://www.benzinga.com/markets/bonds/26/10/62541064/coreweave-debt-stress-mounts-bond-yield-hits-record-as-stock-suffers-44-billion-wipeout); [Morningstar](https://www.morningstar.com/bonds/coreweave-data-center-bonds-slide-capex-debt-overhang-concerns))。

### CoreWeaveの債務構造（10-Q、6/30時点）

元本は**$35.6B**で、内訳は次のとおりである ([StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due); [CoreWeave 10-Q](https://www.sec.gov/Archives/edgar/data/0001769628/000176962826000366/crwv-20260630.htm))。

- GPU担保のプロジェクトローン（DDTLを含む）: $13.6B（**38.4%**）
- 無担保シニア債: $10.0B（28.2%）
- 転換社債: $6.6B（18.5%）
- サプライヤーファイナンス: $5.1B（14.4%）

無担保債の満期はすべて2030〜2032年にある。2027年末までに来る$10.6Bの大半は、顧客契約からの入金に連動して返済されていくGPU担保ローンである。したがって真の破綻経路は2027年の借換えの壁ではない。顧客契約の解約・減額（8-K Item 1.02）によって返済原資が消えることである。

流動性は次のように整理できる。流動負債に分類された債務$7.5Bは現金$5.5Bの約1.4倍だが、未使用枠を含む流動性$15.6Bと比べれば約2.1倍のカバーがある【計算】。調査ノートには「流動債務は現金の0.74倍」という逆向きの記述があったので注意してほしい。Q2の利払いは$558Mで売上の21.7%にあたり、金利が1ポイント動くと四半期で約$30Mの影響がある。

### ローン市場は閉鎖ではなく、選別と値上げ

Muskの「債務市場はほぼ完全に閉じた」という主張は、10月の実際の案件と完全には一致しない。

| 案件 | 条件 |
|---|---|
| CoreWeave 非遡及ローン（3月） | SOFR+2.25% |
| CoreWeave DDTL 5.5（8月） | SOFR+5.50%。ドロー期限は2026年12月 |
| Nebius 364日ブリッジ $3.5B（Citi、10/17締結） | SOFR+2.75%で始まり90日ごとに+25bp。満期は2027/10/16 |
| Lambda 担保付ファシリティ $1.008B（10/1） | 6.78%固定 |
| Cipher $850M | ゼロクーポン転換社債＋既存債と4,070万株の交換。株価は2日で約18%下落 |

出典: [Nebius 6-K](https://www.sec.gov/Archives/edgar/data/0001513845/000110465926117978/tm2628078d1_6k.htm); [kingy.ai](https://kingy.ai/blog/neocloud-funding-ai-bubble/); [24/7 Wall St](https://247wallst.com/investing/2026/10/13/cipher-digital-tumbles-14-on-850m-convertible-note-offering-and-share-exchange-applied-digital-drops-5/)

SpaceXの約7.75〜8.3%とCoreWeaveの15%前後を並べると、AIインフラの資本コストは、発行体にAI以外のキャッシュフローがあるかどうかで二極化している。

### 強制売却はまだ起きていない

AM Computeのトラッカー（10月17日更新）には、GPU担保ローンが差し押さえられ、GPUが競売にかけられた公開記録はない。10月12日のCharacter.AIの破産申請（Chapter 11）は計算資源の買い手側の事例である ([AM Compute](https://www.amcompute.com/gpu-risk/defaults))。

中古GPUの価格には、取引に基づく権威ある指数が存在しない。H100の中古推計はブローカーごとに$6K〜$35Kとばらばらで、ServerBuybackの指数は$15〜28K（6月）である ([ServerBuyback](https://serverbuyback.com/resources/gpu-resale-value-index/); [IntuitionLabs](https://intuitionlabs.ai/articles/data-center-gpu-pricing-2026))。賃料が上がっている間は担保価値も維持されるが、担保価値はスポットに連動して動く。

減価償却は、CoreWeaveが6年で減損ゼロ、Nebiusが約4年（2025年の情報）である ([Bizety](https://bizety.com/2025/09/23/gpu-depreciation-coreweave-vs-nebius/))。耐用年数の短縮や減損（8-K Item 2.06）が出れば、担保価値の下方修正を意味する。

### 広域クレジットは平穏で、ストレスは局所的

US HY OAS（ハイイールド債全体のスプレッド）は**3.40%**（10/22）で、52週レンジ2.60〜3.46%の上端に近いものの崩れてはいない ([FRED](https://fred.stlouisfed.org/series/BAMLH0A0HYM2); [Macrotrends](https://www.macrotrends.net/3006/high-yield-spread))。一方、データセンターABSは一般のABSと逆行して横ばい〜拡大しており、ハイパースケーラーABSは5年国債+150bp（前年比+16bp）だった ([The Real Deal/Barclays](https://therealdeal.com/new-york/2026/09/30/data-center-securities-flash-ai-concerns/))。

### ベンダーの下支えと業界再編の見通し

Nvidiaによる下支えは、短期的にはネオクラウドの調達を支える一方で、需要が自己資金で回っている証拠でもある。たとえばCoreWeaveに対しては、売れ残った容量を最大$6.3B買い取る約束がある ([AI Weekly](https://aiweekly.co/alerts/nvidias-1715b-neocloud-backstop-faces-first-real-market-test))。

Gartnerの予測は「2030年までにネオクラウドの80%超が独立運営をやめる」というもので、買収・統合を含み、倒産率ではない ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2026-10-14-gartner-says-over-us-dollars-three-and-a-half-trillion-of-artificial-intelligence-infrastructure-spending-could-be-exposed-to-impairment-by-the-end-of-2030))。

Muskの「200社超の淘汰」が正しいなら、兆候は上場大手より先に非上場の小規模ネオクラウドに出る。すでに次のような事例がある ([DCD](https://datacenterdynamics.com/en/news/neocloud-firmus-cancels-ipo-blames-market-volatility); [Data Center Knowledge](https://www.datacenterknowledge.com/build-design/microsoft-exits-nscale-data-center-deal-over-uk-power-delays))。

- FirmusがASXへの上場を撤回した。
- Nscaleの上場申請書では、契約総額$103.4Bに対し稼働中の契約は$2.6Bにとどまる。

### 指標一覧（市場）

| 指標 | 何を測るか | 入手先 | 頻度・費用 | 直近値（日付） | 健全 | ストレス | 仮説 |
|---|---|---|---|---|---|---|---|
| CoreWeave 5年CDS | デフォルトリスク | Bloomberg/LSEG/S&P（有料）、CNBC等の報道（無料） | 日次 | 1,195bp（10/15日中）→約1,082bp（10/19）→約1,115bp（10/23頃） | 700bp未満で定着 | 1,500bp超、アップフロント建てへの移行 | H3 |
| CoreWeave無担保債（2030/31/32年） | 債権者の回収期待 | [FINRA TRACE](https://finra-markets.morningstar.com) | 約定ごと・無料 | 2031年債15.76%、2032年債約14.9%（10/19）、一部は78〜79セント | 90セント超 | 70セント割れ、年限間の価格が回収率に収斂 | H3 |
| NBIS/IREN/CIFRの転換社債の新発条件 | 株式経由の調達余力 | 8-K/6-K、TRACE | 発行時・無料 | NBIS 4.50%・2034年・125%償還（8月）、CIFRは株式交換（10月） | 条件が改善 | クーポン・償還プレミアムの上昇、株式交換 | H3 |
| 新規GPU担保ローン・DDTL | 担保融資の開閉 | [EDGAR](https://www.sec.gov/edgar/search/) 8-K Item 1.01/2.03 | 案件ごと・無料 | CoreWeave SOFR+5.50%、Nebius SOFR+2.75%（364日）、Lambda 6.78% | SOFR+3%以下、長期テナー | SOFR+6%超、364日化、案件の途絶 | H3 |
| 中古GPU価格 | 担保価値 | [ServerBuyback](https://serverbuyback.com/resources/gpu-resale-value-index/)、[Compute Exchange](https://blockspace.media/insight/compute-exchange-launches-used-gpu-marketplace/) | 不定期・無料 | H100 $15〜28K（6月） | $20K以上で安定 | $12〜15K割れ、売買の不成立 | H3 |
| 差押え・破綻記録 | 強制清算の発生 | [AM Compute](https://www.amcompute.com/gpu-risk/defaults)、PACER、8-K 1.03/2.04 | 随時 | 記録なし（10/17） | なし | 初の差押え・競売 | H3 |
| HY / CCC / IG OAS | 波及の度合い | [FRED](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)（BAMLH0A0HYM2/BAMLH0A3HYC/BAMLC0A0CM） | 日次・無料 | HY 3.40%（10/22）、IG 82bp（10/8）、CCC約13.4%（二次情報） | HY 3.0%未満 | HY 4%超で他セクターへ波及、5%超で広域ストレス | H3 |
| DC ABS・Meta Hyperion債 | SPV・証券化への評価 | Barclays等（有料）、TRACE | 週次〜約定ごと | DC ABS発行$11.9B（年初来、9月時点）、Hyperion債は91セント（10/20、二次情報） | 一般ABSと連動 | Hyperion債が90セント割れ、後続案件の上乗せ金利が拡大 | H3 |
| Oracle 5年CDS | IG側の代理指標 | [AI Weekly](https://aiweekly.co/alerts/oracle-nvidia-alphabet-spacex-cds-hit-records-on-ai-debt) 等の報道 | 日次（有料） | 約203bp（7月、2008年以来の最高）。10月の値は未確認 | 200bp未満 | 250bp超 | H3 |
| ネオクラウド株・IV・空売り | 株式側のストレス | [Market Chameleon](https://marketchameleon.com/Overview/CRWV/OptionChain/)、[Fintel](https://fintel.io/s/us/crwv)、FINRA | 日次／月2回 | CRWV IV 97〜103%（10/21）、空売り比率17.49%（日付不明） | 株とCDSが同時に改善 | 株が反発してもCDSが追随しない、空売り25%超 | H3 |
| IPOパイプライン | 株式市場の受容度 | EDGAR S-1/RW、ASX | 随時 | Firmusが撤回、Eliceは上場初日-32% | 上場の再開 | Lambda・Crusoe等の延期 | H3 |
| 金利（FedWatch、SOFR） | 変動金利ローンの利払い負担 | [CME FedWatch](https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html) | リアルタイム・無料 | 9月に利上げとの報道（一次資料は未確認） | 利下げの織り込み | 追加利上げの織り込み | H3 |

### 指標一覧（企業開示）

| 開示項目 | 入手先 | 直近値 | 警戒サイン |
|---|---|---|---|
| 債務満期表・流動債務の分類 | 10-Q | CoreWeave: 2026年残り$4.4B、2027年$6.2B | 流動性が流動債務を下回る |
| コベナンツ遵守・ウェーバー | 10-Q、8-K Item 1.01（修正契約） | 6/30時点で遵守 | 遵守の文言が消える、修正契約・ウェーバー |
| 継続企業の前提（"substantial doubt"） | 10-Q/10-K | 記載なし | 出現 |
| RPO・繰延収益・顧客集中度 | 10-Q | CoreWeave RPO $103.7B、Nebius繰延収益$6.0B | RPOの前四半期比減少、上位顧客の契約変更 |
| 8-K Item 1.02（重要契約の終了）/ 2.04（期限の利益喪失）/ 2.06（減損） | [SEC 8-K様式](https://www.sec.gov/files/form8-k.pdf) | なし | 出現＝最重要の警報 |
| Nvidiaの保証・クラウド契約・投資 | [Nvidia 10-Q](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000075/nvda-20260726.htm) | 保証$108.5B、クラウドサービス契約$29B、投資$99B（[Hudson Labs](https://www.hudson-labs.com/research/nvidia-q2-2027-earnings)） | 前四半期比の増加、損失の認識 |

## 需要側に「停滞」の証拠はなく、崩れているのは単価と収益性

### フロンティアの進歩

「フロンティアモデルが頭打ちになった」という主張は、主要な能力指標では確認できない。

- **Epoch ECI**: 首位は約1か月で166から**169**（Claude Opus 5.5、GPT-6 Astra）に上がった。reasoning導入後の上昇ペースは年約14ptで、それ以前の約6ptを上回る ([Epoch Brief](https://epochai.substack.com/p/the-epoch-brief-october-23-2026); [Epoch](https://epoch.ai/data-insights/open-closed-eci-gap))。
- **METR**: タスクの時間地平が倍増するまでの期間は131日に短縮した ([METR](https://metr.org/blog/2026-01-29-time-horizon-1-1/))。
- **反論**: この「再加速」は本物ではないという論評もある ([Paul Kedrosky](https://paulkedrosky.com/the-ai-re-acceleration-that-wasnt/))。

### オープンモデルの追い上げ

縮んでいるのはオープンとクローズドの差である。Artificial Analysisの指数では、Kimi K3.1 Pro（55）が11月初めに重みを公開すれば、クローズド首位との差は約12ptから約3ptに縮む ([AA on X](https://x.com/ArtificialAnlys/status/2113688083145314416); [Artificial Analysis](https://artificialanalysis.ai/))。これはラボの価格決定力の問題であり、計算資源の総需要の問題ではない。

### 量は増えても支出は増えていない

OpenRouterの週間トークン量は**4.87T（2025年10月）から167.65T（2026年10月5日週）**へ増え、オープンウェイトのシェアは**72%**になった ([Global Advisors](https://globaladvisors.biz/2026/10/17/fast-fact-closed-weight-ai-usage-on-openrouter-rose-13-fold-as-its-share-of-tokens-fell/))。ただしOpenRouterは価格に敏感な開発者向けの経路である。Rampのデータでは、接続企業のトークン量の**58.9%**がAnthropicで、企業の利用はなおクローズドモデル主体である (同)。

Rampの別の指標はより警戒的である。8〜9月は企業のトークン量が増えたのに支出はほぼ横ばいで、ブレンド単価が下がり、価格交渉力は顧客側にあるという。米企業のAI有料利用率は55.9%で、導入はSカーブの上部に近いとRampは見ている ([Ramp AI Index](https://ramp.com/data/ai-index-oct-2026))。

フロンティアモデルの価格も下がっている。Opus 5.5は$4/$20で、Opus 5から約20%の値下げとなり、同じ日にOpenAIもGPT-6を値下げした ([AI Weekly](https://aiweekly.co/alerts/openai-anthropic-slash-prices-as-gpt-6-and-opus-55-ship))。

### 「ラボがGPUを放出する」仮説の検証方法

暗号資産トレーダーの主張する「ラボがGPUを放出して推論マージンを取りに行く」動きが起きるなら、次の二つに現れるはずである。

1. OpenRouterのホスト数が増え、価格が底値に収斂する。現在の価格幅はかなり広く、DeepSeek V4.1 Flashは約41ホストで出力$0.18〜2.40/M、GLM-5.3は約49ホストで$1.40〜8.80/Mである ([OpenRouter API](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash/endpoints))。
2. 浮動株（Vast.aiの出品数など）に供給が流入する。

採算の目安は次の式で計算できる。

> GPU 1基あたりの必要出力スループット（トークン/秒）＝ GPU時間単価 ÷（100万トークンあたり単価 × 0.0036）

たとえばB200を$8.50/時で借り、DeepSeek V4.1 Flashを$1.20/Mで提供するなら、約**1,970トークン/秒**が必要になる【計算】。賃料が上がるかトークン単価が下がれば、必要なスループットは直接上がる。推論事業者の例では、Fireworksが年間経常収益$1B超に達し、粗利率は約50%と報じられている（二次情報）([Sacra](https://sacra.com/research/fireworks-ai/); [valueaddvc](https://valueaddvc.com/blog/fireworks-ai-valuation-2026-17-5b-series-d-and-the-1b-arr-inference-business))。

### ラボの数字はむしろ計算資源の不足を示す

**Anthropic**の売上はH1 2026が$16.3B、Q3単独が$16.8B（前四半期比+45%）である。計算資源のコミットメントは$518Bから最大**$750B**に膨らんだ。S-1のリスク要因では、ハイパースケーラーが容量を「削減・値上げ・終了」しうると開示している ([Dealroom](https://dealroom.co/news/164610-anthropics-draft-s-1-reveals-16-3b-revenue-80-7b-loss-and-up-to-750b-com/))。つまりAnthropicが恐れているのは計算資源の不足であり、余剰ではない。コミットメントを年換算売上（約$67B）で割ると約7.7〜11倍になる【計算】。

**OpenAI**の年換算売上は9月末で$50B弱にとどまる。2026年前半には月次の売上目標を複数回下回ったと報じられ（WSJ、二次情報）、コミットメントは$1.4T超に及ぶ ([AI Magazine](https://aimagazine.com/news/openais-billion-users-us-852bn-valuation-and-stargate); [tech-insider](https://tech-insider.org/openai-revenue-miss-friar-altman-stargate-2026/))。弱気シナリオの最大の火種はOpenAIの資金調達と契約履行である。

### ハイパースケーラーとセルサイドの見通し

ハイパースケーラーのクラウド事業は加速している。

| 企業 | クラウド成長率 | 受注残など |
|---|---|---|
| Microsoft | Azure +43% | 受注残$678B（前四半期比+$51B） |
| Google | Google Cloud +82% | 受注残$514B |
| Amazon | AWS +37% | — |
| Oracle | OCI +121% | RPO $664B（前四半期比+$26B、増加ペースは鈍化） |

出典: [Digital Applied](https://www.digitalapplied.com/blog/ai-capex-scorecard-earnings-week-july-2026); [Top1Markets](https://www.top1markets.com/news/alphabet-q3-2026-earnings-preview-cloud-capex); [erp.today](https://erp.today/oracle-q1-fy27-results-664b-backlog-ai-contracts/)

AmazonのJassyは「2027年までほぼ売り切れ」と述べた。「2028年まで売り切れ」という見出しは発言より強い表現である ([explainx](https://explainx.ai/blog/aws-capacity-sold-out-2026-2027-2028-jassy-good-chunk-claimed-vs-verified-2026))。Metaは2027年のcapexを数値で示さず、Q3のFCFは-$2.12Bだった ([Meta 8-K](https://www.sec.gov/Archives/edgar/data/0001326801/000162828026066700/meta-09302026xexhibit991.htm))。

Goldmanは上位5社のAI capexを、2026年**$800B**、2027年**$1.2T（+54%）**、2028年**$1.4T（+12%）**と見ている ([Startup Fortune](https://startupfortune.com/goldman-sachs-says-hyperscalers-will-spend-12-trillion-on-ai-in-2027/))。2028年に伸び率が急に落ちるこの形こそ、半導体サプライヤーにとって典型的な危険信号「capexの額は増えているのに伸び率が鈍る局面」である。

| 指標 | 何を測るか | 入手先 | 頻度・費用 | 直近値（日付） | 健全 | 停滞・過剰 | 仮説 |
|---|---|---|---|---|---|---|---|
| Epoch ECI | フロンティアの能力 | [Epoch Brief](https://epochai.substack.com/p/the-epoch-brief-october-23-2026) | 随時・無料 | 首位169（10/23） | 年+6pt超 | 年率+6pt未満が2四半期続く | H2 |
| METR 時間地平 | エージェント能力の倍増速度 | [METR](https://metr.org/blog/2026-01-29-time-horizon-1-1/) | 不定期・無料 | 倍増まで131日（2026/1） | 短縮 | 210日超に戻る | H2 |
| Artificial Analysis 指数 | オープンとクローズドの差 | [AA](https://artificialanalysis.ai/) | 随時・無料（APIあり） | Opus 5.5が57.6、Kimi K3.1 Proが55.1 | 差が維持される | 首位の更新が6か月止まる、差が3pt未満で定着 | H2 |
| OpenRouter 週間トークン・オープン比率 | 価格に敏感な層の利用量 | [OpenRouter](https://openrouter.ai/rankings) | 週次・無料 | 167.65T/週、オープン72%（10/5週） | 月+30%以上 | 月+10〜15%未満に鈍化 | H2・H1 |
| OpenRouter ホスト別価格 | オープンモデル推論の価格競争 | [endpoints API](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash/endpoints) | 随時・無料 | 出力$0.18〜2.40/M（10/26） | 価格幅が広く、上位ホストが価格を維持 | 全ホストが底値に収斂 | H2・H1 |
| Ramp AI Index | 企業の有料導入率と支出 | [Ramp](https://ramp.com/data/ai-index-oct-2026) | 月次・無料 | 導入率55.9%、支出は横ばい（9月分、10/14公表） | 導入率と支出がともに増加 | 導入率の増加が3か月連続で+0.3pt未満、かつ1人あたり支出が減少 | H2 |
| Census BTOS | 米企業のAI利用率 | [Census](https://www.census.gov/library/stories/2026/05/ai-use-businesses.html) | 隔週・無料 | 19.8%（5/3までの期間） | 上昇 | 20%前後で頭打ち | H2 |
| Googleのトークン処理量 | 最大級の自社推論の需要 | [GIGAZINE](https://gigazine.net/gsc_news/en/20260520-google-monthly-tokens-processed/) | 決算・I/O時 | 月3.2京（2026/5、前年比約7倍） | 前年比3倍以上 | 前年比3倍未満 | H2 |
| Anthropic S-1/A | 売上、粗利、コミットメント、リスク文言 | [EDGAR](https://www.sec.gov/edgar/search/) | 改訂ごと | Q3 $16.8B、コミットメント最大$750B | 前四半期比+20%超、コミットメント倍率が低下 | 前四半期比+10%未満なのにコミットメントが増える | H2・H5 |
| ハイパースケーラーのcapex・受注残 | 最終需要と投資余力 | 各社IR、[Microsoft IR](https://www.microsoft.com/en-us/investor) | 四半期 | 上表のとおり | 2027年capexが+40%以上 | 増加額が2四半期連続で半減、「容量制約」の発言が消える | H2 |
| セルサイドのcapexコンセンサス | 市場の期待値 | Goldman/MS/BofA（報道経由） | 不定期 | 2027年コンセンサス$1.1T、Goldmanは$1.2T | $1.2Tへ収斂 | 2027年の下方修正、2028年の伸びが1桁 | H2 |

## ストランデッド計算資源は需要不足ではなく電力不足の症状

### すでに起きている事例

ストランデッド計算資源はすでに記録されている。

- **AWS**: 社内メールによると、電力のないサイトに置けないNvidia GB300ラック約**$5B**を「Early Rack Receipt」として倉庫で受け入れ、今後も月約$3B増える見込みだという（Business Insider経由）。Amazonは早期の受け入れは通常の慣行だと説明している ([American Bazaar](https://americanbazaaronline.com/2026/10/23/amazons-5-billion-nvidia-ai-servers-sit-idle-in-warehouses-amid-data-center-power-shortages-490651/))。
- **Microsoft–Nscale**: Microsoftは、英国の送電会社が「十分な電力は2030年代前半〜半ばまで届かない」としたことを受け、23,040基のGB300を予定していたLoughtonの契約を10月18日頃に終了した ([Data Center Knowledge](https://www.datacenterknowledge.com/build-design/microsoft-exits-nscale-data-center-deal-over-uk-power-delays))。

賃料の上昇と倉庫に眠るGPUが同時に存在するのは、需要不足ではなく物理的なボトルネックの典型的な姿である。物理的な滞留は、短期的には容量が市場に出ないので賃料を支える。同時に、稼働しない資産に利息だけがかかるため、資金繰りを圧迫する。そして電力がつながった時点で、まとめて供給の波になる。

### 電力と送電網の制約

- **ERCOT（テキサス）**: 大口負荷の接続申請は約410GW（3月）あり、その71.5%は調査書類が未提出、「通電承認済みだが未稼働」が3,241MW、実際に通電しているのは5,778MWにすぎない ([Corley Energy](https://www.corleyenergy.com/ercot-large-load-queue.html))。
- **PJM**: 2028/29年度の容量オークションは上限の$325/MW-日で約定し、必要量に**6,831MW**足りなかった ([PJM](https://insidelines.pjm.com/pjm-capacity-auction-procures-138318-mw-of-generation-resources-as-work-continues-to-address-growing-electricity-demand/))。
- **ガスタービン**: GE Vernovaの受注残と予約枠は116GWで、四半期の出荷3GWに対して新規予約は約20GWある ([GE Vernova](https://www.sec.gov/Archives/edgar/data/1996810/000199681026000147/gevpressrelease2q26.htm))。
- **規制**: テキサス州知事は9月21日、ERCOTと水資源当局の監査（12月中旬見込み）が終わるまで、データセンターの許可を停止するようTCEQに命じた ([Texas Governor](https://gov.texas.gov/news/post/governor-abbott-directs-tceq-to-halt-data-center-permits); [Bracewell](https://www.bracewell.com/resources/governor-abbott-orders-tceq-to-pause-all-permit-issuance-for-data-center-projects/))。停止範囲は送電網を使わない自家発電型（ビハインド・ザ・メーター）の案件にも及ぶと報じられており、2027年に間に合わせるための迂回路も細っている。

### 資本の投入と通電の乖離

建物への資本投入は過去最高である。Censusのデータセンター建設支出は年率換算$85B（8月、前年比+73%）、JLLの集計では北米で66GWが建設中で、その95%に入居契約がある ([Construction Dive](https://www.constructiondive.com/news/data-center-construction-spending-august/831954/); [JLL](https://www.jll.com/en-us/newsroom/data-center-demand-exceeds-expectations-in-h1-2026))。一方、2026年に予定されていた米国の容量の30〜50%が遅延または中止リスクにあり、地域の反対で第2四半期に$68B分の案件が阻止・遅延した ([Yahoo/Sightline](https://finance.yahoo.com/sectors/technology/articles/half-planned-us-data-center-150928890.html); [Tom's Hardware](https://www.tomshardware.com/tech-industry/data-centers/local-opposition-blocked-usd68-billion-worth-of-data-center-projects-in-the-second-quarter-of-2026-data-center-investments-reportedly-still-on-track-to-hit-usd32-trillion-by-2050))。

注視すべき乖離は二つの量の差である。一つは「チップの流入」で、台湾ODMの月次売上とNvidiaの出荷に現れる。Foxconnの9月売上は前年比+38%だった ([Quartz](https://qz.com/foxconn-third-quarter-revenue-ai-demand-100526))。もう一つは「通電の進捗」で、Epochの衛星推計やERCOTの通電MWに現れる。前者が伸び続けるのに後者が横ばいなら、ストランデッド計算資源が増えていることを意味する。

| 指標 | 何を測るか | 入手先 | 頻度・費用 | 直近値（日付） | 緩和 | 悪化 | 仮説 |
|---|---|---|---|---|---|---|---|
| ERCOT大口負荷接続 | 申請から通電までの各段階のMW | [ERCOT資料](https://www.ercot.com/files/docs/2026/05/24/8-Interconnection-and-Grid-Analysis-Update.pdf)、[Corley Energy](https://www.corleyenergy.com/ercot-large-load-queue.html) | 月次〜四半期・無料 | 約410GW、承認済み未稼働3,241MW、通電5,778MW（3/26） | 調査承認・通電の比率が上がる | 申請が増えても通電が横ばい、「承認済み未稼働」が積み上がる | H4 |
| PJM容量オークション | 電力の確保余力 | [PJM](https://insidelines.pjm.com/pjm-capacity-auction-procures-138318-mw-of-generation-resources-as-work-continues-to-address-growing-electricity-demand/)、[Distroforge](https://distroforge.com/blog/pjm-capacity-auction-results-backstop-procurement/) | 年次（12月にバックストップ調達の結果） | 上限で約定、6.8GW不足（7月） | 上限未満で約定 | バックストップ調達が不調 | H4 |
| 大口需要向け電気料金・契約MW | 投機的な申請のふるい落とし | [EEI](https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs) | 随時・無料 | 25州で承認、AEP Ohioは契約17,861MW（関心表明は約30GW） | 契約MWが予定どおり通電 | 退出料金の発動 | H4 |
| ガスタービン受注残 | 自家発電・つなぎ電源の制約 | [GE Vernova](https://www.sec.gov/Archives/edgar/data/1996810/000199681026000147/gevpressrelease2q26.htm)、[Siemens Energy](https://www.utilitydive.com/news/siemens-gas-turbine-backlog-nears-70-gw-as-company-expands-manufacturing/827390/) | 四半期・無料 | GEV 116GW、Siemens 69GW | 出荷の増加 | 予約枠のキャンセル（需要減）または納期の一段の後ずれ（制約悪化） | H4 |
| 変圧器リードタイム | 送配電機器の制約 | [Industrial Sage](https://www.industrialsage.com/power-transformer-lead-times-us-grid-shortage/) | 四半期 | 発電所用変圧器（GSU）は160週超（2026年Q1、二次情報） | 短縮 | 160週超が続く | H4 |
| Censusのデータセンター建設支出 | 建物への資本投入 | census.gov/construction/c30（一般知識、本調査では未取得） | 月次・無料 | 年率換算$85B（8月） | 支出が横ばいで通電が追いつく | 支出が加速し通電が追いつかない | H4 |
| CBRE / JLL | 空室率、建設中の容量、事前契約率 | [CBRE](https://www.cbre.com/insights/books/north-america-data-center-trends-h1-2026)、[JLL](https://www.jll.com/en-us/newsroom/data-center-demand-exceeds-expectations-in-h1-2026) | 半期・無料 | 空室1.4%、事前契約80.4%（CBRE）／95%（JLL） | 空室率が低位 | 事前契約率が75%未満 | H4 |
| Data Center Watch | 地域の反対運動 | [datacenterwatch.org](https://www.datacenterwatch.org/report) | 四半期・無料 | Q2に約$68Bが阻止・遅延、反対団体843 | 減少 | Q3（12月頃公表、時期は未確認）で再増加 | H4 |
| Epoch AI Frontier Data Centers | 衛星画像による実際の通電IT電力 | [Epoch](https://epoch.ai/graphs/largest-ai-data-centers-by-power-capacity) | サイトごと随時・無料 | Colossus 2は946MW、New Carlisleは910MW | 予測どおり増加 | チップ出荷との乖離が拡大 | H4・H5 |
| 台湾ODMの月次売上 | チップの流入 | MOPS（毎月10日まで、一般知識）、[追跡サイト](https://stackpath.ie/global/taiwan-ai-supply-chain-monthly) | 月次・無料 | Foxconn +38%。Quanta +77%、Wistron +87%は単一の追跡サイトの値で未検証 | 通電と同じペースで伸びる | 前月比の急減、「顧客の引き取り延期」 | H4 |
| 倉庫保管・撤退の報道 | 滞留の実例 | Business Insider、DCK等 | 随時 | AWSが約$5B分を保管、Nscale案件から撤退 | — | 同種の報道が増える | H4 |
| テキサス・NYの規制 | 許認可リスク | [Texas Tribune](https://www.texastribune.org/2026/09/21/texas-data-center-moratorium-water-energy/)、[Davis Polk](https://www.davispolk.com/insights/client-update/new-york-state-enacts-data-center-moratorium) | 随時 | TCEQの許可停止（9/21〜）、NYの50MW超に1年の猶予措置（7/14〜） | 12月の監査完了と再開 | 監査の延期、2027年1月の州議会での法制化 | H4・H5 |

## SpaceXは最もスポット感応度の高い計算資源の貸し手で、発言には利害がある

### 「計算資源の提供者」への転換はすでに半分進んでいる

SpaceXのQ3売上は$14.6B（前年比+161%）で、そのうちSuper Intelligence部門が$7.6B（Cursor買収分を含む）、全体の約**52%**を占める【計算】。計算容量は9月末の1.7GWから、年末に2.5〜3GW、2027年末に13GW以上を目指している ([Fool transcript](https://www.fool.com/earnings/call-transcripts/2026/10/20/spacex-spcx-q3-2026-earnings-call-transcript/); [BigGo](https://finance.biggo.com/news/US_SPCX_2026-10-20))。Muskは、容量の約半分を自社で使い半分を貸し出し、短期でスポットに近い価格の契約を好み、新規導入は1年未満で回収できると説明した ([Yahoo/Stocktwits](https://finance.yahoo.com/markets/stocks/articles/crwv-nbis-nvda-jump-overnight-023720804.html))。

この契約方針は、CoreWeaveの契約比率98%とは正反対である。スポットが崩れたとき最も早く売上単価が下がるのはSpaceXだということになる。「1年未満で回収」も現在の価格が続く前提での話である。なお、Foolのトランスクリプトのページにはプロンプトインジェクション的な文言が含まれていたため、引用はSpaceXのIR原本で確認するのが安全である。

### 顧客契約と解約条項

- **Google**: 約11万基のGPUを月$920Mで、2026年10月〜2029年6月まで借りる。2026年12月31日以降はどちらも90日前の通知で解約でき、解約は最短で**2027年4月頃**に効力を持つ ([TechCrunch](https://techcrunch.com/2026/06/05/google-will-pay-spacex-920m-per-month-for-compute/))。暗黙のGPU時間単価はCPUやメモリを含めて約$11.5である【計算】。
- **Anthropic（Colossus 1）**: 22万基超・300MW超を月$1.25Bで2029年まで借りる ([Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/musks-spacex-has-rented-out-access-to-its-supercomputers-220-000-nvidia-gpus-and-300-megawatts-of-ai-compute-power-to-rival-anthropic-musk-says-no-one-set-off-my-evil-detector-antrhropic-also-interested-in-orbital-data-centers))。Colossus 1を貸し出したのは、Grokの訓練への統合がうまくいかなかったためだと報じられている ([TNW](https://thenextweb.com/news/spacex-colossus-1-technical-problems-rented-anthropic))。解約条件は後述の訂正のとおり未解決である。

### $40B債務の中身

Muskは10月25日に「クローズした」と投稿したが、Reutersは「完了」の正確な意味が不明だと注記している ([CNBC](https://www.cnbc.com/2026/10/26/spacex-closes-40-billion-debt-deal-for-ai-chips-elon-musk-.html))。報じられている内容は次のとおりである。

- **構造**: Apollo系のAtlas SPが管理するSPVで調達し、SpaceXのバランスシートから外す。3トランシェの私募で、劣後部分は推定$25〜30B。市場の悪化で価格の再交渉に入っていた ([Investing.com/Bloomberg](https://www.investing.com/news/company-news/spacexs-40bn-ai-debt-deal-faces-hurdles-amid-credit-market-turmoil--bloomberg-4970497))。
- **利回り**: 劣後部分が約8.3%、チップ担保部分が約7.75%（クローズ前の報道）([WebProNews](https://www.webpronews.com/spacex-40-billion-gpu-debt-closed-musk-credit-markets))。
- **チップの到着**: 債務は主に繰上げ償還可能で、GPUは2027年Q1〜Q2に到着する予定である。

Colossus 2は通電中のIT電力が約946MWで、2027年2月頃に1,531MWへ増える予測である ([Epoch](https://epoch.ai/data/ai-data-centers/directory/colossus-2))。ただし電源のガスタービンをめぐっては、59基が連邦の許可なく設置されたとの報道と訴訟がある ([Technology.org](https://www.technology.org/2026/07/15/xai-59-unpermitted-gas-turbines-southaven-colossus-2/))。2027年上期に届くチップと通電MWが一致するかが、SpaceX固有の物理リスクである。

### 発言の利害（ポジショントーク）

10月25日のMuskの発言は、SpaceXにとって都合の良い方向に働く。競合のネオクラウドの資本コストを押し上げ、SpaceXを「淘汰を生き残って統合する側」に位置づけるからである ([Stocktwits](https://stocktwits.com/news-articles/markets/equity/spcx-musk-40b-gpu-deal-warns-neoclouds-dan-ives-game-of-thrones-war/cZUdlckRBUs))。

一方で、5日前の決算説明会では「計算資源の不足は長く続く」と語っていた。これと25日の「ストランデッド計算資源」は、電力不足という一点では整合する。両方を合わせて読むと、Muskの警告は需要についてではなく、競合の資金調達についての発言である。

Chamathも利害関係者である。自らを「通電済み用地の保有者」と称し ([Chamath on X](https://x.com/chamath/status/2114389987563381004))、アリゾナで約2,000エーカー、最大1.5GWの用地に関わっているが、電力会社APSとの契約が次の段階で、通電は確認されていない ([DCD](https://www.datacenterdynamics.com/en/news/arizona-land-consulting-buys-land-for-potential-15gw-data-center/))。「パイプラインの遅延が2027年に人々を驚かせる」という警告は、彼の資産の希少価値を高める方向に働く。

両者の物理面の診断はデータと合う。しかし「債務市場はほぼ閉じた」という資金面の診断は、10月の案件データと部分的に矛盾する。SPCXのロックアップについては、「10月24日（土）に1トランシェが解除され、最大3.284億株が26日（月）から売買可能になる」との報道がある（二次情報）([Stocktwits](https://stocktwits.com/news-articles/markets/equity/spcx-musk-40b-gpu-deal-warns-neoclouds-dan-ives-game-of-thrones-war/cZUdlckRBUs))。正式な条項はS-1/Aと424B4のロックアップ条項で確認すべきである ([SpaceX S-1/A](https://www.sec.gov/Archives/edgar/data/0001181412/000162828026039276/spaceexplorationtechnologi.htm))。

| 指標 | 何を測るか | 入手先 | 頻度・費用 | 直近値（日付） | 健全 | リスク顕在化 | 仮説 |
|---|---|---|---|---|---|---|---|
| $40Bの確定条件 | トランシェ別の利回り、貸し手、SPV | SpaceX 8-K（1.01/2.03）、Bloomberg/FT/Semafor | 随時 | 「クローズ」の投稿（10/25）。Goldmanの関与は未確認 | 投資適格級の条件で確定 | 劣後部分が9%超、規模縮小、「完了」の中身が仮契約 | H5・H3 |
| SpaceXの社債・CDS・格付け | 信用評価 | TRACE、[AI Weekly/LSEG](https://aiweekly.co/alerts/oracle-nvidia-alphabet-spacex-cds-hit-records-on-ai-debt) | 日次／随時 | CDSは7月に過去最高、30年債スプレッド2pt超。10月の値と格付けは未確認 | スプレッドが縮小 | 見通しのネガティブ化、SPVの連結判断 | H5 |
| 顧客の解約権の行使 | 賃貸収入の持続性 | SpaceX 10-Q/8-K Item 1.02、Anthropic S-1/A | 随時 | Googleは12/31以降に90日解約が可能 | 解約ゼロ、延長・追加 | 90日通知の行使、減量オプションの行使 | H5・H2 |
| SI部門の売上・容量 | 計算資源事業の立ち上がり | SpaceX決算 | 四半期 | $7.6B、1.7GW、2027年Q1の売上ガイド$33〜37B | 計画どおり | 更新単価の下落、容量目標の後ずれ | H5・H1 |
| Colossus 2の通電・タービン | 物理的な実現性 | [Epoch](https://epoch.ai/data/ai-data-centers/directory/colossus-2)、[GEM](https://www.gem.wiki/Colossus_2_power_station) | 随時・無料 | 946MW→1,531MW（2027/2頃の予測） | 予測どおり完成 | 判決によるタービン制限、チップ到着との乖離 | H5・H4 |
| ロックアップ解除 | インサイダーの売り圧力 | [S-1/A](https://www.sec.gov/Archives/edgar/data/0001181412/000162828026039276/spaceexplorationtechnologi.htm)、424B4 | トランシェごと | 最大3.284億株が10/26から売買可能（二次情報）。次回は12月との投稿あり（未検証） | — | 解除日前後の強気発言と売り | H5 |

## 半導体株は需要ではなく資金調達と「変化率」を織り込んでいる

### Nvidia

直近の開示は強い。2Q FY27の売上は**$96.2B**、データセンター売上は$89.0B、3Qのガイダンスは**$108B±2%**である ([NVIDIA IR](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/default.aspx))。

一方で10-Qの注記には膨張が目立つ。在庫は1月末比+48%の$31.6B、売掛金は+64%の$63.1Bになった。DSOは約60日で、Nvidia自身は投資適格の一部顧客に支払条件を延ばしたためと説明している。供給・キャパシティのコミットメントは前四半期の$119Bから**$279B**に増え、主にメモリの調達とされる ([Hudson Labs](https://www.hudson-labs.com/research/nvidia-q2-2027-earnings))。11月18日頃（未確定。11/25とする予想もある）の3Q決算では、在庫→評価損→供給コミットメント→クラウドサービス契約→保証と投資、の順で確認するのが効率的である。

### TSMC

月次売上は最も高頻度の一次データである。9月はNT$511.86Bで、4Qのガイダンス中央値は前四半期比+14%を示す。在庫日数は87日から82日へ下がり、川上に在庫は積み上がっていない ([TSMC](https://pr.tsmc.com/english/news/3343); [Motley Fool](https://www.fool.com/earnings/call-transcripts/2026/10/15/tsmc-tsm-q3-2026-earnings-call-transcript/))。

### メモリ

価格の二階微分が株価を動かしている。DRAMの契約価格の上昇率は、2Q +80%、3Q +40%、4Q約+20%（予想）と鈍化している ([StockHub/TrendForce](https://www.stockhub.kr/en/news/news_b7244c205001))。業績は強く、Micronは2027年度の出荷の75%がすでにコミット済みである ([MarketBeat](https://www.marketbeat.com/instant-alerts/transcript-micron-technology-q4-earnings-call-highlights-2026-09-30/))。Jensen Huangも2029年までメモリの供給過剰はないと述べた ([CNBC](https://www.cnbc.com/2026/10/22/jensen-huang-nvidia-memory-selloff-shortage.html))。それでも株価は「上昇率の鈍化」と「CXMT」に反応した。

### 装置

Lamは過去最高の売上を出しつつ、部品の供給制約で12月期のガイダンスを抑え、2027年のWFE（前工程装置市場）は$200B超と示した ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/lam-research-sinks-9-supply-144450114.html))。これは需要不足ではなく出荷能力の不足であり、本来はエアポケットとは逆のシグナルである。

### 日本株

10月23日の東京市場では、アドバンテストが日経平均を約293円押し下げて最大の下落寄与となり、東京エレクトロンやディスコも大きく下げた ([財経新聞/フィスコ](https://www.zaikei.co.jp/article/20261023/874686.html))。米国SOXの急落が翌日の東京に連動し、Nvidiaサプライチェーンの中でもβの高い代理として売られた形である。

データ自体は強い。ディスコの7〜9月の個別出荷額は**1,239億円**（前年比+60%）で四半期の過去最高だったが、株価は下げた ([ジオ InvestLeaders](https://jioinc.jp/investleaders/?p=20195))。SEAJの3か月移動平均は9月に6,290億円（前年比+48.2%）である。

**SEAJの年度予測との比較【計算】**: 2026年度の予測は6兆5,502億円で ([SEAJ需要予測](https://www.seaj.or.jp/file/july2026seajforecastforpress_j.pdf))、上期の推定実績は約3.43兆円（約52%）だった。下期の必要額は月平均約5,200億円で、9月水準から約17%落ちても達成できる。このため1月の予測改定は上方修正の公算が大きい（推定）。

アドバンテスト自身が7月に「需要の一部前倒し」に言及しているため、10月28日の決算では受注の前四半期比が最重要になる ([Morningstar Japan](https://global.morningstar.com/ja/stocks/advantest-earnings-outstanding-results-driven-by-robust-ai-demand))。

| 指標 | 何を測るか | 入手先 | 頻度・費用 | 直近値（日付） | 健全 | エアポケット | 仮説 |
|---|---|---|---|---|---|---|---|
| Nvidia決算・10-Q | AI需要の中核 | [NVIDIA IR](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/default.aspx)、[10-Q](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000075/nvda-20260726.htm) | 四半期・無料 | 売上$96.2B、3Qガイダンス$108B、在庫$31.6B（7/26） | 4Qガイダンスが予想超、DSOが横ばい | 在庫・売掛金が売上より速く伸びる | 全般 |
| TSMC月次売上 | ファウンドリの最速データ | [TSMC PR](https://pr.tsmc.com/english/news/3343) | 毎月10日前後・無料 | 9月 NT$511.86B（+54.6%） | 10・11月がNT$512Bを超える | 前年比30%台へ急減速 | 半導体 |
| DRAM/HBM契約価格 | メモリ価格の変化率 | TrendForce（リリースは無料、詳細は有料） | 月次・四半期 | 4Q約+20%（予想） | 上昇率を維持 | 1Q27に1桁、その後マイナス | 半導体 |
| メモリ大手の決算 | HBMの割当と設備投資 | [SK hynix 6-K](https://www.sec.gov/Archives/edgar/data/0002120882/000119312526420934/d413172d6k.htm)、[Samsung](https://www.koreatimes.co.kr/business/companies/20261008/samsung-electronics-estimates-803-bil-in-q3-operating-profit) | 四半期 | Samsungの3Q営業利益107.4兆ウォン（速報） | 2027年HBM契約の確定 | HBM割当の再交渉、設備の大幅増強 | 半導体 |
| SEAJ 日本製装置販売高 | 日本の装置メーカーの出荷 | [SEAJ](https://www.seaj.or.jp/statistics/) | 月次（3か月移動平均）・無料 | 6,290億円（9月、+48.2%） | 前月比プラス | 前月比マイナスが2〜3か月連続、前年比が20%台以下 | 日本株 |
| SEMI 装置出荷額 | 世界の装置出荷 | [SEMI](https://www.semi.org/en/semi-press-release/global-semiconductor-equipment-billings-increased-23-percent-year-over-year-in-q2-2026-semi-reports) | 四半期 | $40.53B（2Q）、中国比率29.4%【計算】 | 増加 | 減少 | 半導体 |
| 装置大手の決算 | WFEの見通し | Lam・KLA・ASMLのIR | 四半期 | 2027年WFE $200B超（Lam） | 見通しの上方修正 | 受注の取消・延期 | 半導体 |
| 韓国の輸出（1〜20日速報） | 世界最速の半導体月次データ | [Korea Times](https://www.koreatimes.co.kr/economy/20261021/exports-double-in-1st-20-days-of-october-on-robust-chip-shipments)、[Herald](https://biz.heraldcorp.com/article/10909625) | 毎月21日・無料 | 半導体$27.5B（+222.5%）。前年の低基数に注意 | 営業日調整後の1日平均が最高を更新 | 1日平均の鈍化 | 半導体 |
| 台湾の輸出受注 | 3〜6か月先の出荷 | [Focus Taiwan](https://focustaiwan.tw/business/202610200019) | 毎月20日前後・無料 | 9月$114.21B（+62.4%、経済部の予測上限を超過） | 予測レンジを上回る | 予測レンジを下回る | 半導体 |
| SIA・WSTS | 世界の半導体売上 | [AnySilicon/SIA](https://anysilicon.com/news/year-to-date-global-semiconductor-sales-top-1-trillion-through-august/)、[WSTS](https://www.wsts.org/esraCMS/extension/media/f/WST/7618/WSTS_FC-Release-2026-May.pdf) | 月次／半期・無料 | 8月$159.7B（+144%、価格主導）、2027年予測$1.91T | 上方修正 | 秋季予測で2027年を下方修正 | 半導体 |
| SOX・ETFフロー | 市場の需給 | [Crypto Briefing](https://cryptobriefing.com/semiconductor-index-sp500-ratio-lowest-since-april/)、[Market Matters](https://marketmatters.com.au/?p=233956) | 日次・無料 | SOX/S&P500比率が4月以来の低水準、SOXXは3か月連続の資金流出 | 200日線を回復 | 比率が4月の安値を割る | 半導体 |

日本の主要銘柄の決算日と見るべきKPIは次のとおりである。AI関連の接点は一般的な業界知識に基づく整理で、本調査では出典を確認していない。開示の入手先は、決算短信が [TDnet](https://www.release.tdnet.info/)（即日）、半期報告書と有価証券報告書が [EDINET](https://disclosure2.edinet-fsa.go.jp/) である。3月決算企業の半期報告書は期末から45日以内、つまり11月中旬に提出され、有報には売上10%超の主要顧客と地域別売上が載る（いずれも一般知識で未検証）。

| 銘柄 | AI関連の接点（未検証） | 決算短信・説明資料で見るKPI | 次の開示 |
|---|---|---|---|
| アドバンテスト（6857） | GPU向けSoCテスター、HBM向けメモリテスター | 受注高（SoC/メモリ別）の前四半期比、受注残 | 10/28 15:30（[Stock Analysis](https://stockanalysis.com/quote/bmv/6857.N/)） |
| 東京エレクトロン（8035） | エッチング・成膜・EUV用コータ/デベロッパ | アプリ別・地域別（中国比率）の売上、初めて開示する通期予想 | 10/30、次は2027/2/5（[TEL IR](https://www.tel.co.jp/ir/calendar/index.html)） |
| ディスコ（6146） | HBMのウエハ薄化・ダイシング | 四半期の個別出荷額の速報、次四半期の出荷見通し | 中間決算10/22（結果は未取得） |
| レーザーテック（6920）・SCREEN（7735） | EUVマスク検査・洗浄装置 | 受注高、受注残、中国比率 | 10/30（[かぶトレ](https://www.kabutore.biz/kessan/schedule.html?date=2026-10-30)） |
| キオクシア（285A） | AIサーバー向けeSSD | NAND価格、ビット出荷のガイダンス | 10/30または11/12（情報が矛盾、[Investing.com](https://www.investing.com/equities/kioxia-holdings-earnings)） |
| KOKUSAI、イビデン、信越化学、SUMCO、TOWA等 | メモリ投資、パッケージ基板、ウエハ | 受注と設備投資 | 未確認 |

## これまでの主張のうち、訂正・保留すべきもの

| これまでの主張 | ノートでの検証結果 | 正しい扱い |
|---|---|---|
| CoreWeave債務の約80%がGPU担保 | 10-Q（6/30）では、GPU担保プロジェクトローンは$13.6Bで元本の**38.4%**。サプライヤーファイナンス14.4%を足しても約53%。非遡及債務は約10%のみ。80%は単一媒体の記述 ([StockTitan](https://www.stocktitan.net/articles/coreweave-nebius-ai-cloud-debt-when-it-comes-due); [Startup Fortune](https://startupfortune.com/ai-neocloud-stocks-sink-as-coreweave-debt-fears-spread-to-equities/)) | 「約4割がGPU担保ローン、約3割が無担保債、2割弱が転換社債」に訂正する |
| Nvidiaのネオクラウド・エクスポージャー$170B | The InformationがNvidiaの開示を分析した数字で、内訳は保証・その他コミットメント最大$164.5B＋直接投資$7B超 ([TNW](https://thenextweb.com/news/nvidia-170bn-neoclouds-firmus))。10-Qの分析では、オフバランス保証$108.5Bのうち最大$105BはOpenAI用のSB Energy案件向け。ネオクラウドの容量買取に近いクラウド契約は$29B（$36Bとする報道もある）([Hudson Labs](https://www.hudson-labs.com/research/nvidia-q2-2027-earnings); [KuCoin](https://www.kucoin.com/news/flash/nvidia-s-ai-financing-model-faces-pressure-as-neoclouds-struggle)) | 「データセンター関連の保証・投資の総額」として扱う。ネオクラウド固有の分は数百億ドル規模。2028年末に$200Bに達しうるとのNvidia自身の警告は二次情報 ([Bloomingbit](https://en.bloomingbit.io/feed/news/119219)) |
| AnthropicはColossus契約を90日で解約できる | S-1は「2029年5月まで月額、双方が90日前の通知で解約可」と記載。Muskは「180日のリース、その後に相互90日」と説明 ([TechCrunch](https://techcrunch.com/2026/05/28/how-long-is-anthropics-lease-with-spacex-opinions-vary/))。一方、「最大$84.5Bで約80%は解約不能」との報道もある（二次情報）([BigGo](https://finance.biggo.com/news/24d90a7f-d26d-413c-8685-bf4da9cb540d))。月$1.25B×36か月≒$45Bで$84.5Bと合わず【計算】、Anthropic全体のコミットメントの「約80%解約不能」と混同している可能性がある | 未解決。断定しない。Google契約の90日条項は確認済み |
| 債務市場はAI専業のネオクラウドにほぼ閉じた（Musk） | 10月にもNebius、Lambda、Cipher、SpaceXが調達 | 「閉鎖」ではなく「選別と値上げ」 |
| SpaceXの$40BはGoldman/Apolloで、社債は$20〜25B | 主導はApollo、Pimcoが協議に参加。Goldmanの関与は未確認、劣後部分は$25〜30B ([BusinessWorld/FT](https://bworldonline.com/technology/2026/10/07/785188/spacex-seeks-40-billion-financing-led-by-apollo-to-buy-nvidia-chips-ft-reports/)) | 確定条件は未開示 |
| Muskは過剰容量論を「ridiculous」と言った | 調査担当はトランスクリプトで見つけられなかったが、Yahoo Finance（Brian Sozzi、10/21）が10/20の決算説明会での発言として "It is ridiculous. I do not think we are going to have a demand issue here." と引用している ([Yahoo Finance](https://finance.yahoo.com/markets/stocks/article/one-week-after-crushing-neocloud-stocks-like-coreweave-and-nebius-with-a-single-word-spacexs-elon-musk-is-out-with-another-word-that-is-less-dire-104420999.html)) | 大手メディアの報道ベースで確認済み（一次のトランスクリプトでは未照合） |
| SOXで$2兆が消失 | 6営業日の確定値は約$1.64兆。$2兆は日中・見込みベース ([Kitco/Reuters](https://www.kitco.com/news/off-the-wire/2026-10-15/us-chip-stocks-set-wipe-out-2-trillion-after-latest-selloff)) | 約$1.6兆 |
| AWSは2028年まで売り切れ | Jassyの発言は「2027年までほぼ売り切れ、2028年分もかなりの部分がコミット済み」 | 見出しは誇張 |
| Oracle CDSは約1,000bp | 他の情報源では約200〜300bp（7月は203bp）([Wealth Professional](https://www.wealthprofessional.ca/investments/equity-markets/oracles-default-insurance-hits-high-yield-levels-as-ai-debt-mounts/393817)) | 誤記の可能性が高い |
| H100は$1.70前後で取引されている | 7月の記事で、2025年10月の1年契約の底値と混同した可能性 ([AI Weekly](https://aiweekly.co/alerts/kalshi-launches-gpu-compute-forward-curves-for-ai-hedging)) | 古い値か誤引用 |
| GPUの期間カーブはコンタンゴ（Silicon Data CEO） | 公表カーブはバックワーデーション | 日付・年限で違う可能性があり、CMEのカーブで確認する |
| OpenRouterのオープン比率72%は市場全体を表す | 企業のトークン量の58.9%はAnthropic（Ramp） | 一般化しない |
| ネオクラウドの80%が消える（Gartner） | 予測は「独立した事業運営の停止」で、買収・統合を含む | 倒産率ではない |
| IRENは借入れなし | 約$6.45Bの無担保転換社債がある ([IREN 10-K](https://www.sec.gov/Archives/edgar/data/0001878848/000187884826000052/iren-20260630.htm)) | 担保付きの銀行借入れがない、の意と解釈（要確認） |
| Chamathの「liquidated damages」発言、「Opus 5.5が企業支出の34%」 | どちらも一次ソースが見つからない | 未検証 |
| 韓国の10月+222.5% | 前年は秋夕で営業日が少なく、低基数の影響がある | 営業日調整後の1日平均で見る |

## 2026年10月末〜2027年半ばのイベントカレンダー

| 日付 | イベント | 見るポイント | 確度 |
|---|---|---|---|
| 10/27〜28 | FOMC | 追加利上げの有無（変動金利のGPUローンに直結） | 日程は一般知識による推定 |
| 10/28 | SK hynix 3Q（ソウル9時前）、アドバンテスト（15:30）、KLA | HBM4の比率と2027年の契約、SoCテスターの受注、WFE見通し | SK hynixは6-Kで確定 |
| 10/28 引け後 | Microsoft FY27 Q1、Alphabet Q3 | Azureが44〜45%を達成するか、受注残の増加額、2027年capex | MSFTは10/27説もあり、IRで確認 |
| 10/29 | Amazon Q3、Samsungの確報 | AWSの成長率、倉庫保管ラックへの言及 | 二次情報 |
| 10/30 | 東京エレクトロン（通期予想を初開示）、SCREEN、レーザーテック、キオクシア（要確認） | 受注と通期予想 | TELは確定 |
| 11/2・11/3 | Cipher Digital Q3、AMD Q3 | 転換社債発行後の資金繰り、データセンター売上 | AMDは確定 |
| 11月初め | Kimi K3.1 Proの重み公開 | オープンとクローズドの差が約3ptに縮むか | 予定 |
| 11/9 | CME GPU1/GPU2の初取引 | カーブの形と建玉 | 単一情報源、規制審査待ち |
| 11/9〜16 | CoreWeave Q3 | DDTL 5.5のドロー状況、2027年満期への対応、RPO、顧客分散 | 未確定（[TipRanks](https://www.tipranks.com/news/coreweave-crwv-is-about-to-report-q3-earnings-heres-what-to-expect); [days.to](https://days.to/coreweave-earnings)） |
| 11/10前後 | TSMC 10月売上 | NT$512B超を保てるか | 例年の慣行 |
| 11/12 | Foxconn Q3 | AIサーバーの比率 | 確定 |
| 11月中旬 | 日本企業の半期報告書（EDINET）、BDCのQ3決算 | 受注、顧客集中度、プライベートクレジットの評価 | 一般知識 |
| 11/18頃 | Nvidia 3Q FY27と10-Q | 4Qガイダンス、在庫、DSO、コミットメント、保証 | 未確定（11/25説あり） |
| 11/20 15:40 | SEAJ 10月度 | 3か月移動平均の前月比 | 確定 |
| 11/21 | 韓国の11月1〜20日輸出 | 半導体の1日平均 | 慣行 |
| 11月以降 | Anthropicの公開S-1とIPO（最短） | 粗利率、契約義務表、SpaceX契約の開示 | 報道 |
| 12月 | PJMのバックストップ調達結果、ERCOT/水資源当局の監査（中旬）、Data Center Watch Q3 | 電力確保と許可再開の可否 | 予定 |
| 12/31 | CoreWeave DDTL 5.5のドロー期限、Google–SpaceXの90日解約権が発生 | ドローの実施、解約通知の有無 | 確認済み |
| 2027年1月 | テキサス州議会の招集、Nebiusブリッジの初回ステップアップ（1/15頃）、TSMC 4Q（2027年capex）、SEAJ需要予測の改定 | 規制の法制化、借換えの成否 | 推定を含む |
| 2027年1〜2月 | ハイパースケーラーのQ4決算（2027年capexガイダンス）、TEL（2/5） | 2027年capexの伸び率 | 例年の慣行 |
| 2027年Q1〜Q2 | SpaceXの$40B資金によるGPU到着、Colossus 2の完成予測（2月頃）、CoreWeaveの2027年満期$6.2Bの進行 | チップ到着と通電の一致 | 報道・予測 |
| 2027年4月頃 | Google–SpaceX契約の90日解約が最短で効力を持つ | 解約・減量の有無 | 【計算】 |
| 2027年5〜7月 | Google I/O（トークン統計）、CoreWeave DDTL 4.0のドロー期限（6月）、Colossus 2の仮設タービン撤去（年央）、NYの猶予措置の期限（7月） | 需要の伸び、資金と電源の確保 | 報道 |

## 結論

「供給過剰は来るのか」という問いを、需要と供給の綱引きとして立てるのは的外れである。データが示す弱点は需要ではなく、三つの時計のずれにある。

1. **チップの時計**: 繰上げ償還可能な債務や短期の債務で買ったチップが、2027年上期にまとめて届く。
2. **電力の時計**: ERCOTの接続待ち、2030年まで埋まったタービンの生産枠、テキサスの許可停止、英国の2030年代送電という制約がある。
3. **契約の時計**: 顧客の90日解約権が2027年4月頃から効力を持ち始め、CoreWeaveの2027年の返済$6.2Bも進む。

物理的な滞留は、今は賃料を押し上げつつ資金繰りを締め付けている。電力が一斉につながった時点で、Nvidiaの言う8GWのネオクラウド容量、Vera Rubin、SpaceXの13GWが重なれば、薄い浮動株は「品薄」から「洪水」へ短期間で反転しうる。その転換点は、ハイパースケーラーのcapexより先に、浮動株の側に現れるはずである。具体的には、Vast.aiの出品数、スポット/オンデマンド比、OrnnとSilicon Dataの乖離、先物カーブである。

日本の半導体株を持つ個人投資家にとっての含意は二つある。第一に、10月の下落は受注データではなく、資金調達の経路と価格の変化率を織り込んだものである。アドバンテストとTELの受注、SEAJの3か月移動平均が11月〜1月に持ちこたえるかどうかで、「調整」か「反転」かを判別できる。第二に、MuskとChamathの発言は、検証可能な仮説として扱うのが正しい。物理面の診断はデータと一致するが、「債務市場の閉鎖」と「200社の淘汰」は彼ら自身のポジションに有利な方向に誇張されている。その真偽は、上の優先10指標のうち4〜5（CoreWeave債とGPU担保ローン）が先に答える。
