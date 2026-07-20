# Power Apps Canvas App YAML生成 - 必須ルール（Copilot Studio 指示文用）

このアプリ（Canvas App）のYAML（.pa.yaml形式）を生成・編集するときは、以下を**必ず**守ること。
違反してもコンパイルエラーにならない項目が多く、生成後の見た目の崩れとしてしか気づけないため、
1つコントロールを書くたびに下記のリストと照合してから次に進むこと。

## 1. コントロールは必ずModern系を使う（実装フェーズの画面）

以下の対応を厳守する。右側のコントロールは**「会議用モック」専用の例外**であり、実装フェーズの画面には**絶対に使わない**。コンパイルは通ってしまうため、自分で気づいて避ける必要がある。

| 用途 | 必ず使う | 絶対に使わない（モック専用） |
|---|---|---|
| テキスト表示 | `ModernText@1.0.0` | `Label`, `Text@0.0.51`（DataCard専用） |
| テキスト入力 | `ModernTextInput@1.1.0` | `TextInput`, `Classic/TextInput` |
| ドロップダウン | `ModernDropdown@1.0.2` | `Classic/DropDown` |
| 選択肢（検索可・複数） | `ModernCombobox` | `ComboBox`, `Classic/ComboBox` |
| 日付入力 | `ModernDatePicker@1.0.1` | `DatePicker`, `Classic/DatePicker` |
| 選択肢（少数） | `ModernRadio` | `CheckBox`, `Classic/Radio` |
| ボタン | `ModernButton@1.0.0` | `Classic/Button` |
| アイコン | `ModernIcon@1.1.1` | `Classic/Icon`（Icon値が列挙型必須の場面のみ例外） |
| ステータス表示 | `Badge` | 色付き`Rectangle`の自作 |

## 2. Control@Versionは1つも省略しない

`GroupContainer@1.5.0`、`ModernText@1.0.0`、`Badge@1.0.0` のように、**すべてのControlに必ずバージョン番号を付ける。** `Badge`のようにバージョンだけ書き忘れるケースが多いので、書き終えたYAML全体を見直して、バージョンが無いControl行が無いか最後に確認する。

## 3. `ModernText`と`Text@0.0.51`を混同しない

画面上の通常のテキストは`ModernText@1.0.0`。プロパティは`Size`/`Color`/`FontWeight`。
`Text@0.0.51`はDataCard専用で、プロパティ体系が別（`Weight`など）。`Color`は存在しない。
画面に直接置くテキストで`Weight`や`Color`無しの`FontWeight`不明エラーが出たら、この混同を疑う。

## 4. `FillPortions`は省略しない（`=0`でも明示で書く）

`AutoLayout`コンテナの直下に置くすべての子要素に`FillPortions`を明示で書く。

- 固定サイズにしたい要素 → `FillPortions: =0`
- 伸縮させたい要素 → `FillPortions: =1`（比率が必要なら`2`,`3`など）

**省略は`=0`と同じ意味にならない。** 省略した要素は兄弟要素とスペースを取り合い、明示した`Height`/`Width`が無視されてはみ出す・高さがずれる。子要素を1つ書くたびに`FillPortions`があるか確認する。

## 5. `ModernTextInput`に`HintText`は存在しない

見た目のヒント文字列は`Placeholder`。`AccessibleLabel`は画面に表示されない（スクリーンリーダー専用）。`HintText`という名前のプロパティ自体が存在しない。

## 6. 子要素が無いコンテナに`Children: []`と書かない

空のフロースタイル配列（`Children: []`）は構文エラーになる。子要素が無いコンテナ（スペーサー等）は`Children`キー自体を省略する。

## 7. `ManualLayout`は既定にしない。`AutoLayout`を既定にする

`ManualLayout`＋絶対`X`/`Y`は、要素を意図的に重ねる場合など限定的な例外のみ。ヘッダー・サイドナビ・カードの並び・テーブルの行のような繰り返し構造は、`AutoLayout`のゾーン分解（`LayoutDirection`/`LayoutGap`）か`Gallery`で組み立てる。右寄せ要素（通知アイコン・ユーザー名など）も、画面幅から逆算した固定`X`にせず、`FillPortions: =1`のスペーサーで押し出す。

## 8. `ModernText`の`Height`は`Size × 1.5 + 10`以上にする

