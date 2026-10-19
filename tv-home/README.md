# TV Home — フェーズ2 Webダッシュボード

次セッションへの引き継ぎは [START_HERE.md](START_HERE.md) から。現行仕様と未対応事項は [HANDOFF.md](HANDOFF.md)、最新の見た目は [プレビュー](artifacts/dashboard-desktop.png) を参照してください。v0.6.0でApple／iOSの考え方に沿ってデザインを刷新しました（配置と内容はv0.5.5のまま）。デザインの基準は `HANDOFF.md` 第3節です。

`HANDOFF.md` のフェーズ2を実装した、ビルド不要のHTML/CSS/JavaScript＋小さなNode.jsデータサーバーです。時計・天気・経済指標を左、マーケット・ニュース・Spotifyを右にまとめ、Apple TV／iOSのクリアなガラス素材・Inter＋Noto Sans JP・iOSのシステムカラーで統一しています。

## 現在の仕様（v0.9.0）

- **TV専用（v0.9.0）**：スマホ・縦画面用の配置をやめ、1920×1080の画面1枚だけにしました。設定・詳細シート・通知もその画面の中に入り、TVの解像度（WebViewが報告する960×540など）に合わせて全体が一緒に縮尺されます。シートはソファから読めるよう1.25倍。詳細は `HANDOFF.md` 第3.3節。

- **リモコン操作の改善（v0.8.0）**：自然な移動と戻り、経済指標のページ送り、決定で詳細を表示（相場・経済指標・ニュース・データの状態）、設定画面をリモコンだけで操作可能に。詳細は下の「操作」と `HANDOFF.md` 第3.2節。

- **広告ブロック（v0.7.0）**：設定に「広告ブロック」を追加。TVで広告が遮断されているかを確認でき、手順は下の「広告ブロック」にあります。フェーズ3のAPKでは、AdGuard DNSへの切り替えをスイッチ1つで行えます。

- **TV向けの軽量化（v0.6.1）**：カードのぼかしを写真ごとに1回だけ作る方式に変え、常時動くアニメーションをなくし、毎秒の処理を変化した部分だけにしました。計測では待機中のChromium CPUが103%→3%、描画は13fps→60fps。ゆっくりズームは初期設定オフです。詳細は `HANDOFF.md` 第3.1節、計測は `scripts/perf-bench.mjs`。

- **v0.6.0のデザイン刷新**：Apple Weather型の天気、Apple株価アプリ型の相場、カテゴリー色付きの経済指標、iOSの連続曲線アイコンとtvOS型のフォーカス、iOS型の設定画面。TVで読めるよう最小文字を12pxに。正常時は状態表示を出さず、更新待ちのときだけ琥珀色で表示。詳細は `HANDOFF.md` 第3節。
- **ニュース配信元を修正**：旧 `www3.nhk.or.jp` のRSSは2026-08-08で更新が止まっていたため、NHK ONE（`news.web.nhk`）の経済RSSへ切り替えました。

- **朝・夜とも同じフル版**。渋谷区の天気、Spotify。スポーツ欄なし。
- **6時間先までの時間別天気**。時刻、昼夜に合った天気アイコン、気温のライン、降水確率と小さなバーを、現在の天気と同じガラスカードに表示。
- アプリ列は **SmartTube / U-NEXT / Netflix / Prime Video / Disney+ / Spotify / 設定**。画面下の中央に、ロゴだけの角丸ボタンを並べています。**SmartTubeはユーザー指定でYouTubeのアイコン**を使い、表示名と起動先はSmartTubeのままです。地デジはありません。
- NY時間・取引開始カウントダウン・重複するドル円/米国債の日次カードは撤去。**米国主要経済指標カレンダー**に置き換えています。
- **Apple TV / iOSを参考にしたクリアなガラス調UI**。パネルの白い曇りと暗い色を薄くし、背景のぼかしを30pxから20pxへ調整。選択したアプリはブランドの色を保って少し浮き上がり、その上に名前が現れます。ぼかし非対応端末やOSの透明度軽減設定では不透明な背景へ切り替えます。
- **12銘柄を1つの一覧に統合**。SP500 / BTC / HYPE / JP225 / SOXL / XYZ100 / JPY / DRAM / GOLD / CL / 30Y / 10Y。ダウの枠はSOXL、VIXの枠はDRAM。
- **全12銘柄の価格と24時間チャートをHyperliquidから取得**。BTC・HYPEはnative、その他はHIP-3。APIキー・ウォレット不要。
- 相場は右側の**1枚のガラスパネル**に集約。2列×6段の一覧で、銘柄ごとの背景や枠はありません。接続状態・取得銘柄数・価格とチャートの説明は設定へ移し、見出し・件数・24Hバッジ・カード内の設定ボタンも外し、TV版のパネルは860×432px。価格とチャートのサイズは維持しています。
- **時計は上段、情報カードはその下**という構成。天気とマーケットの上端をそろえ、左は天気＋経済指標、右はマーケット＋ニュース・Spotifyを配置。下の3枚も下端をそろえています。余白は時計の右側・外周・列間に残しています。
- 追加の予定カードは置きません。米国経済指標を6件ずつ表示し、先の主要な発表も見渡せます。
- 期間は**24時間固定**。実際の15分足から作る小型チャートと、銘柄ごとのアイコンを表示します。
- 個人の写真は使わず、出典付きのNY写真を同梱。Unsplashの自動取得に切り替えられます。

