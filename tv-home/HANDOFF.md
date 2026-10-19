# TV Home 引き継ぎ書 — v0.23.0

引き継ぎ日：2026-10-19（夜）。対象：Xiaomi TV（65インチ、MiTV-MZTU0、Google TV／Android 14）の自作ホーム画面「TV Home」。

**テレビのホーム画面は、もうこのアプリになっている。** v0.9.0まではWebダッシュボード（フェーズ2）だったが、2026-10-19にユーザーのPC上のセッションで、Androidアプリ（`android/`）にしてテレビの標準ホームと置き換えた（フェーズ3）。以後の変更は、ダッシュボード（`dashboard/`）を直してAPKを作り直し、テレビに入れて確認する流れになる。

**この文書が現在の仕様。** 実行・接続手順の詳細は [README.md](README.md)、過去の相談は [docs/HANDOFF_HISTORY.md](docs/HANDOFF_HISTORY.md)。初期モックや履歴内の未確定事項を、現在の要件と混同しないこと。

![承認済みの最新画面](artifacts/dashboard-desktop.png)

（この画像はv0.9.0時点のWeb版。`artifacts/` は .gitignore の対象で、GitHubにはない。今のテレビの画面は、第3.4節の機能が加わっている。）

## 1. 現在地（v0.23.0、2026-10-20）

- **v0.23.0（詳しい天気、ソースのみ・テレビには未インストール）**：ユーザーの依頼「天気のところを選んだら詳細な天気を」。天気カードをリモコンで選べるようにし（白い枠。経済指標の一番上から↑、相場から←、カードから→で相場、↓で経済指標）、決定で幅の広い詳細シートを開く。中身は、見出し（今の気温と天気、今日の最高・最低、体感）、24時間（2時間ごと12コマ、カードと同じ気温の線と降水確率）、7日間（曜日・天気・降水確率20%以上・最低〜最高の色のバー。今日のバーには今の気温の点）、8つのパネル（体感温度、湿度、風＝16方位と最大瞬間、気圧、UV指数＝WHOの区分と今日の最大、今日の降水量、日の出・日の入、空気＝米国AQIとPM2.5）。データは今までの15分ごとのOpen-Meteoの1回の取得に項目を足しただけ（`forecast_days` 2→7、風は m/s）で、通信回数は増えていない。空気はCAMSの取得にPM2.5を足した。計算部分は `js/weather.js` の `dailyForecast`・`windDirection`・`uvLabel`、`hourlyForecast` の `{count, step}`。単体テスト68件。PCのヘッドレスChromeで、本物のキー入力（経済指標から↑、決定、戻る、→）と詳細の表示を確認した。`browser-ux-check.mjs` に同じ確認を足したが、この環境ではPlaywrightがなく未実行。テレビ実機では未確認。
- **v0.22.0（銘柄の詳細チャート、2026-10-20 00:58にユーザーの確認を得てテレビへインストール。Spotifyが前面のときに入れ替え）**：ユーザーの依頼「銘柄を選ぶと、より詳細なチャートを」で、銘柄の詳細シート（行で決定）を作り直した。(1) 期間の切り替え：1日（15分足）・1週（1時間足）・1か月（4時間足）・3か月（12時間足）・1年（日足）。1日はホームのチャートのデータを使い、ほかは選んだときにHyperliquidの `candleSnapshot` から取得して5分ほど覚えておく。上場が新しい銘柄（2026-10-20時点で30Yは26日分、10Yは69日分、SOXLは75日分など）は、ある分だけ描いて「◯年◯月◯日から」と明記する。(2) 大きいチャート：シートを幅1040px（画面で1300px）にし、右に価格の目盛り（4〜5本のきりのよい値）、下に日本時間の目盛り（時刻・日付・月、1月は年）。見出しの変化率は期間に合わせる（1日はマーク価格の24時間比、ほかは期間最初の足の始値との比較）。下に期間の高値・安値・始値、契約、単位、受信を3列で。(3) 時点ごとの価格：期間ボタンから↓でチャートを選び、← →でカーソルを動かすと、その足の価格・期間の始めからの変化率・日時（足の始まりの時刻）を表示。押し続けると速く動く。↑で選んでいる期間に戻る。マウスはなぞるだけで同じ表示。チャートの部品は `js/market-chart.js` の `drawDetailChart`・`niceTicks`・`timeTicks`。単体テストは64件（`tests/market-chart.test.mjs` を追加）。PCのヘッドレスChromeで、本物のキー入力（→→決定↓←×25、↑）で期間の選択・カーソル・戻りを確認し、30Yの3か月、経済指標の詳細が崩れないことも撮影で確認した。インストール後、ホームがTV Homeのまま、通知へのアクセスとユーザー補助サービスが有効のままであることをADBで確認した。テレビでのリモコン操作（期間の選択・カーソル）はユーザーの確認待ち。
- **v0.21.0（スモークのすりガラス、2026-10-20 00:38にユーザーの確認を得てテレビへインストール。テレビ入力の画面が前面のときに入れ替えた）**：ユーザーの「視認性を保ったままもう少しライトグレーに」「色にこだわりはないので、写真との相性を考えてデザイナーとして一番よい色を」という依頼。8枚の写真でガラスの明るさを変えて測ると、平均の明るさ（sRGB）55→77→88と明るくするほど、最も悪い条件の赤の数字は3.6→2.5→2.2、緑は5.0→3.5→3.1まで落ちた。ライトグレー（88）は夜景を白くかすませ、赤が読めない。そこで、ガラスに固有の色は持たせず（ごくわずかに青みのある無彩色）、後ろの写真の色を借りる「スモークのすりガラス」に決めた。写真の明るさによらず、カードの平均が60〜75に収まる帯にする：明るさ34を超える部分を60へ抑え、上に `rgba(200,210,230,.06)` の淡いベールを重ねる（夜景は黒く沈まず少し明るく、昼は白くかすまない）。文字色は、上昇 `#4ade80`・下落 `#ff7b72`・補助 `.8`・控えめ `.66` に上げ、最も悪い条件で白8.2・緑4.7・赤3.25・控えめ約4.2。あわせて、時計まわりの影を写真の上（ぼかし済み写真の下）に移し、明るい写真で天気のカードだけが暗くなっていたのを直した。インストール後、ホームがTV Homeのまま、通知へのアクセスとユーザー補助サービスが有効のままであることをADBで確認し、テレビの実画面（`adb exec-out screencap -p`、ニューヨークの夕暮れの写真）で、カードがそろったスモークのガラスになり、上部の空が暗くならず、緑・赤・控えめな文字が読めることを確認した。
- **v0.20.0（写真に合わせた影とガラス、2026-10-20 00:22にユーザーの確認を得てテレビへインストール）**：ユーザーの「上部が暗いのは必要か、ガラスの透け具合は」という依頼で、PCのヘッドレスChromeで8枚の写真（夜・夕方・曇り・昼）×8通りの設定を撮影し、文字の後ろの明るさからWCAGのコントラスト比を測った。結果：(1) 画面全体にかけていた暗いグラデーション（上・左・下・周辺減光）は、夜の写真では時計の読みやすさをほぼ変えず（19.5対18.9）写真を暗くするだけ、明るい写真では足りない（小さい文字2.0〜3.3）。(2) ぼかした写真の明るい部分を灰色で頭打ちにする方式は、色付きの光（東京タワーのオレンジなど）を濁った黄緑に変えていた。対応：全体の暗いグラデーションを廃止し、写真ごとに時計の後ろと右下の出典の後ろの明るさ（ぼかした写真の上位10%）を測って、その部分だけに必要な濃さの影（`--clock-shade`・`--caption-shade`、0〜.55）を敷く（`js/frost.js` の `shadeFor`）。ガラスは、明るさが36（sRGB）を超える部分を64に向けて滑らかに抑え、赤緑青を同じ比率で縮めて色合いを保つ方式に変え、上にかける色を `.3`→`.16` に薄くした。写真をCORSで読み込み（Unsplashは許可している）、読めない写真は従来の頭打ちに戻る。あわせて下落の赤を `#ff453a`→`#ff6961`（iOSのコントラストを上げる設定の赤）、控えめな文字を `.54`→`.6` にした。8枚の測定では、カードの白文字の最低コントラストが今の7.7→10.0、緑3.8→4.9、赤2.3→3.6（新しい赤）。夜の写真では時計の影はほぼ0、曇り・夕方の空では.48〜.55。インストール後、ホームがTV Homeのままであること、通知へのアクセスとユーザー補助サービスが有効のままであることをADBで確認した。テレビの画面での見え方はユーザーの確認待ち。
- **v0.19.1（2026-10-19 20:39にユーザーの確認を得てテレビへインストール。Spotifyの再生中に入れ替え、再生は止まっていない）**：テレビの実画面（`adb exec-out screencap -p` で撮影）で、ドックを右へ進んでから左へ戻ると、選んだSmartTubeのアイコンと名前が台の端で切れていた。`scrollIntoView` がタイルを台の端ちょうどにそろえるため。`.native-apps` に `scroll-padding-inline: 50px`（台の内側14px＋名前のはみ出し最大36px）を付け、先頭のアプリの名前は左へのはみ出しを10pxまでにした。PCで16アプリのドックを左端・右端・途中で撮って確認。
- **v0.19.0（デザインの磨き込み、2026-10-19 20:32にユーザーの確認を得てテレビへインストール）**：配置・カード構成は変えずに、(1) カードのガラスを暗い素材にした（ぼかした写真の明るい部分を `rgb(96,100,112)` で頭打ちにし、下地を `rgba(10,13,22,.3)` に。昼の明るい写真でも白文字と上昇・下落の色が読める。夜の写真はほぼ変わらない）、(2) ドックの下にカードと同じガラスの台を敷いた（第3節）、(3) 時計まわりと写真の出典に影を足し、明るい空でも読めるようにした、(4) 正常時の「この先6時間」を消した、(5) チャートの「…まで」を9px→12pxにした、(6) 右上の更新ボタンを控えめにした。PCのヘッドレスChromeで、夜1枚・昼2枚の写真とWeb版・設定シートを撮って確認した。インストール後、ホームがTV Homeのままであること、通知へのアクセスとユーザー補助サービスが有効のままであることをADBで確認した。テレビの画面での見え方はユーザーの確認待ち。
- **テレビに入っているもの**：TV Home `jp.tvhome.launcher` v0.22.0（ソースはv0.23.0。リリースビルド、開発用の鍵で署名）。ホームボタンで開く。標準ホームは無効化済み。詳細と戻し方は第3.4節。
- **デザイン**：v0.5.5の配置のまま、v0.6.0でApple／iOS風に刷新した（第3節）。TV専用（第3.3節）。**ユーザーは「モバイル版は作らなくていい、テレビ専用」と明言**している。スマホ・縦画面の配置を戻さない。ユーザーはApple／iOSのようなデザインが好みで、UIをさらに洗練させたいと考えている。
- **このセッション（2026-10-19、PC上）でやったこと**（いずれもテレビで確認済み。詳細は第3.4節）：
  1. Castでテレビに表示し、Cast受信ブラウザで画面が4倍に拡大される不具合を直した（第3.3節）。
  2. APKを作り、標準ホームを無効化してホーム画面を置き換えた（v0.10.0）。ニュースと経済指標はアプリが自分で取得する（PC不要）。
  3. ドックを実物のアイコンにした。SmartTubeを導入した。BLSの経済指標を取得できるようにした。
  4. Spotifyカードに、テレビのSpotifyアプリで再生中の曲を出す（ログイン不要。通知へのアクセスを許可）。
  5. 背景写真を、Unsplashの世界8都市のダウンタウン（昼夜）に自動で切り替える。
  6. ドック：決定ボタンの長押しで並べ替え・ドックから外す。アプリ一覧。設定シートから「テレビの設定を開く」。
  7. リモコンの設定ボタンで、どの画面からでもテレビの設定が開く（ユーザー補助サービス）。
  8. ホームに戻るのを即座にし、アプリ起動前の約1.3秒の待ちをなくし、カーソル移動を滑らかにした。
