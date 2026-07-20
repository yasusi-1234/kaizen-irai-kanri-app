# コーディング規約（改善依頼管理アプリ）

Power Fx（数式・変数・データ操作）のコーディング規約。
`SCREEN_RENDERING_RULES.md` が「見た目・Control仕様」のルールであるのに対し、本書は「ロジック・数式の書き方」のルール。
`/canvas-app` で数式やロジックを生成・編集するときは、本書の内容を優先して適用する。

---

## 1. 変数の命名規則

Power Appsの変数の種類ごとに接頭辞を固定する。

| 種類 | 接頭辞 | 例 | 用途 |
|---|---|---|---|
| グローバル変数（`Set`） | `glb` | `glbCurrentUserRole` | アプリ全体で使う状態（ログインユーザー情報、ロールなど） |
| コンテキスト変数（`UpdateContext`） | `loc` | `locSelectedRequest` | 画面内だけで完結する状態（選択行、入力値など） |
| コレクション（全件キャッシュ） | `col` + `All` | `colRequestAll` | データソースから取得した全件のローカルキャッシュ |
| コレクション（絞り込み後・表示用） | `col` + `View` | `colRequestView` | 検索・フィルタ・並び替えを適用した、画面に表示する一覧 |
| 名前付き数式（`Named Formula`） | 接頭辞なし（意味のある名詞） | `CurrentUserIsAdmin` | アプリ起動時に自動計算される派生値 |

- `varTemp`, `var1` のような意味のない名前は禁止。必ず「何を表す値か」がわかる名前にする。
- コレクションを「全件キャッシュ」と「表示用に絞り込んだもの」の2段階で持つ画面（一覧画面など）では、`All`/`View` を必ず使い分ける。1つしか持たない画面では `colRequestList` のように用途がわかる名前でよい（無理に `All`/`View` を付けない）。

### 真偽値（Boolean）変数の命名

`glb`/`loc` の接頭辞の後に、値の意味に応じて次のいずれかを続ける。

| 接頭辞 | 意味 | 使う場面 | 例 |
|---|---|---|---|
| `Is` | 状態・モードを表す | 今どういう状態/モードか（トグルできる状態） | `locIsEditMode`, `locIsLoading`, `locIsDialogVisible` |
| `Has` | 存在・保有を表す | 何かを持っている/存在するか | `locHasAttachment`, `locHasUnsavedChanges` |
| `Can` | 可否・権限を表す | その操作が許可されているか（権限・条件による） | `glbCanApprove`, `locCanSubmit`, `glbCanManageMaster` |

どれに当てはまるか迷った場合は「状態の名前で言えるなら `Is`」「『〜がある』で言えるなら `Has`」「『〜できる』で言えるなら `Can`」で判断する。

- 依頼（Request）関連のコレクション/変数は `Request` を、コメントは `Comment` を、マスタは対象名（`Category`, `Priority`, `Status` など）を名前に含める。

## 2. `Set` / `UpdateContext` / `Collect` の使い分け

### グローバル変数（`glb`） vs コンテキスト変数（`loc`）

- **判断基準**: その値を3画面以上から参照する必要があるか？
  - **Yes** → `Set()` によるグローバル変数（`glb`）。ログインユーザー情報、ロール判定など、アプリ全体に関わるものに限定する。
  - **No**（1〜2画面で完結する） → `UpdateContext()` によるコンテキスト変数（`loc`）。基本はこちらを優先する。
- 「今は2画面だけで使っているが将来増えるかも」という理由で先回りして `glb` にしない。実際に3画面目が必要になった時点で `loc` → `glb` に昇格させる。
- `App.OnStart` でのグローバル変数初期化は最小限にする（起動が遅くなるため）。ユーザー情報・ロール判定など起動時に必ず必要なものだけに絞る。

### コレクション（`col`）

- 一覧データや複数レコードの塊は `Collect()` / `ClearCollect()` によるコレクション（`col`）を使う。
- `colXxxAll`（全件キャッシュ）と `colXxxView`（表示用）を分けて持つ場合、`View` の再生成タイミングは以下を基本とする。
  - 画面表示時（`OnVisible`）に `colXxxAll` を取得し、`colXxxView` を初期生成する。
  - 検索・フィルタ・並び替えの各コントロール（`ModernTextInput`, `ModernDropdown` など）の `OnChange` で、`colXxxAll` を元に `colXxxView` を `ClearCollect` し直す。
  - `colXxxAll` 自体を再取得するのは、保存・更新操作の直後、または明示的な「更新」操作のときのみとする（画面を触るたびに毎回サーバーへ取りに行かない）。
