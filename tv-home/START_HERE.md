# TV Home — 最初に読むファイル

TV Home は、自宅の Xiaomi TV（65インチ、Google TV／Android 14）用に作った自作のホーム画面です。**v0.20.0のAndroidアプリとして、テレビのホーム画面になっています**（2026-10-19、標準ホームは無効化済み）。中身は `dashboard/` のダッシュボード（Apple／iOS風、TV専用）を、`android/` のアプリがWebViewで表示する作りです。

## 次のセッションへ渡す方法

次のセッションも**ユーザーのMac上**で動かす（Claude Desktopアプリ）。クラウドのセッションからは家のWi-Fiとテレビに届かないため。

1. GitHubの `haraniikochan-hue/edinet-screener` をcloneしてブランチ `ccr-123aaf7c-88ru7c` に切り替え、`tv-home/` フォルダで作業する。
2. そのフォルダでセッションを開き、[NEXT_SESSION_PROMPT.txt](NEXT_SESSION_PROMPT.txt) の文章を貼る。
3. やりたいことを伝える。

## 読む順番

- [HANDOFF.md](HANDOFF.md)：現在の仕様、確定事項、テレビに加えた変更と戻し方、未対応。**第1節（現在地）・第1.1節（始め方）・第3.4節（TVアプリ）を最初に読む。**
- [AGENTS.md](AGENTS.md) / [CLAUDE.md](CLAUDE.md)：作業のルール。
- [README.md](README.md)：Web版の起動、Spotify・Unsplash等の接続手順。

過去の相談は [docs/HANDOFF_HISTORY.md](docs/HANDOFF_HISTORY.md)、参考画像は [references/README.md](references/README.md)。`mockups/` は初期案で、最新仕様ではありません。

## すぐ動かす

ユーザーのMacには、Node.js・JDK・Android SDK・GitHub CLIが `~/.local` に入っています（HANDOFF第1.1節）。

```sh
PATH=~/.local/node/bin:$PATH npm test      # 単体テスト（57件）
PATH=~/.local/node/bin:$PATH npm run dev   # PCのブラウザで http://127.0.0.1:4173/
cd android && ./gradlew assembleRelease    # テレビ用APK（JAVA_HOME・ANDROID_HOMEは第1.1節）
```

テレビへの入れ替えは `adb install -r` です。テレビのIPアドレスは変わるので、`adb mdns services` で確認します。テレビを変更する操作は、ユーザーの確認を取ってから行います。