- **未確認・保留**：キャスト中の映像の重さ・音切れ（v0.17.0でメモリ解放を弱めたため、ユーザーの再確認が必要）、スリープ復帰・長時間稼働、Unsplashの本番申請、Spotifyのスマホ再生の表示（Webログインは未完了）。第11節も参照。
- **ソース**：GitHubの `haraniikochan-hue/edinet-screener`、ブランチ `ccr-123aaf7c-88ru7c` の `tv-home/`。プルリクエストは未作成で、ユーザーの依頼があるまで作らない。**コミットしたら確認せずにこのブランチへpushする**（ユーザー指示「毎度それ聞かないで勝手にpushして」）。

## 1.1 次のセッションの始め方（ユーザーのPC）

テレビに届くのは、ユーザーのMac上のセッションだけ（クラウドからは家のWi-Fiに届かない）。Claude Desktopアプリのセッションで作業する。

1. このリポジトリをcloneしてブランチ `ccr-123aaf7c-88ru7c` に切り替え、`tv-home/` で作業する。2026-10-19のセッションは一時フォルダだったので、そのフォルダは残っていない前提でよい。
2. Macに入っている道具（いずれも `~/.local`。Macのシステムは変更していない）：
   - Node.js 24.22.0：`~/.local/node/bin`（`PATH=~/.local/node/bin:$PATH npm test`）
   - JDK 17：`JAVA_HOME=~/.local/jdk17/Contents/Home`
   - Android SDK：`ANDROID_HOME=~/.local/android-sdk`（ライセンスはユーザーの同意を得て受諾済み）。adb は `~/.local/android-sdk/platform-tools/adb`
   - GitHub CLI：`~/.local/gh/bin/gh`（haraniikochan-hue でログイン済み。gitのpushもこれで通る）
   - catt（Cast送信）：`~/.local/catt-venv/bin/catt`
   - Homebrewの node はIntel Macではソースからのビルドになり非常に遅いので使わない。
3. **APIキー**：SpotifyのClient IDとUnsplashのAccess Keyは `~/.config/tv-home/local.properties`（権限600、Gitの外）にある。`android/app/build.gradle.kts` はこのファイルと `android/local.properties`（Gitの外）を読む。キーの値をコミット・チャット・スクリーンショットに出さない。
4. **テレビとの接続**：テレビはWi-Fi `harannWiFi_5G`。IPアドレスはDHCPで変わる（2026-10-19の最後は `192.168.0.17`）。`adb mdns services` で今のアドレスとポートを確認し、`adb connect <IP>:5555` でつなぐ（`_adb._tcp` の5555番が使える）。つながらない場合は、ユーザーにテレビの 設定 → システム → 開発者向けオプション → ワイヤレスデバッグ を確認してもらい、必要ならペア設定（`adb pair <IP>:<ポート> <6桁コード>`）からやり直す。
5. **ビルドと入れ替え**：
   ```sh
   cd android
   ./gradlew assembleRelease    # 確認用は assembleDebug（WebViewのDevToolsがADB経由で開く）
   adb install -r app/build/outputs/apk/release/app-release.apk
   ```
   `dashboard/` を直したら、そのままAPKに入る（`dist/` は使わない）。確認でデバッグ版を入れたら、最後に必ずリリース版に戻す。並び順などの保存データは入れ直しても残る。
6. **テレビで確認するときの注意**：
   - ユーザーがテレビを使っていることが多い。`adb shell input keyevent` でキーを送るテストはしない（2026-10-19に、長押しのつもりの操作でSmartTubeが起動して再生画面に入ってしまった）。ページ内の確認はデバッグ版のDevTools（`adb forward tcp:9333 localabstract:webview_devtools_remote_<pid>`）で行い、リモコン操作の確認はユーザーに頼む。
   - TV Homeが前面にあるときに `adb install -r` すると、TV Homeが閉じて、その下にあった直前のアプリ（2026-10-20はSmartTubeの再生画面）が前面に戻る。入れ替えは、スクリーンセーバー中か別のアプリが前面のときに行うのがよい（`dumpsys activity activities | grep topResumedActivity` で確認）。
   - `com.xiaomi.mitv.smartshare`（Miracastの画面ミラーリング）を開くと、テレビのWi-Fiが切り替わり、IPアドレスが変わってADBが切れる。開かない。
   - テレビを変更する操作（アプリのインストール・削除、`pm disable-user`、`settings put` など）は、対象・影響・戻し方を説明し、ユーザーの確認を取ってから行う（第12節）。
7. PCのブラウザで見るだけなら、今までどおり `npm run dev` で `http://127.0.0.1:4173/`。テレビへのCast表示の手順は下に残す（APKがある今は、ほぼ不要）。

ユーザーとのやり取りは日本語で、報告は短く、専門用語を避ける。確定済みの地域・銘柄・アプリ・朝晩の表示・余白は聞き直さない。

- **Castでテレビに出す（2026-10-19に実施・表示確認済み）**：テレビは内蔵Chromecastで、LANでは `MiTV-MZTU0`／名前「リビングルームのテレビ」（mDNSの `_googlecast._tcp`）。テレビの設定やアプリは変えずに、PCから表示できる。
  ```sh
  HOST=0.0.0.0 npm run dev
  ~/.local/catt-venv/bin/catt -d "リビングルームのテレビ" cast_site http://<PCのLAN内IP>:4173/
  ~/.local/catt-venv/bin/catt -d "リビングルームのテレビ" stop    # 終了。送り直す前にも一度止める
  ```
  `cast_site` は受信アプリDashCastを、ページごと移動させる方式（force）で使う。Cast表示ではリモコンの操作は届かない。

## 2. ユーザーと確定した仕様