- フィルタ条件が単純で1箇所でしか使わない場合は、`colXxxView` を別途持たず、Gallery等の `Items` に `Filter(colXxxAll, ...)` を直接書いてよい。絞り込みロジックが複雑・複数箇所で再利用される場合にのみ `colXxxView` として実体化する。

### 画面間の値の受け渡し

- 画面遷移（`Navigate()`）で次の画面に値を渡す場合は、**`Navigate` の第3引数（`UpdateContextRecord`）を第一選択**とする。
- 次の例外の場合のみ、グローバル変数またはコレクションを使ってよい。
  - **グローバル変数**: 遷移先の1画面だけでなく、そこからさらに先の画面でも同じ値が必要な場合（受け渡しが2画面より先まで連鎖する場合）。
  - **コレクション**: 渡したいデータがテーブル型で、かつコンテキスト変数だけでは扱いきれない場合（複数画面をまたいで編集・参照が続く一覧データなど）。

## 3. データソース操作（Patch / SubmitForm / Collect）

- 更新系操作（`Patch`, `SubmitForm`, `Remove`, `RemoveIf`）は、必ず `IfError` または `IsError` でラップし、失敗時に `Notify()` でユーザーにフィードバックする。

```powerfx
IfError(
    Patch(
        Requests,
        ThisItem,
        { Status: "受付済み" }
    ),
    Notify("更新に失敗しました。時間をおいて再度お試しください。", NotificationType.Error)
)
```

- 成功時のフィードバック（画面遷移・`Notify`・`Reset`）も操作の直後に書き、放置しない。
- `Patch` で更新するフィールドは、必要なものだけを明示的に指定する。レコード全体を丸ごと再構築するような冗長な `Patch` は書かない。
- モック段階（実データソース未接続時）では `Patch` / `SubmitForm` / `Flow.Run` / `Collect` / `ClearCollect` は使わず、サンプルの `Table()` をその場で定義して表示のみ行う（`SCREEN_RENDERING_RULES.md` 第2部と同じ方針）。

### ステータス変更処理の共通化

