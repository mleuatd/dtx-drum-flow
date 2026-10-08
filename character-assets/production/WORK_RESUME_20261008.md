# 作業再開入口 — 2026-10-08

目標: 動画と承認Neutralに基づく同一人物、固定ドラム、自然なHit/Reboundを全必要動作について制作し、公開Web背景で検証する。全作業完了ではありません。

## 現在の実績
- Luna最新実装は2,158ノーツ・1,527グループ・30動作・60枚。汎用全曲の全組合せではありません。
- 新規静的QA合格: SN:L、SN:R、HH:R、HH+SN:R/L の4ペア8枚。公開反映と反映後の実測を進行中。
- 公開Webの従来画像を30動作60位相で操作検証: キー/位相60件一致、画像60件読み込み。SN:Rは旧設定でReboundにもHit画像を使用していたため、今回独立Reboundへ修正。表示テストは絵の合格判定とは別。
- 固定ドラムSHA256 dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85 は不変。Neutral SHA256 886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9 は不変。
- 413旧画像の機械検査・一覧確認・3分類はledger/image_audit.json。判定保留は個別拡大未完了で、合格donorとして使わない。旧SN:L、旧HH:Rと旧HH:Lを正しい参考にしない。
- HT:Lの局所試作は袖/肘の白い切れと残像があり不合格。HH v3以前も不合格。

## 固定キャラクター基準
仕様3.4に従い承認Neutralの座標と描線を優先。動画は髪・チェック上着・プリーツ・ブーツの照合に使用。動画は演奏映像ではない。遠い側の右肩は髪に隠れているため推定。右腕は近い左肩の線を編集せず、その背後から前腕を見せる。人物全体のAI再生成出力は採用せず、右腕局所だけ移植し保護領域を元画像へ戻した。

## 保存場所
この入口: character-assets/production/WORK_RESUME_20261008.md
詳細: character-assets/production/20261008/
正式画像: character-assets/layers/character/{sn,hh,combo}/ (今回の4ペアだけ更新)
過去素材は親commit cbfd7bcbe3f634f65136b73b25043cd2c3a4f73f の履歴に残る。
入力ZIP: DTX_Drum_Flow_Work_素材一式と制作仕様書_20261008.zip、libfile_cb32a71ec6688191b3cd32ae3785f0b9。
前回チェックポイントZIP: libfile_44bac41a53bc8191b747aff3e2c80c12。
指定名 WORK_MASTER_SPEC_REVISED.md は入力ZIPに存在せず、同梱 WORK_MASTER_SPEC.md と今回ユーザーの1〜10を適用した。

## 次に行うこと
1. この入口、20261008/qa、ledger/motion_matrix.json を読み、最新mainとの差を調べる。正式8枚の公開反映後、SN:L / SN:R / HH:R / HH+SN:R/Lを再実測し記録する。
2. RC:Rの外向き右腕を局所制作。既存の右腕を画像右の遠い肩からつなぎ、打点1215,145に届かせる。髪/胴/椅子/脚/左腕は保護。合格donorが得られればRD、LT、FT等へ展開。
3. BD:RFのペダル接触は原画上の板を実見して決める。古い効果座標735,650はバスドラム面であり足の打点ではない。足をそこへ移動しない。
4. 全ての残26動作にペア、固定マスク、人体/打点検証、Neutral→Hit→Rebound→Neutralプレビューを作る。候補/不合格を完成数に入れない。
5. 毎ペアまたは中断前にこの入口・台帳をGitHub更新。無人の無期限バックグラウンド実行を約束しない。
