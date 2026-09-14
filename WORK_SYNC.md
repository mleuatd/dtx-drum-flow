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

## 復元について
ChatGPT Site projection の元ソースを通常チャットから直接エクスポートできなかったため、`site/` は現行UI・既知仕様を基に再構築した同期用ソースです。
現行サイトとの差異を発見した場合は、差分をGitHub側に反映して徐々に一致させます。
