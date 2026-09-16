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

## 最新の画像レイヤー検証・公開状態（2026-09-16）

- 実装コミット: `fcec5fb12d4ae53c191dd0ee55e88a5e26577887`
- GitHub上の登録PNG: 10枚
- Luna 1〜16小節: 144ノーツ / 124同時刻グループの全件が9人物フレームへ解決済み
- Character asset validation: success
- Repository validate: success
- Standalone build: success
- GitHub Pages deploy: success
- GitHub Pages URL: https://mleuatd.github.io/dtx-drum-flow/
- 公開ページ実ブラウザ確認: `drum_base.png` と `neutral.png` はともに1448x1086で読込完了、`assets-missing` なし

人物の各ヒット差分はGitHub登録・実行可能な `COMMITTED_DRAFT`。個別の目視承認が済むまでは `APPROVED` に昇格しない。HHの `prep_r` / `rebound_r` / `prep_l` / `hit_l` / `rebound_l` は現在のGitHub `main` には未登録で、将来16分HHや三相アニメーションを実表示する前に必要。

## 最初の4小節・背景レーン表示修正（2026-09-16）

発見した直接原因は、`site/app.js` の `draw()` がCanvas全体を不透明な `#0e172a` で毎フレーム塗りつぶしていたこと。人物・ドラムDOMはCanvasより下の正しいレイヤーに存在していたが、この不透明塗りで完全に隠れていた。

修正方針:
- Luna表示中のCanvas背景を半透明にして、ノーツとレーン線を人物・固定ドラムの上へ重ねる
- `styles.css`、`app.js`、`character-prototype.js` を同じ更新番号でcache bustする
- `asset_inventory.json` の `runtimeScope` を1〜4小節に固定する
- 1〜4小節の28ノーツ / 27グループだけを実行対象にする
- 使用画像をすべてpreloadできた後だけ `character-ready` にする
- DOM datasetへready/active/frame/pose/scopeを出し、公開ページ検証を可能にする

1〜4小節で必要なキーは `SN:L`、`BD:RF`、`HH:R`、`BD+RC:*` の4種類。5〜16小節のデータとPNGは削除せず、次段階用として保持する。

公開検証完了コミット: `3d36aa5d148eebdbdb5fe4afc719c3c52115f543`

公開ページ `https://mleuatd.github.io/dtx-drum-flow/` で以下を実ブラウザ確認済み。
- 初期状態で `character-ready active`、scope=`1-4`、opacity=`0.9`
- 固定ドラムとneutral人物が1448x1086で読込完了
- Canvas自体はtransparentで、Luna用描画塗りだけ半透明
- 5.0秒へ移動すると `SN · L` / `layers/character/sn/hit_l.png` に切替
- 15.0秒へ移動すると4小節範囲外として背景を非表示
- `assets-missing=false`
- Character asset validation / validate / standalone build / Pages deploy はすべてsuccess

## 最初の4小節・パラパラ漫画モーション改善（2026-09-16）

- `site/character-prototype.js` は最寄りの発音時刻に対して `prep -> hit -> rebound` の3位相を選ぶ。
- 最初の4小節で使用する `SN:L`、`BD:RF`、`HH:R`、`BD+RC:*` はすべて3位相へ解決する。
- SN左手の専用戻り差分 `character-assets/layers/character/sn/rebound_l.png` を追加。1448x1086、実alphaあり、SHA-256は `18103689d4f466f082b98b2fa1595e00fd9a2a657e09e77e037e2d1a8a1071f5`。
- HH / BD / BD+RC の戻り差分候補は合計6枚生成したが、市松模様が画像へ焼き込まれたRGBだったためGit登録せず不採用。現段階では安全なneutral戻りを使う。
- 固定ドラム、人物とは別にSVGの発音エフェクトレイヤーを追加。HH / SN / BD / RC / RDの固定座標へ短いコミック風バーストを表示し、BD+RCは2点同時表示する。
- `drum_base.png` のバイト列とSHAは変更していない。
- `assets_manifest.json` と `asset_inventory.json` を更新し、CIは最初の4小節の全キーに prep/hit/rebound が存在すること、SNのhit/reboundが別フレームであることを検査する。
- 次の改善候補は、実alphaを安定して出せる手段でHH / BD / BD+RC専用reboundを追加すること。現在の4小節完成にはneutral戻りでフォールバック可能。

