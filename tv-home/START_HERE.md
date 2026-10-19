# TV Home — 最初に読むファイル

この一式は **v0.9.0のWebダッシュボード**を次セッションへ渡すためのものです。v0.5.5の配置を保ったままApple／iOSの考え方でデザインを刷新し、TV向けの軽量化、広告ブロック、リモコン操作の改善を加え、TV専用（スマホ・縦画面の配置なし）にした版です。

## 次のセッションへ渡す方法

次のセッションは**ユーザーのPC上**で動かす（Claude Desktopアプリ、またはPCのターミナルで `claude remote-control`）。クラウドのセッションからは家のWi-Fiとテレビに届かないため（[HANDOFF.md](HANDOFF.md) 第1.1節）。

1. PCでソースを用意する。GitHubの `haraniikochan-hue/edinet-screener` をcloneしてブランチ `ccr-123aaf7c-88ru7c` に切り替え、`tv-home/` フォルダで作業する。または `tv-home-handoff-v0.9.0.zip` を展開する。
2. そのフォルダでセッションを開き、[NEXT_SESSION_PROMPT.txt](NEXT_SESSION_PROMPT.txt) の文章を貼る。
3. Wi-Fi／テレビで何をしたいか（テレビで表示を見る、型番を調べる、広告ブロック、APKなど）を伝える。

このZIPでコード・画像・仕様・履歴を確認できます。前のチャットの全文を別途渡す必要はありません。

## 読む順番

- [HANDOFF.md](HANDOFF.md)：現在の仕様、確定事項、未対応、次の作業への注意。
- [最新の画面](artifacts/dashboard-desktop.png)：見た目の基準。Disney+・Spotify追加済み。
- [README.md](README.md)：起動、Spotify・Unsplash等の接続手順。
- [verification.json](artifacts/verification.json)：ブラウザ検証と未検証範囲。
- [handoff-check.json](artifacts/handoff-check.json)：今回のクリーンなコピーでの梱包確認。

過去の相談は [docs/HANDOFF_HISTORY.md](docs/HANDOFF_HISTORY.md)、参考画像は [references/README.md](references/README.md)。最新レイアウトは上のPNGと現在のコードです。

## すぐ起動する

Node.js 22.9以降を用意し、展開したプロジェクトフォルダで実行します。npm依存のインストールは不要です。

```sh
npm run dev
```

`http://127.0.0.1:4173/` を開きます。HTMLのダブルクリックではなく、サーバー経由で表示してください。

必要なら `npm test` と `npm run build` を実行できます。APIキーなしでも相場・天気などは動きます。Spotifyの実認証とUnsplashの自動写真取得は別途設定が必要です。

APK・TV実機接続・ホスティング公開はまだです。次の作業は新しい依頼に沿って進めます。