| 項目 | 確定内容 |
| --- | --- |
| 時間帯 | 朝晩とも同じフル版。時間帯によるカード切り替えなし |
| 天気 | 渋谷区。現在の気象、明日の最高・最低、日の出・日の入、空気、次の正時から6時間予報 |
| 時間別天気 | アイコン・気温の曲線・降水確率の数値とバー。直感的に読める表示 |
| 音楽 | Spotify。再生情報カードとアプリドックの両方を使う。カードはテレビのSpotifyアプリで再生中の曲を出す（ログイン不要、ユーザーの選択。第3.4節） |
| スポーツ | 当面表示しない |
| 個人の予定 | 「今日の予定」は不要。個人カレンダーカードを追加しない |
| 経済指標 | 米国の主要指標、日本時間、6件ずつページ送り |
| 相場 | 暗号資産とその他のマーケットを1つの一覧に統合。BTC/HYPEの重複なし |
| チャート | ホームの小さなチャートは24時間固定（銘柄アイコン付き）。銘柄の詳細では1日・1週・1か月・3か月・1年を切り替え、← → で各時点の価格を読める（v0.22.0） |
| 背景写真 | 世界の都市のダウンタウン（昼も夜も）のかっこいい写真（2026-10-19のユーザー指示）。Unsplashから自動取得し、テレビで稼働中（第3.4節） |
| アプリ | 既定の並びは SmartTube / U-NEXT / Netflix / Prime Video / Disney+ / Spotify、続けてテレビのほかのアプリ、最後に「アプリ」（一覧）と「設定」。並べ替え・ドックから外すはユーザーがリモコンで行い、テレビに保存される（第3.4節）。Google Cast・AirPlay・テレビの設定のタイルは、ユーザーと相談のうえ置かない |
| SmartTube | **見た目だけYouTubeアイコン**。名前・TVでの起動対象はSmartTube |
| 地デジ | ショートカット削除済み。TVのチューナー機能を無効化したわけではない |

削除済み：NY時間、市場オープンまでのカウントダウン、別カードのドル円・米国債、独立した暗号資産カード、マーケットの見出し・件数・24Hバッジ・カード内設定ボタン・接続状態フッター。再追加は新しいユーザー指示がある場合に検討する。

## 3. デザインとレイアウトの基準

v0.6.0でApple TV／iOSの考え方に沿ってデザインを作り直した。**配置・余白・カード構成・銘柄・アプリ・朝晩の表示は v0.5.5 のまま**で、見た目・文字・素材・動き・フォーカスを刷新している。実装の正本は `dashboard/styles.css`（冒頭のトークンから読む）。

原則：
- 情報が主役で、装飾は控えめ。正常時は状態表示を出さず、更新待ち・取得失敗のときだけ琥珀色で知らせる。
- TVで読める文字。最小12px（v0.5.5は8〜9pxの文字があった）。
- 1つの素材・1つの見出し様式・1つのフォーカス表現で全体を統一する。

| 要素 | 仕様 |
| --- | --- |
| フォント | Inter（欧文・数字、optical size）＋Noto Sans JP。日本語は `palt`（プロポーショナル仮名）、数字は等幅。Google Fontsから取得し、失敗時はシステムフォント |
| 色 | 文字 `#fff`、補助 `rgba(235,240,255,.8)`、控えめ `.66`、区切り `rgba(255,255,255,.1)`。上昇 `#4ade80`、下落 `#ff7b72`（いずれもv0.21.0、スモークのガラスで読めるよう少し明るく）、降水 `#64d2ff`、注意 `#ffb340`、Spotify `#1ed760`（iOSダークモードのシステムカラー） |
| ガラス | スモークのすりガラス（v0.21.0）。ベール `rgba(200,210,230,.06)`＋上部の淡い反射、blur 24px・saturate 150%、角丸32px。TVのぼかし済み写真は、明るさ34を超える部分を60へ滑らかに抑え、色合いは保つ（`js/frost.js`。写真が読めないときは `rgb(70,74,84)` で頭打ち）。カードの平均の明るさは写真によらず60〜75。ライブのぼかしは brightness(.8)。画面全体の暗いグラデーションはない。時計と右下の出典の後ろだけ、ぼかし済み写真の下に、写真の明るさに応じた影（0〜.55）を敷く。外周に黒の0.5px線。縁は左上が明るいスペキュラーリム（グラデーション枠をmaskで1pxに切り抜き） |
| 見出し | 全カード共通。15px semibold・補助色＋SF Symbols風アイコン（`index.html` 冒頭のSVGスプライト） |
| フォーカス | ボタン類は白いプラッター（tvOS）。経済指標の行とニュース見出しは持ち上がるガラス行。アプリは浮き上がり・影・光が一度走る |

カードごとの要点：
- **時計**：上に時間帯のあいさつ（おはようございます／こんにちは／こんばんは）と「東京」。背景がNYなので時刻の地域を明示する。Inter Thin 140px。分が変わると変わった桁だけがぼかしから現れる（iOSの数字トランジション）。
- **天気**：Apple Weatherウィジェット型。左に地域と現在気温、右に天気アイコン・天気・明日の最高/最低。時間別の気温線は気温に応じた色（青→緑→黄→橙→赤）で、下の塗りは下へフェード。降水確率の数値とバーは維持。日の出・日の入・空気はアイコン付き。出典は正常時は時刻だけ、更新待ちは日付付きの琥珀色。未取得の気温は「--°」。
- **相場**：Apple株価アプリ型。アイコン30px、銘柄18px、名称13px、価格23px、変化率は「+1.03%」「−0.59%」（▴▾は廃止）。区切り線は文字の開始位置から。チャートは基準線から外側へ薄くなる塗りと最新点の淡いハロー。720px以下は1列×12段。
- **経済指標**：行頭にカテゴリー色のバー（FOMC紫、CPI/PPI/PCE橙、雇用統計/JOLTS青、GDPミント）。同じ日の2件目以降は日付を省略。曜日・今日・明日を表示。出典とページ送りは1行に統合。
- **ニュース**：見出しは文節で改行（`word-break: auto-phrase`）。ページドットは表示中の記事が20秒で満ちる（手動で送るとタイマーもリセット）。切り替え時にフェード。
- **Spotify**：ジャケット取得時はカード背景にぼかしたジャケットの色を敷く。再生中はイコライザーが動き、一時停止で止まる。未接続時は緑のプレースホルダーと「Spotifyと連携」。
- **ドック**：v0.19.0から、カードと同じガラスの台（角丸32px、内側14px＝アイコンの角と同心）に載る。台はアプリの数に合わせて縮み、入りきらないときだけ中でスクロールする。TVではぼかし済み写真の切り抜きに台も含める（`updateFrost`）。アイコンはiOSの連続曲線（`assets/squircle.svg` のスーパー楕円マスク）。設定はiOSと同じ灰色グラデーション。ブランドアイコンからbackdrop-filterを外し、TVの描画負荷を下げた。
- **設定**：iOSのグループ表示、トグルスイッチ、カプセルボタン。開くと背景を暗くぼかす。
- **トースト**：画面上部中央のガラスのカプセル（TVでは空いている上段の帯を使う）。
- **起動時**：カードが順に少し浮き上がって現れる。縮尺を適用する前の崩れたレイアウトは表示しない（JSが動かない場合も1.6秒後に表示）。

v0.6.0で削除：左上の「HOME / 街と、いま。」、下端のキー操作ヒントと「WEB PREVIEW」表記（Web版でアプリを押すとトーストで説明する）、常時表示の「データ接続中」、価格の更新フラッシュ（毎秒の更新で常に色が付き落ち着かないため不採用）。

1920×1080の基準座標（v0.5.5から不変）。

| 領域 | X | Y | 幅 | 高さ |
| --- | ---: | ---: | ---: | ---: |
| 時計・日付 | 216 | 104 | 500 | 142 |
| 天気・時間別予報 | 216 | 270 | 500 | 286 |
| 米国経済指標 | 216 | 580 | 500 | 308 |
| マーケット | 844 | 270 | 860 | 432 |
| ニュース＋Spotify | 844 | 726 | 860 | 162 |

- 天気とマーケットの上端270px、経済指標とニュース・Spotifyの下端888px。
- 外周は左右216px・上48px・下52px（TVのセーフエリアに合わせ36pxから拡大）。左列500px、右列860px、列間128px、カード同士は24px。
- 時計は独立した上段。時計右側の空間は意図的な余白。
- マーケットは1枚のパネル、2列×6段。名前・チャート・価格を整列。
- ドックは中央に7ボタン（TVでは左寄せで全アプリ）、72px・間隔24px。ガラスの台の下端が画面下端から52px（アイコンは台の内側14px）。選択時に浮き、上に名前のガラスラベルが出る。
- TV専用。1920×1080の画面1枚を、どの解像度でも縦横比を保って縮尺表示する（第3.3節）。スマホ・縦画面の配置はない。
- OSの動き・透明度を減らす設定、ぼかし非対応時の表示に対応。

## 3.1 TVでの軽さ（v0.6.1）

Xiaomi TVのGPU・CPUで滑らかに動くよう最適化した。見た目はv0.6.0と同じ。計測は `scripts/perf-bench.mjs`（このクラウド環境のヘッドレスChromium、1920×1080、20秒の定常状態、既定設定）。