実装・公開コミット: `b96726f8cd4ab0b27b79b2ed06f8f4a330c6b0aa`

公開ページ実ブラウザQA:
- `character-ready active`、scope=`1-4`、固定ドラム/人物とも1448x1086
- 4.716秒: `SN · L · HIT` / `sn/hit_l.png` / SNエフェクト発火
- 4.770秒: `SN · L · REBOUND` / `sn/rebound_l.png` / エフェクト消去
- 5.146秒: `BD+RC · RF/R · HIT` / `combo/bd_rc_hit.png` / BD座標とRC座標の2バースト発火
- GitHub上のrebound PNGは実alphaあり、SHA-256がmanifestと一致
- GitHub Actions 4件（validate / Character asset validation / Build standalone trainer / deploy-site）はすべてsuccess
- 公開URL: https://mleuatd.github.io/dtx-drum-flow/

バイナリ登録が権限・API制約で失敗した場合は、失敗内容と必要なユーザー操作を `WORK_SYNC.md` または `VARIANT_STATUS.md` に記録してから案内する。

## 5〜8小節の人物アニメーション拡張（2026-09-16）

- 有効範囲を1〜8小節へ拡張。合計61ノーツ / 59発音グループ。
- 5〜8小節単体は33ノーツ / 32グループで、`RD:R`、`SN:L`、`BD:RF`、`BD+RC:*` を使用する。
- RD右手ヒット画像 `layers/character/rd/hit_r.png` は登録済みだったため、新規PNG生成は不要。
- 非連打は発音後0.075秒で必ず承認済みneutralへ戻る。
- 同じキーの次発音まで0.13秒以下の場合だけ16分相当の連打として、neutralへ戻さずreboundを維持する。
- 5〜8小節の全32グループについて、HIT画像32件、0.09秒後のneutral復帰32件、各パートのエフェクト、BD+RC二点エフェクトをJavaScript実行テスト済み。
- 既存の固定ドラム画像およびSHAは変更していない。

実装・公開コミット: `26adb1eabf70c14623a0a12ef4908f349af9eced`

公開ページ実ブラウザQA:
- scope=`1-8`、固定ドラム/人物とも1448x1086、`character-ready active`
- 10.542秒: `RD · R · HIT` / `rd/hit_r.png` / RDエフェクト
- 10.632秒: `NEUTRAL` / `base/neutral.png` / エフェクト消去
- 12.052秒: `BD+RC · RF/R · HIT` / `combo/bd_rc_hit.png` / BD・RC二点エフェクト
- 公開サイト由来のJavaScriptエラーなし
- GitHub Actions 4件（validate / Character asset validation / Build standalone trainer / deploy-site）はすべてsuccess
- 公開URL: https://mleuatd.github.io/dtx-drum-flow/

## 9〜16小節の人物アニメーション拡張（2026-09-16）

- Work上限到達後、通常チャットへ引き継いで作業継続。
- 有効範囲を1〜16小節へ拡張。合計144ノーツ / 124発音グループ。
- 9〜16小節で追加使用する `BD+SN:*` と `RC+SN:*` は既存登録済みPNGを使用し、新規画像生成は不要。
- `BD+SN:*` と `RC+SN:*` に prep / hit / rebound を追加し、hit後はneutralへ復帰。
- 既存の0.075秒neutral復帰、および同一キー0.13秒以下の連打時rebound維持ロジックを継続適用。
- 全124グループについて runtimeFrameMap / runtimePhaseFrameMap / requiredFrames の解決を機械検証し、未解決0件。
- 固定ドラム画像および既存PNGのSHAは変更していない。

