# 作業再開入口 — 2026-10-08

**全作業は未完了です。** 目標はLuna全30動作60枚を自然な人体・固定ドラムで完成し公開Webで検証することです。

## 現在の状態
- 30動作60位相の既存Web切替と画像読み込みを実測済み。描画成功と絵の合格は別です。
- 新しい静的QA合格は10ペア20枚: SN:L、SN:R、HH:R、HH+SN:R/L、RC:R、RC+SN:R/L、RD:R、RD+SN:R/L、LT:R、LT+SN:R/L。最初の8ペア16位相は公開Webで検証済み。残り20ペア。LT2ペアと頭部前後修正は公開検証待ち。
- 固定ドラムと承認NeutralのSHAは不変。髪・胴・脚・近い腕を保護し、必要な腕だけ局所編集。全身AI出力は完成画像として採用しない。
- 413過去画像の一覧と分類: 20261008/ledger/image_audit.json。個別拡大未完了の判定保留を成功donorとして使わない。
- RDの最初のAI生成は打点が高すぎて不合格。元Neutralの手とスティックを局所変形したv2を使用。HT:L試作は袖の白い切れと残像で不合格。
- ドラム原画の一部RGBAをそのまま複製した前景PNGと腕前景canvasで、髪/身体をタム・ライドの後ろに置く合成処理を追加。原画改変ではない。公開Webの見た目・性能の検証は次の作業。

## 保存場所
入口: character-assets/production/WORK_RESUME_20261008.md
詳細: character-assets/production/20261008/{ledger,qa,scripts,donors}/
正式画像: character-assets/layers/character/ 各楽器とcombo。
入力: DTX_Drum_Flow_Work_素材一式と制作仕様書_20261008.zip、libfile_cb32a71ec6688191b3cd32ae3785f0b9。指定名WORK_MASTER_SPEC_REVISED.mdはZIPになく、同梱WORK_MASTER_SPEC.mdとユーザー1〜10を適用。

## 再開手順
1. 最新mainとこの入口、ledger/motion_matrix.jsonを読む。公開サイトのcache version 20261008-occlusion-r4 と前景レイヤーを確認。8ペア16位相を実測し、人体と打点も画面で確認。
2. LT:R局所Hit/Reboundは合格し正式画像へ反映。HT:LとBD:RFの局所生成が進行中。赤いガイドは参考だけで完成画像に含めない。LT打面は885,416付近、旧885,455は側面。
3. HT左右、LT左右、FT左右、BD右足を制作し、合格部位だけ組み合わせて残20ペアを制作。BD旧735,650はドラム面で足の打点ではない。実際のペダル板を使用。
4. 各ペアで人体・同一人物・Hit接触・Rebound離隔・固定部分を検査し、不合格は修正。GitHubに実体・台帳・失敗理由・次位置を保存する。
5. 公開Webの全30動作60位相と再生、PC/モバイルを検証。画像の合格と読み込みの合格を区別する。

## 確定したチェック
commit41635d06b706d8e399821f9ff80b369c87c3bc19のvalidateとRuntime Pose SN-L Source QAはGitHub Actions SUCCESS。以後の変更は改めて確認。画像の独立したReboundを使うようSN:R設定を修正済み。

## 今回の公開実測
9f45a995ca168da0fce884b46e80b064f7ee9f69 / r4: 8ペア16位相すべて正しいキー・位相・新PNG読み込み・前景canvasフレーム一致。Runtime Character QA、Character asset validation、deploy-siteはGitHub Actions SUCCESS。QA JSONは20261008/qa/browser_post_promote_8_pairs.json。新しい頭部mask修正後は再確認する。