| 指標 | v0.6.0 | v0.6.1 |
| --- | ---: | ---: |
| Chromium全体のCPU（待機中） | 103.5% | 2.9% |
| 描画フレーム（rAF計測時） | 13.5fps・50ms超の停止238回 | 59.9fps・0回 |
| メインスレッド（CPU 4倍低速化） | 95.9ms/秒 | 19.0ms/秒 |
| 長いタスク（CPU 4倍低速化） | 2回 | 0回 |
| Google Fontsが4秒遅いときの初回描画 | 5.4秒 | 0.5秒 |

ヘッドレスはソフトウェア描画のためGPUの負荷が誇張される。TV実機の値ではない。実機では `chrome://inspect` のPerformanceで確認する。

原因と対策：
- **ライブのぼかし（backdrop-filter）が最大の負荷**だった。背景のズーム、写真の切り替え、カード内の動きのたびに5枚すべてを毎フレームぼかし直していた。TVステージでは、写真ごとに480px幅のcanvasへ1回だけぼかした画像（`js/frost.js`）をカードの角丸形に `clip-path` で切り抜いて下に敷き、カードの `backdrop-filter` を外す。写真の切り替えでは写真とぼかし画像が一緒にクロスフェードする。`clip-path: path()` 非対応ならライブのぼかしのまま。
- **常に動くアニメーションをなくした**：ニュースの進行ドット（v0.6.0で追加）を廃止、イコライザーは静止アイコン、再生バーは1秒ごとのtransform更新。
- **ゆっくりズームは初期設定オフ**（設定で変更可）。オンのときも650段階のステップで、再描画は1秒10回。設定画面を開いている間は止める。
- 小さなガラス（アプリ名ラベル・上部ボタン・トースト・設定画面・詳細シート）は半透明の単色。
- JS：Intlの書式オブジェクトを1回だけ作る、変化した文字だけ書き換える、チャートはデータが変わったときだけ作り直す、時計・あいさつ・日付は分が変わったときだけ更新。
- 価格欄は独立した描画レイヤー（`will-change`）、カードと相場の行は `contain: layout paint` で、毎秒の更新が周りを描き直さない。
- 写真の `filter`、天気アイコンの `drop-shadow`、アプリの影の `blur` を廃止。Spotifyの背景はジャケットを24pxのcanvasに1回描いて引き伸ばす。
- フォント：Inter（欧文）は `assets/fonts/` に同梱（73KB、SIL OFL）。Noto Sans JPは初回描画を止めずに読み込み、届くまではAndroid TV標準のNoto Sans CJK JP（同じデザイン）。CSPがインラインのonloadを禁止しているため、切り替えは `app.js` で行う。TV起動直後にWi-Fiが未接続でも画面がすぐ出る。

今後もTVで動かす前提で、カードの中に常時動くものや `backdrop-filter`・`filter: blur()` を足さない。追加したら `scripts/perf-bench.mjs` で比べる。

## 3.2 リモコン操作（v0.8.0）

実際にキー操作で全要素を辿って見つけた問題を直した。主なもの：設定画面で最初のプルダウンから先へ進めない、スイッチを決定で切り替えられない、アプリ列で↓を押すと右下の写真ボタンへ飛ぶ、決定でTVのホームから外部サイトへ移ってしまう、相場がリモコンで選べずツールチップの契約情報がTVで見えない、戻るがホームで何もしない。

- **移動の仕組み（`js/navigation.js`）**：`data-nav-group` でブロックを定義（top・market・calendar・news・music・dock・photo）。矢印はまずブロック内の最寄りへ動き、端では `data-nav-up/down/left/right`（ブロック名か `none`）に従い、なければ方向にある最寄りへ。直前に出たブロックへ逆方向で戻ると元の要素に戻る。ブロックをまたいだ直後に逆の矢印を押すと、ブロック内の移動やページ送りより優先して必ず元の要素へ戻る（v0.9.0。SmartTubeで↑→経済指標の最後の行→↓が、ページ送りにならずSmartTubeへ戻る）。`data-nav-skip` は移動対象外（写真の出典リンク、経済指標のページ送りボタン。マウスでは使える）。閉じた `<details>` の中身と非表示要素は `checkVisibility()` で除外する。
- **経済指標**：最後の行で↓は次のページ、最初の行で↑は前のページ（`calendarEdge`）。
- **戻る**：ダイアログを閉じる。ホームではアプリ列の最後に選んだアプリへ。60秒操作がなければ同じ位置へ戻る（`IDLE_HOME`）。
- **ダイアログ内**：縦方向は横のずれを軽く見て次の項目を優先する。←→は入力欄ではカーソル移動、プルダウンでは項目移動（値は変えない）。決定でチェックボックスと `role="button"` の要素も動く。設定の項目は1行に1つ（iOSの設定と同じ並び）。
- **詳細シート**：決定で開き、戻るで閉じて元の要素に戻る。天気（v0.23.0、天気カードで決定。今・24時間・7日間・8つのパネル）、相場（v0.22.0から幅の広いシート。期間ボタン→チャート（← → でカーソル、↑で期間へ）→期間の高値・安値・始値、契約ID、単位、受信時刻・配信元、注記）、経済指標（日本時間・米国東部時間・あと何日・発表元・備考）、ニュース（NHKのRSSの要約、最大240字）、データの状態（配信元ごとの最新／更新待ち／取得不可と「今すぐ再取得」）。外部リンクは `window.Android` がない（ブラウザ）ときだけ出す。
- 「一部更新待ち」はボタンになり、正常時は `visibility:hidden` でフォーカス対象からも外れる。写真が1枚なら写真切り替えを出さない。TVアプリでは全画面ボタンを出さない。Spotifyカードの連携はTVアプリでは入力欄でなくボタンにフォーカスする（画面キーボードがいきなり出ないように）。
- 選択中の行（相場・経済指標）とニュース見出しは、3m先でも分かるよう少し明るいガラスの行に強めた。
- **フェーズ3への注意**：AndroidのBACKキーをWebViewへ `Escape`（または `BrowserBack`）のキーイベントとして渡す。D-padの決定は通常どおりEnterとして届く。
- 検証：`scripts/browser-ux-check.mjs`（配信元はすべて制御レスポンス）。

## 3.3 TV専用の画面（v0.9.0）

ユーザーの指示「モバイル版は作らなくていいよテレビ専用だから」により、スマホ・タブレット・縦画面の配置（約70行のCSS）と `.tv` での切り替えを削除した。

- **画面は1枚**：`#screen`（1920×1080）の中に、ダッシュボード（`#stage`）・設定・詳細シート・トーストをすべて入れ、`fit()` が `#screen` だけを `scale()` する。縦横比が違えば中央に寄せ、余白には背景写真が見える。ページはスクロールしない（矢印キーは常に `preventDefault`、スクロールするのはダイアログの中とAndroidのアプリ一覧だけ）。
- **なぜ**：Google TVのWebViewは1080p・4KのTVでも多くの場合 960×540 CSS px（密度2倍）を報告する（実機未確認）。v0.8.0までは設定・詳細シート・トーストが縮尺の外にあり、その環境では他の要素の2倍の大きさになっていた。
- **シートの大きさ**：設定と詳細シートは `.modal-overlay` の `zoom: 1.25` で、画面の1920px基準で幅900px（画面の約47%）。文字（説明13px→約16px、詳細本文18px→約22px）がソファから読める大きさになる。高さは画面内に収まり、リモコンで移動すると `scroll-padding` を残してスクロールする。トーストは画面基準で上から40px・20px。
- 表示されていなかった経済指標のカテゴリー行（`.calendar-meta`）は作らない。入場アニメーションはフェードのみ（各カードがぼかし済み写真の上に留まるため）。
- 検証：`browser-check.mjs` は3840×2160・1366×768・1280×720・960×540で、ページのスクロールなし・ぼかし済みカード・設定シートが画面と一緒に縮尺されること（幅＝900×縮尺）を確認。`browser-ux-check.mjs` は960×540（2倍密度）でもリモコン移動・詳細シート・設定のスクロール・トーストを確認する。
- 実機での見え方（文字の大きさ、オーバースキャン）は未確認。小さすぎる場合は、画面全体ではなくシート・カードの文字を調整する。
- **Castの受信ブラウザで見つかった問題（2026-10-19修正）**：Chrome 92（CrKey 1.56、Android 14）の受信ブラウザで計測すると、表示領域・`clientWidth`・`visualViewport`・`screen` はすべて960×540、`devicePixelRatio` は2。一方で `innerWidth`/`innerHeight` だけが読み込みの約2秒後に3840×2160へ変わり、`fit()` の縮尺が4倍になって画面が大きく拡大されていた。`fit()` は `document.documentElement.clientWidth/clientHeight` で測るように変更した。テレビで全体がちょうど収まることをユーザーが目視で確認した。960×540・2倍密度という想定は、このCast受信ブラウザについては実測で正しかった（WebViewは未計測）。
- **Chrome 92で使えない機能（未対応）**：`AbortSignal.timeout`（Chrome 103以降）は `js/adblock.js` と `js/spotify.js` で使っている。広告ブロックの確認では例外が「接続不可」と判定され、結果が誤りになりうる。Spotifyは取得に失敗する。CSSの `:has()`（Chrome 105以降）は3か所あり、効かないと見た目が少し変わるだけ。`checkVisibility()` には代わりの処理がある。テレビのWebViewの版を調べたうえで、必要なら直す。

