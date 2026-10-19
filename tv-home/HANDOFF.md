# TV Home 引き継ぎ書 — v0.5.5

引き継ぎ日：2026-10-19。対象：Xiaomi TV用ホーム画面のフェーズ2・Webダッシュボード。

ユーザーの最新評価は **「めちゃくちゃいい感じ、今のほぼ完成形」**。次セッションへ渡すために整理した。アプリの基準は直前に渡した `tv-home-phase2-v11.zip` のv0.5.5で、今回デザインや挙動は変更していない。新たなUI改訂やフェーズ3への着手は依頼されていない。

**この文書が現在の仕様。** 実行・接続手順の詳細は [README.md](README.md)、過去の相談は [docs/HANDOFF_HISTORY.md](docs/HANDOFF_HISTORY.md)。初期モックや履歴内の未確定事項を、現在の要件と混同しないこと。

![承認済みの最新画面](artifacts/dashboard-desktop.png)

## 1. 現在地と再開方法

- 最新アプリは **0.5.5**。最後の機能追加はDisney+とSpotifyのアプリドック。
- Web版は実装済み。12銘柄の実価格・24時間チャート、渋谷の天気、米国経済指標、ニュースを表示する。
- UIはほぼ完成として評価済み。今の配置・余白・透明感を今後の基準にする。
- APK、TVへのインストール、ADB設定変更、公開ホスティングは未実施。
- Spotifyの実認証、Unsplashの実Access Keyは未接続。設定画面と接続処理は実装済み。
- 作業ディレクトリにGit履歴はない。引き継ぎZIPがソース一式となる。
- 前セッションの開発サーバーは終了済み。新しい環境で起動する。前の環境やURLが存続するとは限らない。

再開時の順序：

1. [START_HERE.md](START_HERE.md) とこの文書を読む。
2. 上の最新画面と [モバイル画面](artifacts/dashboard-mobile.png) を確認する。
3. Node.js 22.9以降で `npm run dev`。`http://127.0.0.1:4173/` を開く。
4. ユーザーの次の依頼に沿って作業する。確定済みの地域・銘柄・アプリ・朝晩の表示を聞き直す必要はない。

実行時npm依存はなく、`npm install` は不要。検証環境はNode.js 24.19.0。

## 2. ユーザーと確定した仕様

| 項目 | 確定内容 |
| --- | --- |
| 時間帯 | 朝晩とも同じフル版。時間帯によるカード切り替えなし |
| 天気 | 渋谷区。現在の気象、明日の最高・最低、日の出・日の入、空気、次の正時から6時間予報 |
| 時間別天気 | アイコン・気温の曲線・降水確率の数値とバー。直感的に読める表示 |
| 音楽 | Spotify。再生情報カードとアプリドックの両方を使う |
| スポーツ | 当面表示しない |
| 個人の予定 | 「今日の予定」は不要。個人カレンダーカードを追加しない |
| 経済指標 | 米国の主要指標、日本時間、6件ずつページ送り |
| 相場 | 暗号資産とその他のマーケットを1つの一覧に統合。BTC/HYPEの重複なし |
| チャート | 24時間固定。小さなチャートと銘柄アイコンを付ける |
| 背景写真 | 外部取得を希望。現状はNYの同梱写真、Unsplash自動取得は接続待ち |
| アプリ | SmartTube / U-NEXT / Netflix / Prime Video / Disney+ / Spotify / 設定 |
| SmartTube | **見た目だけYouTubeアイコン**。名前・TVでの起動対象はSmartTube |
| 地デジ | ショートカット削除済み。TVのチューナー機能を無効化したわけではない |

削除済み：NY時間、市場オープンまでのカウントダウン、別カードのドル円・米国債、独立した暗号資産カード、マーケットの見出し・件数・24Hバッジ・カード内設定ボタン・接続状態フッター。再追加は新しいユーザー指示がある場合に検討する。

## 3. デザインとレイアウトの基準

