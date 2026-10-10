# dtx-drum-flow

ChatGPT Workと通常チャットで共同管理する **DTX Drum Flow** のソース・変更履歴・同期用リポジトリです。

## 現在の公開サイト
https://dtx-drum-flow.mleuatd.chatgpt.site

## 使い方
- `main`: 現在の基準となる安定版
- 変更はGitのコミット履歴で管理
- ユーザーに見える挙動変更は `CHANGELOG.md` に記録
- プロジェクト識別情報・同期ルールは `PROJECT_MANIFEST.md` を参照

## 最優先の改善項目
元音源とドラムノーツの同期精度改善。
ドラムstemだけを信用せず、元音源のトランジェント、BPM/拍グリッド、帯域別情報、局所パターン整合性を併用して打点時刻を補正する方針です。
