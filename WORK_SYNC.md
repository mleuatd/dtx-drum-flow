# Work / Normal Chat 同期ルール

このリポジトリを DTX Drum Flow の共通ソース・履歴管理先として扱います。

## 基準
- Repository: `mleuatd/dtx-drum-flow`
- Stable branch: `main`
- Live URL: https://dtx-drum-flow.mleuatd.chatgpt.site
- ChatGPT Site project ID: `appgprj_6aa76fd7a1e48191b27d3b4793a85e70`

## 作業時
1. 作業開始前に GitHub の `main` を確認する。
2. Work または通常チャットで変更したコードは GitHub に反映する。
3. 目に見える仕様変更は `CHANGELOG.md` に記録する。
4. 公開サイトのURLは変更しない。
5. Site側へ反映できる環境では、このリポジトリの `site/` を基準に反映する。
6. Site側だけに変更が入った場合は、可能な限り同じ変更を GitHub の `site/` に戻して履歴を一致させる。
7. キャラクター画像差分は `character-assets/` を唯一の管理元として扱う。
8. キャラクター差分を作る前に `character-assets/VARIANT_STATUS.md` と `character-assets/LAYER_RULES.md` を確認する。
9. ドラムは固定レイヤーとして扱い、各ポーズで再生成・位置移動しない。
10. 人物差分は同一1448x1086キャンバス・x=0,y=0で管理する。
11. 16分連打・同時発音などの画像選択規則は `character-assets/config/animation_rules.json` を基準にする。

## 復元について
ChatGPT Site projection の元ソースを通常チャットから直接エクスポートできなかったため、`site/` は現行UI・既知仕様を基に再構築した同期用ソースです。
現行サイトとの差異を発見した場合は、差分をGitHub側に反映して徐々に一致させます。


## 必須の作業開始ルール（2026-09-16追加）

このプロジェクトは通常チャット・Work・別チャットをまたいで継続するため、作業開始時に会話履歴だけを信用しない。

毎回、実装・画像生成・差分追加・Git操作の前に、最低限以下を確認すること。

1. `WORK_SYNC.md`
2. `PROJECT_MANIFEST.md`
3. `CHANGELOG.md`
4. `character-assets/VARIANT_STATUS.md`
5. `character-assets/LAYER_RULES.md`
6. Luna Say Maybe 16小節プロトタイプ作業なら
   `character-assets/prototypes/luna_say_maybe_16m/README.md`
   と
   `character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json`

GitHub の `main` を共有情報の正本（source of truth）とする。

チャット内の説明とGitHub上の情報が食い違う場合は、GitHubの最新mainを確認してから判断する。ただし、ユーザーが現在の会話で明示した最新指示は最優先で、その変更内容をGitHub側の管理ファイルへ反映する。

重要な決定・進捗・未完了事項・画像パス・バイナリ登録状況・詰まっている理由は、会話だけに残さずGitHubへ記録する。

特に画像差分作業では、
- どの画像が基準か
- どの画像が承認済みか
- どのPNGがGitHubへバイナリ登録済みか
- どの差分が生成済み / 未生成か
- どの譜面ノーツに対応するか
を `VARIANT_STATUS.md` と prototype 配下の inventory / manifest に記録する。

新しいチャットへ移った場合でも、まずこれらのファイルを読むことで作業状態を復元し、ユーザーに同じ説明や再確認を繰り返さないこと。

GitHubへのバイナリ登録が必要な場合は、テキスト用 `create_file/update_file` ではなく、原則として
`create_blob(base64) -> create_tree -> create_commit -> update_ref`
のGit data API方式を試す。

## GitHubバイナリ登録の確認済み手順（2026-09-16）

GitHub connector で次の手順が成功済み。LISSAによるGitHub画面操作は不要。

1. ローカルPNGをbase64化する。
2. `create_blob` を `encoding=base64` で呼び、各blob SHAを得る。
3. `main` の最新commitとbase tree SHAを取得する。
4. `create_tree` で `mode=100644`、`type=blob`、対象パスとblob SHAを追加する。
5. `create_commit` で最新commitを親にする。
6. `update_ref` を `branch_name=main`、`force=false` で呼ぶ。
7. GitHubのtree/contents APIでファイルの存在、サイズ、blob SHAを再確認する。

初回成功コミットは `db3fdcd0b2038b5bb78f59d805472102fc621881`。現在は固定ドラム、neutral、Luna 1〜16小節で必要な人物差分の合計10 PNGが `main` に存在する。

画像のバイト同一性は `character-assets/config/assets_manifest.json` のSHA-256を正本とし、`tools/character_layers/validate_assets.py` とCIで検査する。`drum_base.png` は `lockedDrumSha256` と一致しない変更を失敗させる。

バイナリ登録が権限・API制約で失敗した場合は、失敗内容と必要なユーザー操作を `WORK_SYNC.md` または `VARIANT_STATUS.md` に記録してから案内する。