Apple TV／最近のiOSを参考にした、クリアなガラス・細い時計・静かな区切り線・ロゴ中心のドック。背景が見える余白を重視する。ユーザーは、画面をカードで埋めること、相場を大きくしすぎること、銘柄別の独立タイル、ニュースとSpotifyの間の大きな空白、マーケットだけが上に浮く配置を指摘してきた。現在の構成で解消している。

1920×1080の基準座標。実装の正本は `dashboard/styles.css`。

| 領域 | X | Y | 幅 | 高さ |
| --- | ---: | ---: | ---: | ---: |
| 時計・日付 | 216 | 104 | 500 | 142 |
| 天気・時間別予報 | 216 | 270 | 500 | 286 |
| 米国経済指標 | 216 | 580 | 500 | 308 |
| マーケット | 844 | 270 | 860 | 432 |
| ニュース＋Spotify | 844 | 726 | 860 | 162 |

- 天気とマーケットの上端270px、経済指標とニュース・Spotifyの下端888px。
- 外周は左右216px・上48px・下36px。左列500px、右列860px、列間128px、カード同士は24px。
- 時計は独立した上段。時計右側の空間は意図的な余白。
- マーケットは1枚のパネル、2列×6段。アイコン28px、価格24px、小型チャート約78×30px。名前・チャート・価格を整列。
- ニュースとSpotifyは隣接。TVのニュース見出しは2行。
- ドックは中央に7ボタン、基準サイズ72px・間隔22px。選択時に浮き、上に名前のガラスラベルが出る。
- 横向きPCは1920×1080のステージを縮尺表示。1000px以下または縦画面は縦並び。640px以下の相場は1列×12段。
- 小画面のドックは横スクロール。矢印キーで選んだボタンも表示範囲へ移動する。
- ガラスは下地 `rgba(14,25,39,.14)`、縁 `#e5f3ff26`、角丸30px、ぼかし20px、彩度125%。文字 `#fafcff`、補助 `#dde7ee`、控えめな文字 `#b7c7d3`、上昇 `#77e6b9`、下落 `#ff92a5`。
- フォントはOutfit／Zen Kaku Gothic New。Google Fontsから取得し、失敗時はシステムフォント。フォントはローカル同梱していない。
- OSの動き・透明度を減らす設定、ぼかし非対応時の表示に対応。

## 4. 12銘柄と価格の意味

順序と対応は [market-definitions.js](dashboard/js/market-definitions.js) が正本。

| 表示 | Hyperliquid契約ID | 補足 |
| --- | --- | --- |
| SP500 | `xyz:SP500` | S&P 500参照の無期限先物 |
| BTC | `BTC` | native。USDT建て・USDC証拠金 |
| HYPE | `HYPE` | native。USDC建て・USDC証拠金 |
| JP225 | `xyz:JP225` | 日経225参照 |
| SOXL | `xyz:SOXL` | 半導体ブル3倍ETF参照。SILVERの代わり |
| XYZ100 | `xyz:XYZ100` | trade.xyz独自の米国非金融100銘柄指数。公式NDXと同一視しない |
| JPY | `xyz:JPY` | 米ドル／円。逆数にしない |
| DRAM | `xyz:DRAM` | DRAM契約。独自の推測換算をしない |
| GOLD | `xyz:GOLD` | 金。USD／トロイオンス |
| CL | `xyz:CL` | WTI原油。USD／バレル |
| 30Y | `para:30Y` | 米30年金利の契約価格。%・bpに独自換算しない |
| 10Y | `para:10Y` | 米10年金利の契約価格。%・bpに独自換算しない |

VIX・ダウ・SILVERは表示しない。現物指数やETFの市場価格そのものと取り違えない。

