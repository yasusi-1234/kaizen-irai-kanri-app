# Power Apps Canvas App 画面レンダリング規約（汎用版）

Power Apps Canvas Appの画面を作成・修正する際に従うルール。AIエージェント（Copilot Studioのナレッジ、Claude Code等）でYAMLを生成・編集する際は、この内容を優先して適用する。

対象デバイス: 本書は**PC（デスクトップ）専用・マウス操作・横長レイアウト**を前提とした例として書かれている。タブレット/スマホ対応が必要な場合はレイアウト方針（AutoLayoutの比率、タッチターゲットサイズなど）を別途調整すること。
配色の指定なし → 本書の第2章にサンプルの配色パレットを用意しているので、指定が無いプロジェクトではこれを初期値として使ってよい（自社ブランドがあれば差し替える）。

本書は大きく2部構成:

- **第1部**: 見た目（トーン・配色・タイポグラフィ・レイアウト・命名）のルール
- **第2部**: YAML生成の技術仕様ルール（存在しない Control名・Variant・Property を推測で出力してエラーになることを防ぐためのもの。実機で確認された既知の落とし穴・同期バグも含む）

> **生成前に必ず確認: 画面上の通常のテキスト表示には `ModernText@1.0.0` を使う。** `Text@0.0.51` は**DataCardの内部専用**コントロールで、プロパティ体系が全く異なり（`Color`/`FontWeight`/`Size`が無く、`Weight`など別名になる）、画面に直接置くと`Unknown property`エラーが大量発生する。**画面に置くテキストコントロールを1つ書くたびに、Controlの値が`ModernText@1.0.0`になっているか（`Text@0.0.51`になっていないか）を確認してから次に進む。** 詳細は[7章の対応表](#最優先で確認すること-似た名前・似た用途のコントロールプロパティの使い分け)。

> **生成前に必ず確認: 実装フェーズの画面では `Label`/`TextInput`/`ComboBox`/`DatePicker` を使わない。** これらは「会議用モック」専用の例外コントロールであり、実装フェーズでは `ModernText`/`ModernTextInput`/`ModernCombobox`または`ModernDropdown`/`ModernDatePicker`を使う。コンパイルは通ってしまう（エラーにならない）ため、生成後の見直しでも気づきにくい。コントロールを1つ配置するたびに、Control名が`Modern`で始まっているか（DataCard内部など明確な例外を除く）を確認する。詳細は[5章のコントロール選定ルール](#5-コントロール選定ルール)。

> **生成前に必ず確認: 水平・垂直コンテナ（`AutoLayout`）の直下に置くすべての子要素に、`FillPortions`を明示で書く（固定サイズにしたい要素は`FillPortions: =0`、伸縮させたい要素だけ`0`以外）。** `FillPortions`を1つでも書き忘れると、その要素は「0」としてではなく兄弟要素とスペースを分け合う扱いになり、明示した`Height`/`Width`が無視されて、はみ出し・詰まり・比率の崩れが起きる。**この崩れはコンパイルエラーにならず、Playモードで初めて見た目の崩れとして現れる。** コンテナの子要素を1つ書くたびに、その子要素に`FillPortions`があるか（無ければ追加し忘れていないか）を確認する。詳細は[8章 配置ルール](#配置ルール)。

---

# 第1部: デザイン・レイアウトルール

## 1. デザイントーン

- 「業務効率化ツール」としての信頼性・視認性を最優先する。派手さより一貫性。
- 情報密度はやや高め（一覧・ステータス・件数が一目でわかること）を許容するが、余白のない詰め込みは避ける。
- 各画面は「今なにをする画面か」が3秒でわかる見出し階層を持つこと。

## 2. カラーパレット（サンプル。プロジェクトごとに差し替える）

以下は業務アプリ向けのサンプルパレット。ブランドカラーの指定がある場合はそちらを優先し、無い場合の初期値として使う。

| 用途 | 色 | 備考 |
|---|---|---|
| 背景（メイン） | `RGBA(246, 247, 249, 1)` の薄いグレー | `Color.White` 直置きは禁止。わずかにトーンを入れる |
| サーフェス（カード等） | `Color.White` | 背景とのコントラストで浮かせる |
| プライマリ（主要アクション） | `RGBA(37, 99, 235, 1)`（青） | ボタン・選択状態・強調に統一使用 |
| アクセント | `RGBA(13, 148, 136, 1)`（ティール） | 補助的な強調のみ。多用しない |
| テキスト（主） | `RGBA(17, 24, 39, 1)` | 見出し・本文 |
| テキスト（副） | `RGBA(107, 114, 128, 1)` | 補足・メタ情報 |

### ステータスカラー（`Badge` の `ThemeColor` を正とする、パターンの例）

ステータスやカテゴリなど「一覧の中で状態を色分けして見せたいもの」がある場合の設計パターン。

ステータス表示は必ず `Badge` コントロールを使い、色は `RGBA` 直書きではなく `ThemeColor`（`BadgeCanvas.ThemeColor`）で指定する。この列挙値は `describe_control` で確認済みの実在する値のみ（`Brand`, `Danger`, `Important`, `Informative`, `Severe`, `Subtle`, `Success`, `Warning`）。**色は8種類しかない**ので、ステータス数がそれより多い場合は同じ`ThemeColor`を使い回し、`Appearance`（`Tint`/`Outline`など）で区別する。

**`Appearance` は基本的に `Tint` を使う。** 区別が必要な例外だけ `Outline` 等にする。`Filled`/`Ghost` は理由なく使わない。

以下は「改善依頼の受付〜完了」のような9ステータスのワークフローを例にした対応表（**ステータス名・件数は自プロジェクトのものに置き換える**。ここでは「色の割り当て方・1箇所にまとめる設計」のパターンを示すのが目的）。

| ステータス（例） | ThemeColor | Appearance | 意図 |
|---|---|---|---|
| 未受付 | `Subtle` | `Tint` | 未着手・中立 |
| 受付済み | `Informative` | `Tint` | 認識された状態 |
| 対応中 | `Brand` | `Tint` | 作業中（アプリのメインカラー） |
| 確認待ち | `Warning` | `Tint` | 他者のアクション待ち |
| 完了 | `Success` | `Tint` | 正常終了 |
| 差戻し | `Severe` | `Tint` | 問題が見つかり要再対応 |
| 保留 | `Important` | `Tint` | 一時停止・目立たせる |
| 対応不可 | `Danger` | `Tint` | 対応不可で終了 |
| 取消 | `Subtle` | `Outline` | 「未受付」と区別するため枠線のみ（基本の`Tint`からの唯一の例外） |

同じステータスには常に同じ `ThemeColor`/`Appearance` の組み合わせを使う。画面ごとに変えない（実装上は、この対応表をNamed Formula 1箇所にまとめ、各画面はそこを`LookUp`で参照する。第8章「再利用性」参照）。

```powerfx
// Badge の ThemeColor / Appearance 指定例
ThemeColor: ='BadgeCanvas.ThemeColor'.Warning
Appearance: ='BadgeCanvas.Appearance'.Tint
```

## 3. タイポグラフィ

- `Label` ではなく `ModernText` を使用する（第2部のコントロール仕様参照）。
- 画面タイトル: Size 24〜28 / `FontWeight.Bold`
- セクション見出し: Size 18〜20 / `FontWeight.Semibold`（なければ Bold）
- 本文・表内テキスト: Size 14
- 補足・キャプション: Size 12 / テキスト（副）カラー
- 左揃えを基本とする（業務データは中央揃えにしない）。中央揃えは空状態メッセージなど限定的な場面のみ。

## 4. レイアウト原則（PC前提）

- **画面全体は必ずコンテナ（`GroupContainer`）で管理する。** Screen直下に個々のControlを無秩序に置かない。
- 基本構成は `Header` / `SearchArea` / `ContentArea` / `ActionArea` のようなゾーニングを優先する。
- **`AutoLayout` を既定にする。`ManualLayout`＋絶対座標（`X`/`Y`）は限定的な例外だけに使う。** 画面幅に応じて内容が破綻しないようにするため。

### 参考画像（スクリーンショット・デザインカンプ）を再現するときも、まずAutoLayoutのゾーンに分解する

「この画像の通りに作って」という指示を受けたときに、**画像上の各要素のピクセル位置を測って`ManualLayout`＋`X`/`Y`でそのまま再現しようとしない。** これをやると、ヘッダーバー・サイドナビの各項目・統計カードの並び・フィルタ行・テーブルの見出し行とデータ行など、本来くり返し構造として扱うべき部分まで個別の絶対座標になり、次のような問題が実際に起きる。

- 画面幅やコンテンツ量が変わると要素が重なる・崩れる。
- ラベルと入力欄など隣接する要素のY座標を手計算するため、計算を誤ると要素同士が重なる。
- `ManualLayout`の子要素は`GroupContainer`の必須プロパティ（`Width`/`Height`）を書き忘れやすく、書き忘れると描画が崩れる。

**正しい手順**: 画像を見たらまず「ヘッダー」「サイドナビ」「メインコンテンツ（さらにタイトル行／統計カード行／フィルタ行／テーブル見出し行／テーブル本体）」のような**ゾーンに分解**する。各ゾーンは`AutoLayout`の`GroupContainer`（`LayoutDirection`/`LayoutGap`/`LayoutAlignItems`/Padding系）で組み立てる。「同じ形の項目が複数並んでいる」（サイドナビの項目、統計カード、テーブルの行など）場合は、絶対座標を個別計算するのではなく、`Gallery`か、`AutoLayout`の`GroupContainer`を縦・横に並べて`LayoutGap`で間隔を作る。

```yaml
# ❌ サイドナビの各項目を絶対座標で個別に配置（画面サイズが変わると崩れる、Y座標の手計算を間違えやすい）
grpSidebar:
  Control: GroupContainer
  Variant: ManualLayout
  Properties:
    Height: =600
    Width: =260
  Children:
    - navItem1:
        Properties:
          X: =0
          Y: =20
          Height: =48
          Width: =260
    - navItem2:
        Properties:
          X: =0
          Y: =68   # 20 + 48 を手計算。項目が増減するたびに全項目のYを計算し直す必要がある
          Height: =48
          Width: =260

# ✅ AutoLayout（縦並び）+ LayoutGapで自動的に並べる。項目の増減にも強い
grpSidebar:
  Control: GroupContainer
  Variant: AutoLayout
  Properties:
    LayoutDirection: =LayoutDirection.Vertical
    Height: =600
    Width: =260
  Children:
    - navItem1:
        Properties:
          AlignInContainer: =AlignInContainer.Start
          FillPortions: =0
          Height: =48
          Width: =260
    - navItem2:
        Properties:
          AlignInContainer: =AlignInContainer.Start
          FillPortions: =0
          Height: =48
          Width: =260
```

`ManualLayout`を使ってよいのは、要素同士をあえて重ねたい場合（アイコンの上に小さなバッジを重ねる、背景画像の上にテキストを重ねる等）や、`AutoLayout`のゾーン分解では表現しづらい自由配置が本当に必要な、限定的な場合だけにする。画面の大部分（ヘッダー・サイドナビ・行・カードの並びなど）が`ManualLayout`だらけになっている場合は、設計を見直すサインである。

### ヘッダー行内の右寄せ要素（通知アイコン・ユーザー名など）も絶対座標にしない

画面上部のヘッダーバーで、左にタイトル・右に通知アイコンやユーザー名を配置したい場合、**右側の要素に「想定した画面幅からの引き算」で`X`を決め打ちしない。** 実際に通知アイコンに`X: =1300`、ユーザー名に`X: =1360`のような固定座標が使われ、その値は「画面幅1366pxを想定して右端から逆算した位置」だった。画面幅がそれと異なる環境（別解像度、サイドバーの有無など）では右寄せ要素が余白に浮いたり、逆にはみ出したりする。

**正しい手順**: ヘッダー行全体を`AutoLayout`の水平コンテナにし、左側の要素（タイトルなど）と右側の要素（アイコン・ユーザー名など）をそれぞれ別の`GroupContainer`（`LayoutDirection.Horizontal`、`FillPortions: =0`）にまとめた上で、**間に`FillPortions: =1`の空コンテナ（スペーサー）を挟むか、ヘッダー行自体に`LayoutJustifyContent.SpaceBetween`を指定して**両端に押し出す。

```yaml
# ❌ 右寄せ要素の位置を画面幅から逆算した固定Xで指定（画面幅が変わると崩れる）
grpAppHeader:
  Variant: ManualLayout
  Children:
    - txtAppTitle:
        Properties:
          X: =24
    - icoNotification:
        Properties:
          X: =1300   # ← 1366px幅を想定した決め打ち
    - txtUserName:
        Properties:
          X: =1360   # ← 同上

# ✅ AutoLayout + スペーサー（FillPortions: =1）で右端に押し出す。画面幅に追従する
grpAppHeader:
  Control: GroupContainer
  Variant: AutoLayout
  Properties:
    LayoutDirection: =LayoutDirection.Horizontal
    FillPortions: =0
    Width: =Parent.Width
  Children:
    - txtAppTitle:
        Properties:
          AlignInContainer: =AlignInContainer.Center
          FillPortions: =0
    - grpHeaderSpacer:
        Control: GroupContainer
        Properties:
          FillPortions: =1   # 唯一FillPortionsを0以外にする例外。理由: 左右を押し広げる目的
    - grpHeaderRight:
        Control: GroupContainer
        Variant: AutoLayout
        Properties:
          LayoutDirection: =LayoutDirection.Horizontal
          AlignInContainer: =AlignInContainer.Center
          FillPortions: =0
        Children:
          - icoNotification:
              Properties:
                AlignInContainer: =AlignInContainer.Center
                FillPortions: =0
          - txtUserName:
              Properties:
                AlignInContainer: =AlignInContainer.Center
                FillPortions: =0
```

- 水平コンテナ・垂直コンテナ内の要素は `FillPortions` を `0` とする（詳細は[第8章 配置ルール](#配置ルール)）。
- コンテナ内の要素は `AlignInContainer` を**必ず明示的に指定する**（`Start`など）。指定を省略すると既定値が `Stretch` になり、縦方向・横方向どちらでも意図せず親いっぱいに引き伸ばされることがあるため、「使わない」ではなく「Stretch以外を明示する」で徹底する。
- コンテナ内に要素を配置する際、意図しない隙間（余白）ができる構成にしない。**これは縦方向（Height）・横方向（Width）の両方に適用する。** 片方だけ気を付けて他方を見落とさないこと（計算方法は[第8章 配置ルール](#配置ルール)）。
- **同じ画面内で縦に並ぶセクション（ヘッダー行・カード行・一覧など）は、外側の幅を揃える。** あるセクションだけ固定幅にし、他は`Parent.Width - N`のような可変幅のまま、という不揃いにしない。1つのセクションの内部の隙間を直すときは、その行単体だけを見て終わらせず、同じ画面の他のセクションと幅が揃っているかも必ず確認する（局所最適で終わらせない）。
- コンテナは内部要素との間に**最低 `4px`** のパディング（`PaddingTop`/`PaddingBottom`/`PaddingLeft`/`PaddingRight`）を確保する。
- 視覚効果（`DropShadow`・`BorderStyle`など）は `Fill` を持つ「見える面」にだけ設定する。純粋なレイアウト用のラッパーコンテナには付けない（詳細は[第8章](#視覚効果は見える面にだけ付ける)）。
- `DropShadow` を持つ要素を入れる親コンテナは、子要素とぴったり同じサイズにせず4px程度の余白を持たせ、`LayoutAlignItems.Center` で中央配置する（影の見切れ防止。詳細は[第8章](#dropshadowを持つ要素は親コンテナに余白を持たせる)）。
- **`GroupContainer` はすべて `DropShadow` を明示的に指定する（影が不要なら `DropShadow.None`）。省略しない。** `Fill`（背景）が無いコンテナでも、未指定のままだと既定の影が表示されることがある。「省略＝影は出ない」と判断しない。
- 子要素の `Height`/`Width` は、親コンテナのサイズからパディング分を差し引いた値にする（計算方法は[第8章 配置ルール](#配置ルール)）。潰れないように注意し、どうしても潰れる場合や画面幅を取る場合はスクロールバーで調整する。
- 標準余白: セクション間 24px、要素間 12〜16px、カード内パディング 16〜20px（いずれも上記の最低4pxを満たした上での目安）。
- 一覧画面は「左: フィルタ/検索」「右 or 下: 一覧本体」のような明確なゾーニングを行う。
- ヘッダー（画面タイトル・戻る導線・主要アクションボタン）は画面上部に固定的に配置する。

## 5. コントロール選定ルール

目的別に以下を優先して使う。**ここに挙げるコントロールでも、実装前に必ず第2部の仕様（またはMCPの `describe_control`）で Control@Version・Variant・Propertyを確認してから使うこと。**

| 目的 | 使用するコントロール | 避けるもの |
|---|---|---|
| 一覧・データ表示（無限スクロールが必要な場合） | `Gallery`。無限スクロール方式にする場合は、実装前に`describe_control`でスクロール継続読み込み用のプロパティ（バージョンにより異なる）を必ず確認する。推測でプロパティ名を作らない | `Classic` 系、`ModernDataGrid`（ページング前提のため無限スクロール要件とは相性が悪い） |
| ステータス表示 | `Badge` | 色付き `Rectangle` + `Label` の自作 |
| 入力フォーム（会議用モック） | `GroupContainer` + 入力コントロールの組み合わせ | `Form`（実データソース前提になりやすいため） |
| 入力フォーム（実装フェーズ） | `Form` + `TypedDataCard` | 個別入力を並べただけの疑似フォーム |
| テキスト入力 | `ModernTextInput` | `Classic/TextInput`, `TextInput`（モック以外） |
| 日付入力 | `ModernDatePicker` | `Classic/DatePicker`, `DatePicker`（モック以外） |
| 選択肢（少数） | `ModernRadio` | `Classic/Radio`, `CheckBox`（モック以外） |
| 選択肢（多数/検索可） | `ModernCombobox` | `Classic/ComboBox`, `ComboBox`（モック以外） |
| ドロップダウン | `ModernDropdown` | `Classic/DropDown` |
| タブ切り替え | `ModernTabList` | ボタン列 + 手動ハイライト |
| ボタン | `ModernButton` | `Classic/Button` |
| アイコン | `ModernIcon`（Classic Iconの`Icon.XXX`形式が必要な場面のみ`Classic/Icon`） | — |
| テキスト表示 | `ModernText` | `Label`（DataCard内部など特別な理由がある場合を除く） |

**原則**: `Classic/*` は使わない。同目的の `Modern*` コントロールが存在する場合は必ずそちらを使う。**`Label`/`TextInput`/`ComboBox`/`DatePicker`は「モック専用」の例外コントロールであり、実装フェーズの画面には使わない。** コンパイルは通ってしまうため、エラーとして気づけない。コントロールを1つ配置するたびに、上の対応表で「実装フェーズで使うべきもの」になっているかを確認する。

```yaml
# ❌ 実装フェーズなのにモック専用コントロールを使う（コンパイルは通るが規約違反）
lblPageTitle:
  Control: Label@2.5.1
txtSearch:
  Control: TextInput@0.0.54
cmbStatusFilter:
  Control: ComboBox@0.0.51
dtpDueFilter:
  Control: DatePicker@0.0.46

# ✅ 実装フェーズはModern系コントロールを使う
txtPageTitle:
  Control: ModernText@1.0.0
inpSearch:
  Control: ModernTextInput@1.1.0
ddlStatusFilter:
  Control: ModernDropdown@1.0.2
dtpDueFilter:
  Control: ModernDatePicker@1.0.1
```

**コンポーネントの優先利用**: ヘッダー・サイドナビ・ステータスバッジ・確認ダイアログなど繰り返し使うUI要素は、都度 `Gallery`/`GroupContainer` などのプリミティブから組み立て直さず、自プロジェクトのコーディング規約で定義したコンポーネント（例: `cmpHeader`, `cmpSideNav`, `cmpStatusBadge`）を優先して使う。

## 6. 命名規則

### 画面名
`〇〇Screen` の PascalCase（例: `ListScreen`, `DetailScreen`, `FormScreen`, `DashboardScreen`）。
`Screen1` のような連番名は禁止。

### コントロール名
`種別プレフィックス + 目的` の camelCase。

| 種別 | プレフィックス | 例 |
|---|---|---|
| ボタン | `btn` | `btnSubmit` |
| 一覧（Gallery） | `gal` | `galItemList` |
| コンテナ | `grp` | `grpHeader` |
| テキスト表示 | `txt` | `txtScreenTitle` |
| 入力欄 | `inp` | `inpTitle` |
| ステータスバッジ | `badge` | `badgeStatus` |
| ドロップダウン | `ddl` | `ddlCategory` |
| 日付入力 | `dtp` | `dtpDueDate` |
| 選択肢（ラジオ/コンボ） | `sel` | `selPriority` |
| タブ | `tab` | `tabStatusFilter` |
| アイコン | `ico` | `icoSearch` |
| コンポーネント | `cmp` | `cmpHeader`, `cmpStatusBadge` |

`Button1`, `Label2` のような自動採番名を残さない。コントロール名は**アプリ全体で一意**にする必要がある（画面をまたいで同じ構造を使い回す場合、画面ごとの接尾辞を付けるなどして重複を避ける）。

## 7. インタラクション・状態

- 画面遷移・選択状態・編集モードなどは `Set()`/`UpdateContext()` による変数で明示的に管理する。変数名は自プロジェクトの命名規則（例: グローバル変数`glb`、コンテキスト変数`loc`のようなプレフィックス）に従う。
- ボタンは押下不可な状況で `DisplayMode.Disabled` にする（グレーアウトを見た目だけで表現しない）。
- 一覧の行選択や絞り込み結果は `Visible` / フィルタ式で反映し、画面上に「今なにが選ばれているか」を示す。
- 保存・削除など不可逆な操作は確認導線（確認ダイアログ相当のUI）を挟む。
- ステータス変更のように複数画面・複数ボタンで共通するロジック（`Patch`と副作用）は、画面に直接書かず共通コンポーネントに集約するのが望ましい。同じ判定・更新ロジックを画面ごとにコピーしない。

---

# 第2部: YAML生成の技術仕様ルール（AIナレッジ用）

**目的**: AIがPower Apps Canvas AppのYAMLを生成する際に、存在しないControl名・Variant・Propertyを出力してエラーになることを防ぐ。
以下に記載したControl名、Version、Variant、主要Propertiesを優先して使用すること。
**不明なControlやPropertyは推測で作成しないこと。** 不明な場合は `describe_control` / `list_controls` など外部リソースを参考に生成すること。

### 最優先で確認すること: 似た名前・似た用途のコントロール／プロパティの使い分け

**この規約に沿ってYAMLを生成したにもかかわらず、実機で繰り返し発生したエラーのほとんどは「似た名前・似た用途の別コントロール／別プロパティを取り違えたもの」だった。** 個別の章を読む前に、まずこの一覧で意図したものが正しいか確認する。

| 用途 | 使うもの | 補足 |
|---|---|---|
| 画面上の通常のテキスト表示 | `ModernText@1.0.0`（`Size`/`Color`/`FontWeight`を使う） | `Text@0.0.51`は**DataCard専用**のコントロールで、プロパティ体系が異なる（例: `FontWeight`ではなく`Weight`）。通常の画面テキストに使うと大量の「不明なProperty」エラーになる。`Label`もDataCard内部など特別な理由がある場合のみ |
| アイコン表示（Modern系コントロールの並び） | `ModernIcon`の`Icon`は型が**Text（自由文字列）**。必ず`Icon: ="Home"`のように書く | `Classic/Icon`の`Icon`は**列挙型**（例: `Icon: =Icon.ChevronRight`）。`ModernIcon`に`Icon: =Icon.BulletedList`のような列挙型ドット記法を使うと型不一致でエラーになる（実機で確認済み）。「文字列を優先する」ではなく「列挙型は使えない」と覚える |
| アイコンの色 | `ModernIcon`は`IconColor` | `ModernText`は`Color`。`ModernIcon`に`Color`は存在せず、`Unknown property`エラーになる。「文字色系プロパティ＝`Color`」と覚えず、コントロールごとに`IconColor`/`Color`/`FontColor`を使い分ける |
| 通常のテキスト・カード等の背景色 | `GroupContainer`は`Fill` | `ModernButton`に`Fill`は存在しない（ボタンの見た目は`Appearance`/`BasePaletteColor`で調整する） |
| 文字色 | `ModernText`は`Color` | `Badge`は`FontColor`（`ModernText`には存在しない） |
| フォントサイズ | `ModernText`は`Size` | `Badge`は`FontSize`（`ModernText`には存在しない） |
| 単一選択の初期値 | `ModernDropdown`は`Default`（`Items`と同じ形のレコード） | `ModernCombobox`は`DefaultSelectedItems`（複数選択用。`ModernDropdown`には存在しない） |
| 見た目に表示するヒント文字列 | `Placeholder` | `AccessibleLabel`は画面に表示されない（スクリーンリーダー向けの説明文のみ） |

**列挙型（Enum）の完全修飾名は、コントロールごとにプレフィックスの有無・形式がバラバラ。** 同じ「`Appearance`」というプロパティ名でも、`describe_control`で実際に確認したところ次のように型名が全く違った。

| コントロール | `Appearance`の列挙型名 | 書き方の例 |
|---|---|---|
| `Badge` | `BadgeCanvas.Appearance` | `='BadgeCanvas.Appearance'.Tint` |
| `ModernButton` | `ButtonAppearance` | `=ButtonAppearance.Primary` |
| `ModernDropdown` | `Appearance`（プレフィックス無し） | `=Appearance.Outline` |

**`'ModernControlsCommon.Appearance'`のような、規則性から類推した型名を作らない。** 同じ「値の候補」（`Outline`など）が複数のコントロールで共通していても、型名（プレフィックスを付けるかどうか）は個別に異なる。未確認の列挙型プロパティを書くときは、値の候補だけでなく**型名の完全修飾形式も`describe_control`で確認**してから使う。

### 最優先で確認すること: サイズは「決め打ち」せず、必ず計算する

**この規約通りの計算式・チェックリストが用意されているにもかかわらず、実機で生成されたYAMLでは、テキストの`Height`もコンテナの`Height`も、計算せずに丸い数字を決め打ちしていた。** その結果、次の2種類の不具合が実際に発生した。

1. **`ModernText`の`Height`不足によるスクロールバー**: 生成されたテキストのほぼ全てで`Height`が`Size × 1.5 + 10`を下回っていた（例: `Size:20`の見出しに`Height:28`→本来`40`必要、`Size:12`のラベルに`Height:18`→本来`28`必要）。**`ModernText`の`Height`を書くたびに、必ず`Size × 1.5 + 10`を計算してから値を決める。** [第9章の早見表](#moderntext)も参照。
2. **コンテナの`Height`/`Width`が中身より小さく、はみ出す**: 「検索エリアの高さは`80`くらいだろう」のように先に丸い数字を決めてしまい、後から中に入れる要素（ラベル+ドロップダウンの組み合わせなど）の合計サイズを確認していなかった。実際に「ラベル(18)+隙間(4)+ドロップダウン(40)=62px必要」な組み合わせを、パディング上下32pxを差し引くと使える高さが48pxしかない`Height:80`のコンテナに入れてしまい、14pxオーバーしていた。**コンテナの`Height`/`Width`を決めるときは、丸い数字を先に決めるのではなく、必ず「中身の合計サイズ＋パディング＋`LayoutGap`」を計算してから、その計算結果をコンテナの`Height`/`Width`に使う**（詳細は[「幅・高さのバランス」](#幅高さのバランス隙間を作らない)・[「パディングとサイズの計算」](#パディングとサイズの計算)）。

どちらも**YAMLとしては正しく解釈され、コンパイルエラーにはならない**（実行時にスクロールバーやはみ出しとして現れるだけ）。エラーが出ないからといって安心せず、`Height`/`Width`を書くたびに機械的に計算する。

### 一覧のヘッダー行とデータ行の列位置を一致させる

見出し行（テーブルヘッダー）と`Gallery`のデータ行で、列の位置・幅を**別々の方式で計算すると列がずれる。** 実際に、見出し行は`FillPortions`（比率、例: `3,2,2,1,2,2,2`）で列幅を決め、データ行は`Parent.TemplateWidth`に独自の%を掛けた`X`座標（例: `0`, `0.29`, `0.46`, `0.60`...）で位置を決める、という**方式の異なる列定義**を混在させたため、見出しの下にデータが正しく揃わない不具合が発生した。

- 見出し行を`FillPortions`で組んだら、データ行（`Gallery`のテンプレート内）の各列も**同じ`FillPortions`比率**で組む（テンプレート内を`AutoLayout`の水平コンテナにし、同じ`FillPortions`値の子要素として並べる）。
- `ManualLayout`で`X`/`Y`の絶対配置がどうしても必要な場合は、見出し行・データ行の**両方**を同じ計算式（同じ%、同じ固定px）で作る。片方だけ`FillPortions`、片方だけ独自の%計算、という混在は絶対にしない。
- 列を1つ足す・幅を変えるときは、見出し行とデータ行の**両方**を同時に直す（片方だけ直して終わらせない）。

### 親のWidthが可変（計算式）なのに、子要素のWidthを決め打ちの固定pxにしない

親コンテナの`Width`が固定値ではなく**計算式**（例: `(Parent.Width - 48 - 64) / 5`のような、画面幅に応じて変わる式）のとき、その中の子要素（ラベルなど）の`Width`を、親と無関係な**決め打ちの固定px**（例: `160`）にすると、画面幅によっては子要素の方が実際の親の幅より広くなり、**はみ出す・切れる**ことがある。実際に、カードの幅は画面幅で変わる計算式なのに、中のラベルの`Width`が固定`160`のままになっており、画面が狭いときにテキストが欠ける不具合が発生した。

- 親の`Width`が計算式なら、子要素の`Width`も**その計算式を基準にする**（例: `Width: =Parent.Width - 32`。`PaddingLeft`/`PaddingRight`が16ずつなら32を引く）。親が可変幅なのに子だけ決め打ちの固定pxにしない。
- 複数の固定`Width`列を横に並べる場合（テーブルの列など）、**列幅の合計＋パディングが、実際に使う最小の画面幅を超えないか確認する。** 超える可能性がある場合は、どれか1列（タスク名など伸縮してよい列）を`FillPortions`で伸縮可能にし、余り・不足分を吸収させる。全列を固定pxにすると、画面が想定より狭いときに右側の列が切れる。
- `Badge`など「列の幅より小さい要素」を列に配置する場合、余った分を埋める透明なスペーサー（`Width`だけ指定した空の`GroupContainer`）を追加して、その列全体の幅が見出し行の対応する列幅と一致するようにする（優先度列で`Badge(50)+スペーサー(40)=90`のように、見出しの列幅と合計を必ず一致させる）。

コントロールを選ぶとき・プロパティ名を書くときは、**「同じような役割の別コントロールのものを書いていないか」を必ず自問する。** 迷ったら、この規約の該当コントロールの「使用可能な主なProperties」一覧に実際に載っているかを確認してから使う。

## 8. 共通ルール

- YAMLは以下の階層を基本とする。

```yaml
Screens:
  ScreenName:
    Properties:
      ...
    Children:
      - ControlName:
          Control: ControlType@Version
          Variant: VariantName
          Properties:
            ...
          Children:
            ...
```

- Controlには必ず実在する `Control@Version` を指定する。
- Variantが必要なControlでは必ずVariantを指定する。
- Properties配下に設定値を記載する。
- Power Fx式は先頭に `=` を付ける。
- 文字列はダブルクォートで囲む。
- 子要素を持つControlは `Children` を使用する。
- 未確認のPropertyは使用しない。
- 会議用モックでは `Patch` / `SubmitForm` / `Flow.Run` / `Collect` / `ClearCollect` は使用しない。
- **重要: `ItemDisplayText` は列名の文字列（`="Value"`）ではなく、`ThisItem` を使ったPower Fx式（`=ThisItem.Value`）で書く。** `ModernDropdown`/`ModernCombobox`/`ModernRadio`/`ModernTabList` など「Itemsを持つ一覧系のModernコントロール」すべてに共通するルール。`="Value"` のような列名の文字列を渡すと、コンパイルは通るが実行時に各項目のテキストが**すべて空欄**になり、ドロップダウンの選択肢やラジオボタンのラベルが何も見えない状態になる（見た目には壊れているとすら気づきにくい）。

```yaml
# ❌ コンパイルは通るが、項目のテキストが全部空欄になる
ItemDisplayText: ="Value"
Items: =Table({ Value: "低" }, { Value: "中" }, { Value: "高" })

# ✅ ThisItem経由で列を参照する
ItemDisplayText: =ThisItem.Value
Items: =Table({ Value: "低" }, { Value: "中" }, { Value: "高" })
```

### ModernDropdown / ModernCombobox の「未選択」判定はコントロール自身の`Selected`/`SelectedItems`に頼らない

**`Default` を指定していない `ModernDropdown`/`ModernCombobox` でも、`Selected`/`SelectedItems` が空（`Blank()`）になるとは限らない。** 実機で「フィルタを何もかけていないのに一覧が0件になる」障害として実際に発生した。

- `IsBlank(ddlCategory.Selected.Title)` や `CountRows(cmbAssignee.SelectedItems) = 0` のような式で「ユーザーがまだ何も選んでいないか」を判定しようとすると、内部的に何か選択済み状態になっているため `false`（＝選択済み扱い）になり、意図せず絞り込み条件が有効化されてしまうことがある。
- この状態で `Filter` の条件に使うと、他の絞り込み条件を全部外していても該当ゼロ件になる。`IfError` で包んでも救えない。**`IfError` は本当にエラーが起きたときだけ`fallback`を返す関数であり、単に条件式が`false`と評価される場合はエラーではないため素通しする。** 「原因不明の0件」に遭遇したとき、`IfError`のせいだと決めつけて別の箇所を疑わない、ということがないようにする。

**回避策**: コントロール自身の選択状態を直接参照せず、**「ユーザーが実際に選択操作をしたかどうか」を明示的な`loc`変数で管理し、`OnChange`でのみ更新する。**

```powerfx
// ❌ コントロール自身のSelectedに「未選択=Blank」を期待する
// OnVisible: 何もしない（ddlCategoryはDefault未指定）
// Filter条件:
(IsBlank(ddlCategory.Selected.Title) || CategoryTitle = ddlCategory.Selected.Title)

// ✅ 明示的なloc変数で「絞り込み中か」を管理する
// OnVisible:
UpdateContext({ locCategoryFilterTitle: Blank() })

// ddlCategoryのOnChange（ユーザーが実際に選んだときだけ発火）:
UpdateContext({ locCategoryFilterTitle: ddlCategory.Selected.Title })

// Filter条件（loc変数を見る。ddlCategory.Selectedは直接参照しない）:
(IsBlank(locCategoryFilterTitle) || CategoryTitle = locCategoryFilterTitle)

// 検索条件クリアボタンでも、Reset(ddlCategory)と合わせてloc変数もBlank()に戻す
```

- 複数選択（`ModernCombobox`の`SelectedItems`）の場合も同様に、`CountRows(...) > 0`をそのまま条件に使わず、`OnChange`で真偽値の`loc`変数（例: `locHasAssigneeFilter`）を更新し、そちらで「絞り込みが有効か」を判定する。実際に選択されたリストの中身（`SelectedItems`自体）を参照するのは、その`loc`変数が`true`のときだけにする。
- この問題は`ModernDropdown`と`ModernCombobox`の両方で確認済み。同系統の選択コントロール（`ModernRadio`等）を同様の「未選択判定」に使う場合も、同じ回避策を優先し、コントロール自身の`Selected`が`Blank()`になることを無条件に信頼しない。

### 配置ルール

- Screen直下、`ManualLayout` 配下のControlは原則 `X`, `Y`, `Width`, `Height` を指定する。
- `AutoLayout` 配下の子Controlは `X`, `Y` を省略してよい。
- `AutoLayout` 配下でも `Width`, `Height`, `LayoutMinWidth`, `LayoutMinHeight` は必要に応じて指定する。
- **水平コンテナ・垂直コンテナ（`LayoutDirection: Horizontal`/`Vertical`）内の子要素は、`FillPortions` を `0` とする。** 可変幅で引き伸ばしたい特別な理由がある場合のみ例外的に`0`以外を指定し、その理由をコメントで残す。
  - **`FillPortions` が `0` 以外の子要素は、`Width`/`Height` を明示的に指定していても無視され、`FillPortions`の比率に基づく自動幅（残りスペースを埋める広さ）が優先されることを実機で確認済み。** `Width: =Parent.Width - 84` のように正しく計算した式を書いていても、同じ要素に `FillPortions: =2` のような`0`以外の値が残っていると、その式は無視されて要素が想定より広く描画され、隣の兄弟要素に重なってはみ出す。「明示的な`Width`があるから大丈夫」とは判断せず、**`FillPortions`が`0`になっているかを必ずセットで確認する。**

    ```yaml
    # ❌ Widthを正しく計算していても、FillPortionsが0以外だと無視されて隣の要素に重なる
    grpCard:
      Properties:
        FillPortions: =2   # ← これが原因でWidthが無視される
        Width: =Parent.Width - 84

    # ✅ FillPortionsを0にして、明示Widthを確実に効かせる
    grpCard:
      Properties:
        FillPortions: =0
        Width: =Parent.Width - 84
    ```
  - **`FillPortions` プロパティ自体を書かない（省略する）ことは `=0` と同じ意味にならない。実機で確認済み。** 固定サイズにしたい要素だからと「`FillPortions`は関係ないので書かなくていい」と判断すると、その要素は兄弟要素（`FillPortions`を明示している側）とスペースを分け合ってしまい、意図しない比率で引き伸ばされる。実際に、垂直コンテナ内でヘッダー行（`Height: =60`で固定したいだけの意図）に`FillPortions`を書かず、隣の本体行に`FillPortions: =1`だけ書いたところ、ヘッダーが画面の約半分の高さまで引き伸ばされ、`Height: =60`の指定が無視される崩れが発生した。**固定サイズにしたい要素にも必ず`FillPortions: =0`を明示で書く。「書かない」を選択肢にしない。**

    ```yaml
    # ❌ ヘッダーはFillPortionsを省略（0のつもりでも0にはならない）→ 本体と半々に引き伸ばされる
    grpAppHeader:
      Properties:
        Height: =60   # ← 無視され、実際は画面の半分近くまで伸びる
        Fill: =RGBA(37, 99, 235, 1)
    grpBody:
      Properties:
        FillPortions: =1

    # ✅ 固定サイズにしたい要素にも FillPortions: =0 を必ず明示する
    grpAppHeader:
      Properties:
        FillPortions: =0
        Height: =60
        Fill: =RGBA(37, 99, 235, 1)
    grpBody:
      Properties:
        FillPortions: =1
    ```
- **`AlignInContainer` は子要素すべてに明示的に指定する（例: `AlignInContainer.Start`）。省略しない。** Power Appsは未指定の場合の既定値が `Stretch` になることがあり、指定を省略すると縦方向・横方向どちらでも意図せず親いっぱいに引き伸ばされる。「Stretchを使わない」だけでなく「明示的に別の値を書く」ことが必須。子要素は `Width`/`Height` も明示して配置する。
- **`GroupContainer` は `DropShadow` を必ず明示的に指定する（影が不要なら `DropShadow.None`）。省略しない。** `AlignInContainer` と同様、未指定の場合の既定値が `None`（影なし）とは限らない。`Fill`（背景）を持たないコンテナでも、既定の影が輪郭に沿って表示されることがあるため、「背景が無いから影も見えないはず」という判断はしない。影を意図的に使う要素（カードなど）以外は、すべて `DropShadow.None` を明示する。
- **「未指定のプロパティは中立・無効化されている」と決めつけない。** Power Appsのコントロールは、プロパティを省略した際の既定値が必ずしも中立（Stretchしない・影が出ない、等）とは限らない。見た目に関わるプロパティ（`AlignInContainer`, `DropShadow` に限らず）は、動作を推測せずに明示的な値を書く。
- 位置が崩れそうな場合は `Width`, `Height` を明示する。

### 幅・高さのバランス（隙間を作らない）

コンテナ内に要素を配置する際、コンテナのサイズと子要素群の合計サイズが合っておらず、意図しない隙間（空白）ができるレイアウトにしない。

- コンテナの `Width`/`Height` は、内部の子要素の合計サイズ（各子要素の `Width`/`Height` の合計 + パディング + `LayoutGap × (子要素数 - 1)`）に対して過不足のない値にする。子要素の合計より大きいサイズを与えて余白を残さない。
- 横並び（`LayoutDirection: Horizontal`）で `LayoutJustifyContent.SpaceBetween`/`SpaceAround` を安易に使わない。要素数が少ない・コンテナ幅に余裕がある場合、これらは要素間に大きな隙間を生む。要素を詰めて並べたい場合は `LayoutJustifyContent.Start` と `LayoutGap` の組み合わせを基本にする。
- コンテナの `Width`/`Height` を `Parent.Width - N` のような親基準の計算式にする場合は、内部の子要素群の合計サイズも同じ基準（同じ `N` や `Parent` 参照）で計算し、両者の帳尻を合わせる。

```
コンテナの Width = PaddingLeft + PaddingRight + Σ(子要素の Width) + LayoutGap × (子要素数 - 1)
```

### 兄弟セクション間の幅の一貫性

1つのセクション（行）だけを見て「その中の隙間」を直すと、今度は**画面内の他のセクションと幅が揃わなくなる**ことがある。これも意図しない不整合であり、隙間と同様に修正対象とする。

- 画面を縦方向に見たとき、ヘッダー行・カード行・一覧・アクション行などのセクションは、**同じ外側の幅**（例: すべて `Parent.Width - 48`）で揃える。
- あるセクションの子要素が固定幅で合計サイズが決まっている場合（例: カードを複数並べる）、そのセクション自体の `Width` を固定値にするのではなく、**子要素側に `FillPortions` を使って伸縮させ、セクションの外側の幅は他と揃える**ことを優先する（例: カードを4等分で伸縮させる。コメントで理由を残す）。
- 1つの行の内部の隙間を直したときは、直した行の `Width` の決め方（固定値か `Parent.Width - N` か）が、同じ画面の他の行と一致しているかを必ず見比べる。局所的な修正だけで終わらせない。

#### 具体例: 2カラム以上のレイアウトで、幅の狭い画面ではみ出さず・広い画面でも右に隙間を残さない

「左: メイン情報」「右: サブ情報（コメント欄など）」のような複数カラムを横に並べる画面で、両カラムに固定ピクセル幅（例: `Width: =560` / `Width: =360`）を指定すると、次の**両方**の問題が起きる。

- 画面（コンテナ）がカラム幅の合計より**狭い**とき: カラムどうしが重なる／画面からはみ出す。
- 画面がカラム幅の合計より**広い**とき: カラムは伸びずに左詰めのまま残り、コンテナの右側に大きな空白ができる（実際に2カラムレイアウトの詳細画面で発生した）。

固定 `Width` ではなく、**`FillPortions` + `LayoutMinWidth`** の組み合わせを標準パターンとする。**`Width` プロパティ自体は指定しない**（[「`FillPortions` が0以外だと明示Widthは無視される」ルール](#配置ルール)の通り、`FillPortions`と`Width`を両方書いても矛盾するだけで意味がない）。

```yaml
# ❌ 固定Widthの合計が画面幅より狭いと右に空白、広いとはみ出す
grpTwoColumnBody:
  Properties:
    LayoutDirection: =LayoutDirection.Horizontal
    Width: =Parent.Width - 48   # 可変
  Children:
    - grpLeftColumn:
        Properties:
          FillPortions: =0
          Width: =560            # 固定ピクセル
    - grpRightColumn:
        Properties:
          FillPortions: =0
          Width: =360            # 固定ピクセル

# ✅ FillPortionsで伸縮させ、LayoutMinWidthを最小幅の下限にする
grpTwoColumnBody:
  Properties:
    LayoutDirection: =LayoutDirection.Horizontal
    Width: =Parent.Width - 48
  Children:
    - grpLeftColumn:
        Properties:
          FillPortions: =3        # 元の560:360 ≒ 3:2の比率を維持
          LayoutMinWidth: =560    # 元の固定値を下限として維持
          # Widthは指定しない
    - grpRightColumn:
        Properties:
          FillPortions: =2
          LayoutMinWidth: =360
          # Widthは指定しない
```

- カラム内部の子要素（見出し・本文・一覧など）も、カラム自体の `Width` が固定値だった間は `Width: =520`（=560-左右Padding20×2）のような固定値になっていることが多い。カラム側を可変幅にしたら、**内部の子要素側も `Width: =Parent.Width - (PaddingLeft + PaddingRight)` に合わせて可変化する**のを忘れない（カラムだけ広がって中の文字エリアは元の固定幅のまま、というズレを残さない）。

### パディングとサイズの計算

コンテナは内部要素との間に**最低 `4px`** のパディングを確保する（`PaddingTop`/`PaddingBottom`/`PaddingLeft`/`PaddingRight`）。子要素の `Height`/`Width` は、親コンテナの `Height`/`Width` からパディング分を差し引いた値にする。

```
子要素の Height = 親コンテナの Height − PaddingTop − PaddingBottom
子要素の Width  = 親コンテナの Width  − PaddingLeft − PaddingRight
```

例: コンテナの `Height` が `30`、`PaddingTop: 4`、`PaddingBottom: 4` の場合、内部の子要素の `Height` は `30 - 4 - 4 = 22` とする。

```yaml
grpExample:
  Control: GroupContainer
  Variant: AutoLayout
  Properties:
    Height: =30
    PaddingTop: =4
    PaddingBottom: =4
  Children:
    - txtInner:
        Control: ModernText
        Properties:
          Height: =22   # 30 - 4(Top) - 4(Bottom)
          Width: =200
          AlignInContainer: =AlignInContainer.Start   # 省略しない。省略すると既定でStretchになりうる
```

子要素が複数あり `LayoutGap` を使う場合は、パディングに加えて要素間の `LayoutGap × (子要素数 - 1)` 分も差し引いて各子要素のサイズを配分する。

**よくある計算ミス**: 兄弟要素の `Height`/`Width` を「`Parent.Height - 兄弟の合計`」のように計算するとき、**`Parent`（コンテナ自身）が持つ `PaddingTop`/`PaddingBottom`（横方向なら`PaddingLeft`/`PaddingRight`）分を引き忘れる**ミスが起きやすい。`Parent.Height`/`Parent.Width` はコンテナの外側サイズであり、パディングを差し引いた「使える内側サイズ」ではないことに注意する。

```
✅ 正しい計算:
  スクロール領域の Height = Parent.Height
    − 兄弟要素の Height の合計
    − LayoutGap × (子要素数 - 1)
    − Parent自身の PaddingTop − Parent自身の PaddingBottom
```

このミスを放置すると、スクロール領域が実際より大きく確保されて下端の要素（ボタン行など）が画面外にはみ出したり、潰れて見えたりする。

### 子要素に `Width: =Parent.Width` / `Height: =Parent.Height` をそのまま書かない（実際に発生したはみ出しバグ）

パディングを持つコンテナの直下の子要素に、`Width: =Parent.Width`（または `Height: =Parent.Height`）を**そのまま**書くと、親のパディング分だけ子要素が親の右端・下端からはみ出す。これは「計算し忘れ」の中でも特に見た目上は一見正しく見えてしまう（数式が単純で「親と同じ幅」に見えるため、レビューで見落としやすい）ため、個別に明記する。

`Parent.Width`/`Parent.Height` は常にコンテナの**外側**サイズ（パディング込みの箱そのもの）を返す。パディングを差し引いた「中に入る実サイズ」を返すものではない。

```yaml
# ❌ カード内側のラベルが左右のPaddingLeft/PaddingRight分だけカードの外にはみ出す
grpStatCard:
  Control: GroupContainer
  Variant: AutoLayout
  Properties:
    PaddingLeft: =16
    PaddingRight: =16
  Children:
    - txtCardLabel:
        Properties:
          Width: =Parent.Width   # grpStatCard自体の外側幅と同じ = 左右16pxずつはみ出す

# ✅ 親のPaddingLeft+PaddingRight分を差し引く
grpStatCard:
  Control: GroupContainer
  Variant: AutoLayout
  Properties:
    PaddingLeft: =16
    PaddingRight: =16
  Children:
    - txtCardLabel:
        Properties:
          Width: =Parent.Width - 32   # 16(Left) + 16(Right)
```

- 1箇所を直して終わらせず、**同じ画面・他の画面全体で `Width: =Parent.Width` / `Height: =Parent.Height` というリテラルな数式を横断的に検索**し、その親コンテナにPaddingが設定されている場合はすべて同様に修正する（実際に1画面内で統計カード4つ・グラフパネル5つの計18箇所で同時多発していた）。
- 親コンテナにPaddingが無い（`Padding*`を一切指定していない、またはすべて`0`）場合に限り、`Width: =Parent.Width`をそのまま使ってよい。

### 固定ヘッダー・固定フッター + 中央だけスクロールする構成

「画面タイトルは固定、下部のアクションボタンも固定、中央のコンテンツだけスクロールさせたい」という要件では、**`LayoutOverflowY: =LayoutOverflow.Scroll` を画面全体（最上位のコンテナ）に付けない。** それだと固定したいはずのヘッダー・フッターごとスクロールしてしまい、「スクロールしているのに操作したい部分が画面外に出て操作できない」という状態になる。

- ヘッダー・スクロール領域・フッターを**同じ親の3つの兄弟要素**として並べる。
- `LayoutOverflowY: =LayoutOverflow.Scroll` は、**中央のスクロールさせたい領域専用の新しいラッパーコンテナ**にだけ付ける。
- そのラッパーの `Height` は、上記「よくある計算ミス」の計算式（親のPaddingを含めて正しく差し引く）で求める。

```yaml
# ✅ ヘッダー / スクロール領域 / フッター を兄弟として並べる
grpMain:
  Control: GroupContainer
  Variant: AutoLayout
  Properties:
    Height: =Parent.Height
    LayoutDirection: =LayoutDirection.Vertical
    LayoutGap: =16
    PaddingTop: =24
    PaddingBottom: =24
  Children:
    - txtTitle:            # 固定ヘッダー
        Properties:
          Height: =46
    - grpScrollArea:        # ここだけスクロール
        Control: GroupContainer
        Properties:
          Height: =Parent.Height - 122   # 46(title) + 44(actions) + 32(gap×2) + 48(自分のPadding)
          LayoutOverflowY: =LayoutOverflow.Scroll
        Children:
          - grpContent:     # 実コンテンツ（スクロール領域より背が高くてよい）
    - grpActions:           # 固定フッター
        Properties:
          Height: =44
```

### 視覚効果は「見える面」にだけ付ける

`DropShadow`・`BorderStyle`などの視覚効果は、実際に見える面（`Fill` で背景色を持つ要素）にだけ設定する。**`Fill` を持たない、純粋にレイアウトのためだけのラッパーコンテナには視覚効果を付けない。**

- レイアウト用ラッパー（複数の子要素を並べるためだけのコンテナ、それ自体は透明・背景なし）に`DropShadow`を設定すると、見た目には何もない箱の輪郭に沿って影が描画されてしまうことがある。これが内部の各要素の影と重なり、二重の影や不要な大きな影として見た目が崩れる原因になる。
- 「構造（配置のための入れ物）」と「見た目（実際に表示される面）」を分けて考える。視覚効果は見た目を担う要素だけに設定し、構造専用のコンテナには何も付けない。
- **`Fill: =RGBA(255, 255, 255, 1)`（白背景）を持つ「カード」「パネル」（統計カード、フィルタパネルなど、背景色でグレーの画面から浮かせて見せたい面）は、一貫して `DropShadow.Semilight` を使う。** サイドバーや行テンプレートの背景など、浮かせる意図のない白背景要素は `DropShadow.None` のままにする（同じ「白背景」でも役割で判断する）。
- **重要（既知の同期バグ）: `DropShadow.Light` は使わない。** `describe_control` 上は有効な列挙値として存在し、`compile_canvas` もエラーなく通るが、**coauthoringセッションのサーバー側に値が反映されずロールバックされる**（`sync_canvas` で確認すると消えている）。`Light` だけがこの症状で、`Regular`/`Semilight` は正常に反映されることを確認済み。「軽い影」を付けたい場合は `DropShadow.Light` ではなく `DropShadow.Semilight` を使う。`compile_canvas` の成功はこのバグを検知できないため、影を追加・変更したときは `sync_canvas` で実際にサーバーに反映されているか確認すること（詳細は[第12章チェックリスト](#12-出力前チェックリスト)）。

### 重要（既知の同期バグ）: プロパティが部分的にしか反映されないことがある

`DropShadow.Light` に限らず、**特定の (コントロール, プロパティ, 値) の組み合わせが、`compile_canvas` が成功していてもサーバー側に反映されず、`sync_canvas` で見ると値ごと消えている**ことがある。1〜2箇所ではなく、一度に大量の変更を行った直後に数十箇所単位で発生することがあり、しかも影響範囲は特定のコントロール種別・特定のプロパティ名に限定されない（`FillPortions`, `LayoutAlignItems`, `AlignInContainer`, `Width`, `Height`, `ItemDisplayText`, `Alignment` など、あらゆるプロパティで起こり得ることを確認済み）。

**見分け方**: `compile_canvas` が成功と報告しても、それは「サーバーに正しく反映された」ことの証明にはならない。**変更内容が視覚的に重要な画面では、`sync_canvas` で一時ディレクトリに同期し、実際に反映されているかを直接比較して確認する。**

**回避策（確認済み）**: 一度反映に失敗した値は、同じ値をそのまま何度 `compile_canvas` しても反映されないことが多い（再試行だけでは直らない）。その代わり、**一旦まったく別の値に変更して `compile_canvas` → 反映を確認 → 本来の値に戻して `compile_canvas`** という2段階を踏むと、反映されることが多い。それでも本来の値だけが繰り返し弾かれる場合は、さらに別の値を経由する（3段階目）。数値プロパティ（`Width`/`Height`/`FillPortions`など）で見た目に影響しない誤差（数px程度）なら、無理に元の値に戻さず、実際に反映された値をそのまま採用してよい。列挙値プロパティ（`Alignment`など）でどうしても反映されない場合は、そのプロパティ自体を削除して既定動作に委ねることも検討する。

```
1. 元の値のままcompile_canvas → sync_canvasで確認 → 反映されていない
2. 別の値（例: 一時的にまったく違う値）に変更してcompile_canvas → sync_canvasで確認 → 反映された
3. 本来の値に戻してcompile_canvas → sync_canvasで確認
   - 反映されていれば完了
   - まだ反映されていなければ、見た目に影響しない差なら反映された値を採用する。
     影響する場合はさらに別の値を経由して2〜3を繰り返す
```

**さらに重い症状（実際に発生）**: 数十コントロール規模の一括変更（例: 全画面のボタンをシャドウラッパーで一括ラップ）を行った直後、**ローカルのファイルは正しいまま何も変えていないのに、`compile_canvas`を実行するたびにサーバー側の反映状態が「反映されている」⇄「一部の変更だけロールバックされている（例: 最初の1個だけ残り、後から追加した分だけ消える）」で行ったり来たりする**ことを確認した。これはプロパティ単位の反映漏れよりも重く、コントロールそのものが丸ごと現れたり消えたりする。
- 本人（ユーザー）のStudioタブの表示も、このサーバー側の実際の状態と一致する（タブ側の表示が古いだけ、ではなく本当にサーバーが不安定）。
- **回避策**: タブを閉じて再接続し、その上で明示的に「保存」（可能なら「公開」）する。共同編集セッションの一時的な状態に留めず、保存で確定させることで安定した（未検証だが今回はこれで解消した）。
- ブラウザの編集キャンバス（デザイン画面）の見た目が、保存・再接続の前後で一時的に崩れて見える（コントロールが空欄・位置ズレに見える等）ことがある。これは編集キャンバスの描画が古い状態のままキャッシュされているだけで、実際の動作を反映していないことがある。**見た目の最終判断は編集キャンバスではなくPlayモード（プレビュー実行）で行う。**

### DropShadowを持つ要素は親コンテナに余白を持たせる

`DropShadow`（`Semilight`/`Regular`/`Light`など）を設定した要素を親コンテナに入れる場合、**親コンテナの `Height`/`Width` を子要素とぴったり同じにしない。** 影は要素の外枠から数px はみ出して描画されるため、親と子のサイズが完全に一致していると、親コンテナの境界線で影が見切れて（クリップされて）しまう。

- 親コンテナの `Height`（横並びの場合は `Width` も）を、子要素の実サイズより**目安4px程度大きく**する。
- 親コンテナに `LayoutAlignItems: =LayoutAlignItems.Center` を指定し、子要素を中央に配置する。余白を上下（または左右）均等に配分し、影がどちら向きにはみ出しても切れないようにする。

```yaml
# ❌ 影が見切れる: 親と子の高さが完全一致
grpCardRow:
  Control: GroupContainer
  Variant: AutoLayout
  Properties:
    Height: =110   # カードの高さとぴったり同じ
  Children:
    - card1:
        Control: GroupContainer
        Properties:
          Height: =110
          DropShadow: =DropShadow.Semilight

# ✅ 親に4pxの余白を持たせ、中央揃えにする
grpCardRow:
  Control: GroupContainer
  Variant: AutoLayout
  Properties:
    Height: =114   # カードの高さ + 4px
    LayoutAlignItems: =LayoutAlignItems.Center
  Children:
    - card1:
        Control: GroupContainer
        Properties:
          Height: =110
          DropShadow: =DropShadow.Semilight
```

同じ理由で、影付き要素を画面の一番外側（コンテナに包まれていない状態）に置く場合も、画面の端ギリギリに配置せず数px の余白を取る。

### Galleryの行間・高さの計算（`TemplatePadding` に頼らない）

`Gallery`（`Vertical`）の行間は `TemplatePadding` ではなく、`TemplateSize` と行テンプレート自身の `Height` の差分で作る。

- `TemplatePadding` は未指定のとき中立（`0`）とは限らない既定値を持つ。指定を省略すると想定外の行間が加算され、「行数 × `TemplateSize` で計算が合っているはずなのにスクロールバーが出る」原因になる（[「未指定のプロパティは中立・無効と決めつけない」](#配置ルール)の具体例の1つ）。逆に、原因調査のために `TemplatePadding: =0` を明示しただけで終わらせると、既定値が担っていた行間の余白まで消えて見た目が窮屈になる。**`TemplatePadding` は必ず `=0` を明示した上で、行間は `TemplateSize` 側で確保する。**
- 行間は `TemplateSize`（Galleryが1行に割り当てる高さ）と、行テンプレートControl自身の `Height` の差分で作る。例: 行の実体 `Height` が `48`で行間を`8px`にしたい場合、`TemplateSize: =56`。
- `Gallery.Height` は `TemplateSize × 表示行数` に対して余裕（目安 +10px程度）を持たせる。ぴったり同じ値にすると、境界のわずかな誤差でスクロールバーが出ることがある。
- 親のラッパーコンテナ（影付きカードなど）の `Height` は、`Gallery.Height` の変更に合わせて[パディングとサイズの計算](#パディングとサイズの計算)のルールで再計算する。

```
Gallery.Height ≈ TemplateSize × 表示行数 + 余裕(10px程度)
行間 = TemplateSize − 行テンプレートControlのHeight
```

```yaml
# ❌ TemplatePaddingを0にしただけでは行間が失われて窮屈になる
galItemList:
  Control: Gallery
  Variant: Vertical
  Properties:
    Height: =270
    TemplatePadding: =0
    TemplateSize: =52   # 行のHeight(48)との差が4pxしかなく窮屈
  Children:
    - grpRowTemplate:
        Properties:
          Height: =48

# ✅ TemplateSizeと行Heightの差分で行間を確保し、Heightにも余裕を持たせる
galItemList:
  Control: Gallery
  Variant: Vertical
  Properties:
    Height: =290   # TemplateSize(56) x 5行 = 280 + 余裕10px
    TemplatePadding: =0   # 行間はTemplateSizeとHeightの差で作るため0固定
    TemplateSize: =56   # 行のHeight(48) + 行間8px
  Children:
    - grpRowTemplate:
        Properties:
          Height: =48
```

## 9. コントロール仕様リファレンス

**Control@Versionの信頼性について**: 以下の `Control@Version` は過去のプロジェクトでの実績値であり、新しい環境で検証済みとは限らない。**同じPower Platformでも、環境・テナントによって実際に使えるコントロールのバージョンが異なることを実機で確認済み**（例: 同じ`ModernTextInput`でも環境によって`1.1.0`だったり`0.0.54`だったりする）。バージョン不一致自体は警告どまりで大きな問題にならないことが多いが、**バージョンが変わると使えるProperty名も変わっている場合がある**ため、以下の一覧をそのまま信用せず、可能であれば実装前にその環境の`describe_control`（またはPower Apps Studioの詳細ペイン）で実際のProperty名を確認する。特に「似た名前の兄弟コントロール」間でのProperty名の取り違え（`ModernText`の`Color`と`Badge`の`FontColor`、`ModernDropdown`の`Default`と`ModernCombobox`の`DefaultSelectedItems`など）は実際にエラーとして発生しているので注意する。バージョン不一致・Property不一致でエラーが出た場合は、その時点の正しい値でこの章を更新する。

### Screen
- 使用可能な主なProperties: `LoadingSpinnerColor`
```yaml
Screens:
  ScreenName:
    Properties:
      LoadingSpinnerColor: =RGBA(56, 96, 178, 1)
```

### GroupContainer
- Control: `GroupContainer@1.5.0`
- Variant: `ManualLayout` / `AutoLayout`
- 必須: `Variant`, `Width`, `Height`
- ManualLayout時: 子ControlはX/Yで配置し、X, Y, Width, Heightを明示する。
- AutoLayout時: `LayoutDirection` を指定する。`LayoutGap`, `LayoutAlignItems`, Padding系を必要に応じて指定する。子ControlのX/Yは省略してよい。
- 使用可能な主なProperties: `BorderStyle`, `BorderThickness`, `Fill`, `Height`, `Width`, `X`, `Y`, `PaddingBottom`, `PaddingLeft`, `PaddingRight`, `PaddingTop`, `LayoutAlignItems`, `LayoutDirection`, `LayoutGap`, `AlignInContainer`, `FillPortions`, `LayoutMinHeight`, `LayoutMinWidth`
- LayoutDirection例: `=LayoutDirection.Horizontal` / `=LayoutDirection.Vertical`

### Gallery
- Control: `Gallery@2.15.0`
- Variant例: `BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0`, `BrowseLayout_Horizontal_TwoTextOneImageVariant_ver5.0`, `BrowseLayout_Flexible_SocialFeed_ver5.0`
- 必須: `Variant`, `Items`, `Width`, `Height`
- 推奨: `X`, `Y`, `TemplatePadding`, `TemplateSize`
- 重要: GalleryはVariantを必ず指定する。ItemsをGalleryには必ず指定する。モックではTable形式の仮データを使用してよい。Gallery配下の子Controlでは `ThisItem` / `Parent` / `Self` を使用可能。
- 重要（行間・スクロールバー対策）: `TemplatePadding` は必ず `=0` を明示し、行間は `TemplateSize` と行テンプレートControlの `Height` の差分で作る。詳細は[「Galleryの行間・高さの計算」](#galleryの行間高さの計算templatepadding-に頼らない)を参照。

### Label
- Control: `Label@2.5.1`
- 必須: `Text`, `Width`, `Height`
- 推奨: `X`, `Y`, `Color`, `Font`, `FontWeight`, `Size`, Padding系
- 使用可能な主なProperties: `Align`, `AutoHeight`, `BorderColor`, `Color`, `Font`, `FontWeight`, `Height`, `OnSelect`, Padding系, `Size`, `Text`, `VerticalAlign`, `Visible`, `Width`, `X`, `Y`
- 注意: `Text` 未指定は禁止。

### ModernText
- Control: `ModernText@1.0.0`
- 必須: `Text`, `Width`, `Height`
- 推奨: `X`, `Y`, `Color`, `Font`, `FontWeight`, `Size`, `Visible`
- 注意: `Text` 未指定は禁止。フォントサイズのプロパティ名は `FontSize` ではなく `Size`（`Badge` は逆に `FontSize` なので混同しない）。
- **文字色のプロパティ名は `Color`。** サイズが`Size`、色が`Color`——`ModernText`のフォント関連プロパティは短い名前で統一されている（`Badge`は逆に`FontSize`/`FontColor`という長い名前なので、コントロールごとに正しい方を使う）。
- **注意（スクロールバー回避）**: `Height` が `Size` に対して小さすぎると、テキスト自体に不要なスクロールバーが表示される。**この症状は編集キャンバスでは出ず、再生モード（Play）でだけ出る。** 編集キャンバスでの目視だけで値を決めると、実際には2〜3px足りず、Playモードでスクロールバーが出るケースがある。以下は `Height ≥ Size × 1.5 + 10` の式から機械的に算出した値（編集画面で足りているように見えても、この値を下回らないこと）:

  | Size | 最小 Height |
  |---|---|
  | 11 | 27 |
  | 12 | 28 |
  | 13 | 30 |
  | 15 | 33 |
  | 16 | 34 |
  | 18 | 37 |
  | 20 | 40 |
  | 22 | 43 |
  | 24 | 46 |
  | 28 | 52 |

  表にない `Size` を使う場合は `Height ≥ Size × 1.5 + 10` で計算する（表の値と一致しない独自の目分量にしない）。`Wrap: =true` で複数行になる場合は、上記を1行あたりの最小値として扱い、行数分の余裕を追加すること。

  **さらに推奨: 固定の数値を目分量・暗算で決めず、`Height` 自体を `Size` から計算する式にする。** `Height: =Self.Size * 1.5 + 10` のように書けば、`Size` を変更してもこの制約が自動的に満たされ続け、暗算ミスによる違反が構造的に起きなくなる（複数行時は `+ 行数分の高さ` を式に足す）。数値を決め打ちする場合より優先してこちらを使う。

  ```yaml
  # ❌ Sizeから逆算した数値を手入力(暗算ミスや後からのSize変更で崩れやすい)
  txtCardValue:
    Properties:
      Size: =24
      Height: =32   # 本来 46 必要（24*1.5+10）だが目分量で32にしてしまった

  # ✅ Heightを Size からの計算式にして、常に条件を満たすようにする
  txtCardValue:
    Properties:
      Size: =24
      Height: =Self.Size * 1.5 + 10
  ```
  - この違反は編集キャンバスでは気づけずPlayモードでしか顕在化しないため、可能であれば「`ModernText`の`Height`が`Size*1.5+10`を下回っていないか」を機械的に検出する簡単なチェックスクリプトを用意し、`ModernText`を追加・変更するたびに実行することを推奨する（目視確認だけに頼らない）。

### ModernButton
- Control: `ModernButton@1.0.0`
- 必須: `Text`, `Width`, `Height`
- 推奨: `X`, `Y`, `AccessibleLabel`, `BasePaletteColor`, `Icon`, `Font`, `FontWeight`, `Visible`, `DisplayMode`
- 使用可能な主なProperties: `Text`, `AccessibleLabel`, `Align`, `BasePaletteColor`, `BorderStyle`, `BorderThickness`, `Font`, `FontWeight`, `Icon`, Padding系, Radius系, `Size`, `VerticalAlign`, `Width`, `Height`, `X`, `Y`
- 注意: `Text` 未指定は禁止。Iconだけのボタンにする場合も、`Text` または `AccessibleLabel` を設定する。
- **`DropShadow`プロパティが存在しない。** ボタンに影を付けたい場合は、下記「ボタンに影を付ける（シャドウラッパー）」の通り`GroupContainer`でラップする。

#### ボタンに影を付ける（シャドウラッパー）

`ModernButton`自体には`DropShadow`が無いため、影を付けたい場合は**`Variant: ManualLayout`の`GroupContainer`でボタンをラップし、そのコンテナ側に`DropShadow`を設定する。**

手順:
1. ラッパー（`GroupContainer`, `Variant: ManualLayout`）の`Height`/`Width`を、元のボタンの`Height`/`Width`と**完全に同じ値**にする（影がボタンの輪郭にぴったり沿うようにするため。他の「DropShadowを持つ要素は親に余白を持たせる」ルールとは異なり、ここではラッパー自身が影を持つ面なので、ボタンとラッパーの間に余白は不要）。
2. ボタンの`AlignInContainer`（と`Visible`があればそれも）をラッパー側に移す。`ManualLayout`の子は`AlignInContainer`を取らないため。**`Visible`を移し忘れると、ボタンが非表示になってもラッパーの影の箱だけが残ってしまう。**
3. ボタン自身に`X: =0`, `Y: =0`を追加し、`Height`/`Width`はラッパーと同じ値をそのまま指定する。
4. ラッパーの`DropShadow`は`DropShadow.Semilight`にする（`DropShadow.Light`は既知の同期バグで消えるため使わない。[該当ルール](#dropshadowを持つ要素は親コンテナに余白を持たせる)参照）。
5. ラッパーの新しいコントロール名は、元のボタン名がアプリ全体で一意だったことを利用して`grpBtn<元のボタン名からbtn接頭辞を除いた部分>Shadow`とする（例: `btnSubmit` → `grpBtnSubmitShadow`）。これで新規名もアプリ全体で一意になる。

```yaml
# ❌ ModernButtonにDropShadowを直接書くとエラーになる（存在しないプロパティ）
- btnSubmit:
    Control: ModernButton
    Properties:
      DropShadow: =DropShadow.Semilight   # 存在しない
      Height: =40
      Width: =110

# ✅ ManualLayoutのGroupContainerでラップする
- grpBtnSubmitShadow:
    Control: GroupContainer
    Variant: ManualLayout
    Properties:
      AlignInContainer: =AlignInContainer.Start   # 元のボタンから移動
      DropShadow: =DropShadow.Semilight
      FillPortions: =0
      Height: =40                                   # ボタンと同じ値
      Visible: =locItem.Status = "Draft"             # 元のボタンにVisibleがあれば移動
      Width: =110                                    # ボタンと同じ値
    Children:
      - btnSubmit:
          Control: ModernButton
          Properties:
            Height: =40    # ラッパーと同じ値
            OnSelect: |-
              =IfError(...)
            Text: ="送信"
            Width: =110    # ラッパーと同じ値
            X: =0
            Y: =0
```

- `Icon`だけの正方形ボタン（`Layout: =ButtonLayout.IconOnly`、削除ボタンなど）にも同じ手順を適用する。ラッパーはボタンと同じ正方形サイズにする。
- ラッパーが窮屈（親の行の高さとぴったり同じ）だと、影が親コンテナの境界で見切れることがある（[「DropShadowを持つ要素は親コンテナに余白を持たせる」](#dropshadowを持つ要素は親コンテナに余白を持たせる)ルール通り）。親の行の高さに数px余裕があるか確認し、無ければラッパーの高さを親の行より少しだけ小さくするなどして余白を確保する。
- 一覧の行の中の小さなアイコンボタン（有効/無効トグル、削除ボタンなど）は、密集したテーブル行の中で個別に影を付けると見た目がうるさくなることがある。影を付けるかどうかは一律に決めず、実際の見た目で判断する（テーブル行内のボタンは影なしのままにする、という判断も妥当）。

### ModernTextInput
- Control: `ModernTextInput@1.1.0`（環境によっては`0.0.54`など別バージョンの場合がある。実装前に`describe_control`で確認する）
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `Default`, `Placeholder`, `AccessibleLabel`, `BasePaletteColor`, `BorderStyle`, `BorderThickness`
- 使用可能な主なProperties: `AccessibleLabel`, `BasePaletteColor`, `BorderStyle`, `BorderThickness`, `Default`, `Font`, `MaxLength`, `Placeholder`, `Type`, Padding系, Radius系, `Width`, `Height`, `X`, `Y`
- 未入力時のヒント表示は、プロパティ名 **`Placeholder`** に文字列を指定する（例: `Placeholder: ="キーワードで検索"`）。複数行入力にする場合は `Type: =TextInputType.Multiline`、最大文字数は `MaxLength` で指定する。
- **`AccessibleLabel`は画面には表示されない。** スクリーンリーダー向けの説明文だけを設定するプロパティであり、視覚的なヒント文字列にはならない。検索欄などで「何を入力する欄か」を見た目にも示したい場合は、`AccessibleLabel`だけを設定して満足せず、必ず`Placeholder`も設定する（`AccessibleLabel`しか設定しないと、コンパイルは通るが画面には何も表示されず、コントロールの既定のヒント文言のままになる。見た目に現れないため気づきにくい）。
- **`ModernTextInput`に`HintText`というプロパティは存在しない。** 他のUIフレームワークでよく使われる名前につられて`HintText`を書いてしまい、`Unknown property`エラーになるケースが複数回発生している。ヒント文字列のプロパティ名は`Placeholder`の1つだけと覚える。

### ModernDropdown
- Control: `ModernDropdown@1.0.1`
- 必須: `Items`, `Width`, `Height`
- 推奨: `X`, `Y`, `Default`, `Appearance`, `ItemDisplayText`, `AccessibleLabel`
- 使用可能な主なProperties: `AccessibleLabel`, `Appearance`, `BasePaletteColor`, `BorderColor`, `BorderStyle`, `BorderThickness`, `Color`, `Default`, `Fill`, `Font`, `ItemDisplayText`, `Items`, Padding系, Radius系, `Width`, `Height`, `X`, `Y`
- 注意: `Items` 未指定は禁止。`Default` が不明な場合は `Default` を出力しない。`Default: |+ =` のような不正な空値は禁止。
- **単一選択（`ModernDropdown`）の初期値プロパティは `Default`。** 複数選択が必要な場合は`ModernDropdown`ではなく`ModernCombobox`を使う（初期値プロパティ名もコントロールごとに異なる）。単一選択か複数選択かで、コントロールとプロパティ名の両方が変わる点に注意する。
- **`Default`は`Items`の1行と同じ形の「レコード」を指定する。文字列だけを指定しない。** `Items`が`=Table({Value:"すべて"}, {Value:"高"}, ...)`のような「`Value`列を持つレコードのテーブル」なら、`Default`も`={ Value: "すべて" }`のようにレコードにする。`Default: ="すべて"`のように文字列だけを指定すると型が一致せず、初期選択が正しく機能しない（見た目には気づきにくいが、実際に「担当者の初期値が『すべて』のはずが別の項目が選ばれてしまう」不具合として発生した）。

  ```yaml
  # ❌ Defaultが文字列（Itemsの行の型と一致しない）
  ddlStatusFilter:
    Properties:
      Default: ="すべて"
      Items: =Table({Value:"すべて"},{Value:"進行中"},{Value:"完了"})

  # ✅ Defaultも Items の1行と同じレコード形にする
  ddlStatusFilter:
    Properties:
      Default: |-
        ={ Value: "すべて" }
      Items: =Table({Value:"すべて"},{Value:"進行中"},{Value:"完了"})
  ```
- **重要: `Placeholder` プロパティは存在しない**（`ModernTextInput`/`ModernDatePicker`と違い、未選択時に何も表示するものがない）。`Default`のレコードが実際に選択済みとして視覚的に反映されないケースがあり、その場合ドロップダウンが空欄に見えて何のフィルタか利用者にわからなくなる。**フィルタ用途などで複数のドロップダウンを並べる場合は、各ドロップダウンの上（または横）に小さな`ModernText`ラベルを必ず添える**（`Default`の表示に頼らない）。
- `Appearance`（`FilledDarker`/`FilledLighter`/`Outline`）を明示すること。未指定のままにしない。**列挙型名は`Appearance`単体（プレフィックス無し）。** `=Appearance.Outline`と書く。`'ModernControlsCommon.Appearance'.Outline`のような存在しない型名を作らない（`describe_control`で確認済み）。

### ModernCombobox
- Control: `ModernCombobox@1.1.0`
- 必須: `Items`, `Width`, `Height`
- 推奨: `X`, `Y`, `DefaultSelectedItems`, `ItemDisplayText`, `AccessibleLabel`
- 使用可能な主なProperties: `AccessibleLabel`, `BasePaletteColor`, `BorderColor`, `BorderStyle`, `BorderThickness`, `Color`, `Fill`, `Font`, `ItemDisplayText`, `Items`, Padding系, Radius系, `Width`, `Height`, `X`, `Y`
- 注意: `Items` 未指定は禁止。

### ModernDatePicker
- Control: `ModernDatePicker@1.0.0`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `DefaultDate`, `BasePaletteColor`
- 使用可能な主なProperties: `BasePaletteColor`, `BorderColor`, `BorderStyle`, `BorderThickness`, `Color`, `DefaultDate`, `Fill`, `Font`, `FontWeight`, Padding系, Radius系, `Size`, `Strikethrough`, `Width`, `Height`, `X`, `Y`
- 注意: 初期値を設定する入力Propertyは `DefaultDate`（`Date`型）。`SelectedDate` は選択結果を読み取るための**出力専用**プロパティで、Propertiesには書けない。編集画面で既存の日付を初期表示したい場合は必ず `DefaultDate` を使う。

### Badge
- Control: `Badge@0.0.24`
- 必須: `Content`, `Width`, `Height`
- 推奨: `X`, `Y`, `ThemeColor`, `Appearance`, `BasePaletteColor`, `Align`, `VerticalAlign`
- 使用可能な主なProperties: `Content`, `Align`, `Appearance`, `BasePaletteColor`, `DisplayMode`, `Font`, `FontColor`, `FontSize`, `FontWeight`, `Shape`, `ThemeColor`, `VerticalAlign`, `Visible`, `Width`, `Height`, `X`, `Y`
- ThemeColor（`describe_control`で確認済みの実在する値のみ）: `Brand`, `Danger`, `Important`, `Informative`, `Severe`, `Subtle`, `Success`, `Warning`。例: `='BadgeCanvas.ThemeColor'.Danger`
- Appearance: `Filled`, `Ghost`, `Outline`, `Tint`。**基本的に `Tint` を使う**（例外は[第2章のステータスカラー表](#ステータスカラーbadge-の-themecolor-を正とするパターンの例)を参照）。例: `='BadgeCanvas.Appearance'.Tint`
- ステータス表示時の具体的な組み合わせの考え方は [第2章のステータスカラー表](#ステータスカラーbadge-の-themecolor-を正とするパターンの例) を参照。
- 注意: `Content` 未指定は禁止。`Width` / `Height` 未指定は禁止。

### ModernIcon
- Control: `ModernIcon@1.1.0`
- 必須: `Icon`, `Width`, `Height`
- 推奨: `X`, `Y`, `IconStyle`, `IconColor`
- 使用可能な主なProperties: `BorderColor`, `BorderStyle`, `BorderThickness`, `Fill`, `Icon`, `IconColor`, `IconStyle`, Padding系, Radius系, `Rotation`, `Width`, `Height`, `X`, `Y`
- Icon例: `="ArrowDown"` / IconStyle例: `=IconStyle.Filled`

### Icon プロパティの値（`ModernButton`/`ModernIcon` 共通・重要）

`ModernButton`・`ModernIcon` の `Icon` プロパティは自由文字列で、`Icon: Enum` のような列挙型ではないため `describe_control` では正誤を検証できない。Power Appsのモダンコントロールで使えるのは、Fluent UIアイコン全体（約2900種）ではなく**181種類の限定セット**のみ。

- **名前が181種類に一致しない場合、エラーにはならず単なる円（circle）アイコンとして表示される。** コンパイルは通ってしまうため、見た目で気づくまで気づけない。
- 大文字小文字も区別される。

これまでに確認済みの、汎用的によく使うアイコンの対応表（例）:

| 用途 | Icon値 | 備考 |
|---|---|---|
| ホーム | `Home` | 確認済み・有効 |
| 追加・新規登録 | `Add` | 確認済み・有効 |
| 設定・管理 | `Settings` | 確認済み・有効 |
| 削除 | `Delete` | 確認済み・有効 |
| 一覧・リスト | `DocumentBulletList` | ❌`BulletedList`は181種類に含まれず無効。これに置き換える |
| ダッシュボード・分析 | `PulseSquare` | ❌`BarChart4`は181種類に含まれず無効。このアイコンセットに専用のチャート系アイコンが無い場合は、近い意味の`PulseSquare`で代替する |

新しいアイコンが必要な場合は、[Power Apps FluentIcon Reference](https://github.com/thepowerappsguy/power-apps-fluenticon-reference)（181種類の一覧と見た目）で存在を確認してから使う。推測で名前を作らない。

### Classic/Icon
- Control: `Classic/Icon@2.5.0`
- 必須: `Icon`, `Width`, `Height`
- 推奨: `X`, `Y`, `Tooltip`, `AccessibleLabel`
- 使用可能な主なProperties: `AccessibleLabel`, `BorderColor`, `BorderThickness`, `Color`, `DisabledBorderColor`, `DisabledColor`, `Height`, `Icon`, `OnSelect`, Padding系, `Tooltip`, `Width`, `X`, `Y`
- Icon例: `=Icon.ChevronRight` / `=Icon.Cancel`

### Image
- Control: `Image@2.2.3`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `Image`, `ImagePosition`, `Tooltip`
- 使用可能な主なProperties: `BorderColor`, `BorderThickness`, `Height`, `Width`, `X`, `Y`, `Image`, `ImagePosition`, `OnSelect`, Radius系, Padding系, `Tooltip`
- ImagePosition例: `=ImagePosition.Fill`

### Rectangle / Circle
- Control: `Rectangle@2.3.0` / `Circle@2.3.0`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `Fill`
- 使用可能な主なProperties: `BorderColor`, `Fill`, `Height`, `Width`, `X`, `Y`, `OnSelect`, `Visible`

### Header
- Control: `Header@0.0.44`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `Title`, `BorderColor`, `Font`
- 使用可能な主なProperties: `BorderColor`, `BorderRadiusBottomLeft`, `BorderRadiusBottomRight`, `BorderRadiusTopLeft`, `BorderRadiusTopRight`, `BorderStyle`, `BorderThickness`, `Font`, `Title`, `TitleFontSize`, `Width`, `Height`, `X`, `Y`

### Form
- Control: `Form@2.4.4`
- Layout: `Vertical`
- 必須: `Layout`, `DataSource`, `Width`, `Height`
- 推奨: `X`, `Y`, `BorderColor`, `BorderThickness`
- 注意: 会議用モックでは原則Formを使用しない。Formは実データソース前提になりやすいため、登録画面モックではContainer + 入力Controlを優先する。

### TypedDataCard
- Control: `TypedDataCard@1.0.7`
- Variant例: `TextualEdit`, `ComboBoxEdit`, `ComboBoxMultiSelectEdit`, `DateEdit`
- 必須: `Variant`, `DataField`, `Default`, `DisplayName`, `Required`, `Update`, `Width`
- 推奨: `X`, `Y`, `IsLocked`
- 重要: DataCardではVariant必須。DataCard配下には `FieldName` / `FieldValue` / `ErrorMessage` / `FieldRequired` のMetadataKeyを持つ子Controlを配置する。

### Text（DataCard用）
- Control: `Text@0.0.51`
- 用途: DataCardのラベル、エラー、必須マークなど。
- 必須: `Text`, `Width`, `Height`
- 推奨: `X`, `Y`, `Weight`, `Wrap`
- MetadataKey例: `FieldName`, `FieldValue`, `ErrorMessage`, `FieldRequired`

### TextInput
- Control: `TextInput@0.0.54`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `Value`, `AccessibleLabel`, `DisplayMode`
- 使用可能な主なProperties: `AccessibleLabel`, `DisplayMode`, `Mode`, `Required`, `ValidationState`, `Value`, `Width`, `Height`, `X`, `Y`
- Mode例: `="'TextInputCanvas.Mode'.TextInputModeSingleLine"`

### ComboBox
- Control: `ComboBox@0.0.51`
- 必須: `Items`, `Width`, `Height`
- 推奨: `X`, `Y`, `DefaultSelectedItems`, `DisplayMode`, `Required`, `SelectMultiple`
- 注意: `Items` 未指定は禁止。

### DatePicker
- Control: `DatePicker@0.0.46`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `SelectedDate`, `StartDate`, `EndDate`

### ModernNumberInput
- Control: `ModernNumberInput@1.1.0`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `Min`, `Max`, `BasePaletteColor`
- 使用可能な主なProperties: `AccessibleLabel`, `BasePaletteColor`, `BorderColor`, `BorderStyle`, `BorderThickness`, `Color`, `Fill`, `Font`, `Max`, `Min`, Padding系, Radius系, `Size`, `Width`, `Height`, `X`, `Y`

### CheckBox
- Control: `CheckBox@0.0.30`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `AccessibleLabel`, `CheckboxSize`

### ModernRadio
- Control: `ModernRadio@1.0.0`
- 必須: `Items`, `Width`, `Height`
- 推奨: `X`, `Y`, `ItemDisplayText`
- 注意: `Items` 未指定は禁止。

### ModernTabList
- Control: `ModernTabList@1.0.0`
- 必須: `Items`, `Width`, `Height`
- 推奨: `X`, `Y`, `Size`, `Alignment`, `Appearance`, `TabSize`
- 注意: `Items` 未指定は禁止。
- **重要: `Alignment`（`LayoutDirection.Horizontal`/`Vertical`）・`Appearance`（`TabListAppearance.Subtle`など）・`TabSize`（`TabSize.Small`/`Medium`/`Large`）を省略すると、タブが正しく描画されず小さな点のようにしか表示されないことがある。** 3つとも明示的に指定すること。

### ModernSlider
- Control: `ModernSlider@1.0.0`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `Min`, `Max`

### ModernInformationButton
- Control: `ModernInformationButton@1.0.0`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `BasePaletteColor`, `IconColor`

### Spinner
- Control: `Spinner@1.4.6`
- 必須: `Width`, `Height`
- 推奨: `X`, `Y`, `Label`, `SpinnerColor`, `TrackColor`

### ModernLink
- Control: `ModernLink@1.0.0`
- 必須: `Text`, `URL`, `Width`, `Height`
- 推奨: `X`, `Y`, `AccessibleLabel`
- 注意: `URL` 未指定は禁止。`Text` 未指定は禁止。

### HtmlViewer
- Control: `HtmlViewer@2.1.0`
- 必須: `HtmlText`, `Width`, `Height`
- 推奨: `X`, `Y`, `Font`
- 注意: `HtmlText` 未指定は禁止。

### Charts / Legend / PowerBI
- BarChart: `BarChart@2.4.0` / PieChart: `PieChart@2.3.0` / Legend: `Legend@2.1.0` / PowerBI: `PowerBI@2.4.0`
- 注意: 会議用モックでは原則Charts / PowerBIは使用しない。必要な場合のみ既存YAMLを参考にする。ChartはItems設定が複雑なため、推測で作成しない。

### 上記に無いコントロール（ModernDataGrid, ModernCard, Avatar, Progress など）
- 上の一覧は過去のプロジェクトで実績のある仕様。新しいプロジェクトで初めて使う場合は、**必ず `describe_control` でControl@Version・Variant・必須Propertyを取得してから使用する。** 推測で仕様を作らない。

## 10. AI生成時の禁止事項

- Control名やControl@Versionを推測で作らない。
- Variantを省略しない（`GroupContainer`, `Gallery`, `TypedDataCard` は特に必須）。
- 存在しないPropertyを作らない。
- `ModernButton` / `Button` の `Text` を省略しない。
- `Text` 系Controlの `Text` を省略しない。
- `Badge` の `Content` を省略しない。
- `Dropdown` / `ComboBox` / `Gallery` / `ModernRadio` / `ModernTabList` の `Items` を省略しない。
- モック生成時にDataSource、Patch、SubmitForm、Flow.Runを勝手に作らない。
- `Default` が不明な場合に不正な複数行YAML（例: `Default: |+ =`）を出力しない。
- SharePoint等の列名を勝手に仮定しない。
- 複雑なPower Fxを勝手に書かない。
- ステータスを色付き `Rectangle` で自作しない（`Badge` を使う）。
- `Badge` の `ThemeColor`/`Appearance` に、第9章に列挙した実在の値以外（例: 存在しない `Info` など）を使わない。
- `ModernButton`/`ModernIcon` の `Icon` に、第9章の対応表または[FluentIcon Reference](https://github.com/thepowerappsguy/power-apps-fluenticon-reference)で確認していない名前を推測で使わない（無効な名前はエラーにならず円アイコンになるため気づきにくい）。
- `Color.White` 直置きの無装飾な背景にしない。
- `Button1`, `Label2` のような初期値のままのコントロール名を残さない。
- 保存・削除ボタンに確認導線がない状態にしない。
- 水平・垂直コンテナ内の要素に、理由なく `0` 以外の `FillPortions` を指定しない。
- コンテナのパディング（最低4px）を差し引かずに、子要素の `Height`/`Width` を親と同じ値のまま指定しない（はみ出し・スクロールバーの原因になる）。
- コンテナ内の要素で `AlignInContainer` の指定を省略しない（省略すると既定値が `Stretch` になることがある）。
- コンテナのサイズと子要素群の合計サイズが、縦・横どちらか一方だけでなく**両方とも**合っておらず、意図しない隙間ができるレイアウトにしない。
- 1つのセクションの隙間だけを直して、同じ画面内の他のセクションと外側の幅が揃っているかを確認しないまま終わらせない。
- `DropShadow` を持つ要素の親コンテナを、子要素とぴったり同じサイズのままにしない（影が見切れる）。
- `Fill` を持たないレイアウト専用のラッパーコンテナに `DropShadow`・`BorderStyle` などの視覚効果を付けない。
- `GroupContainer` の `DropShadow` を省略しない（既定値が `None` とは限らない）。影が不要な場合も `DropShadow.None` を明示する。
- プロパティを省略したときの既定値を「中立・無効」と推測で決めつけない。
- `Gallery` の `TemplatePadding` を未指定のまま行間ができることを期待しない（`=0` を明示し、行間は `TemplateSize` と行テンプレートの `Height` の差分で作る）。
- **子要素が無い`GroupContainer`に `Children: []` のようなフロースタイル（`[...]`）の空配列を書かない。** `.pa.yaml`のパーサーはこの書き方を構文エラー（`YamlInvalidSyntax; Expected 'Scalar', got 'SequenceStart'`）にする。スペーサー用など子要素を持たないコンテナを作るときは、**`Children` キー自体を省略する。**

  ```yaml
  # ❌ 空のフロースタイル配列 → コンパイルエラー(PA1001)になる
  grpSpacer:
    Control: GroupContainer
    Properties:
      FillPortions: =1
    Children: []

  # ✅ 子要素が無い場合は Children キーごと書かない
  grpSpacer:
    Control: GroupContainer
    Properties:
      FillPortions: =1
  ```
- `ModernDropdown`/`ModernCombobox`の「未選択」判定を、コントロール自身の`Selected`/`SelectedItems`が`Blank()`になることを前提に書かない（`Default`未指定でも`Blank()`にならないことがある）。

## 11. AI生成時の推奨事項

- まず `GroupContainer` で大枠を作る。
- `Header` / `SearchArea` / `ContentArea` / `ActionArea` の構成を優先する。
- 会議用モックでは `Label`, `ModernText`, `ModernButton`, `ModernTextInput`, `ModernDropdown`, `Gallery`, `Badge` を中心に使う。
- `Form` や `TypedDataCard` は実データソース前提になりやすいため、モックでは必要最小限にする。
- `Gallery` はサンプルデータを使用する。
- ロジックは後工程の実装エージェントに任せる。
- 出力前にYAML構造、`Control@Version`、`Variant`、`Properties` 階層を自己チェックする。

## 12. 出力前チェックリスト

- [ ] `Control@Version` があるか
- [ ] Variantが必要なControlにVariantがあるか（`GroupContainer`, `Gallery`, `TypedDataCard`）
- [ ] `Gallery` に `Items` があるか
- [ ] `ModernButton` / `Button` に `Text` があるか
- [ ] `Text` / `Label` に `Text` があるか
- [ ] `Badge` に `Content` があるか
- [ ] `Dropdown` / `ComboBox` / `ModernRadio` / `ModernTabList` に `Items` があるか
- [ ] `ModernLink` に `Text` と `URL` があるか
- [ ] `HtmlViewer` に `HtmlText` があるか
- [ ] `ManualLayout` 配下のControlに `X`/`Y`/`Width`/`Height` があるか
- [ ] 子要素が無いコンテナ（スペーサーなど）で `Children: []` のようなフロースタイル空配列を書いていないか。子要素が無いなら `Children` キー自体を省略しているか
- [ ] **画面の大部分（ヘッダー・サイドナビ・カードの並び・テーブルの行など）が`ManualLayout`＋絶対座標だらけになっていないか。** 参考画像を再現する指示のときほど陥りやすい。くり返し構造は`AutoLayout`のゾーン分解（または`Gallery`）で組み立てているか（[該当ルール](#参考画像スクリーンショットデザインカンプを再現するときもまずautoLayoutのゾーンに分解する)参照）
- [ ] ヘッダー行などの右寄せ要素（通知アイコン・ユーザー名など）の位置を、画面幅から逆算した固定`X`で決め打ちしていないか。`AutoLayout`の水平コンテナ＋`FillPortions: =1`のスペーサー（または`LayoutJustifyContent.SpaceBetween`）で右端に押し出しているか
- [ ] `ModernTextInput`で見た目のヒント文字列を表示したいのに、`AccessibleLabel`だけを設定して`Placeholder`を設定し忘れていないか（`AccessibleLabel`は画面に表示されない）
- [ ] `ModernDropdown`/`ModernCombobox`の`Default`が、`Items`の1行と同じ形の**レコード**になっているか（`Default: ="すべて"`のような文字列だけになっていないか）
- [ ] 一覧の見出し行とデータ行（`Gallery`のテンプレート）の列幅を、**同じ方式（同じ`FillPortions`比率、または同じ計算式の`X`/`Width`）**で定義しているか（片方が`FillPortions`、もう片方が独自の%計算のような混在は列がずれる原因になる）
- [ ] 親の`Width`が計算式（画面幅に応じて変わる値）のとき、子要素の`Width`も決め打ちの固定pxではなく、その計算式を基準にしているか（[該当ルール](#親のwidthが可変計算式なのに子要素のwidthを決め打ちの固定pxにしない)参照）
- [ ] 固定`Width`の列を複数横に並べる場合、合計＋パディングが実際の画面幅を超えず、`Badge`等の余った分をスペーサーで埋めて見出し行の列幅と一致させているか
- [ ] コンテナの`Height`/`Width`を、丸い数字の決め打ちではなく、**中身の合計サイズ＋パディング＋`LayoutGap`を実際に計算してから**決めているか（[「最優先で確認すること: サイズは決め打ちしない」](#最優先で確認すること-サイズは決め打ちせず必ず計算する)参照）
- [ ] `AutoLayout` 配下で不要な `X`/`Y` を無理に指定していないか
- [ ] `Properties` 階層に正しく記載されているか
- [ ] `Children` 階層が正しいか
- [ ] `Badge` の `ThemeColor`/`Appearance` が第9章の実在値と一致しているか
- [ ] `Icon` の値が第9章の対応表・[FluentIcon Reference](https://github.com/thepowerappsguy/power-apps-fluenticon-reference)で確認済みか（実機やプレビューで円アイコンになっていないか）
- [ ] コントロール名が第6章のプレフィックス（`ddl`/`dtp`/`sel`/`tab`/`ico`/`cmp` を含む）に沿っているか
- [ ] 無限スクロールが必要な一覧画面で、読み込み継続用プロパティを `describe_control` で確認したか
- [ ] `ModernText` の `Height` が `Size` に対して十分か（第9章の表、または `Height ≥ Size × 1.5 + 10`）。テキストにスクロールバーが出ていないか。**`ModernText`を追加・変更したら`compile_canvas`の前に、Height<Size*1.5+10を機械的に検出するチェック（可能ならスクリプト化）を行い、全画面で違反がないか確認する**（このルールは編集キャンバスでは症状が出ずPlayモードでしか気づけないため、目視確認だけに頼らない）
- [ ] 水平・垂直コンテナ内の**すべての**子要素に `FillPortions: =0` が明示で書かれているか（例外がある場合は理由をコメントしているか）。**固定サイズにしたい要素だからと`FillPortions`自体を省略していないか**を1つずつ確認する。`Width`/`Height` を明示計算していても `FillPortions` が `0` 以外（省略も含む）だとその式が無視され、兄弟要素とスペースを分け合って想定外の比率に引き伸ばされるため、明示`Width`があるからと`FillPortions`の確認を省略しない
- [ ] `AlignInContainer` がすべての子要素に明示的に指定されているか（省略していないか、`Stretch`になっていないか）
- [ ] コンテナのサイズと子要素群の合計サイズが、**縦（Height）・横（Width）の両方とも**合っており、意図しない隙間ができていないか
- [ ] 同じ画面内で縦に並ぶセクション（ヘッダー行・カード行・一覧など）の外側の幅が、他のセクションと揃っているか（1つの行だけ直して終わらせていないか）
- [ ] 2カラム以上を横に並べる画面（詳細＋コメント欄など）で、各カラムに固定 `Width`（ピクセル値）を指定していないか。固定値の場合は `FillPortions` + `LayoutMinWidth` に置き換え、画面が広いときに右側へ空白が残らないようにしているか（[具体例](#具体例-2カラム以上のレイアウトで幅の狭い画面ではみ出さず広い画面でも右に隙間を残さない)参照）。カラムを可変化したら、カラム内部の子要素の固定`Width`も追従して可変化しているか
- [ ] `DropShadow` を持つ要素の親コンテナに、子要素より一回り大きいサイズと `LayoutAlignItems.Center` が設定されているか（影の見切れがないか）
- [ ] `Fill` を持たないレイアウト専用のラッパーコンテナに、視覚効果（`DropShadow`・`BorderStyle`など）が付いていないか
- [ ] すべての `GroupContainer` で `DropShadow` が明示されているか（省略していないか）。値に `DropShadow.Light` を使っていないか（既知の同期バグで消えるため `DropShadow.Semilight` を使う）
- [ ] `DropShadow` を追加・変更した画面は、`compile_canvas` の成功だけで判断せず `sync_canvas` でサーバー側に実際に反映されているか確認したか
- [ ] `ModernButton`に影を付けたい場合、`DropShadow`をボタンへ直接書いていないか（存在しないプロパティ）。[「ボタンに影を付ける（シャドウラッパー）」](#ボタンに影を付けるシャドウラッパー)の`ManualLayout`ラッパー方式になっているか。ボタンに`Visible`があった場合、ラッパー側に移してあるか（移し忘れると非表示時に影の箱だけ残る）
- [ ] 一度に多数のプロパティを変更した（数十箇所規模）画面では、`sync_canvas` で実際の反映状況を確認したか。反映されていない場合は「別の値に変更→反映確認→本来の値に戻す」の2〜3段階を試したか（詳細は[プロパティが部分的にしか反映されないことがある](#重要既知の同期バグ-プロパティが部分的にしか反映されないことがある)）
- [ ] `AlignInContainer` を一括で追加するスクリプトを使った場合、対象コントロールの親が `Variant: ManualLayout` になっていないか確認したか（`ManualLayout`配下の子には`AlignInContainer`は適用されない）
- [ ] コンテナに最低4pxのパディングがあり、子要素の `Height`/`Width` がパディング（・`LayoutGap`）分を差し引いた値になっているか
- [ ] 子要素の `Width`/`Height` に `=Parent.Width`/`=Parent.Height` をパディング未考慮のまま書いていないか（[該当ルール](#子要素に-width-parentwidth--height-parentheight-をそのまま書かない実際に発生したはみ出しバグ)参照。1箇所見つけたら画面全体・他の画面も横断的に検索する）
- [ ] `Gallery` の `TemplatePadding` が `=0` で明示され、行間は `TemplateSize` と行テンプレートの `Height` の差分で作られているか（`Gallery.Height` に行数分の余裕(+10px程度)があるか）。**画面内に複数`Gallery`がある場合、1つ直して満足せず、同じ画面・他の画面の`Gallery`も全部確認する**（1箇所だけ直して他を放置したことが実際にあった）
- [ ] 兄弟要素の高さを「`Parent.Height - 合計`」で計算するとき、`Parent`自身の`PaddingTop`/`PaddingBottom`（横方向なら`PaddingLeft`/`PaddingRight`）を引き忘れていないか（詳細は[パディングとサイズの計算](#パディングとサイズの計算)の「よくある計算ミス」）
- [ ] 画面の一部だけを固定してスクロールさせたいとき、`LayoutOverflowY: =Scroll` を画面全体ではなく中央のスクロール専用ラッパーだけに付けているか（詳細は[固定ヘッダー・固定フッター + 中央だけスクロールする構成](#固定ヘッダー固定フッター--中央だけスクロールする構成)）
- [ ] `ModernDropdown` を複数並べる（検索・絞り込みパネルなど）とき、各ドロップダウンに何を選ぶためのものか分かるラベル（`ModernText`）を添えているか（`ModernDropdown`に`Placeholder`は無い）
- [ ] `ModernDropdown`/`ModernCombobox`の「未選択」判定を、`OnChange`で更新する明示的な`loc`変数で行っているか（コントロール自身の`Selected`/`SelectedItems`を直接判定に使っていないか）
- [ ] `ModernTabList` に `Alignment`/`Appearance`/`TabSize` を明示しているか（省略するとタブが小さな点にしか見えないことがある）
- [ ] `ItemDisplayText` が `=ThisItem.列名` の形式になっているか（`="列名"` という文字列になっていないか。全項目が空欄で表示される既知の原因）
- [ ] 不明なPropertyを推測で作っていないか。特に**似た兄弟コントロール同士でProperty名を取り違えていないか**確認する（`ModernText`の色は`Color`、`ModernDropdown`の初期値は`Default`、`ModernTextInput`のヒント文字列は`Placeholder`、が正しいプロパティ名。実際にAIがこれらを別の名前と取り違えてエラーになった実例がある）
- [ ] 保存処理・更新処理・削除処理を意図せず書いていないか（会議用モックの場合）
- [ ] 画面名・コントロール名が命名規則（第1部6章）に沿っているか
- [ ] ステータス色が本書のパレット（第1部2章）と一致しているか
- [ ] `compile_canvas` でエラーが出ていないか
- [ ] PCの横長表示で崩れず、主要操作が上部で完結しているか