## 3.4 TVアプリ＝ホーム画面（v0.10.0、フェーズ3、2026-10-19）

ユーザーの依頼「正式にこっちに変えたい」により、ダッシュボードをAndroidアプリにしてテレビのホーム画面へ置き換えた。方針はユーザーが選んだ：**アプリ単体で動かす**（PC不要）、**標準ホームは完全に置き換える**。

- **実機の状態（ユーザーの確認を得て実施）**：`jp.tvhome.launcher`（TV Home、v0.10.0）をADBでインストール。標準ホーム `com.google.android.apps.tv.launcherx` と、代わりにホームに出てくる初期設定ウィザード `com.google.android.tungsten.setupwraith` を `pm disable-user --user 0` で無効化。ホームボタンでTV Homeが開くことを確認した。先に試した `cmd package set-home-activity`（無効化なし）はGoogle TVに無視された。
- **戻し方**：PCから `adb shell pm enable com.google.android.apps.tv.launcherx` と `adb shell pm enable com.google.android.tungsten.setupwraith`。アプリを消すなら `adb uninstall jp.tvhome.launcher`。テレビ単体でも、ドックの「テレビの設定」→ アプリ → システムアプリ → Google TV Home →「有効にする」で戻せる。
- **ソース**：`android/`（Kotlin、Gradle 8.10.2、AGP 8.7.3、compileSdk 35、minSdk 28）。`MainActivity.kt` 1ファイル。ビルド時に `dashboard/` をAPKの `assets/www/` へコピーし、`WebViewAssetLoader` で `https://appassets.androidplatform.net/` から配信する。`dist/` は使わない。
- **ニュース・経済指標**：Nodeサーバーの処理を `dashboard/js/feeds.js`（NHKのRSS解析、BLS/BEAの日程と同梱日程の統合）と `dashboard/js/economic-calendar.js`（`lib/` から移動。`lib/economic-calendar.mjs` は再エクスポート）に移し、`server.mjs` とアプリで共用する。アプリでは `app.js` が自分で解析し、配信元にCORSがないため、取得だけをアプリの `/api/upstream?url=` が代行する。代行できるのは `UPSTREAM_FEEDS` の3つのURLだけ（Kotlin側にも同じ一覧）。
- **ドック**：`window.Android.getApps()` が固定の順（SmartTube → U-NEXT → Netflix → Prime Video → Disney+ → Spotify）のうちインストール済みのもの、「テレビの設定」（Androidの設定を開く）、残りのTVアプリ（名前順）を最大16件返し、最後にダッシュボードの「設定」が付く。標準ホームがないため、他のアプリへの入口として残りも並べた。地デジ（`com.mitv.livetv`、削除済みの確定事項）とXiaomiのシステムツール（`com.xiaomi.mitv.*`）は出さない。起動できるのは一覧に出したパッケージだけ。
- **実機のパッケージ名（ADBで確認）**：SmartTube `org.smarttube.stable`、U-NEXT `jp.unext.tv.player`、Netflix `com.netflix.ninja`、Prime Video `com.amazon.amazonvideo.livingroom`、Disney+ `com.disney.disneyplus`、Spotify `com.spotify.tv.android`。公式YouTube（`com.google.android.youtube.tv`）は別に入っていて、ドックの後半に並ぶ。
- **SmartTube（ユーザーの確認を得て導入）**：作者の公式GitHub（yuliskov/SmartTube）の安定版 `SmartTube_stable_32.56_armeabi-v7a.apk`（テレビのCPUは armeabi-v7a）。GitHubが公開しているSHA-256と照合してから `adb install` した。消すなら `adb uninstall org.smarttube.stable`。更新はPlayストアではなく、SmartTube自身の更新通知から行う。
- **ドックのアイコン**：`getApps()` は各アプリのアイコンをPNGのdata URL（192px）で `icon` に入れて返す。アダプティブアイコンは、見える範囲いっぱいに描く。ページ側の角丸（squircle）で全タイルを同じ形に切り抜く。同梱のロゴがあるブランド（SmartTube・U-NEXT・Netflix・Prime Video・Disney+・Spotify）は、今までどおり同梱ロゴを使う。それ以外（テレビの設定・ABEMA・DAZN・Hulu・Lemino・Playストア・TVer・YouTube・ブラウザー）は実物のアイコンを使う。`launcher.js` は `data:image/png;base64,` 以外の値を画像として使わない。名前ラベルの最大幅は、アイコン幅＋72px。
- **リモコン**：戻るはページへ `Escape` として届く。ホームのときはアプリを閉じない。TV Homeの表示中にホームを押すと `Escape` を送り、シートを閉じてドックへ戻る。外部サイトへの移動は無視する。
- **デバッグ**：デバッグビルド（`assembleDebug`）だけ、WebViewのDevToolsをADB経由で開ける（`adb forward tcp:9333 localabstract:webview_devtools_remote_<pid>`）。テレビに入っているのはリリースビルド（開発用の鍵で署名）。
- **BLSの取得**：BLS（`www.bls.gov`）は接続方式（TLSやHTTP/2の特徴）でクライアントを判定している。AndroidのHttpURLConnection、Android 14内蔵のHttpEngine（Cronet）、Macのcurlは403になり、PCのNodeとテレビのWebView（Chrome 155）は200になる（ヘッダーを変えても結果は同じだった）。このためアプリは、配信元が403を返したときだけ、画面に出さないWebViewで取得し直す。そのWebViewは、空のページを配信元のオリジンで開き、同一オリジンの `fetch` で読む（最大20秒）。2026-10-19に、テレビで「BLS・BEA 自動更新」になり「一部更新待ち」が消えたことを確認した。HttpEngineを試した際は `ACCESS_NETWORK_STATE` がないためにクラッシュを繰り返したので、HttpEngineは外した。
- **Spotifyカード（v0.11.0）**：ユーザーの選択で、**テレビのSpotifyアプリ（`com.spotify.tv.android`）の再生情報**を使う。ログインは不要。アプリはこのMediaSessionを `MediaSessionManager` で読み、Web APIの currently-playing と同じ形（`source:"tv"`、ジャケットは300pxのJPEGのdata URL）で `window.Android.nowPlaying()` から返す。曲や再生状態が変わると、アプリが `window.tvHomeMedia()` を呼ぶので、すぐ反映される（30秒ごとの取得も続ける）。表示はテレビで再生している曲だけで、スマホでの再生は出ない。2026-10-19に、テレビで再生中の曲名・アーティスト・ジャケット・再生中の表示・進行バーが出ることを確認した。
  - 読むには「通知へのアクセス」が必要。ユーザーの確認を得て `adb shell cmd notification allow_listener jp.tvhome.launcher/jp.tvhome.MediaListener` で許可した（`MediaListener` は許可のためだけのサービスで、通知は読まない）。戻すなら `disallow_listener`、またはテレビの設定 → アプリ → 特別なアプリアクセス → 通知へのアクセス。許可がない場合、`nowPlaying()` は空文字を返し、カードはWebログインの方式に戻る。
  - **Webログイン（未完了）**：Spotifyのログイン画面は、ブリッジのない別のWebViewで開き、`https://appassets.androidplatform.net/index.html` へ戻ったらダッシュボードがPKCEを完了する。テレビ版では、ログイン情報をlocalStorageに保存して再起動後も残す。Client ID（ユーザーが作成）は `android/local.properties` の `spotify.clientId`（コミットしない）から `BuildConfig` に入れる。ログイン画面までは表示できたが、メールのリンクをスマホで開くと「別のブラウザでログインしています」となり、ログインは完了していない。テレビの再生情報を使う方式に切り替えたため、今は使っていない。