- 公開RESTとWebSocket。APIキー・ウォレット不要。
- 価格は `markPx`、24時間変化率は `(markPx / prevDayPx - 1) × 100`。
- チャートは直近24時間の実際の15分足終値。取引価格でありマーク価格の履歴ではない。現在足は途中の値。
- 点線は期間最初の足の始値。基準より上が緑、下が赤。欠損時間の線をつながず、古い終点を現在まで延ばさない。
- 公開メタデータで上場・非廃止を確認後、正確な契約を購読。正常中も5分ごとに再確認。廃止契約の残存価格を出さない。
- WebSocket正常時は最大毎秒描画。切断時は30秒ごとのHTTP取得。チャートは5分更新、最大3並列。
- 古い値は「更新待ち」や取得時刻で区別。価格は最大24時間、チャートは最大1時間のキャッシュ。
- 接続状態・注記・凡例はドックの「設定」内。`crypto-feed`、`stock-source`、`crypto-note`、`chart-legend`、`market-dot` のDOMを更新処理が参照するため維持する。
- CoinGeckoとTradingViewは代替・参考設定。通常はHyperliquidの自作表示。CoinGecko選択時はBTC/HYPEをUSD参考価格にしnativeの価格・履歴を混ぜない。TradingViewは別商品・別配信元であり全銘柄の配信を保証しない。

## 5. その他のデータと更新

| 機能 | データ元 | 更新・注意 |
| --- | --- | --- |
| 時計・日付 | 端末時刻 | Asia/Tokyo。1秒ごとの処理 |
| 天気・時間別予報 | Open-Meteo | 15分。渋谷区 `35.6589, 139.70665`。キー不要 |
| 空気 | Open-Meteo Air Quality | 30分。CAMSモデルの米国AQI。花粉は未対応 |
| 米国経済指標 | BLS・BEA公式ICS | 6時間。CPI、雇用統計、PPI、JOLTS、GDP、PCE |
| FOMC | FRB公式日程の保存JSON | 2026-10-18確認、2027年末まで。変更時は更新が必要 |
| ニュース | NHK経済RSS | 15分取得。3見出しを20秒で切り替え。48時間以上前の配信を明示 |
| Spotify | Currently Playing API | 30秒。実アカウント未接続 |
| 写真 | 同梱CC0写真／Unsplash | Unsplashは1時間に24枚取得、既定60秒で切り替え |

時間別天気は日本時間の次の正時から6時間。日付跨ぎ・昼夜・雨雪雷・降水確率・欠測に対応。気温の線の縦幅は最低6℃で、小変動を誇張しない。3時間超の予報は古い情報として表示。地域変更時に以前の地域の値を使い回さない。

経済指標は日付・名称・日本時間を6件表示し、ページ送りで先へ進める。夏時間・日付跨ぎを処理。行は公式日程へリンク。予想・実績値は未接続で、作り物を補わない。保存日程の期限はBLSが2026年12月、BEA・FRBが2027年12月。取得失敗時は配信元ごとに保存日程を使い、「一部更新待ち」を表示する。後日のセッションでは収録期限も確認する。

## 6. Spotify・Unsplashの接続

両方とも実キー／実認証は受領していない。ZIPに秘密情報やブラウザのセッション情報は含まれない。詳しい設定と公式リンクは [README.md](README.md)。

**Spotifyの再生情報カード**

1. Spotify Developer Dashboardでアプリを作成。
2. ローカル用Redirect URIを `http://127.0.0.1:4173/` に登録。ホスト・ポート・末尾 `/` を一致させる。
3. 画面の設定へClient IDを入力して連携する。サーバーの `SPOTIFY_CLIENT_ID` でも指定可能。
4. `user-read-currently-playing` の許可を受ける。Client Secretは使わない。

PKCE・state照合・10分の有効期限・トークン更新を実装。トークンはsessionStorageのみでタブ終了時に失われる。Spotify側の開発モード・ユーザー等の条件は実接続時に確認。ドックのSpotifyボタンはTVアプリ用で、カードのOAuthとは別機能。TVの初回ログイン方法は未設計。

**Unsplashの背景写真**

