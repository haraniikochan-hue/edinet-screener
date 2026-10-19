# CLAUDE.md

このリポジトリは、自宅の Xiaomi TV（Google TV 想定）用の自作ホーム画面（ランチャー）とダッシュボードを作るプロジェクト。

- 最初に **`START_HERE.md`・`HANDOFF.md`・`AGENTS.md`** を読む。現行はv0.6.0（v0.5.5の配置を保ったデザイン刷新）。ユーザーはApple／iOSのようなデザインを好み、UIをさらに洗練させたいと考えている。
- デザインの基準は `dashboard/` と `artifacts/dashboard-desktop.png`。`mockups/` と `docs/HANDOFF_HISTORY.md` は過去の経緯。
- 確定済みの地域・銘柄・朝晩の表示・アプリ・余白を引き継ぐ。SmartTubeは見た目だけYouTubeであり、起動先をYouTubeに変えない。
- 未接続事項と次の作業候補は `HANDOFF.md` に記載。次の依頼に必要な未確認情報だけ質問する。
- `dashboard/`を編集し、`npm run build`で`dist/`を再生成する。実API・制御レスポンス・実機未検証を区別して記録する。
- API キーはコミットしない。
- TVのシステムアプリを無効化するコマンドは、対象と影響を説明してユーザーの確認を取ってから実行する。引き継ぎ作成はTV変更や公開の許可ではない。