実装コミット:
- `bee716b24d78c75c79a3e36cb1b8a2787f7c79a8` 16小節runtime scope / combo phase map
- `ddb2ac74b41c5d095cffcaf16044c838179b9fae` browser runtime 16小節化
- `540f8b5de2f365ac324d10be0addf4e0114a0c22` character module cache refresh
- `73ef11536aba28d65333fcf3ea65d24d2ee62a01` public HTML cache key更新
- `4caf11deabd1e6d23f04af6e2bedec9549b54221` UI contractを16小節へ更新
- `d18dc283643295744c06f3c8f96a4ccdf3844229` prototype README更新

次回の通常チャット/Work開始時は、このファイルとGitHub `main` の最新コミットを必ず確認してから続行する。
## 17〜148小節・全曲人物アニメーション拡張（2026-09-16）

- ユーザー指示により16小節以降を中断せず継続し、Luna Say Maybe FINAL譜面の全148小節をruntime対象へ拡張。
- 全曲規模: 2,158ノーツ / 1,527発音グループ / 最終ノーツ258.851273秒。
- browser character runtimeは16小節専用animation JSONではなく `site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json` を直接読む。
- SN=L、BD=RF、その他の既存手パート=Rをruntime既定として解決。
- 全23種類の出現グループキーをframe/phaseへ解決し、機械検証で1,527/1,527グループ未解決0件。
- 既存PNGで専用表現できない後半パターンは、安全な既存ポーズへフォールバックしつつ、発音位置エフェクトは実パート位置へ出す。
- HT/LT/FTのエフェクト座標を追加。3パート同時打ち用にeffectTertiaryを追加。
- 現時点で575グループが人物ポーズfallback。うち100グループのタム単独はneutral人物 + 正しいタム位置エフェクト。
- 固定ドラムPNGと既存人物PNGのバイナリ/SHAは変更していない。
- 専用タム画像・後半combo画像・HH左手画像は `character-assets/VARIANT_STATUS.md` に未完了として残し、runtime自体は止めない。

主な実装コミット:
- `4b5876175827e7657810c16db40a9656a9d4870a` full-song frame fallback定義
- `cf44d7fbfd5765766da46d608e6a3032a3fd31e8` FINAL譜面直結runtime
- `c66af0b4b322f1fc45b704ae2c384b047230af10` 3点同時hit effect
- `067b09f579f08003529248766cb442ccca3794df` full-song cache refresh
- `955608a888c1e82e34626d1da359eca1d6611059` full-chart asset validation
- `95b845643f063739e7d43fbc32b2c153fede847c` full-song UI contract
- `ea71e8872b61043e9e9fc8bc304d226236d44425` changelog更新
- `4b2b93d04dafbc5208dbf26792a5afffa4124107` project milestone更新
- `dacbc9aa0a52c21c04088c881e77bf10b67bccef` fallback/TODO状態更新
- `4fbadc7ae9db8fe3c9477f0fcdbabae73e60cd43` prototypeから全曲への継続方針記録

次回はGitHub mainの最新状態から、fallbackになっている後半専用人物PNGを優先度順に置換していく。
### 全曲runtime QA追記

- `runtimeFallbackKeys` を明示し、現在の発音グループが専用ポーズかfallbackかを `characterBackdrop.dataset.fallback` / `dataset.animationKey` で判別可能にした。
- fallback宣言キーは15種類、実際のfallbackグループは575件。
- 最新機械検証でも全1,527グループ unresolved=0。
- 3点同時打ちeffect、全曲cache bust、fallback key validator、UI contractもmainへ反映済み。

追加コミット:
- `8e9b8f37e59d6fb4d793ec8b50047ae88294243f` fallback key metadata
- `3b2694ac28cee1655022533796ca014f7f9b9361` runtime fallback QA dataset
- `fa6105286158a0e0c6c0bc0be83d6de5dd952f0b` app cache refresh
- `1757caa2f5ff7ffb7938e93653817ffe6212ac6b` HTML cache refresh
- `fb64f49d7d993a70985fa67416e699aacdd7b787` fallback QA UI contract
- `136514ee04c6750e8fa1ef954eec607a098a1739` fallback key validator