1. Unsplash Developersでアプリを作成しAccess Keyを取得。Secret Keyは不要。
2. `.env.local` がなければ `.env.example` をコピーし、サーバー側の `UNSPLASH_ACCESS_KEY` を設定。既存ファイルは必要な項目のみ編集する。
3. 再起動後「設定 → 背景写真 → Unsplashから自動取得」で保存。

APIが返す画像URLを直接表示し、撮影者とUnsplashへのリンクを付ける。API取得は写真切り替えごとではなく1時間単位。現状はLuca BravoのNY写真1枚を同梱CC0として表示。出典は [ATTRIBUTION.txt](dashboard/assets/ATTRIBUTION.txt)。将来スクリーンセーバー専用の配布・ダウンロード機能等を追加する場合、その用途のAPI条件を確認する。外部サービスの条件は将来変わりうる。

## 7. アプリドックとAndroid接続

Web版の順序：SmartTube（YouTubeの見た目）、U-NEXT、Netflix、Prime Video、Disney+、Spotify、設定。

- ロゴは `dashboard/assets/apps/` に同梱。[出典](dashboard/assets/apps/SOURCES.md)あり。表示のための外部画像リクエストは不要。
- 矢印キーで移動、Enterで決定、マウスを重ねても選択。名前のラベルと短い押下アニメーション。
- Web単独ではネイティブアプリを起動せず、その旨を表示する。インストール済みとは仮定しない。
- 接続口：`window.Android.getApps()` と `window.Android.launchApp(packageName)`。
- `getApps()` は `name` と `packageName` を持つ配列のJSON文字列。実機から得た妥当なパッケージ名を使う。
- 実一覧が返るとWebの固定ドックを置き換える。現在は **最大12アプリ＋設定**。実機の順序・ピン留め・固定ドックとの統合はフェーズ3で検討する。
- 表示名に対応する既知ロゴと未知アプリの頭文字表示に対応。起動するパッケージをロゴから推測しない。SmartTubeをYouTubeの起動先にしない。

フェーズ3の想定はKotlinの薄いランチャー＋WebView。`WebViewAssetLoader`等で安全なオリジンを用意する。従来の `addJavascriptInterface` はiframeにも公開されるため、現在はAndroidブリッジ検出中に外部TradingView iframeを無効化している。併用するならオリジン制限付きWebMessage API等で設計する。

## 8. 実行構成とファイルの役割

Node.js標準機能のサーバー＋HTML/CSS/ES Modules。React等への移行は依頼されていない。

```text
START_HERE.md                  次セッションの入口
HANDOFF.md                     現行仕様・確定事項・未対応
NEXT_SESSION_PROMPT.txt         次のチャットに貼る文章
README.md                      実行とデータ接続の詳細
AGENTS.md / CLAUDE.md           次のコーディング担当への指示
dashboard/                     編集する公開ソース
  index.html                   画面構造・ドック・設定
  styles.css                   TV/PC/スマホの配置とガラス表現
  js/app.js                    描画・状態・定期取得・設定の統合
  js/data.js                   初期設定・公開API・保存と入力検証
  js/hyperliquid.js             native/HIP-3、REST/WebSocket
  js/market-definitions.js      12契約の厳密な対応
  js/market-chart.js            24hチャート
  js/weather.js                時間別天気、欠測・古い情報の扱い
  js/calendar.js               日本時間の指標・ページ分割
  js/spotify.js                OAuth PKCE・トークン・再生中の曲
  js/slideshow.js              背景の先読み・切り替え
  js/launcher.js               Androidアプリのロゴ・押下演出
  js/navigation.js             D-pad・設定のフォーカス管理
  js/tradingview.js             参考ウィジェットの隔離
  data/                        公式日程の保存データ
  assets/                      背景・ロゴ・アイコンと出典
server.mjs                     dashboard配信と固定API
lib/economic-calendar.mjs      公式ICSの解析・日程の統合
dist/                          buildで再生成するWebView用静的成果物
scripts/                       ビルド・ブラウザ検証
tests/                         Node.jsの単体テスト
artifacts/                     最新画面・検証結果
references/                    ユーザー提供の3枚の参考画像
mockups/                       初期HTML/PNG。最新画面の正本ではない
docs/HANDOFF_HISTORY.md         初期相談からv0.5.5までの履歴
PACKAGE_INFO.json              今回の引き継ぎパッケージ情報
MANIFEST.sha256                ZIP内のファイル完全性確認
```