## 起動

Node.js **22.9以降**（検証環境は24.19）。外部npm依存関係はありません。

```sh
cd tv-home-handoff
npm run dev
```

ブラウザで **http://127.0.0.1:4173/** を開きます。終了は `Ctrl+C`。

同じLANの別の端末（TVのブラウザなど）からPCのサーバーに接続する場合：

```sh
HOST=0.0.0.0 npm run dev
```

その端末で `http://<PCのLAN内IP>:4173/` を開きます。画面はTV専用なので、縦長の画面では1920×1080の画面がそのまま縮小表示されます。**Spotify認証はHTTPSまたは明示的なループバックIPが必要**なので、LANのHTTP表示だけでは認証できません。クラウド実行環境の127.0.0.1は手元の端末から直接開けません。

HTTPプロキシが必要なNode.js 24環境では、継承したプロキシ変数を保持して `NODE_USE_ENV_PROXY=1 npm run dev` とします。TLS検証を無効化する必要はありません。

## データと更新

| 項目 | 配信元 / 更新 | 表示の意味 |
|---|---|---|
| 12銘柄の価格 | Hyperliquid / WebSocket、描画は最大毎秒 | 各無期限先物のマーク価格。切断・停滞時は30秒ごとのHTTP取得 |
| 各銘柄のチャート | Hyperliquid `candleSnapshot` / 5分 | 直近24時間の15分足終値。現在足は途中の値 |
| BTC・HYPEの代替ソース | CoinGecko / 2分 | 設定で選択可能。USD参考価格。この場合BTC・HYPEのチャートは未接続表示 |
| 天気・6時間予報・日の出/入 | Open-Meteo / 15分 | 渋谷区のモデル予測。気温（℃）、天気コード、降水確率（%）、明日の最高/最低 |
| 空気 | Open-Meteo / 30分 | CAMSモデルの米国AQI。日本の花粉は未対応 |
| 米国経済指標 | BLS・BEA公式ICS / 6時間 | CPI、雇用統計、PPI、JOLTS、GDP、PCE。日本時間で表示 |
| FOMC | FRB公式2026〜2027年カレンダー | 通常の14:00 ETを予定時刻としてJST変換。2026-10-18確認。日程変更時はJSON更新 |
| ニュース | NHK ONE 経済RSS / 15分 | 見出し3本を20秒で切替。48時間以上前の配信を明示 |
| Spotify | OAuth PKCE / 30秒 | Client IDとユーザー認証が必要。実アカウントは未検証 |
| 背景 | 同梱CC0写真 / Unsplash API | キー設定後24枚を1時間ごとに取得、既定1分で切替 |
| アプリ一覧 | Android JS Bridge | Web版のアプリ起動は未対応。APK接続はフェーズ3 |

### 時間別天気

現在の天気・日別予報と同じOpen-Meteoリクエストに、時間別の `temperature_2m`、`weather_code`、`is_day`、`precipitation_probability` を追加しています。APIキーは不要です。

