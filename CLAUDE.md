# 改善依頼管理アプリ

Power Apps Canvas App project. 6画面（HomeScreen, RequestListScreen, RequestFormScreen, RequestDetailScreen, DashboardScreen, MasterManagementScreen）のモック実装済み。モックデータは `App.pa.yaml` の Named Formula + 起動時のローカルコレクションで管理。

## Environment

- Power Apps environment ID: `0db1f4ed-2637-ebe6-b892-29f7067990b2`
- App ID: `4fe8e136-f95d-4e0b-93bb-5d97cc62b204`
- Cluster: `prod` (make.powerapps.com)

## Working with this project

- Canvas Authoring MCP server is connected to the coauthoring session above (via `/canvas-apps:configure-canvas-mcp`).
- Use `/canvas-app` to create or edit the Canvas App and its `.pa.yaml` files.
- Keep the Power Apps Studio browser tab open while working — closing it ends the coauthoring session.
- Screen rendering rules (color palette, control selection, naming conventions, layout) are defined in [SCREEN_RENDERING_RULES.md](SCREEN_RENDERING_RULES.md). Always follow it when creating or editing screens.
- App requirements (purpose, user roles, status workflow, screen specs) are defined in [REQUIREMENTS.md](REQUIREMENTS.md), converted from `要件整理.xlsx`. Check its "未確定・要確認事項一覧" section for open questions before building screens that depend on them.
- Power Fx coding conventions (variable naming, Set/UpdateContext/Collect usage, error handling, delegation, reuse) are defined in [CODING_STANDARDS.md](CODING_STANDARDS.md). Always follow it when generating or editing formulas/logic.
- The data model (SharePoint Lists: tables, columns, physical/logical names, required constraints) is defined in [DATA_MODEL.md](DATA_MODEL.md). Check its "未確認・要確認事項" section before creating the actual Lists.

## 画面実装時の作業順序

`.pa.yaml` を新規作成・編集するときは、この順序で進める。リファクタリング（命名の一貫性向上、共通化、整理など）は必ず最後に行い、動作確認より前に済ませない。

1. **重複チェック** — 新しく追加するコントロール名が、そのファイル内だけでなく**アプリ全体（他の画面ファイルも含む）**で一意か確認する。Power Appsのコントロール名はアプリ全体でユニークである必要があり、画面間で同じ名前（`grpRoot`, `btnNavHome` など）を使い回すと `compile_canvas` でエラーになる。
2. **YAML検証** — レコードリテラル（`{ Key: value }`）を含む数式がプレーンスカラーのまま書かれていないか確認し、必要な箇所をクォートする。複数行の数式は `|-` を使う。
3. **コンパイル** — `compile_canvas` を実行し、構文・プロパティ・参照のエラーを解消する。
4. **命名チェック** — [SCREEN_RENDERING_RULES.md](SCREEN_RENDERING_RULES.md) 6章の命名規則（画面名・コントロール名のプレフィックス）に沿っているか確認する。
5. **レビュー** — [REQUIREMENTS.md](REQUIREMENTS.md) の該当画面仕様、[CODING_STANDARDS.md](CODING_STANDARDS.md) の数式規約と突き合わせて内容を確認する。
6. **リファクタリング** — 上記すべてが完了した後に、重複ロジックの共通化・コメント整理などを行う。

### `AlignInContainer`/`DropShadow` を一律追加するときの注意

[SCREEN_RENDERING_RULES.md](SCREEN_RENDERING_RULES.md) のルールに従い、`AlignInContainer` や `DropShadow` を複数コントロールへまとめて追加するときは、**一律で同じ値（`Start`/`None`など）を入れない。**

- 追加する前に、**親コンテナに `LayoutAlignItems` が既に設定されていないか**を先に確認する。親が `LayoutAlignItems.Center`/`End` になっている場合、子要素の `AlignInContainer` を一律 `Start` にすると、既存の意図した中央寄せ・右寄せを無言で上書きしてしまう。
- 正しい手順: ①対象コントロールの親の `LayoutAlignItems` を確認する → ②親の設定に合わせた値（`Start`/`Center`/`End`）を子要素の `AlignInContainer` に設定する → ③まとめて追加した後は、必ず親ごとに値が親の意図と一致しているか読み直す。
- 機械的なスクリプト（`sed`/Pythonなど）で一括挿入する場合は特に注意する。挿入後に `grep` 等で「`LayoutAlignItems` を持つ親コンテナ」を洗い出し、その配下の子要素の値が一致しているか個別に確認すること。