`npm run dev` は `dashboard/` を配信。`npm run build` はJS構文を確認して `dist/` を作り直す。**編集はdashboard側で行う**。`dist/`だけの変更は次回ビルドで失われる。

相場・天気は主にブラウザから取得。ニュース・カレンダー自動更新・UnsplashはNodeサーバーを使う。`dist/`だけの静的ホスティングでは全サーバー機能は動かない。ファイルのダブルクリックでもES Modules/APIは動かないためHTTPで配信する。

設定はlocalStorageの `tv-home-config`、取得データは `tv-cache:` キーへ保存。Spotify認証はsessionStorageの `tv-spotify-auth`／`tv-spotify-session`。ブラウザ保存内容はZIPに含まれず、別ブラウザ・別オリジンへ自動移行しない。

`MARKET_DATA_URL`／`MARKET_DATA_TOKEN`、旧 `/api/market`・為替・金利APIや市場時計のファイルは互換性と既存テストのため残っている。現在の相場一覧の取得元ではなく、削除済みカードを戻すための指示でもない。

## 9. 起動・検証コマンド

```sh
cd tv-home-handoff
npm run dev
```

`http://127.0.0.1:4173/` を開く。終了はCtrl+C。設定項目は `.env.example` を参照。

```sh
npm test
npm run build
```

同じLANのスマホから開くなら `HOST=0.0.0.0 npm run dev` としてPCのLANアドレスへ接続する。Spotify認証にはHTTPSまたは明示的なループバックIPが必要で、LAN内HTTPでは同じ条件にならない。クラウドの127.0.0.1へ手元のスマホから直接つながるわけではない。

プロキシが必要なNode.js 24環境では、注入済み環境変数を保って `NODE_USE_ENV_PROXY=1 npm run dev`。TLS検証を無効にしない。新環境のネットワーク・認証状況はその環境で確認する。

