# 完了・再開入口 — DTX Drum Flow / 2026-10-08

**現行Lunaの全30動作・Hit/Rebound60PNGの制作と公開Web動作検証を完了しました。**

## 完了範囲
- 曲: Luna say maybe、小節1〜148、2,158ノーツ／1,527グループ。
- 全30セット60PNGを元の承認人物の局所編集で制作。頭・体格・服・髪を統一し、見える手足・関節・袖/手首の接続・打点・跳ね返りを確認。
- PC1280×900とXperia縦384×864、それぞれ全60位相がPASS（計120位相チェック）。腕前景canvasと元画像由来の髪前景の同期もPASS。
- PC/スマートフォンの通常速度1と半速0.5の実再生4ケースがPASS。時間が進み、9種類のフレームへ切替。計48サンプルすべて画像読み込み済み。最終実測142レコード、失敗0。
- 公開検証コミット: 1a7c373b04b0fd61ee094fb1e56832acc86da0c1
- 完了した公開検証: https://github.com/mleuatd/dtx-drum-flow/actions/runs/37764871537
- 静的検証と公開再生を区別して記録。公開での手動切替確認は19セット38位相、全30セットはGitHub Actionsの実ブラウザでPC/スマートフォン検証済み。

## 前後関係と固定条件
固定ドラム原画は変更なし。原画の必要な画素だけを複製したドラム前景、演奏する腕の前景、元Neutral由来の髪前景を使用。
髪が手前の場合、ドラム→スティック→髪の順に重なります。完全に隠れる部分はユーザー指定どおり評価・再構築せず、無理に露出させません。
原画SHA: dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85
承認NeutralSHA: 886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9

## 実体・証跡の場所
- 完成PNG: character-assets/layers/character/ のsn,hh,rc,rd,ht,lt,ft,bd,combo。
- 全位相・再生の実測JSON: [final_public_runtime.json](20261008/qa/final_public_runtime.json) のbrowserFrameEvidence。
- 完了時の独立した実測報告と画面: 20261008/qa/final_public_runtime_verified_frames.json / public_final_pc.png / public_final_mobile.png（証跡取得Actionsで保存）。
- 制作台帳: 20261008/ledger/motion_matrix.json。正式PNGのSHA: config/assets_manifest.json と prototypes/luna_say_maybe_16m/asset_inventory.json。
- 各腕・足の検証/失敗理由: 20261008/qa/。元画像からの局所素材: 20261008/donors/。再現手順: 20261008/scripts/。
- 413過去画像の成功・失敗・保留の分類: 20261008/ledger/image_audit.json。個別拡大未確認の保留は成功参照として使いません。
- 入力仕様: 20261008/sources/WORK_MASTER_SPEC.md。素材ZIP内には指定されたREVISED名がなく、同梱仕様とユーザー指示を適用しました。

## 修正した失敗
- BDの逆向き靴→後ろから見た踵の局所部品へ修正。ふくらはぎの矩形継ぎ目→元の輪郭を連続して変形。
- HT左の下向きRebound→回転方向を修正。左袖の輪郭切れ→元の黒い輪郭を含めて復元。
- FT右の切断袖の突起→元の髪に隠れる局所範囲へ修正。
- 再生時にPNG再読み込みで一瞬未表示→読み込み済みImageノードを保持して直接交換し、腕前景も同時描画。
- 全画像の同時Image.decodeによる不安定な初期化→4並列の先読みとcanvasによる画素描画確認へ変更。画像の欠損/描画エラーは引き続き不合格。
- 古いBRUSHUP台帳SHA不一致→正式60PNGのSHAへ同期。
- 公開サーバーがスネア1枚に一時的503→先読みに最大3回の再取得を追加。ドラム/Neutral/前景/髪も同じ読み込み済みノードの経路へ統一し、公開で再検証PASS。
- UI contractのPromise.allSettledという実装文字列への依存→独立したHit/Rebound実体と全フレーム先読みの契約を検査。

## 再開方法
完成PNGはすでにGitHubにあります。作り直し不要です。
修正する場合はこの入口とfinal_public_runtime.jsonを読み、対象の動作キーだけを編集・再検証します。
scratchが消えた場合は最新repoを取得し、production/20261008/scripts/restore_source_workspace.pyで元画像と候補用作業領域を復元。再現スクリプトはrepo内のscriptsから実行します。
ローカル/CUAは最終作業中に切断しましたが、GitHub APIとActionsで検証・保存を継続して完了しました。過去の切断記録はENVIRONMENT_STOP_CHECKPOINT.md。現在の未完了画像セットは0です。
