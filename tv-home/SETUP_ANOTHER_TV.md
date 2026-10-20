# 別のPCとテレビにTV Homeを入れる手順

今のテレビ（Xiaomi TV、Google TV／Android 14）と同じTV Homeを、別のPCから別のテレビへ入れるための手順です。PCでアプリ（APK）を作り、Wi-Fi経由でテレビに入れて、テレビのホーム画面にします。入れたあとは、テレビだけで動きます（PCは要りません）。

いちばん楽なのは、新しいPCでClaude（デスクトップアプリ）のセッションを開き、[NEW_TV_SETUP_PROMPT.txt](NEW_TV_SETUP_PROMPT.txt) の文章を貼って任せる方法です。Claudeはこの文書を読んで進め、テレビを変える操作の前には、そのたびに確認を求めます。あなたの作業は、下の「あなたがやること」の3つだけです。

## あなたがやること

1. **今のMacから2つのファイルを新しいPCへ移す**（AirDropやUSBメモリで。メールやチャットには貼らない）
   - `~/.config/tv-home/local.properties`：Unsplashのキー（背景写真）とSpotifyのClient ID。新しいPCでも同じ場所に置く。ない場合は、Unsplashのキーを作り直す（下の「キー」）。
   - `~/.android/debug.keystore`：アプリの署名に使う鍵。同じ鍵で作ると、どちらのPCからでも同じテレビのアプリを更新できる。新しいPCでも同じ場所に置く。
2. **新しいテレビで、開発者向けオプションとワイヤレスデバッグをオンにする**（リモコンで）
   - 設定 → システム → デバイス情報 →「Android TV OS ビルド」を7回押す
   - 設定 → システム → 開発者向けオプション →「ワイヤレスデバッグ」をオン →「ペア設定コードによるデバイスのペア設定」を開く
   - 画面に出るIPアドレス:ポートと6桁のコードを、Claudeに伝える
3. **Claudeが確認を求めたら、答える**。最後に、リモコンで「設定 → 背景写真 → Unsplashから自動取得 → 保存」を選ぶ。

テレビとPCは同じWi-Fiにつないでおきます。

## 全体の流れ（Claudeが進める部分）

| 順 | 内容 | テレビの変更 |
| --- | --- | --- |
| 1 | PCに道具を入れる（Node.js・JDK 17・Android SDK・GitHub CLI） | なし |
| 2 | GitHubからソースを取る | なし |
| 3 | テストを通し、APKを作る | なし |
| 4 | テレビとADBでつなぐ | なし（ペア設定のみ） |
| 5 | TV Homeを入れ、ホームとして開くことを確かめる | あり（アプリの追加） |
| 6 | 標準のホームを止めて、ホームボタンでTV Homeが開くようにする | あり |
| 7 | 許可を2つ出す（Spotifyの再生中の曲、音量とボタン） | あり |
| 8 | 任意：SmartTube、広告ブロック（プライベートDNS） | あり |

「テレビの変更：あり」の手順は、Claudeが対象・影響・戻し方を説明してから、あなたの確認を得て行います。

## 1. PCの道具

Macでは、システムを変えずにすべて `~/.local` に入れます（今のMacと同じ。Homebrewのnodeは、Intel Macではソースからのビルドになり非常に遅いので使わない）。

| 道具 | 版 | 置き場所 | 入手先 |
| --- | --- | --- | --- |
| Node.js | 22以上（今は24.22.0） | `~/.local/node` | nodejs.org の公式アーカイブ |
| JDK | 17（今はTemurin 17） | `~/.local/jdk17` | adoptium.net の公式アーカイブ |
| Android SDK | platform-tools・`platforms;android-35`・`build-tools;35.0.0` | `~/.local/android-sdk` | developer.android.com のcommand-line toolsから `sdkmanager` で入れる。ライセンスへの同意はユーザーに確認してから |
| GitHub CLI | 最新 | `~/.local/gh` | GitHubの公式リリース。`gh auth login` はユーザーが行う |

Gradle 8.10.2 は `android/gradlew` が自動で取ってきます。

