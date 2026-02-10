# テスト要件

## 留意

vscode は `$$...$$` だけでなく `\begin{...}...\end{...}` を数式だと認識するが、
このパーサーは dollers 形式 `$$...$$` を唯一数式だと認識する。

インラインの数式は `$...$` を唯一数式だと認識する

正規表現で書くと次の通り

- inline: `\$(\S[^$]*?[^\s\\]{1}?)\$`
  - 始端の `$` の右側、終端の `$` の左側に `\s` があってはならない。(vscode はあってもいい)
- block: `\${2}([^$]*?)\${2}`

数式ブロックのなかで ALIGNER environment が存在する場合、環境内のパースのみ行う。
例えば次のコードは vscode 上では ALIGNER の外側のタグのみを表示するが、
このパーサーは ALIGNER の内側のタグのみを認識し、並べる。

```markdown
$$
\begin{align}
a &= b \tag{1} \\
c &= d \tag{2}
\end{align} \tag{1}
$$
```

## TagRenumberer.\_search_math_block

```python
TagRenumberer._search_math_block(tokens: list[Token]) -> list[str]
```

- テストケース
  - 箇条書きの中に数式があっても認識する
  - 表の中の数式があっても認識する
  - ソースコード内 (\`\`\`...\`\`\`) に数式があっても認識しない
- テスト項目
  - 検出されたトークンの数
  - 入力トークンと出力文字列の関係
  - 検出されたトークンの位置がリストの中で昇順

## TagRenumberer.\_search_inline_block

```python
TagRenumberer._search_inline_block(tokens: list[Token]) -> list[str]
```

- テストケース
  - 箇条書きの中に数式があっても認識する
  - 表の中の数式があっても認識する
  - ソースコード内 (\`\`\`...\`\`\`) に数式があっても認識しない
- テスト項目
  - 検出されたトークンの数
  - 入力トークンと出力文字列の関係
  - 検出されたトークンの位置がリストの中で昇順

## TagRenumberer.\_ensure_sentinel_line_breaker_inplace

```python
TagRenumberer._ensure_sentinel_line_breaker_inplace(nodes: list[LatexNode]) -> None
```

- テストケース
  - `\\` の後に、次にあげるもの以外のTokenが現れない限り、sentinel line breaker を追加しない
    - 正規表現 `\s+` で表すことができるような LatexCharNode
    - LatexCommentNode
    - `\tag`, `\tag*`, `\notag`
  - ALIGNER の中に environment がある場合、environment の中の `\\` を無視するか
- テスト項目
  - sentinel line breaker が追加されているか否か
  - 追加されている場合、その位置

## TagRenumberer.\_find_replacements_in_aligner

```python
TagRenumberer._find_replacements_in_aligner(nodes: list[LatexNode]) -> list[Rewrite]
```

- テストケース
  - ライン上で `\tag` 単体の場合置き換える
  - ライン上で `\tag*` 単体の場合置き換えない
  - ライン上で `\notag` 単体の場合置き換えない
  - ライン上で `\tag`, `\tag*`, `\notag` が混在している場合
    - `\tag` や `\tag*` は `\notag` に優先する(vscode準拠)
    - `\tag` と `\tag*` が混在している場合、vscode ではエラーとなるため、テストケースに含めない。
  - `\tag{1}` の場合と `\tag 1` の場合どちらも置き換える
- テスト項目
  - Rewrite の数
  - Rewrite の順序が昇順か
  - Insertion か、Replacement か
  - Rewrite.start
  - Rewrite.length
  - Replacement.label_start
  - Replacement.label_length

## TagRenumberer.\_find_replacement_in_single_line

```python
TagRenumberer._find_replacement_in_single_line(nodes: list[LatexNode]) -> list[Rewrite]
```

- テストケース
  - ライン上で `\tag` 単体の場合置き換える
  - ライン上で `\tag*` 単体の場合置き換えない
  - ライン上で `\notag` 単体の場合置き換えない
  - ライン上で `\tag`, `\tag*`, `\notag` が混在している場合
    - `\tag` や `\tag*` は `\notag` に優先する(vscode準拠)
    - `\tag` と `\tag*` が混在している場合、vscode ではエラーとなるため、テストケースに含めない。
  - `\tag{1}` の場合と `\tag 1` の場合どちらも置き換える
- テスト項目
  - Rewrite の数
  - Insertion か、Replacement か
  - Rewrite.start
  - Rewrite.length
  - Replacement.label_start
  - Replacement.label_length

## TagRenumberer.renumber_tags

```python
TagRenumberer.renumber_tags(text: str) -> str
```

- テストケース
  - ALIGNER 環境がある場合、ALIGNER 環境内だけを考慮する
  - ALIGNER 環境でない場合、`\tag` は一つだけ
  - 同じラベルの `\tag` が文字列内に複数回出現したり、update_map に登録されているラベルが出現
    - `\ref` にそのラベルがなかったら問題ない
    - この関数内では**重複ラベル**として登録される。
- テスト項目
  - `\tag` が番号順
  - TagRenumberer.next_tag
  - TagRenumberer.update_map

## TagRenumberer.renumber_refs

```python
TagRenumberer.renumber_refs(text: str) -> str
```

- テストケース
  - `$(...)$` を認識
  - `$ (...) $` を認識しない
  - `$( 1)$` のように、ラベルの両端にスペースがある場合
    - ラベル両端の `\s` は削除され、ラベルは `1` となる
  - TagRenumberer.update_map に登録されていない
  - **重複ラベル**として登録されている
  - 同じラベルが複数
- テスト項目
  - TagRenumberer.update_map に沿った`\ref`
  - **重複ラベル**の出現で、異常終了。メッセージが正常に出力される