日本時間で**次の正時から6時間分**を表示し、時刻が進むと表示対象も自動で繰り上がります。日付をまたぐ最初の時刻は「明日 0時」のように表示。アイコンは晴れ・夜の月・晴れ時々くもり・くもり・雨・雪・霧・雷雨を区別します。降水確率は数値と短いバーで示し、40%以上を青で強調します。降水量や雨の確定情報ではありません。

気温の線は取得値をそのまま使い、小さな変動を誇張しないよう縦方向の幅を最低6℃にしています。欠けた気温は「—」として線を切り、降水確率の欠測も0%に置き換えません。時刻の欠測によって隣の時間を詰めることもありません。データがない場合は未取得表示です。

取得失敗時は最大24時間の保存済み天気を利用し、「保存した予報・更新待ち」と表示します。取得時刻または現在気象の参照時刻が3時間を超えて古くなった場合も更新待ちに変わります。地域変更時は古い地域の予報を消し、新しい地域を取得します。日本時間の扱い、日跨ぎ、欠測、古いキャッシュをテストしています。

参考：[Open-Meteo Forecast API](https://open-meteo.com/en/docs)

### 銘柄の対応

| 画面 | Hyperliquidの契約ID | 名称・単位 |
|---|---|---|
| SP500 | `xyz:SP500` | S&P 500を参照する無期限先物、指数ポイント |
| BTC | `BTC` | Bitcoin、USDT建て・USDC証拠金 |
| HYPE | `HYPE` | Hyperliquid、USDC建て・USDC証拠金 |
| JP225 | `xyz:JP225` | 日経225を参照する無期限先物 |
| SOXL | `xyz:SOXL` | 半導体ブル3倍ETFを参照する無期限先物 |
| XYZ100 | `xyz:XYZ100` | trade.xyz独自の米国非金融100銘柄指数。公式NDXと同一視しない |
| JPY | `xyz:JPY` | 1米ドルあたりの円。逆数に変換しない |
| DRAM | `xyz:DRAM` | DRAM契約。詳細な参照対象を推定した換算はしない |
| GOLD | `xyz:GOLD` | 金、USD / トロイオンス |
| CL | `xyz:CL` | WTI原油、USD / バレル |
| 30Y | `para:30Y` | 米30年金利の契約価格。そのまま表示し%やbpに換算しない |
| 10Y | `para:10Y` | 米10年金利の契約価格。そのまま表示し%やbpに換算しない |

2026-10-18 UTCに公開メタデータ・価格・ローソク足・WebSocketを確認。これらは**現物指数・ETF・スポット相場そのものではありません**。銘柄IDと名前は `dashboard/js/market-definitions.js` に明示し、曖昧な文字列検索や別商品の自動代入はしません。VIXは上場廃止扱いだったため、残存価格を表示しません。

### 価格、変化率、チャート

価格は `markPx`、変化率は `(markPx / prevDayPx - 1) × 100`。通貨換算はしません。行のツールチップとアクセシブル名に正確な契約ID、単位、受信時刻を含め、全体の注記に無期限先物であることを表示します。

チャートは取引価格の履歴で、マーク価格の履歴ではありません。15分足の終値（現在足は途中の値）を時刻に沿って配置し、点線には期間最初の足の始値を使います。基準より上は緑、下は赤。欠けた足はつながず、最後の足が古い場合も現在時刻まで引き延ばしません。薄商いで最終足が古い銘柄は「○○:○○まで」を表示します。チャートは12件を最大3並列で取得し、5分間キャッシュします。

公開 `metaAndAssetCtxs` で各デプロイヤーの実在・上場状態を確認してから `activeAssetCtx` を購読します。正常なストリーム中も5分ごとに上場状態を再確認。上場廃止・消えた銘柄の価格とチャートは消し、購読を解除します。静かな1銘柄によって他銘柄の接続を切らない設計です。

全対象の価格が新しく、購読した全銘柄を20秒以内に受信している場合のみLIVE表示。Hyperliquidの更新が90秒止まると「更新待ち」に変わります。APIの受信頻度は配信元の価格遅延を保証するものではありません。非表示タブでは新規取得とWebSocketを止めます。

通信障害時は取得済み価格を最大24時間保持し、更新待ちを表示。履歴は最大1時間、経済指標カレンダー・写真は7日間まで保存値を利用します。エラー時は再試行を遅らせます。CoinGecko選択時のBTC・HYPEにはHyperliquidの価格やチャートを混ぜません。ドル円・金利はウォッチリスト内だけに表示します。

参考：[Info / Perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals) / [WebSocket](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions) / [Native契約仕様](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications) / [trade.xyz契約仕様](https://docs.trade.xyz/perpetuals/specifications-and-schedules/specification-index)

### 米国経済指標カレンダー

BLSとBEAの公式カレンダーをサーバーで6時間ごとに確認し、FRBの確認済みFOMC日程と統合します。CPI・雇用統計・PPI・JOLTS・GDP・PCE・FOMCに絞り、次の6件を日付・指標名・発表時刻の3列で表示。下の矢印で後の予定へ移動でき、行を選ぶと公式日程を開きます。**時刻はすべて日本時間**。米国夏時間と、日付が翌日になる発表に対応しています。予想・実績の数値は未接続です。

予定の取消・変更、同時刻の複数指標を区別します。一部の配信元が取得できない場合は他の配信元を維持し、確認済みスナップショットに切り替えた旨を表示します。静的配信だけの場合も `data/economic-calendar.json` の日程を表示できますが、自動更新にはNodeサーバーが必要です。

同梱日程の確認日は2026-10-18 UTC。BLSは2026年12月まで、BEAとFOMCは2027年12月までの公表済み日程を収録。BLS/BEAは新しい公式配信に追従します。FOMCの変更はスナップショット更新が必要です。収録期間を過ぎた配信元は更新待ちを明示します。公式日程は変更される場合があります。

参考：[BLS Calendar](https://www.bls.gov/schedule/) / [BEA Calendar](https://www.bea.gov/news/schedule) / [FRB FOMC](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)

### アイコンと参考ウィジェット

10銘柄のアイコンはHyperliquidの公開銘柄画像。30Y・10Yは独自作成した一般的な国債アイコンです。出典は `dashboard/assets/markets/SOURCES.json`。名称・商標は各権利者に帰属します。

設定にはTradingViewの参考表示も残しています。**こちらは別の配信元・商品であり、HIP-3契約の価格を表示するものではありません**。配信の可否と遅延は銘柄ごとに異なります。外部スクリプトはアプリとは別オリジンのsandbox付きiframe内だけで動きます。従来のAndroidブリッジ検出中は無効です。通常はTV Home / Hyperliquid表示を使ってください。

旧 `MARKET_DATA_URL` / `/api/market` 接続口は互換性のためサーバーに残していますが、現在の12銘柄表示には使用しません。

### Spotify

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) でアプリを作成します。
2. Redirect URIに `http://127.0.0.1:4173/` を登録します。ホスト・ポート・末尾 `/` まで一致させます。
3. 設定画面に**Client ID**を入力し、「保存してSpotifyを連携」を押します。`SPOTIFY_CLIENT_ID` 環境変数による設定も可能です。
4. Spotifyで `user-read-currently-playing` を許可します。再生中の曲・アーティスト・ジャケット・進捗を表示します。

Client Secretは使用しません。PKCEのstate照合・10分の有効期限・リフレッシュ処理を実装しています。トークンはブラウザの**sessionStorageのみ**に保存し、タブを閉じると失われます。端末をまたぐ連携はしません。アプリの開発モード・利用ユーザー・プランはSpotify側の現行条件に従います。再生操作やSpotify以外のアプリの再生情報は扱いません。

参考：[Authorization Code with PKCE](https://developer.spotify.com/documentation/web-api/tutorials/code-pkce-flow) / [Redirect URI](https://developer.spotify.com/documentation/web-api/concepts/redirect_uri)

### 写真：Unsplashを第一候補にした理由

NYなど都市風景の検索、横長指定、撮影者情報を取得でき、50リクエスト/時のデモ枠でも1時間ごとの24枚取得に十分です。**写真の表示切替とAPI取得は別**で、1分ごとにAPIを叩きません。APIが返した画像URLを直接使用し、撮影者・Unsplashへのリンクを常時表示します。

Pexelsも候補ですが、APIドキュメントには壁紙アプリを含むコア機能の再現の制限があります。今回の情報ダッシュボードにはUnsplashを第一候補とし、将来スクリーンセーバー専用アプリにする際はその用途で改めて条件を確認します。Wikimedia Commonsはキー不要の代替候補ですが、写真ごとにライセンスとクレジット形式が異なります。

接続に必要なものは **UnsplashアカウントとAccess Key** です。Secret Keyや写真の手動選択は不要です。

1. [Unsplash DevelopersのYour apps](https://unsplash.com/oauth/applications) にログインし、**New Application** でアプリを作成します。アプリ名（例：TV Home）と、NYの写真を背景に表示する個人用情報ダッシュボードである旨を入力します。
2. アプリのKeys欄から **Access Key** を取得します。キーはチャットに貼らず、サーバーの設定ファイルに入力してください。
3. プロジェクト直下に `.env.local` がなければ `.env.example` をコピーし、次を設定します。既存ファイルがある場合はこの行だけ編集します。

   ```dotenv
   UNSPLASH_ACCESS_KEY=取得したAccess_Key
   ```

4. サーバーを再起動（`npm run dev`）し、画面の **設定 → 背景写真 → Unsplashから自動取得 → 設定を保存** を選びます。設定画面に「APIキー設定済み」と表示されます。

デモモードは50リクエスト/時。現実装はNYの横長写真を24枚まとめて1時間ごとに検索し、取得した写真を初期設定で1分ごとに切り替えます。画像CDNへのアクセスはAPI回数に含まれません。本番利用へ進める場合はUnsplashのProduction申請条件を確認してください。実キーでの接続はまだ検証していません。

キー未設定・取得失敗時は保存済み写真、または同梱写真を表示します。画像URLの直接利用と撮影者/Unsplashへのリンクは実装済みです。手動ダウンロード・壁紙への保存機能はありません。追加する場合はUnsplashのdownload tracking要件も実装してください。

参考：[Unsplash API](https://unsplash.com/documentation) / [Pexels API](https://www.pexels.com/api/documentation/) / [同梱写真のライセンス](dashboard/assets/ATTRIBUTION.txt)

### 広告ブロック

TV Home自体には広告がありません。TV全体の広告とトラッカーは、Androidの**プライベートDNS**に [AdGuard DNS](https://adguard-dns.io/) を設定して遮断します。広告配信ドメインの名前解決に `0.0.0.0` を返す仕組みで、アプリの追加は不要です。2026-10-19に、AdGuard DNSが広告ドメインを遮断し、このダッシュボードの配信元（Open-Meteo・NHK・Hyperliquid・Spotify・Unsplash・BLS/BEA）とドックのアプリ（YouTube・Netflix・Prime Video・Disney+・U-NEXT）の主なドメインは遮断しないことを確認しました。

**効果を確認する**：画面の **設定 → 広告ブロック → 確認する**。広告配信ドメインに接続できるかだけを調べ、「広告ブロック 有効／無効」を表示します（内容は読み込まず、Cookieも送りません）。

**設定する（どれか1つ）**

1. **TVの設定画面**：設定 → ネットワークとインターネット → プライベートDNS に `dns.adguard-dns.com`。Google TVでは項目がない機種が多く、その場合は次の方法を使います。
2. **PCからADB**（TVの設定をコマンドで変更します。システムアプリの無効化はしません）
   1. TVの設定でデバイス情報の「ビルド」を7回押して開発者向けオプションを出し、USBデバッグまたはワイヤレスデバッグをオンにする。
   2. 同じWi-FiのPCで `adb connect <TVのIPアドレス>`（ワイヤレスデバッグは先に `adb pair`）。TVに出る確認を許可する。
   3. 次を実行する。

      ```sh
      adb shell settings put global private_dns_specifier dns.adguard-dns.com
      adb shell settings put global private_dns_mode hostname
      ```

   元に戻すときは `adb shell settings put global private_dns_mode opportunistic`（Android標準の「自動」）。
3. **ルーター**：DNSを `94.140.14.14` / `94.140.15.15`（AdGuard DNS）にする。家の全端末に効きます。

**フェーズ3のAPK**では、設定画面の「TV全体で広告をブロック」スイッチ1つで切り替えられるようにします（Web側は実装済み、`HANDOFF.md` 第7節）。

**できないこと**
- YouTubeの広告は動画と同じドメインから届くためDNSでは消えません。ドックのSmartTubeが広告を除去します。
- Prime Videoの広告付きプラン、Netflixの広告付きプラン、Spotify無料版の広告は、動画・音声そのものに組み込まれているため消せません。無理に遮断すると再生できなくなることがあります。
- アプリやサイトが動かなくなったら、上の「元に戻す」でAndroid標準に戻してください。
- 遮断する範囲を変えたい場合は [NextDNS](https://nextdns.io/) なども使えます。設定の「DNSサーバー」にホスト名（例：`xxxxxx.dns.nextdns.io`）を入れます。

## 操作

TVのリモコン（↑↓←→・決定・戻る）で全部操作できるように作っています。PCでは矢印キー・Enter・Escが同じ役割です。

- **移動**：画面はブロック（上部ボタン・相場・経済指標・ニュース・Spotify・アプリ・写真）に分かれ、矢印はまずブロックの中を動き、端で隣のブロックへ移ります。来た方向へ戻ると元の場所に戻ります（例：Netflixで↑→ニュース→↓でNetflix。SmartTubeで↑→経済指標の最後の行→↓でSmartTube）。アプリの列より下には行きません。
- **経済指標**：↓で予定を順に見られ、最後の行の先で次のページ、最初の行の上で前のページに切り替わります。
- **決定（OK）**：相場の行は24時間の大きなチャート・高値／安値・契約・単位・受信時刻、経済指標は米国東部時間と発表元、ニュースは要約、「一部更新待ち」はどのデータが待っているかを表示します。TVを離れるリンクは開かず、PCのブラウザでだけ「公式日程を開く」などのボタンを出します。
- **戻る**：開いている画面を閉じます。ホームではアプリの列（最後に選んだアプリ）に戻ります。1分操作がないときも同じ位置に戻り、選択の光が画面に残り続けません。
- **設定**：↑↓で全項目を上から順に移動できます（プルダウンや入力欄で止まりません）。プルダウンは決定で選択肢を開き、スイッチは決定で切り替わります。
- 写真が1枚だけのときは「写真を切り替え」を出しません。TVアプリでは全画面ボタンも出しません。
- 地域検索とSpotifyの初回認証はPCのブラウザで行う想定です（画面はTV専用で、スマホでは縮小表示になります）。TVでのテキスト入力・認証方法はフェーズ3で設計します。
- 画面は1920×1080の1枚だけ（TV専用）。TVの解像度に合わせて全体を縮尺し、ページはスクロールしません。左右216px・上48px・下52pxの余白。左列500px、右列860px、列間128px。カード同士は24px間隔。
- OSの「視差効果を減らす」設定に対応。背景のゆっくりズームは初期設定オフで、設定でオンにできます（TVでは描画の負荷が増えます）。

## 検証・ビルド

```sh
npm test
npm run build
```

`dist/` はHTML/CSS/ES Modules/写真だけです。APIキー・`.env.local`は含みません。HTMLのファイル直開きではES Modules/APIが動かないため、HTTPで配信してください。

ブラウザテストは任意です。実行する環境にPlaywrightとChromiumがある場合：

```sh
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-check.mjs
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-integrations-check.mjs
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-market-check.mjs
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-weather-check.mjs
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs CHROMIUM_PATH=/path/to/chromium node scripts/browser-ux-check.mjs
```

`browser-check.mjs` は4K・1366×768・1280×720・960×540（Google TVのWebViewで一般的な値）で、画面全体と設定シートが一緒に縮尺されることを確認します。`browser-ux-check.mjs` はリモコン操作を1920×1080と960×540（2倍密度）で確認します。

動作の重さを比べるときは、サーバーを起動したまま次を実行します（Linuxでは描画を含むChromium全体のCPUも表示）。第3引数はCPUの低速化倍率で、`4` にすると非力な端末に近づきます。

```sh
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs node scripts/perf-bench.mjs http://127.0.0.1:4173/ 20 1
```

通常のブラウザ検証には天気・Hyperliquid・BLS・BEAへのネットワーク接続が必要です。結果とスクリーンショットは `artifacts/` に保存します。Hyperliquidは実際のREST取得とWebSocket更新も確認しました。切断/再接続・HTTPフォールバック・上場廃止・古い値の表示・CoinGeckoへの切替は制御したレスポンスで検証しています。地域検索、SpotifyのOAuth成功/不正state、写真切替、Androidブリッジ、広告ブロックの判定もテスト用レスポンスで検証しています。単体テストは47件。天気の夜間・降水・欠測・日跨ぎ・通信障害・地域変更は専用のブラウザ検証でも確認しています。12契約すべての実データ価格・チャートと、実データ6時間予報を確認しています。Spotifyの実アカウント認証・Unsplashの実キー・TV実機は未検証です。

## ファイル構成とフェーズ3

```text
dashboard/             WebViewに同梱する公開ファイル
  index.html           画面構成
  styles.css           TV画面（1920×1080）のスタイル
  js/app.js            描画・更新・設定・UI統合
  js/data.js           公開API、キャッシュ、銘柄、設定
  js/weather.js        日本時間の6時間予報、天気アイコン、気温と降水確率の描画
  js/hyperliquid.js     native / HIP-3の価格と履歴、公開REST/WebSocket
  js/market-definitions.js  正確な12契約ID・表示名・単位
  js/market-chart.js    時刻と欠損を保つ24時間の小型チャート
  js/calendar.js       日本時間の日付と今後の指標のページ分割
  js/market-clock.js   米東部時間のタイムゾーン計算
  js/navigation.js     D-padとダイアログのフォーカス管理
  js/launcher.js       Androidアプリのロゴ・名前・押したときの動き
  js/spotify.js        PKCE認証、トークン更新、再生情報
  js/slideshow.js      2レイヤーのプリロード・フェード
  js/tradingview.js    外部オリジンに隔離した公式埋め込み
  data/events.json     確認済みFOMC原本
  data/economic-calendar.json  公式配信から作成した保存用日程
  js/feeds.js          ニュースと経済指標の取得・解析（サーバーとTVアプリで共用）
  js/economic-calendar.js  BLS/BEAのICS解析、取消・変更と時刻の処理
android/               TVアプリ（ホーム画面）。ビルドと入れ替えはHANDOFF第3.4節
lib/economic-calendar.mjs  dashboard/js/economic-calendar.js の再エクスポート
server.mjs             静的配信と固定APIのサーバー処理
tests/                 時刻・取得失敗・RSS/CSV・秘密ファイル保護のテスト
scripts/               静的ビルドと任意のブラウザ検証
```

APK側で `window.Android.getApps()`（JSON）と `launchApp(packageName)` を公開すると、実機のアプリ一覧に置き換えられる接続口があります。

既知の表示名にはWeb版と同じロゴを使い、それ以外は頭文字を表示します。起動先はブリッジから返されたパッケージ名だけを使用し、アイコンから推測しません。アプリが多い場合は横スクロールし、矢印キーで選択中のボタンを表示範囲内へ移します。ロゴの出典は `dashboard/assets/apps/SOURCES.md` に記載しています。

```json
[{"name":"Netflix","packageName":"com.netflix.ninja"}]
```

ネイティブ実装・APK・ADB操作はまだ行っていません。`WebViewAssetLoader` などでWeb側を安全なオリジンから配信し、許可したメインフレームだけにブリッジを公開してください。Androidの従来の `addJavascriptInterface` はiframeにも公開されるため、**外部iframeからブリッジに触れないよう、TradingViewと併用する場合はオリジン制限付きのWebMessage API等に変更する必要があります**。従来ブリッジ（window.Android）を検出した場合、本実装はTradingViewを無効化し自作表示に戻します。別オリジンiframeだけではAndroidのブリッジ制限にはなりません。

端末型番、PC/スマホ開発ループ、SpotifyのTV上の認証方法は未決定です。TVのシステムアプリの変更はありません。

## ホスティング

今回の環境ではSitesの公開用ヘルパーが提供されておらず、Sitesへの登録・公開は行っていません。実装は通常のNode.jsサーバーで動作します。静的な `dist/` だけを配信する場合、ニュース・カレンダーの自動更新・Unsplashには別途サーバーが必要です。12銘柄のHIP-3価格と履歴はブラウザから取得します。設定の「別サーバーのURL」で接続できますが、そのサーバーにはHTTPSと配信元に限定したCORS設定が必要です。