- **背景写真（v0.12.0）**：ユーザーの希望は「ニューヨークやロンドン、パリなど、色々な都市のダウンタウンの昼夜のかっこいい写真」。`dashboard/js/feeds.js` の `PHOTO_CITIES`（ニューヨーク・ロンドン・パリ・シカゴ・東京・香港・シンガポール・ドバイ）から、それぞれUnsplashの `photos/random` で3枚ずつ取り、混ぜて24枚にする（1時間ごと、8リクエスト。デモ段階の上限は1時間50回）。写真の左下には都市名と撮影者を出す。アプリでは `/api/unsplash?query=` をKotlinが代行し、Access Keyを付ける。検索語は `PHOTO_QUERIES` の8つだけ許可する。Access Keyは `android/local.properties` の `unsplash.accessKey`（コミットしない）から `BuildConfig` に入れ、ページには渡さない。テレビの設定で写真の取得元を「Unsplashから自動取得」に保存済み。2026-10-19に、8都市×3枚が取得されて切り替わることをテレビで確認した。Unsplashの本番申請（上限の引き上げ）と、写真の利用時に必要な download エンドポイントの呼び出しは未対応。
- **キャスト（v0.13.0で追加、v0.14.0で外した）**：テレビはGoogle Cast（`com.google.android.apps.mediashell`）とAirPlay（MediaTekの `com.mediatek.partner.airplay_sys`、HomeKit対応）を内蔵し、どちらも常に受信している（mDNSで「リビングルームのテレビ」）。一度ドックにタイルを置いたが、ユーザーと相談のうえ「押す意味がない」として外した。Androidの「画面ミラーリング」（Miracast、`com.xiaomi.mitv.smartshare`）は、開くとテレビのWi-Fiが切り替わり、IPアドレスが変わってADBが切れた。Galaxy（Smart View＝Miracast）には、Google Homeアプリの「画面をキャスト」を案内した。
- **裏にいるときのメモリ（v0.14.0）**：キャスト中に映像が重く音が途切れるとの相談。テレビとスマホのWi-Fiはどちらも5GHzで良好（テレビは `harannWiFi_5G`、-31dBm、780Mbps）。テレビのメモリは1.8GB（空きは約0.5GB）で、TV Homeは裏にいる間も約0.5GB（アプリ約350MB＋WebViewの描画プロセス約160MB）を使っていた。Androidはホームアプリを前面と同じ扱いにするため、バックグラウンド向けのメモリ解放の合図（`TRIM_MEMORY_BACKGROUND`）は届かない（`am send-trim-memory` も前面扱いで拒否）。そこで、ほかのアプリ・キャストが前面になったらすぐ `pauseTimers()`、30秒後（またはメモリ不足の合図 `TRIM_MEMORY_RUNNING_LOW` のとき）にWebViewを破棄し、ホームに戻ったら作り直すようにした。2026-10-19の計測では、514MB → 330MB（約180MB減）。WebViewの描画プロセスは残る。キャストの重さが実際に改善したかは、ユーザーの確認待ち。
- **アプリ起動とカーソル移動の速さ（v0.18.0）**：計測で、ドックのボタンを押すたびにTV Homeが全アプリのラベルとアイコンを取り直し、起動を頼むまで約1.3〜1.6秒待たせていたと分かった（`getApps()` 1592ms／2回目1275ms。アイコン取得のたびに `queryIntentActivities` も走っていた）。アプリ一覧は起動時に裏で1回だけ作り、アプリの追加・更新・削除の通知（`PACKAGE_ADDED/REMOVED/CHANGED`）で作り直すようにした（ページへは `window.tvHomeAppsChanged()`）。アイコンは160pxの不可逆WebP（`data:image/webp`）にした。結果は `getApps()` 14ms、一覧データ63KB（14アプリ）。カーソル移動は、相場・経済指標の行とドックのアイコンに `will-change: transform` を付け、持ち上がりをGPUの合成で行うようにした（テレビのWebViewでの計測：相場の行を順に選ぶと、50ms超のコマ落ちが10回→1回、最大233ms→83〜100ms）。Playストアのタイルは、テレビ版の暗いアイコンを端まで伸ばしていたため、ユーザーの指示で、Wikimedia Commonsの公式アイコン（`assets/apps/google-play.svg`）を白い背景に置く形にした。
- **ホームへの戻りの速さ（v0.17.0）**：v0.14.0では、ほかのアプリが前面になって30秒たつとWebViewを破棄していたため、ホームに戻るたびに作り直しと起動演出（約1.3秒）が入り、ユーザーに「遅い」と言われた。ユーザーの希望「スマホみたいにすぐ開く」を優先し、30秒での破棄はやめた。裏では `pauseTimers()` だけを行い、WebViewの破棄はメモリ不足の合図（`TRIM_MEMORY_RUNNING_LOW` 以上）のときだけにした。破棄後に作り直すときは `index.html?instant` を開き、起動演出を省く（`body.instant`）。戻ったときは、時計をすぐ更新し、相場のWebSocketは0.3秒後、各データの再取得は0.6秒後から0.2秒ずつずらして始め、カクつきを避ける。2026-10-19に、ホームボタンですぐ戻ることをユーザーが確認した。このため、キャスト中にTV Homeが使うメモリは、v0.14.0より約180MB多い状態に戻っている。
- **リモコンの設定ボタン（v0.16.0）**：ユーザーの依頼「設定ボタンで即座にテレビの設定を開く」。リモコンは `Xiaomi RC Consumer Control` から `KEYCODE_SETTINGS`（176、scan 0x0c018f）を送る。Xiaomiのシステム（`MiTVWindowPolicyInjector`）がこのキーを先に取り、`TOGGLE_NOTIFICATION_HANDLER_PANEL` で標準ホームのパネルを開こうとする。標準ホームが無効なので失敗し、アプリにはキーが届かない。このintentはシステムアプリしか受け取れず、TV Homeで受けても無視された（試して撤去した）。そこで、ユーザーの確認を得て、ユーザー補助サービス `jp.tvhome.SettingsKeyService`（`flagRequestFilterKeyEvents`）を作った。設定ボタンだけを受け取って `Settings.ACTION_SETTINGS` を開き、ほかのキーはそのまま流し、記録しない。PCから `settings put secure enabled_accessibility_services jp.tvhome.launcher/jp.tvhome.SettingsKeyService` と `accessibility_enabled 1` で有効にした（変更前は null／0）。ホームでもほかのアプリでも開くことを、ユーザーがリモコンで確認した。戻すには `settings delete secure enabled_accessibility_services` と `settings put secure accessibility_enabled 0`、またはテレビの設定 → ユーザー補助 →「TV Home 設定ボタン」をオフにする。APKを入れ直しても有効のまま残ることを確認済み。
- **ドックの編集とアプリ一覧（v0.15.0）**：ユーザーの依頼で追加。2026-10-19にユーザーがリモコンで動作を確認した。
  - **長押しメニュー**：ドックのアプリで決定ボタンを長押し（550ms、またはキーのリピートが来た時点）すると、iOS風のメニュー（並べ替え／ドックから外す／キャンセル）が出る。短く押せば今までどおり起動する（決定はキーを離したときに処理）。ホームボタンの長押しはAndroidが先に受け取るため使えない、とユーザーに説明済み。PCのブラウザでは右クリックでも開く。
  - **並べ替え**：選んだアプリが持ち上がり、←→で移動、決定か戻るで確定する。
  - **ドックから外す**：アンインストールではなく、表示しないだけ。並び順と外したアプリは、localStorageの `tv-home-dock`（`{order, hidden}`、`dashboard/js/dock.js`）に保存する。あとから入れたアプリはドックの最後に加わる。
  - **アプリ一覧**：ドックの「設定」の手前にある「アプリ」（四角4つのアイコン）。テレビの全アプリを名前順のグリッド（6列）で出す。決定で起動、長押しで「ドックに追加／ドックから外す」。
  - **テレビの設定**：ドックの「テレビの設定」タイルは廃止した（歯車が2つ並んで紛らわしかったため）。代わりに、ドックの「設定」シートのいちばん上に「テレビの設定を開く」を置いた（`window.Android.openTvSettings()`）。
  - `getApps()` は件数の上限なしで全アプリを返し、ドックの並びはページ側で決める。地デジとXiaomiのシステムツールは、今までどおり出さない。
  - **検証時の注意**：`adb shell input keyevent --longpress` は、このテレビでは短い押し方として届く。テスト中にドック先頭のSmartTubeが起動し、続けて送ったキーで動画の再生画面に入ってしまった。ユーザーがテレビを使っている可能性があるので、キー操作を送るテストは避け、DevToolsでの確認か、ユーザーにリモコンで試してもらう。
- **未対応**：広告ブロックの切り替え（`setPrivateDns`）も未実装。ただしテレビのプライベートDNSは、すでに `dns.adguard-dns.com`（hostname）に設定されていた。

ビルドと入れ替え：

```sh
cd android
JAVA_HOME=<JDK17> ANDROID_HOME=<Android SDK> ./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk
```

テレビのIPアドレスはDHCPで変わる（2026-10-19に `192.168.0.17` になった）。`adb mdns services` で今のアドレスを確認する。このPCでは JDK 17 が `~/.local/jdk17/Contents/Home`、Android SDK が `~/.local/android-sdk`、adb が `~/.local/android-sdk/platform-tools/adb`。テレビとはワイヤレスデバッグでペア設定済み（`adb mdns services` で接続ポートが分かる。`192.168.0.178:5555` のADBも出ている）。

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
| ニュース | NHK ONE 経済RSS（`news.web.nhk`） | 15分取得。3見出しを20秒で切り替え（詳細を開いている間は止める）。決定でRSSの要約（最大240字）を表示。48時間以上前の配信を明示。旧 `www3.nhk.or.jp` のRSSは2026-08-08で更新が止まっていたため v0.6.0で変更 |
| Spotify | テレビのSpotifyアプリのMediaSession（TVアプリ）／Currently Playing API（Web版、未接続） | TVアプリは曲や状態が変わるとすぐ反映、Web版は30秒 |
| 写真 | 同梱CC0写真／Unsplash | Unsplashは1時間に8都市×3枚（計24枚）を取得し、既定60秒で切り替え。写真ごとにTV用のぼかし画像を1回作る |