Windowsの場合も同じ構成で動きます。キーと署名の鍵は `%USERPROFILE%\.config\tv-home\local.properties` と `%USERPROFILE%\.android\debug.keystore` に置き、ビルドは `gradlew.bat` を使います。

## 2. ソースとキー

```sh
gh repo clone haraniikochan-hue/edinet-screener -- --branch ccr-123aaf7c-88ru7c
cd edinet-screener/tv-home
PATH=~/.local/node/bin:$PATH npm test
```

**キー**：`android/app/build.gradle.kts` が、ビルドのときに `~/.config/tv-home/local.properties` を読みます。中身は次の2行です（値はコミットしない、チャットに出さない）。

```
spotify.clientId=<32桁の16進数>
unsplash.accessKey=<UnsplashのAccess Key>
```

- Unsplashのキーがないと、背景は同梱の夜景1枚だけになります。作り直すときは、[Unsplash Developers](https://unsplash.com/oauth/applications) の New Application で作り、Access Keyを使います（README「写真」の節）。デモ枠は1時間50回です。1台のテレビが使うのは1時間に2回と、時間帯が変わるときの2回なので、同じキーを2台で使っても足ります。
- SpotifyのClient IDは、今は使っていません（カードはテレビのSpotifyアプリの再生中の曲を出すため）。空でも動きます。
- キーはAPKの中に入ります。作ったAPKは人に渡さないでください。

## 3. APKを作る

```sh
cd android
JAVA_HOME=~/.local/jdk17/Contents/Home ANDROID_HOME=~/.local/android-sdk ./gradlew testReleaseUnitTest assembleRelease
# できるもの：app/build/outputs/apk/release/app-release.apk
```

## 4. テレビとつなぐ

```sh
ADB=~/.local/android-sdk/platform-tools/adb
$ADB pair <IP>:<ペア設定のポート> <6桁のコード>   # ユーザーがテレビに出した値
$ADB mdns services                                # 接続先（_adb-tls-connect か _adb._tcp）を見る
$ADB connect <IP>:<ポート>
$ADB shell getprop ro.build.version.release       # Android 9以上が必要（minSdk 28）
```

テレビのIPアドレスはDHCPで変わります。つながらないときは `adb mdns services` で探し直します。

## 5. TV Homeを入れる（テレビの変更）

```sh
$ADB install -r app/build/outputs/apk/release/app-release.apk
$ADB shell am start -n jp.tvhome.launcher/jp.tvhome.MainActivity    # 開くことを確かめる
```

戻し方：`$ADB uninstall jp.tvhome.launcher`

## 6. ホーム画面にする（テレビの変更）

TV Homeが開くことを確かめてから行います。Google TVは、標準のホームを止めないと、ホームボタンで標準のホームが開きます（`cmd package set-home-activity` はGoogle TVに無視された）。

```sh
$ADB shell cmd package resolve-activity -c android.intent.category.HOME -a android.intent.action.MAIN   # 今のホームを見る
$ADB shell pm disable-user --user 0 com.google.android.apps.tv.launcherx      # Google TVの標準ホーム
$ADB shell pm disable-user --user 0 com.google.android.tungsten.setupwraith   # 代わりに出てくる初期設定の画面
```

ホームボタンでTV Homeが開けば完了です。Google TV以外のテレビでは、標準のホームのパッケージ名が違います。1行目の結果を見て決めます。Google Play開発者サービス・システムUI・チューナー関連は止めません。

戻し方：`$ADB shell pm enable com.google.android.apps.tv.launcherx` と `$ADB shell pm enable com.google.android.tungsten.setupwraith`。テレビだけで戻すときは、ドックの「設定」→「テレビの設定を開く」→ アプリ → システムアプリ → Google TV Home →「有効にする」。

## 7. 許可を2つ出す（テレビの変更）

```sh
# Spotifyカードに、テレビのSpotifyアプリで再生中の曲を出す（通知へのアクセス。通知は読まない）
$ADB shell cmd notification allow_listener jp.tvhome.launcher/jp.tvhome.MediaListener

# 「TV Home 音量とボタン」：音量の長押しの加速と、プライムビデオのボタンでSpotifyを開く
$ADB shell settings get secure enabled_accessibility_services   # 先に今の値を見る（ほかのサービスがあれば ':' でつなぐ）
$ADB shell settings put secure enabled_accessibility_services jp.tvhome.launcher/jp.tvhome.SettingsKeyService
$ADB shell settings put secure accessibility_enabled 1
```

確認：`$ADB shell dumpsys accessibility | grep "Bound services"` に「TV Home 音量とボタン」が出る。

戻し方：`$ADB shell cmd notification disallow_listener jp.tvhome.launcher/jp.tvhome.MediaListener`、`$ADB shell settings delete secure enabled_accessibility_services`（元の値があれば、その値に戻す）と `$ADB shell settings put secure accessibility_enabled 0`。テレビの設定 → ユーザー補助 でも切れます。

## 8. 任意

- **SmartTube**（広告なしのYouTube。ドックではYouTubeの絵で出る）：作者の公式GitHub（yuliskov/SmartTube）のReleasesから、テレビのCPU（`$ADB shell getprop ro.product.cpu.abi`。今のテレビは armeabi-v7a）に合う stable のAPKを取ります。GitHubが公開しているSHA-256と照合してから `adb install` します。戻し方：`$ADB uninstall org.smarttube.stable`
- **広告ブロック**：テレビのプライベートDNSを `dns.adguard-dns.com` にする（今のテレビの設定。`settings get global private_dns_specifier` で見られる）。設定画面にこの項目がない機種では、`$ADB shell settings put global private_dns_mode hostname` と `$ADB shell settings put global private_dns_specifier dns.adguard-dns.com` で設定します。戻し方は `settings put global private_dns_mode opportunistic`。

## 9. テレビで設定する（リモコンで）

- ドックの「設定」→ 背景写真 → **Unsplashから自動取得** → 保存。これで、ニューヨークの日中・夕暮れ・夜景の写真に切り替わり、ライト・ダークのテーマも変わります。
- ドックの並び：SmartTube・U-NEXT・Netflix・Prime Video・Disney+・Spotify の順に、入っているものだけが先頭に並び、ほかのアプリが続きます。決定ボタンの長押しで、並べ替えとドックから外すができます。並びはテレビごとに保存されます（前のテレビからは移りません）。
- 天気の地域は渋谷区です。設定で変えられます。

## 10. できあがりの確認

- [ ] ホームボタンでTV Homeが開く。0.7秒以内に2回押すと、テレビの設定が開く
- [ ] 時計・天気・相場・経済指標・ニュースが出る（右上に「一部更新待ち」が残らない）
- [ ] 背景がニューヨークの写真で、時間帯でライトとダークが変わる
- [ ] Spotifyアプリで再生すると、カードに曲名とジャケットが出る
- [ ] 音量ボタンを押し続けると、だんだん速く変わる
- [ ] ホームからプライムビデオのボタンを押すと、Spotifyが開く（一瞬プライムビデオが見える）

## 11. 今のテレビ（Xiaomi）と違うテレビのとき

- 画面は1920×1080を縮尺して表示するので、解像度が違っても崩れません。
- **プライムビデオのボタン**：プライムビデオが前に出た直後にSpotifyへ切り替える方式なので、ボタンでプライムビデオが開くテレビなら動きます。
- **ホームボタン2回でテレビの設定**：Androidの設定画面を開くので、どのテレビでも動きます。
- **音量の加速**：テレビが音量の変化をシステムに知らせる限り動きます。リモコンが音量をテレビ以外（サウンドバーなど）に送る場合は効きません。
- 標準のホームのパッケージ名（第6節）、開発者向けオプションの場所、ドックの固定アプリのパッケージ名（`MainActivity.kt` の `PINNED`）が違うことがあります。

## 12. その後の更新

`dashboard/` やアプリを直したら、同じ手順3でAPKを作り、`adb install -r` で入れ替えます（設定・ドックの並びは残ります）。同じ署名の鍵（`debug.keystore`）を使っていれば、どちらのPCからでも更新できます。鍵が違うと入れ替えが拒まれます。その場合はアンインストールが必要で、テレビの設定とドックの並びが消えます。

今のテレビの経緯・仕様・確定事項は [HANDOFF.md](HANDOFF.md) にあります。