小さすぎる`Height`は、コンパイルは通るが再生モードでのみテキストにスクロールバーが出る（編集画面では気づけない）。数値を決め打ちする前に必ず計算する。

| Size | 最小Height |
|---|---|
| 12 | 28 |
| 14 | 31 |
| 18 | 37 |
| 20 | 40 |
| 24 | 46 |
| 26 | 49 |

## 9. `ItemDisplayText`は`ThisItem`経由の式にする

`ItemDisplayText: =ThisItem.Value`のように書く。`="Value"`のような文字列そのものを書くと、コンパイルは通るが実行時に一覧の全項目が空欄になる。

## 10. アイコンの色は`ModernIcon`だけ`IconColor`

`ModernIcon`の色は`Color`ではなく`IconColor`。`ModernText`は`Color`、`Badge`は`FontColor`。コントロールごとに色プロパティ名が違うので、`Color`だと思い込まず使う前に確認する。

## 11. 列挙型（Enum）の完全修飾名を規則性から類推しない

`Appearance`のような同じプロパティ名でも、コントロールごとに列挙型名の書き方が違う。

- `Badge`の`Appearance` → `='BadgeCanvas.Appearance'.Tint`
- `ModernButton`の`Appearance` → `=ButtonAppearance.Primary`
- `ModernDropdown`の`Appearance` → `=Appearance.Outline`（プレフィックス無し）

`'ModernControlsCommon.Appearance'`のような、他コントロールの命名から類推した型名を作らない。値の候補（`Outline`など）が同じでも型名は個別に違う。

## 12. コンテナの`Height`は中身の合計を計算してから決める

ラベル(Height28)+入力欄(Height40)+LayoutGap(2)を縦に並べるなら、コンテナの`Height`は最低70必要。`Height:56`のように丸めた数字を先に決めて中身の合計を確認しないと、内部要素がコンテナからはみ出す（コンパイルは通る）。フィルタ欄のように「ラベル＋入力欄」を1セットにした小さいコンテナを複数並べるときは特に、全セットで同じ計算ミスをしていないか確認する。

## 13. `ModernButton`に`Fill`は存在しない

ボタンの背景色は`Fill`ではなく`Appearance`（`Primary`/`Secondary`/`Subtle`など）または`BasePaletteColor`で調整する。`GroupContainer`の背景色プロパティ（`Fill`）と混同しない。

## 14. `ModernIcon`の`Icon`は列挙型ではなく文字列（Text型）

`Icon: =Icon.BulletedList`のような列挙型ドット記法は型不一致でエラーになる。必ず`Icon: ="List"`のように文字列で書く。`Classic/Icon`は列挙型だが`ModernIcon`は違う。

## 15. `FillPortions`が`0`以外の要素に、意味のない`Width`/`Height`の数字を書かない

`FillPortions`が`0`以外の要素は`Width`/`Height`を指定しても無視される。「とりあえず`100`と書く」のような意味の無い値を埋めない。書くなら親の計算式に基づく値にするか、そもそも書かない。

## 16. 可変幅の親コンテナの中の子要素に、固定`Width`を決め打ちしない

`FillPortions`で幅が可変になっている親コンテナ（カードなど）の中に入れる子要素（ラベルなど）は、`Width: =120`のような固定pxにしない。親が狭くなったときに子要素がはみ出す。`Width: =Parent.Width`（親にPaddingがあれば`Parent.Width - Padding分`）のように、親を基準にした式にする。

## 17. `Gallery`に`Layout`というプロパティは存在しない

表示方向（横並び/縦並び）は`Variant`名に既に含まれている（`BrowseLayout_Horizontal_...`＝横並び、`BrowseLayout_Vertical_...`＝縦並び）。`Layout: =Layout.Horizontal`のような追加のプロパティを書かない。方向を変えたいときは`Variant`名自体を変える。

## 18. `ModernDropdown`に`DefaultSelectedItems`は存在しない

`DefaultSelectedItems`は`ModernCombobox`（複数選択）専用。`ModernDropdown`（単一選択）の初期値は`Default`に`Items`と同じ形の**単一レコード**を指定する（`Table`ではない）。

```yaml
# ❌ ModernComboboxのプロパティ
DefaultSelectedItems: =Table({Value:"すべて"})

# ✅ ModernDropdownはDefaultに単一レコード
Default: |-
  ={ Value: "すべて" }
```

---

書き終えたら、上記18項目を1つずつ見直してから提出すること。