時間別天気は日本時間の次の正時から6時間。日付跨ぎ・昼夜・雨雪雷・降水確率・欠測に対応。気温の線の縦幅は最低6℃で、小変動を誇張しない。3時間超の予報は古い情報として表示。地域変更時に以前の地域の値を使い回さない。

経済指標は日付・名称・日本時間を6件表示し、ページ送りで先へ進める。夏時間・日付跨ぎを処理。行は公式日程へリンク。予想・実績値は未接続で、作り物を補わない。保存日程の期限はBLSが2026年12月、BEA・FRBが2027年12月。取得失敗時は配信元ごとに保存日程を使い、「一部更新待ち」を表示する。後日のセッションでは収録期限も確認する。

## 6. Spotify・Unsplashの接続

**2026-10-19更新**：テレビのアプリでは、Unsplashは稼働中、Spotifyカードはテレビの再生情報を使う（第3.4節）。キーはユーザーのMacの `~/.config/tv-home/local.properties` にあり、Gitには入れない。以下はPCの `npm run dev`（Web版）で使う場合の手順。詳しい設定と公式リンクは [README.md](README.md)。

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
- 接続口：`window.Android.getApps()` と `window.Android.launchApp(packageName)`。広告ブロック用に任意で `getPrivateDns()` と `setPrivateDns(host)`（下記）。
- `getApps()` は `name` と `packageName` を持つ配列のJSON文字列。実機から得た妥当なパッケージ名を使う。
- 実一覧が返るとWebの固定ドックを置き換える。v0.15.0からは件数の上限なしで全アプリを返し、並びと表示はページ側（`dashboard/js/dock.js`）で決める（第3.4節）。実機の順序・ピン留め・固定ドックとの統合はフェーズ3で検討する。
- 表示名に対応する既知ロゴと未知アプリの頭文字表示に対応。起動するパッケージをロゴから推測しない。SmartTubeをYouTubeの起動先にしない。

フェーズ3の想定はKotlinの薄いランチャー＋WebView。`WebViewAssetLoader`等で安全なオリジンを用意する。従来の `addJavascriptInterface` はiframeにも公開されるため、現在はAndroidブリッジ検出中に外部TradingView iframeを無効化している。併用するならオリジン制限付きWebMessage API等で設計する。

### 広告ブロック（v0.7.0）

TV全体の広告は、AndroidのプライベートDNSをAdGuard DNS（`dns.adguard-dns.com`、DNS over TLS）にして遮断する。広告・トラッカーのドメインに `0.0.0.0` を返す。2026-10-19に、広告ドメインが `0.0.0.0` になり、本ダッシュボードの配信元とドックのアプリの主なドメインは通常どおり解決されることをDoHで確認した。YouTubeの広告はDNSでは消えないためSmartTubeが担う。動画・音声に組み込まれた広告（Prime Video・Netflixの広告付きプラン、Spotify無料版）は対象外。ユーザー向けの手順はREADMEの「広告ブロック」。

- **Web（実装済み）**：設定の「広告ブロック」。`js/adblock.js` が広告配信ホスト2つと、遮断されない比較用ホスト（`www.gstatic.com/generate_204`）へ `no-cors`・Cookieなしで接続し、有効／一部／無効／確認不可を表示する。応答は読まない。設定を開いたときに、前回の確認から60秒以上経っていれば自動で確認する。
- **フェーズ3のブリッジ（Web側は実装済み、制御レスポンスで検証）**：`getPrivateDns()` が `{"mode":"off|opportunistic|hostname","specifier":"…"}` のJSON文字列を返し、`setPrivateDns(host)` がホスト名（空文字でAndroid標準の `opportunistic` に戻す）を受け取り `{"ok":true}` または `{"ok":false,"error":"permission"}` を返す。両方あると設定にスイッチとDNSサーバー欄が出る。Web側はホスト名を検証してから渡す（設定の `adblockDns`、初期値 `dns.adguard-dns.com`）。
- Kotlin側の想定（未実装）：`Settings.Global` の `private_dns_specifier` と `private_dns_mode` を書く。`WRITE_SECURE_SETTINGS` はインストール後にPCから一度だけ `adb shell pm grant <パッケージ名> android.permission.WRITE_SECURE_SETTINGS` で与える。Kotlin側でもホスト名を検証する。

```kotlin
@JavascriptInterface fun getPrivateDns(): String = JSONObject()
  .put("mode", Settings.Global.getString(contentResolver, "private_dns_mode") ?: "opportunistic")
  .put("specifier", Settings.Global.getString(contentResolver, "private_dns_specifier") ?: "").toString()
@JavascriptInterface fun setPrivateDns(host: String): String = try {
  if (host.isEmpty()) Settings.Global.putString(contentResolver, "private_dns_mode", "opportunistic")
  else {
    require(Regex("^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\\.)+[a-z][a-z0-9-]{0,61}[a-z0-9]$").matches(host))
    Settings.Global.putString(contentResolver, "private_dns_specifier", host)
    Settings.Global.putString(contentResolver, "private_dns_mode", "hostname")
  }
  "{\"ok\":true}"
} catch (e: SecurityException) { "{\"ok\":false,\"error\":\"permission\"}" }
  catch (e: IllegalArgumentException) { "{\"ok\":false,\"error\":\"invalid\"}" }
```

- **安全上の注意**：このブリッジはTVのシステム設定を書き換えられる。従来の `addJavascriptInterface` はiframeを含む全フレームに公開されるため、`WebViewAssetLoader` で配信するアプリ自身のオリジンだけに公開する（WebMessageの許可オリジン指定など）。外部ページを同じWebViewで開かない。DNSの変更は元に戻せる設定変更で、システムアプリの無効化ではないが、実機へのコマンド実行は従来どおりユーザーの確認を取ってから行う。

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
  styles.css                   TV画面（1920×1080）の配置とガラス表現
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
  js/feeds.js                 ニュースと経済指標の取得・解析（サーバーとアプリで共用）
  js/economic-calendar.js      公式ICSの解析・日程の統合
android/                       TVアプリ（Kotlin＋WebView、第3.4節）
lib/economic-calendar.mjs      js/economic-calendar.js の再エクスポート
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

同じLANの別の端末（TVのブラウザなど）から開くなら `HOST=0.0.0.0 npm run dev` としてPCのLANアドレスへ接続する。画面はTV専用で、縦長の画面では縮小表示になる。Spotify認証にはHTTPSまたは明示的なループバックIPが必要で、LAN内HTTPでは同じ条件にならない。クラウドの127.0.0.1へ手元の端末から直接つながるわけではない。

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

