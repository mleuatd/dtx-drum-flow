# 作業再開入口 — 2026-10-08

**環境復旧後、作業を再開しました。** 過去の切断記録は ENVIRONMENT_STOP_CHECKPOINT.md。現在は髪の前後レイヤーr6を追加し、バスドラム右足を再制作中です。全体完了ではありません。

**全作業は未完了です。** 目標はLuna全30動作60枚を自然な人体・固定ドラムで完成し公開Webで検証することです。

## 現在の状態
- 30動作60位相の既存Web切替と画像読み込みを実測済み。描画成功と絵の合格は別です。
- 新しい静的QA合格は10ペア20枚: SN:L、SN:R、HH:R、HH+SN:R/L、RC:R、RC+SN:R/L、RD:R、RD+SN:R/L、LT:R、LT+SN:R/L。10ペア20位相すべて公開Webで画像読み込み・Hit/Rebound・腕前景フレーム同期を検証済み。追加証跡: qa/browser_post_promote_lt_r5.json。残り20ペア。新しい髪前景r6は公開目視検証待ち。
- 固定ドラムと承認NeutralのSHAは不変。髪・胴・脚・近い腕を保護し、必要な腕だけ局所編集。全身AI出力は完成画像として採用しない。
- 413過去画像の一覧と分類: 20261008/ledger/image_audit.json。個別拡大未完了の判定保留を成功donorとして使わない。
- RDの最初のAI生成は打点が高すぎて不合格。元Neutralの手とスティックを局所変形したv2を使用。HT:L試作は袖の白い切れと残像で不合格。
- ドラム原画の一部RGBAをそのまま複製した前景PNGと腕前景canvasで、髪/身体をタム・ライドの後ろに置く合成処理を追加。原画改変ではない。r4は公開Webで16位相の画像/前景canvas同期を検証済み。r5頭部修正とLTは個別目視再検証待ち。

## 保存場所
入口: character-assets/production/WORK_RESUME_20261008.md
詳細: character-assets/production/20261008/{ledger,qa,scripts,donors}/
正式画像: character-assets/layers/character/ 各楽器とcombo。
入力: DTX_Drum_Flow_Work_素材一式と制作仕様書_20261008.zip、libfile_cb32a71ec6688191b3cd32ae3785f0b9。指定名WORK_MASTER_SPEC_REVISED.mdはZIPになく、同梱WORK_MASTER_SPEC.mdとユーザー1〜10を適用。

## 再開手順
1. 最新mainとこの入口、ledger/motion_matrix.jsonを読む。公開サイトのcache version 20261008-lt-r5 と前景レイヤーを確認。8ペア16位相を実測し、人体と打点も画面で確認。
2. LT:R局所Hit/Reboundは合格し正式画像へ反映。HT:Lは生成打点不一致で不合格、BD:RFとFT:Rは局所修正候補。環境切断で候補処理/連続QAが未完了。赤いガイドは参考だけで完成画像に含めない。LT打面は885,416付近、旧885,455は側面。
3. HT左右、LT左右、FT左右、BD右足を制作し、合格部位だけ組み合わせて残20ペアを制作。BD旧735,650はドラム面で足の打点ではない。実際のペダル板を使用。
4. 各ペアで人体・同一人物・Hit接触・Rebound離隔・固定部分を検査し、不合格は修正。GitHubに実体・台帳・失敗理由・次位置を保存する。
5. 公開Webの全30動作60位相と再生、PC/モバイルを検証。画像の合格と読み込みの合格を区別する。

## 確定したチェック
commit41635d06b706d8e399821f9ff80b369c87c3bc19のvalidateとRuntime Pose SN-L Source QAはGitHub Actions SUCCESS。以後の変更は改めて確認。画像の独立したReboundを使うようSN:R設定を修正済み。

## 今回の公開実測
9f45a995ca168da0fce884b46e80b064f7ee9f69 / r4: 8ペア16位相すべて正しいキー・位相・新PNG読み込み・前景canvasフレーム一致。Runtime Character QA、Character asset validation、deploy-siteはGitHub Actions SUCCESS。QA JSONは20261008/qa/browser_post_promote_8_pairs.json。新しい頭部mask修正後は再確認する。

## r5自動検査
commit3546e9e488c88879d1bfc8bd75d156308a9b366aのvalidate、Character asset validation、Runtime Character QA、Drum Runtime Browser QA、deploy-siteはGitHub Actions SUCCESS。これは個別画像の人体目視合格を置き換えない。既存Dropbox mirror workflowのみ失敗、GitHubのPNG/スクリプト/台帳は保存済み。

## 最新ユーザー指示と次の位置
- 髪が手前の場合、ドラム→スティック→髪の順。完全に隠れる箇所は評価・再構築不要。見えている人体と境界のみ評価。
- r6: 元Neutralの髪画素だけを複製、旧右手を除外、y350未満を除外してライドを切らない。qa/hair_depth_source.json の画素不一致0。公開後の視覚評価は未完了。
- BD局所生成2件を保存。最初はつま先方向逆で不合格、2件目は後ろ向きの部品候補で最終画像ではない。donors/right_boot_rear_candidate.png をペダルに局所投影し、元の膝・胴・左脚・ドラムを保護してHit/Reboundを作る。
- scripts/add_hair_depth_layer.py は新規ベース用で再実行するとJSが重複する。現在の実装に再適用しない。