PlaywrightとChromiumがある場合の任意検証。別ターミナルでサーバーを起動してから実行する。

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-check.mjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-integrations-check.mjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-market-check.mjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-weather-check.mjs
```

実施環境のパスは `/opt/codex/cua_node/lib/node_modules/playwright/index.mjs` と `/usr/bin/chromium`。別環境での存在は保証しない。これらのブラウザツールはZIPに含まれない。実APIを使うブラウザ検証は配信元・ネットワークに依存する。

## 10. 検証結果とその範囲

- **v0.5.5の実APIと表示・操作の検証**：[browser-check.json](artifacts/browser-check.json)。12契約の実価格・WebSocket・24h履歴、6時間の実予報、経済指標のページ送り、設定、通信断キャッシュ、ドックを確認。
- 画面サイズは1920×1080、1366×768、768×1024、660×1000、390×844、320×720。横方向のページはみ出しなし。小画面でも全7ボタンに移動できる。
- 最新実行ではBLS/BEAのライブ取得成功、FRBは保存日程。過去のBEA取得失敗時も保存日程と「更新待ち」を確認している。
- **v0.5.5の制御レスポンス検証**：[integration-check.json](artifacts/integration-check.json)。Spotify PKCE正常系・不正state、背景切り替え、Androidブリッジのロゴと渡された起動先、13ボタンのスクロール、動きの軽減を確認。実認証や実機の検証ではない。
- [weather-check.json](artifacts/weather-check.json) はv0.5.0の記録。夜・欠測・日付跨ぎ・地域変更等の制御レスポンス検証。
- [market-check.json](artifacts/market-check.json) はv0.4.0の記録。廃止・切断・古い値・ソース切り替えの制御レスポンス検証。
- 単体テストは38件。過去のアプリ検証は [verification.json](artifacts/verification.json)、今回のクリーンなコピーからのテスト・ビルド・ローカル配信確認は [handoff-check.json](artifacts/handoff-check.json) を参照。
- 今回の梱包確認は別の記録として保存し、ブラウザ検証の日時を今回実施したかのように書き換えない。

スクリーンショットの価格・時刻は撮影当時の実データ。現在価格の保証や固定表示のサンプルではない。

## 11. 未完了と次の作業候補

| 項目 | 現状 | 必要になったときの次の行動 |
| --- | --- | --- |
| TV型番・OS | 未確認 | 型番、Google TV/Android TV/PatchWall、WebView/Androidの版を確認 |
| 作業端末と接続経路 | 未確認 | PC利用可否、スマホ/Termux、同一LAN・ADB接続を確認 |
| APK | 未作成 | Kotlin/WebView、ランチャー宣言、アプリ列挙と起動、リモコン・戻る・復帰を実装 |
| サーバー運用 | ローカルのみ | TVから届くNodeの配置とHTTPSを決める。静的配信だけでは全API機能を維持できない |
| Spotify | フロー実装、実認証なし | Client ID・リダイレクト先・利用ユーザーを設定し実接続 |
| Unsplash | フロー実装、実キーなし | サーバーにAccess Key設定、実画像切り替えとクレジット確認 |
| TVでの認証・保存 | 未設計 | 初回ログイン・長期保存・端末間の受け渡しを設計 |
| 性能と実機表示 | ブラウザで検証 | 文字サイズ、オーバースキャン、ぼかし負荷、スリープ復帰、長時間稼働を測定 |
| 個人写真・スポーツ・予定追加 | 現在の要件にはない | 新たに希望された場合だけ検討 |
| スクリーンセーバー | 将来の任意フェーズ | DreamService等。未着手 |

次の優先作業はまだ指定されていない。この一覧は残作業の説明であり、すべてを直ちに開始する指示ではない。フェーズ3や実認証へ進む段階で、その作業に必要な未確認事項だけ聞く。

## 12. 次の担当者への注意

- UIの基準は最新PNGと現在のコード。過去モックへ戻したり、余白へ新しいカードを埋めたりしない。
- 接続情報がない部分は必要な情報を明示する。実接続・実機確認・公開を済ませたことにしない。
- 仮価格・架空チャート・推測の指標値を本番表示に加えない。テストの制御レスポンスと実データの証拠を分ける。
- キーやトークンを `dashboard/`・`dist/`・ZIP・スクリーンショットへ含めない。秘密情報はサーバー側で管理する。
- 現在はTVのシステム設定を変更していない。システムアプリの無効化は対象と影響を説明してユーザーに確認してから行う。Google Play開発者サービス・システムUI・チューナー関連を安易に止めず、標準ランチャーは代替の動作確認前に無効化しない。
- 引き継ぎ作成の依頼を、TV変更・デプロイ・インストールの許可とみなさない。
- この環境ではSites公開ヘルパーがなく未公開だった。次の環境も同じとは限らない。localhostを外部公開URLとして案内しない。
- レイアウト変更時は文字・価格・チャート・選択ラベルの衝突と複数画面幅を確認。完成形の意図を保つ小さな修正を優先する。

## 13. 同梱内容とファイルの完全性

ソース、ビルド済みdist、サーバー、テスト、実行スクリプト、設定例、出典、最新画面、検証記録、ユーザー提供画像3枚、初期モック、履歴を同梱。秘密設定・ブラウザセッション・外部ブラウザ実行環境は含まない。

展開後のプロジェクト直下で `sha256sum -c MANIFEST.sha256` を実行すると、欠損・変更を確認できる。manifest自身は対象外。ソース編集後にハッシュが変わるのは正常。

次のチャットにはZIPを添付し、[NEXT_SESSION_PROMPT.txt](NEXT_SESSION_PROMPT.txt) の文章を貼ればよい。