- **v0.6.0の実APIと表示・操作の検証**：[browser-check.json](artifacts/browser-check.json)（2026-10-19再実行）。12契約の実価格・WebSocket・24h履歴、6時間の実予報、経済指標のページ送り、設定、通信断キャッシュ、ドックを確認。
- 画面サイズ：v0.8.0までは1920×1080、1366×768と、スマホ・縦画面（768×1024、660×1000、390×844、320×720）。v0.9.0からはTV専用で3840×2160、1920×1080、1366×768、1280×720、960×540。
- 最新実行ではBLS/BEAのライブ取得成功、FRBは保存日程。過去のBEA取得失敗時も保存日程と「更新待ち」を確認している。
- **v0.6.0の制御レスポンス検証**：[integration-check.json](artifacts/integration-check.json)（2026-10-19再実行）。Spotify PKCE正常系・不正state、背景切り替え、Androidブリッジのロゴと渡された起動先、13ボタンのスクロール、動きの軽減を確認。実認証や実機の検証ではない。
- [weather-check.json](artifacts/weather-check.json) はv0.6.0で再実行した記録。夜・欠測・日付跨ぎ・地域変更等の制御レスポンス検証。
- [market-check.json](artifacts/market-check.json) はv0.4.0の記録。廃止・切断・古い値・ソース切り替えの制御レスポンス検証。
- 単体テストは39件。過去のアプリ検証は [verification.json](artifacts/verification.json)、今回のクリーンなコピーからのテスト・ビルド・ローカル配信確認は [handoff-check.json](artifacts/handoff-check.json) を参照。
- 今回の梱包確認は別の記録として保存し、ブラウザ検証の日時を今回実施したかのように書き換えない。
- **v0.6.0（2026-10-19）**：単体テスト39件（NHK ONEのリンク許可と類似ドメイン拒否を追加）、`npm run build`、実APIの `browser-check.mjs`（全6画面サイズ・ドック・設定・通信断キャッシュ・TradingView）、`browser-integrations-check.mjs`、`browser-weather-check.mjs` が成功。`browser-check.mjs` の下端ヒント行の判定は「ドックが下端から40px以上内側」に置き換えた。
- **v0.6.1（2026-10-19）**：単体テスト41件（frostの切り抜き形状を追加）、`npm run build`、`browser-integrations-check.mjs`、`browser-weather-check.mjs` が成功。`browser-check.mjs` には「TVステージはfrostを使い、カードに `backdrop-filter` がない」「frostはTVステージだけ」「ゆっくりズームは初期オフで、設定でオンにできる」の確認を追加し、最終コードで2回連続成功（直前のほぼ同じコードでも5回成功）。Open-Meteoの予報APIがこの環境から一時的に応答しなかった間の2回は天気の取得待ちでタイムアウト。それとは別に、最初の1回だけ失敗メッセージを記録できなかったアサーション失敗があり、その後の7回では再現していない。
- **v0.7.0（2026-10-19）**：単体テスト47件（広告ブロックのホスト名検証・判定・ブリッジ・設定の6件を追加）、実APIの `browser-check.mjs`、`browser-weather-check.mjs`、`browser-integrations-check.mjs` が成功。統合検証に、広告ドメインの遮断あり／なしの判定と、模擬ブリッジへ検証済みホスト名と空文字（自動に戻す）だけが渡ること、不正なDNSサーバーを保存時に拒否することを追加した。実機のプライベートDNS変更とAPKのブリッジは未検証。
- **v0.8.0（2026-10-19）**：単体テスト47件（RSSの要約と長さ上限を追加）、新しい `browser-ux-check.mjs`（リモコン移動・ページ送り・戻る・詳細シート・設定のリモコン操作・放置時の戻り）、`browser-integrations-check.mjs`、`browser-weather-check.mjs` が成功。性能は待機中のChromium CPU 4%で、v0.6.1から悪化なし。この日はOpen-Meteoの予報APIがこの環境から接続できず、実APIの `browser-check.mjs` は天気の取得待ちでタイムアウトした。予報APIだけを制御レスポンスに置き換えた一時コピーでは全項目が成功した（記録とスクリーンショットは上書きしていない。`artifacts/` の画面はv0.7.0の実API実行時のもの）。
- **v0.9.0（2026-10-19）**：単体テスト47件、`npm run build`、`browser-ux-check.mjs`（960×540・2倍密度の確認と、↑の直後の↓で元に戻る確認を追加）、`browser-integrations-check.mjs`、`browser-weather-check.mjs` が成功。性能は待機中のChromium CPU 1.4%（天気は取得不可の状態）。Open-Meteoの予報APIはこの日もこの環境から接続できず、実APIの `browser-check.mjs` は予報と空気質だけを制御レスポンスに置き換えた一時コピーで全項目が成功（相場・WebSocket・経済指標・ニュース・TradingViewは実API、4画面サイズの縮尺確認を含む）。記録とスクリーンショットは上書きしていない。スマホ・縦画面のスクリーンショット（`dashboard-768/660/320/mobile.png`）は削除した。
- **v0.19.0（2026-10-19、ユーザーのMac）**：単体テスト57件が成功。ヘッドレスChrome（Androidブリッジを模擬）で1920×1080を撮影し、夜の同梱写真・Unsplashの昼の写真2枚（曇りのシカゴ、夕方のニューヨーク）・Web版・設定シートで、文字と色の読みやすさ、ドックの台と選択時の浮き上がり・名前ラベルを確認した。Playwrightがないためブラウザ検証スクリプトは実行していない（`browser-weather-check.mjs` は「この先6時間」を出さない仕様に合わせて修正済み）。2026-10-19 20:32にテレビへインストール（スクリーンセーバー中に `adb install -r`）。テレビの画面での見え方・負荷はユーザーの確認待ち。
- **PCのセッション（2026-10-19）**：ユーザーのMac（Intel、Node.js 24.22.0を `~/.local/node` に配置）で、単体テスト47件と `npm run build` が成功した。`npm run dev` でPCのブラウザに実データ（相場・天気・経済指標・ニュース）が表示された。Castでテレビへ送り、縮尺を修正した後に全体が収まることをユーザーが目視で確認した（第3.3節）。テレビの設定・アプリは変更していない。ブラウザ検証スクリプトはこの環境では実行していない（Playwrightがない）。
- `browser-market-check.mjs` は冒頭の1件（WebSocketの82,000を期待するが、同時刻のHTTPスナップショット81,000が後から描画される）が失敗する。**同じ失敗が未変更のv0.5.5でも再現**するため既存のテストの競合で、今回の変更によるものではない。その1件だけを飛ばした一時コピーでは、上場廃止・切断時のHTTP切り替え・古い値の表示・CoinGecko切り替えがすべて成功した（`artifacts/market-check.json` はv0.4.0の記録のまま）。

スクリーンショットの価格・時刻は撮影当時の実データ。現在価格の保証や固定表示のサンプルではない。

## 11. 未完了と次の作業候補

| 項目 | 現状 | 必要になったときの次の行動 |
| --- | --- | --- |
| TV型番・OS | 一部確認（2026-10-19、Castから） | 65インチ、Cast上の型番 `MiTV-MZTU0`、Android 14（Build UKN1.240806.017）、Cast受信ブラウザはChrome 92・960×540・密度2。Google TVかPatchWallか、WebViewの版は未確認（ADBで調べる） |
| 作業端末と接続経路 | ユーザーのMac（Intel）からADB接続済み | 第1.1節 |
| APK | v0.10.0をテレビにインストール済み・ホームに設定済み（第3.4節） | （ドックのアイコン・SmartTube・BLSは2026-10-19に対応済み）アプリ内の広告ブロック切り替え、スリープ復帰・長時間稼働の確認 |
| サーバー運用 | アプリでは不要 | ニュース・経済指標はアプリが自分で取得する。Unsplashを使う場合だけ、キーを置く場所を決める |
| Spotify | TVアプリはテレビの再生情報で稼働。Webログイン（スマホ再生の表示）は未完了 | スマホの再生も出したい、と言われたら、PCでログインしてトークンをテレビに渡す方式などを検討 |
| Unsplash | TVアプリで稼働（8都市×3枚/時） | 本番申請（上限引き上げ）、download エンドポイント、都市の変更はユーザーの希望次第 |
| TVでの認証・保存 | 設定・並び順はWebViewのlocalStorage | アプリを消すと消える。必要ならバックアップ方法を検討 |
| 性能と実機表示 | ブラウザで検証 | 文字サイズ、オーバースキャン、ぼかし負荷、スリープ復帰、長時間稼働を測定 |
| 個人写真・スポーツ・予定追加 | 現在の要件にはない | 新たに希望された場合だけ検討 |
| スクリーンセーバー | 将来の任意フェーズ | DreamService等。未着手 |

次の優先作業はまだ指定されていない。この一覧は残作業の説明であり、すべてを直ちに開始する指示ではない。フェーズ3や実認証へ進む段階で、その作業に必要な未確認事項だけ聞く。

## 12. 次の担当者への注意

- UIの基準は最新PNGと現在のコード。過去モックへ戻したり、余白へ新しいカードを埋めたりしない。
- 接続情報がない部分は必要な情報を明示する。実接続・実機確認・公開を済ませたことにしない。
- 仮価格・架空チャート・推測の指標値を本番表示に加えない。テストの制御レスポンスと実データの証拠を分ける。
- キーやトークンを `dashboard/`・`dist/`・ZIP・スクリーンショットへ含めない。秘密情報はサーバー側で管理する。
- 2026-10-19に、ユーザーの確認を得てTV Homeをインストールし、標準ホーム（launcherx）と初期設定ウィザード（setupwraith）を無効化した（戻し方は第3.4節）。その後、Spotify表示のための通知へのアクセスと、設定ボタンのためのユーザー補助サービスを、それぞれユーザーの確認を得て有効にした（第3.4節）。それ以外のシステム設定は変更していない。システムアプリの無効化は対象と影響を説明してユーザーに確認してから行う。Google Play開発者サービス・システムUI・チューナー関連を安易に止めず、標準ランチャーは代替の動作確認前に無効化しない。
- 引き継ぎ作成の依頼を、TV変更・デプロイ・インストールの許可とみなさない。
- この環境ではSites公開ヘルパーがなく未公開だった。次の環境も同じとは限らない。localhostを外部公開URLとして案内しない。
- レイアウト変更時は文字・価格・チャート・選択ラベルの衝突と複数画面幅を確認。完成形の意図を保つ小さな修正を優先する。

## 13. 同梱内容とファイルの完全性

ソース、ビルド済みdist、サーバー、テスト、実行スクリプト、設定例、出典、最新画面、検証記録、ユーザー提供画像3枚、初期モック、履歴を同梱。秘密設定・ブラウザセッション・外部ブラウザ実行環境は含まない。

展開後のプロジェクト直下で `sha256sum -c MANIFEST.sha256` を実行すると、欠損・変更を確認できる。manifest自身は対象外。ソース編集後にハッシュが変わるのは正常。

次のチャットにはZIPを添付し、[NEXT_SESSION_PROMPT.txt](NEXT_SESSION_PROMPT.txt) の文章を貼ればよい。
