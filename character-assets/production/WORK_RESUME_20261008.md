# 作業再開入口 — 2026-10-08

**現在: 全30動作のHit/Rebound60PNGを制作・静的目視QA済み。公開Webの最終全位相・再生検証は進行中。** 隠れて完全に見えない部分はユーザー指定により評価対象外。見える人体・境界・打点を確認。

- 19セット38位相は公開画面で新PNG、キー、位相、前景canvas、髪レイヤー同期を検証済み。
- 今回残り11セット22枚を反映: HT左右、LT左、FT左右、FT+SN右/左、BD+HT左右、BD+FT左右、BD+FT+SN。r8公開後に全60位相を再確認する。
- 固定ドラム/承認NeutralのSHAは不変。各画像は元人物の局所編集、体格・頭・服・近い脚を保護。旧失敗画像は正しいdonorとして採用しない。
- レイヤー: 固定ドラム、人物、原画由来のドラム前景、腕前景、元Neutral由来の髪前景。髪が近い箇所のスティックは髪の奥へ隠す。
- 413過去画像の成功/失敗/保留台帳は20261008/ledger/image_audit.json。個別拡大未完了は保留のまま、成功資料にしない。

## 保存場所と再開位置
正式PNG: character-assets/layers/character/ の各楽器とcombo。
実装: site/character-prototype.js / styles.css / index.html。
入力仕様: 20261008/sources/WORK_MASTER_SPEC.md。指定REVISED名は素材ZIPに存在せず、同梱仕様とユーザー指示を適用。
台帳: 20261008/ledger/motion_matrix.json。実体SHA: config/assets_manifest.json / prototypes/luna_say_maybe_16m/asset_inventory.json。
検証: 20261008/qa/browser_post_promote_bd_r7.json / remaining_tom_pairs_source_v1.json / 各腕QA。
局所donorと再現手順: 20261008/donors/ / scripts/。

**次の作業: r8公開を確認し、全30キー60位相の正しいPNG/前景/髪同期、再生と位置移動を検証し、結果JSONと目視証跡を保存。最終検証未実施を完了扱いしない。**

## 失敗と修正
BD逆向き靴不合格→後ろから見た踵を局所donor化、ペダルへ投影。BD白い矩形継ぎ目不合格→元のふくらはぎを変形して連続接続。HT:L下向きRebound不合格→回転符号修正。FT:R髪より上の切断袖の突起不合格→隠れる位置まで局所切り出しと移動。左袖の輪郭欠損不合格→元の黒い輪郭を含む範囲へ拡大。

過去の環境切断履歴: 20261008/ENVIRONMENT_STOP_CHECKPOINT.md。現環境は復旧済み。

## 最終環境切断とCIによる継続
60PNG制作コミット6bf7bf0bc067f9df4982ea117af9d316d60473a3はdeploy-site、validate、Character asset validation、Drum Runtime Browser QA、Runtime Character QAがSUCCESS。ただし当時Runtime Character QAの既存ターゲットはM113のHH+SN1キーのみであり、全60位相の証明ではない。
最終検証中にexec-server transport disconnectedでローカルとCUAが使用不能。GitHub APIは使用できるため、全30キー/小節1〜148、PC1280x900とXperia384x864、髪/腕canvas同期、実再生のCI検証を追加して継続。旧BRUSHUP_LEDGERの全60SHAを正式PNGに同期し、Visual Integrity Batch PrepのSHA不一致を修正。画像の見た目合格をCIで代替したとは扱わない。
再開時はqa/final_public_runtime.jsonと最新Runtime Character QA runを読む。PASSなら保存済みCI証跡を参照、FAILなら該当位相・レイヤー・再生を直す。手動最終全60位相は未実施、手動確認は19セット38位相まで。