- ステータス変更は、必ず [REQUIREMENTS.md の 3.4 節](REQUIREMENTS.md#34-ステータス別の操作ボタン画面④の仕様に対応) に定義された遷移のみを許可する。
- この制約を徹底するため、ステータス変更を行う `Patch` は各画面・各ボタンに直接書かず、**共通コンポーネント（例: `cmpStatusActionButton`）に集約する。**
  - 入力プロパティに対象レコードと遷移先ステータス（`InTargetRequest`, `InNewStatus`）を渡し、コンポーネント内部で許可された遷移かどうかの判定・`Patch`・エラーハンドリングをまとめて行う。
  - 各画面のボタンはこのコンポーネントを置くだけにし、`Patch` やステータスの遷移可否判定を画面側に重複して書かない。
- 新しいステータス遷移が必要になった場合も、このコンポーネント内の判定ロジック1箇所を直せばよい状態を保つ。

### 楽観的ロック（同時編集対策）

複数人が同じ依頼を同時に開いて更新する可能性があるため、以下の方式で対応する。

- `Patch` が失敗した場合（`IsError`）は、「他のユーザーが先に更新した可能性がある」ものとして扱う。
- 失敗時は、対象レコードをデータソースから再取得（`LookUp` などで最新化）し、画面の表示（`loc` のローカル状態）を最新の内容で上書きする。
- その上で `Notify()` により「最新の内容に更新されたため、再読み込みしました。内容をご確認のうえ、必要であれば操作をやり直してください。」等を表示し、ユーザーの入力をそのまま強制的に上書き保存はしない。
- 更新系ボタンは連打による二重実行を防ぐため、実行中は `locIsSubmitting`（[1章](#真偽値boolean変数の命名)の命名規則）で `DisplayMode.Disabled` にする。

```powerfx
UpdateContext({ locIsSubmitting: true });
IfError(
    Patch(
        Requests,
        locSelectedRequest,
        { Status: "受付済み" }
    ),
    // 競合更新の可能性: 最新データを再取得して再表示し、ユーザーの操作はやり直してもらう
    UpdateContext({ locSelectedRequest: LookUp(Requests, ID = locSelectedRequest.ID) });
    Notify("最新の内容に更新されたため再読み込みしました。ご確認のうえ再度操作してください。", NotificationType.Warning)
);
UpdateContext({ locIsSubmitting: false })
```

### 添付ファイルの扱い

- `Attachments` コントロールを介した添付ファイルの追加・削除は `Patch` 側では配列（`Table`）として扱われる点に注意する。
- 詳細な運用ルール（サイズ上限、許可する拡張子など）は、実装フェーズで添付ファイル機能に着手する際に本章へ追記する。現時点では上記の共通ルール（`IfError`でのラップ、失敗時の`Notify`）を踏襲すれば十分とする。

## 4. 数式の書き方

- 3行を超える数式は必ず改行・インデントして書く。1行に詰め込まない。
- **関数呼び出しのネストが2階層を超える場合は改行する。** 文字数ではなくネスト階層を基準とする（日本語コメントが混じると文字数基準は当てにならないため）。

```powerfx
// 1階層のみ → 改行不要
CountRows(colRequestAll)

// 2階層以上のネスト → 改行する
Filter(
    Sort(colRequestAll, DueDate),
    Status <> "完了"
)
```

- ネストした `If` は禁止。分岐条件によって書き方を使い分ける。
  - **値の完全一致で分岐する場合**（文字列・数値などの単純な一致判定） → `Switch` を使う。
  - **範囲・比較・複合条件で分岐する場合**（`<`, `>`, `And`, `Or` などを使う判定） → `Switch` では書けないため、`If` の複数条件版（`If(cond1, result1, cond2, result2, ..., defaultResult)`）をフラットに並べて書く。ネストさせず、`Switch` と同じ見た目になるように書く。

```powerfx
// ❌ 避ける（ネストしたIf）
If(Status = "未受付", "受付する", If(Status = "受付済み", "対応開始", If(Status = "対応中", "確認依頼", "")))

// ✅ 値の完全一致 → Switch
Switch(
    Status,
    "未受付", "受付する",
    "受付済み", "対応開始",
    "対応中", "確認依頼",
    ""
)

// ✅ 範囲・複合条件 → Ifをネストさせずフラットに並べる
If(
    DueDate < Today(), "期限超過",
    DueDate = Today(), "本日期限",
    "期限内"
)
```

- 同じ式（同じデータソースへの参照、同じフィルタ条件）を画面内で2回以上書く場合は、コンテキスト変数やコレクションに一度だけ計算して使い回す。式の重複コピペは禁止。
- 複雑な計算で中間結果に名前を付けたい場合は `With()` を使う。

```powerfx
With(
    { overdueCount: CountRows(Filter(colRequestAll, DueDate < Today(), Status <> "完了")) },
    If(overdueCount > 0, $"期限超過 {overdueCount} 件", "期限超過なし")
)
```

- 真偽値を返す式は `If(cond, true, false)` のような冗長な書き方をせず、`cond` をそのまま使う。[1章](#真偽値boolean変数の命名)の命名規則に沿った変数であれば、そのまま条件として使えるはずである。

```powerfx
// ❌ 避ける
If(locIsEditMode = true, ...)

// ✅ こちらを使う
If(locIsEditMode, ...)
```

- 文字列結合は `&` の羅列ではなく、複数箇所を組み立てる場合は `$"..."`（文字列補間）を使う。

### `ModernDropdown`/`ModernCombobox` の「未選択」判定はコントロール自身の`Selected`/`SelectedItems`に頼らない

**`Default` を指定していない `ModernDropdown`/`ModernCombobox` でも、`Selected`/`SelectedItems` が空（`Blank()`）になるとは限らない。** 実機で「フィルタを何もかけていないのに一覧が0件になる」障害として実際に発生した。

- `IsBlank(ddlCategoryLs.Selected.Title)` や `CountRows(cmbAssigneeFilter.SelectedItems) = 0` のような式で「ユーザーがまだ何も選んでいないか」を判定しようとすると、内部的に何か選択済み状態になっているため `false`（＝選択済み扱い）になり、意図せず絞り込み条件が有効化されてしまうことがある。
- この状態で `Filter` の条件に使うと、他の絞り込み条件を全部外していても該当ゼロ件になる。`IfError` で包んでも救えない。**`IfError` は本当にエラーが起きたときだけ`fallback`を返す関数であり、単に条件式が`false`と評価される場合はエラーではないため素通しする。** 「原因不明の0件」に遭遇したとき、`IfError`のせいだと決めつけて別の箇所を疑わない、ということがないようにする。

**回避策**: コントロール自身の選択状態を直接参照せず、**「ユーザーが実際に選択操作をしたかどうか」を明示的な`loc`変数で管理し、`OnChange`でのみ更新する。**

```powerfx
// ❌ コントロール自身のSelectedに「未選択=Blank」を期待する
// OnVisible: 何もしない（ddlCategoryLsはDefault未指定）
// Filter条件:
(IsBlank(ddlCategoryLs.Selected.Title) || CategoryTitle = ddlCategoryLs.Selected.Title)

// ✅ 明示的なloc変数で「絞り込み中か」を管理する
// OnVisible:
UpdateContext({ locCategoryFilterTitle: Blank() })

// ddlCategoryLsのOnChange（ユーザーが実際に選んだときだけ発火）:
UpdateContext({ locCategoryFilterTitle: ddlCategoryLs.Selected.Title })

// Filter条件（loc変数を見る。ddlCategoryLs.Selectedは直接参照しない）:
(IsBlank(locCategoryFilterTitle) || CategoryTitle = locCategoryFilterTitle)

// 検索条件クリアボタンでも、Reset(ddlCategoryLs)と合わせてloc変数もBlank()に戻す
```

- 複数選択（`ModernCombobox`の`SelectedItems`）の場合も同様に、`CountRows(...) > 0`をそのまま条件に使わず、`OnChange`で真偽値の`loc`変数（例: `locHasAssigneeFilter`）を更新し、そちらで「絞り込みが有効か」を判定する。実際に選択されたリストの中身（`SelectedItems`自体）を参照するのは、その`loc`変数が`true`のときだけにする。
- この問題は`ModernDropdown`と`ModernCombobox`の両方で確認済み。同系統の選択コントロール（`ModernRadio`等）を同様の「未選択判定」に使う場合も、同じ回避策を優先し、コントロール自身の`Selected`が`Blank()`になることを無条件に信頼しない。

## 5. デリゲーション

- `Filter` / `Search` / `Sort` は、対象データソースがデリゲート可能な関数・演算子のみで組み立てる。デリゲーション非対応の関数（`CountRows` を大規模データに使う、`in` 演算子の誤用など）をフィルタ条件に含めない。
- 依頼一覧（`②依頼一覧画面`）のように将来的にレコード数が増える画面は特に注意し、絞り込み条件はデータソース側で評価される形（列に対する単純な比較演算子の組み合わせ）で書く。
- デリゲーション非対応の警告（黄色い三角）が出る式は放置せず、書き方を見直す。どうしても回避できない場合は、その理由をコメントで残す。

### デリゲート不可な条件はどうしても必要な場合、2段階方式にする

フリーワード検索（複数列にまたがる部分一致など）のように、どうしてもデリゲートできない条件がある場合は、1回の `Filter` に全条件を混ぜない。次の2段階に分けて書く。

1. **1段階目（サーバー側）**: デリゲート可能な条件（ステータス・カテゴリ・優先度・担当者など、列への単純な比較演算子）だけで `Filter` し、`colRequestFiltered` のようなコレクションに `ClearCollect` する。この時点ではデータソース全体に対して正しく絞り込まれている。
2. **2段階目（ローカル）**: 1段階目で絞り込んだ結果（後述の上限内に収まっている）に対して、デリゲート非対応の条件（フリーワードの部分一致など）を `Filter` でさらに絞り込む。ローカルなコレクションに対する `Filter` はデリゲーションの対象外なので警告は出ない。

```powerfx
// 1段階目: デリゲート可能な条件だけでサーバー側に絞り込む
ClearCollect(
    colRequestFiltered,
    Filter(
        Requests,
        (IsBlank(locFilterStatus) Or Status = locFilterStatus),
        (IsBlank(locFilterCategory) Or Category = locFilterCategory),
        (IsBlank(locFilterPriority) Or Priority = locFilterPriority)
    )
);

// 2段階目: フリーワード検索（デリゲート非対応）は1段階目の結果に対してのみ行う
ClearCollect(
    colRequestView,
    If(
        IsBlank(locSearchText),
        colRequestFiltered,
        Filter(
            colRequestFiltered,
            locSearchText in Title Or locSearchText in Content
        )
    )
)
```

- 注意: 1段階目の絞り込み結果自体が後述の上限（2000件）を超える可能性がある場合は、2段階方式でも取りこぼしが起きる。その際はデフォルトで「自分の依頼のみ」等の条件を必須にするなど、1段階目の時点で十分に絞り込める設計にする。

### データ行数の上限

- 非デリゲート処理が絡む画面では、`App` の詳細設定（Data row limit for non-delegable queries）を既定の500件から **2000件** に引き上げる。
- 2000件でも収まらない可能性がある場合は、上記の「1段階目で十分に絞り込む」設計を優先し、上限のさらなる引き上げでは対処しない。

### データソースの種類について

- デリゲート可能な関数・演算子はデータソースの種類（SharePoint / Dataverse など）によって異なる。データソースは本書作成時点では未確定（`REQUIREMENTS.md` にも記載なし）のため、データソース確定時に本章の記述を見直す。

## 6. エラーハンドリング・ユーザー通知

- ユーザー操作の失敗（保存失敗、必須項目未入力など）は必ず `Notify()` でフィードバックする。サイレントに失敗させない。
- 確認ダイアログが必要な操作（登録・削除・取消など不可逆な操作）は、`SCREEN_RENDERING_RULES.md` の「インタラクション・状態」ルールに従い、`loc` のコンテキスト変数でダイアログ表示状態を管理する。

### `Notify` の種類の使い分け

| 種類 | 使う場面 |
|---|---|
| `NotificationType.Success` | ユーザーが意図した操作（保存・登録・ステータス変更など）が正常に完了した |
| `NotificationType.Error` | 操作が失敗した（`Patch` 失敗、権限エラーなど） |
| `NotificationType.Warning` | 操作自体は完了したが注意が必要（[3章](#楽観的ロック同時編集対策)の楽観的ロックで再取得が発生した、期限が近い、など） |
| `NotificationType.Information` | エラーでも警告でもない、単なる状態通知（フィルタ結果0件など） |

- 表示時間は基本的に既定値のまま指定しない。ただし `NotificationType.Error` のみ、読み切る前に消えないよう明示的に長め（目安5000ms）を指定する。

```powerfx
Notify("更新に失敗しました。時間をおいて再度お試しください。", NotificationType.Error, 5000)
```

### 必須項目の入力チェック

- 送信ボタンの `DisplayMode` による全体制御に加えて、**未入力の項目自体にもエラー表示を行う。** 送信ボタンが押せないだけでは、ユーザーがどの項目のせいか気づけないため。
- 各入力コントロールの直下に、エラー用の `ModernText`（赤字、[SCREEN_RENDERING_RULES.md](SCREEN_RENDERING_RULES.md) の禁止色ではなく明確な警告色）を配置し、該当項目が未入力のときだけ `Visible` にする。
- エラー表示は「画面を開いた直後」ではなく、**送信を1度試みた後**、または該当項目からフォーカスが外れた後に表示する。何も入力していない初期状態からいきなり赤字だらけにしない。
- このオン/オフは `locIsValidationVisible`（[1章](#真偽値boolean変数の命名)の命名規則）のようなコンテキスト変数で管理し、送信ボタン押下時に `true` にする。

```powerfx
// 送信ボタン OnSelect
UpdateContext({ locIsValidationVisible: true });
If(
    IsBlank(inpTitle.Value) Or IsBlank(inpCategory.Selected),
    Notify("必須項目が未入力です。", NotificationType.Error),
    /* 登録処理へ */
)

// タイトル欄のエラーラベル Visible
locIsValidationVisible And IsBlank(inpTitle.Value)
```

## 7. コメント

- 数式が「何をしているか」ではなく「なぜそう書いたか」が非自明な場合のみコメント（`//`）を書く。単純な代入や自明なフィルタにコメントは不要。
- デリゲーション制約やPower Apps特有の制約を回避するための書き方には、理由を1行コメントで残す。
- コメントは日本語で統一する（本書・他の規約ドキュメントと同様）。

```powerfx
// CountRows はデリゲート非対応のため、事前に ClearCollect したコレクションに対して実行する
CountRows(colRequestAll)
```

## 8. 再利用性

### Named Formula とコンポーネントの使い分け

**Named Formula はパラメータを取れず、`ThisItem` のような画面文脈も持てない。** そのため用途は次のように分ける。

| 用途 | 手段 |
|---|---|
| 副作用のない値・定数テーブルの一元化（例: ステータスごとの色のマッピング表） | **Named Formula**（`App.Formulas` に切り出す） |
| レコードごとに結果が変わる判定（例: この依頼が期限超過かどうか） | 呼び出し側で `LookUp`/`Filter` 等を使い、都度その場で評価する（Named Formula化はしない） |
| `Patch`/`Notify` など副作用を伴う再利用ロジック（例: [3章](#ステータス変更処理の共通化)のステータス変更） | **コンポーネント**（入力プロパティで対象を受け取り、内部で副作用を実行する） |
| 繰り返し使うUIパターン（ステータスバッジ、確認ダイアログなど） | **コンポーネント化**を検討する |

- ステータスの `Badge` 表示（`ThemeColor`/`Appearance`）は、[SCREEN_RENDERING_RULES.md の 2章](SCREEN_RENDERING_RULES.md#ステータスカラーbadge-の-themecolor-を正とする) の対応表と一致する定数テーブルを Named Formula として1箇所に定義し、使う側は `LookUp` で参照する。画面ごとに `Switch`/`If` で色分けロジックをコピーしない。

```powerfx
// App.Formulas（Named Formula）
StatusThemeMap = Table(
    { Status: "未受付", ThemeColor: 'BadgeCanvas.ThemeColor'.Subtle, Appearance: 'BadgeCanvas.Appearance'.Tint },
    { Status: "受付済み", ThemeColor: 'BadgeCanvas.ThemeColor'.Informative, Appearance: 'BadgeCanvas.Appearance'.Tint },
    { Status: "対応中", ThemeColor: 'BadgeCanvas.ThemeColor'.Brand, Appearance: 'BadgeCanvas.Appearance'.Tint },
    { Status: "確認待ち", ThemeColor: 'BadgeCanvas.ThemeColor'.Warning, Appearance: 'BadgeCanvas.Appearance'.Tint },
    { Status: "完了", ThemeColor: 'BadgeCanvas.ThemeColor'.Success, Appearance: 'BadgeCanvas.Appearance'.Tint },
    { Status: "差戻し", ThemeColor: 'BadgeCanvas.ThemeColor'.Severe, Appearance: 'BadgeCanvas.Appearance'.Tint },
    { Status: "保留", ThemeColor: 'BadgeCanvas.ThemeColor'.Important, Appearance: 'BadgeCanvas.Appearance'.Tint },
    { Status: "対応不可", ThemeColor: 'BadgeCanvas.ThemeColor'.Danger, Appearance: 'BadgeCanvas.Appearance'.Tint },
    { Status: "取消", ThemeColor: 'BadgeCanvas.ThemeColor'.Subtle, Appearance: 'BadgeCanvas.Appearance'.Outline }
);

// 使う側（画面・コンポーネント内、Badgeコントロールのプロパティ）
ThemeColor: =LookUp(StatusThemeMap, Status = ThisItem.Status).ThemeColor
Appearance: =LookUp(StatusThemeMap, Status = ThisItem.Status).Appearance
```

## 9. 出力前チェックリスト

**変数・命名（1〜2章）**

- [ ] 変数名が接頭辞規則（`glb`/`loc`/`col`）に沿っているか
- [ ] 真偽値変数が `Is`/`Has`/`Can` の意味に沿って命名されているか
- [ ] コレクションの `All`/`View` を必要な画面で使い分けているか
- [ ] グローバル変数（`glb`）は本当に3画面以上から参照する値だけか（先回りでglbにしていないか）
- [ ] 画面間の値渡しは `Navigate` の第3引数を基本にしているか（`glb`/コレクションは例外条件に該当する場合のみか）

**データソース操作（3章）**

- [ ] 更新系操作（`Patch`/`SubmitForm`/`Remove`）が `IfError`/`IsError` でラップされているか
- [ ] ステータス変更が画面に直接 `Patch` されず、共通コンポーネント経由になっているか
- [ ] ステータス遷移が `REQUIREMENTS.md` の 3.4 節から外れていないか
- [ ] `Patch` 失敗時に最新データを再取得し、`Notify` で利用者に伝えているか（楽観的ロック対応）
- [ ] 更新系ボタンが連打防止（`locIsSubmitting`）で二重実行しないようになっているか
- [ ] モック段階で `Patch`/`SubmitForm`/`Flow.Run` を誤って使っていないか

**数式の書き方（4章）**

- [ ] ネストした `If` がなく、`Switch` または フラットな複数条件 `If` になっているか
- [ ] 関数ネストが2階層を超える式は改行されているか
- [ ] 同じ式を2回以上書いていないか（変数・`With`・Named Formulaへの切り出し漏れ）
- [ ] `ModernDropdown`/`ModernCombobox`の「未選択」判定を`IsBlank(ddlXxx.Selected...)`/`CountRows(cmbXxx.SelectedItems) = 0`のようにコントロール自身の状態で直接判定していないか（`Default`未指定でも`Blank()`にならないことがある。`OnChange`で更新する明示的な`loc`変数を使う）

**デリゲーション（5章）**

- [ ] デリゲーション警告が出ていないか
- [ ] デリゲート不可な条件が、1段階目（サーバー側）と2段階目（ローカル）に分けて書かれているか
- [ ] 該当画面の Data row limit が 2000 に引き上げられているか

**通知・入力チェック（6章）**

- [ ] `Notify` の種類（Success/Error/Warning/Information）が場面に合っているか
- [ ] `NotificationType.Error` の表示時間が明示されているか（目安5000ms）
- [ ] 必須項目ごとのエラー表示があり、送信ボタンの `DisplayMode` だけに頼っていないか

**再利用性（8章）**

- [ ] ステータスカラー等の定数マッピングが Named Formula 1箇所にまとまっているか（画面ごとにコピーしていないか）
- [ ] 副作用を伴うロジックを誤って Named Formula にしていないか（コンポーネントになっているか）

**コンポーネント設計（10章）**

- [ ] 2回以上使う処理・長くなる処理がコンポーネント化されているか
- [ ] コンポーネント名が `cmp` 接頭辞、プロパティが `In`/`Out`/`On` 命名規則に沿っているか
- [ ] 1コンポーネントが1つの責務に収まっているか（構造系コンポーネントにロジックが混在していないか）

**YAML記法（11章）**

- [ ] 新規コントロール名がアプリ全体（他画面含む）で重複していないか
- [ ] `{ }` を含む数式（レコードリテラル・文字列補間）が1行のプレーンスカラーのまま書かれていないか（クォート漏れ）
- [ ] `Formulas` は `App.Properties.Formulas` の配下に書かれているか
- [ ] `Sort`/`DateDiff` 等の列挙値が完全修飾名（`SortOrder.Descending`, `TimeUnit.Days` 等）になっているか
- [ ] `FontSize`/`Size` などコントロールごとに異なるプロパティ名を取り違えていないか

## 10. 関数化・コンポーネント設計

Power Fxには独立した関数定義の仕組みがないため、「関数化」は基本的に**コンポーネント化**を意味する。コンポーネントはこのアプリ内で完結させ、他アプリと共有するComponent Libraryとしては管理しない。

### コンポーネント化する基準

- 同じ処理を2回以上書く場合（長さに関わらず）
- 1つの数式が長くなり読みにくくなる場合
- 繰り返し使うUI構造（ヘッダー、サイドナビ、ステータスバッジ、確認ダイアログなど）

### コンポーネントの種類分け

| 種類 | 役割 | 例 |
|---|---|---|
| ロジック系（behavior） | 副作用（`Patch`/`Notify`など）を伴う処理をまとめる | `cmpStatusActionButton`（[3章](#ステータス変更処理の共通化)） |
| 構造系（structural） | 見た目・レイアウトのまとまりを再利用する | `cmpHeader`, `cmpSideNav`, `cmpStatusBadge` |

### 命名規則

- 接頭辞 `cmp` + 役割名のPascalCase（例: `cmpHeader`, `cmpSideNav`）
- 入力プロパティは `In` + 名詞、出力プロパティは `Out` + 名詞（[1章](#変数の命名規則)の命名規則と統一）
- ボタン押下等のイベントを外に伝える動作プロパティ（behavior property）は `On` + 動詞（例: `OnConfirm`, `OnCancel`）

### 設計原則

- 1コンポーネント1責務。`cmpHeader` にナビゲーションと認証判定ロジックを両方持たせない。
- 構造系コンポーネントは見た目に専念させ、データ取得や `Patch` などのロジックは持たせない。必要なデータは呼び出し元から入力プロパティで渡す。
- ロールによって表示が変わる `cmpHeader`/`cmpSideNav` は、ロール判定を毎回コンポーネント内に書かず、[8章](#named-formula-とコンポーネントの使い分け)の Named Formula（例: `CurrentUserIsAdmin`）を直接参照させ、判定ロジックを重複させない。

## 11. YAML記述で実際に発生したエラーと回避策

6画面のモック実装時に `compile_canvas` で実際に検出されたエラーと回避策の記録。同じ原因でのエラーを繰り返さないこと。

### コントロール名はアプリ全体で一意にする

Power Appsのコントロール名は**画面をまたいでアプリ全体で一意**でなければならない。1画面内でユニークなだけでは不十分。ヘッダー・サイドナビなど複数画面で同じ構造を使い回す際、`grpRoot` や `btnNavHome` のような同一名を複数画面にそのまま書くと、2画面目以降の `compile_canvas` で `An entity with name 'xxx' already exists` エラーになる。

- 画面間で構造を使い回す場合は、コントロール名に画面ごとの接尾辞を付ける（例: `grpRootHm`（Home）, `grpRootLs`（一覧）など）。
- 恒久対応としては、[10章](#10-関数化コンポーネント設計)の `cmpHeader`/`cmpSideNav` コンポーネント化で名前の重複自体をなくすことを優先する。

### レコードリテラル・文字列補間を含む数式は必ずクォートする

`{ }` を含む数式を1行のプレーンスカラーとして書くと、YAMLが `key:` をマッピングのキーとして誤解釈し `YamlInvalidSyntax` になる。`Navigate` の第3引数、`UpdateContext({...})`、`Patch(ds, record, {...})` の更新レコード、`$"...{式}..."` の文字列補間はすべて対象。該当行は数式全体をシングルクォートで囲む。

```yaml
# ❌ エラーになる
OnSelect: =Navigate(RequestDetailScreen, ScreenTransition.None, { locSelectedRequestId: ThisItem.RequestId })
Text: =$"担当者: {locRequest.Assignee}"

# ✅ 正しい
OnSelect: '=Navigate(RequestDetailScreen, ScreenTransition.None, { locSelectedRequestId: ThisItem.RequestId })'
Text: '=$"担当者: {locRequest.Assignee}"'
```

### Named Formulaは `App.Properties.Formulas` 配下に書く

トップレベルの `Formulas:`（`App:` の兄弟キー）は存在しないプロパティとしてエラーになる。`App.Properties.Formulas` の配下に書く。

```yaml
# ❌ エラーになる
App:
  Properties:
    Theme: =PowerAppsTheme
Formulas: |-
  =MyFormula = ...;

# ✅ 正しい
App:
  Properties:
    Theme: =PowerAppsTheme
    Formulas: |-
      =MyFormula = ...;
```

### 列挙型は完全修飾名で書く

`Sort()` の並び順、`DateDiff()` の単位などの列挙値は、名前空間ごと書かないと認識されない。

```yaml
# ❌ エラーになる
Sort(collection, Column, Descending)
DateDiff(start, end, Days)

# ✅ 正しい
Sort(collection, Column, SortOrder.Descending)
DateDiff(start, end, TimeUnit.Days)
```

名前空間にピリオドを含む型（`BadgeCanvas.ThemeColor` など）は、シングルクォートで型名を囲んでから `.値` を続ける。`BadgeCanvas.Appearance` も同様。

```yaml
# ❌ エラーになる
Appearance: BadgeCanvas.Appearance.Filled

# ✅ 正しい
Appearance: 'BadgeCanvas.Appearance'.Filled
```

### プロパティ名はコントロールごとに異なる。推測しない

似た役割のプロパティでも、コントロールによって名前が違う。実装前に `describe_control` で確認する（[SCREEN_RENDERING_RULES.md 第2部](SCREEN_RENDERING_RULES.md)の「推測で作らない」原則と同じ）。

- `ModernText` / `ModernButton` のフォントサイズは `FontSize` ではなく `Size`。
- `Badge` のフォントサイズは `FontSize`（`ModernText`/`ModernButton`とは名前が異なる）。
