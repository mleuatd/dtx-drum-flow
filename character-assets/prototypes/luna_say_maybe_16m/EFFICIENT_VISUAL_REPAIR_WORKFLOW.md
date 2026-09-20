# 原寸監査画像の効率的修復手順

対象監査: `FULL_IMAGE_VISUAL_AUDIT_20260920.json`

## 目的

62枚を毎回まとめて取得・再生成せず、監査FAILを1ファイルずつ最小変更で修復し、原寸目視確認後にだけ同型不具合へ横展開する。

## 正本

- 最新GitHub `main`
- `character-assets/prototypes/luna_say_maybe_16m/FULL_IMAGE_VISUAL_AUDIT_20260920.json`
- `character-assets/prototypes/luna_say_maybe_16m/generation-spec/`
- runtimeで使用中の `character-assets/layers/character/` 配下PNG
- Dropbox原寸画像は上記runtime PNGの確認用複製とし、同一内容なら再転送しない

## 1ファイル修復ループ

1. 監査JSONから対象1件の `filename`、`actionKey`、`phase`、`defects`、`defectRegions`、`severity` を読む。
2. runtimeマッピングから正式PNGを1枚だけ特定する。
3. 対象PNG、同一actionのPASS済み兄弟phase、neutral、必要な場合だけ最小限の既存ドナーを取得する。62枚一括ZIPは作らない。
4. 原寸で異常ROIを確認し、次の優先順で修復方法を選ぶ。
   1. 同一actionの監査PASS済み兄弟phaseをそのまま再利用
   2. 承認済み既存PNGからROIだけ決定論的に移植
   3. Pillow等で余分な残留パーツだけを透明化・局所補修
5. 顔、髪、衣装、カメラ、固定ドラム、対象外の手足は変更しない。人物全体の生成・再配置は行わない。
6. 1448×1086 RGBA、alpha、対象外差分、手足数、腰→脚→足→ペダルの連続性、余分なスティック・矩形スプライスの有無を確認する。
7. 修正版1枚だけを正式runtimeパスへ反映し、修復手順とSHA-256を記録する。
8. 原寸PNGの直接リンクを提示し、ユーザー目視確認で停止する。承認前に他画像へ横展開しない。

## 失敗時の切替規則

- 局所消去で新しい切断線や矩形境界が出たら、その案は正式反映しない。
- 2回続けて同じ方式が失敗したら、同一actionのPASS済み兄弟phaseまたは別の承認済みドナーへ切り替える。
- 機械QAだけで完了扱いにせず、原寸実画像の目視確認を必須とする。

## 008 試験修復

- 対象: `008_bd_rf_hit.png`
- runtime: `character-assets/layers/character/bd/hit_rf.png`
- 監査異常: 両脚の間の第3脚・ブーツ状残留、腰・スカート下端から脚への分断、矩形スプライス
- 採用方式: 同一actionで監査PASSの `character-assets/layers/character/bd/rebound_rf.png` を承認ドナーとして再利用
- 承認ドナーSHA-256: `6a4fe9c5f2d56adf88fd020ef84bf1d975d9a4e6ecf5d002e5db00a329b0b660`
- 修復後SHA-256: `eb6935313168f29f8f804bb4b7e2f4aeb4896172b326411e01476975de3e3eb8`
- 理由: 元hitの脚パッチ自体が矩形背景を含み、消し込みでは新しい切断線が残るため。同一actionの正常画像を使うことで人体・衣装・カメラを変えずに破綻を除去できる。
- 停止条件: 008の原寸目視確認完了まで、010、014、028、032その他へ展開しない。

## 008 メッシュ変形試験（runtime未反映）

- 実装: `tools/character_layers/build_mesh_warp_pose.py`
- 設定: `character-assets/generation-trials/mesh-warp-008-v1/008_mesh_config.json`
- 入力は監査PASS済みの `rebound_rf.png`。右脚のROIだけを薄板スプラインで連続変形する。
- 顔・髪・腕・左脚・固定ドラムは変形しない。ドラムは別の固定レイヤーとして確認用画像だけに合成する。
- 形状、線、チェック柄、alphaを同じ写像で同時に変形し、矩形パーツ貼付けを禁止する。
- 境界固定点をROI四辺に置く。初回試行で生じた腰境界の不連続を、この固定点と右脚限定ROIで防止した。
- 再生成の実測は1.77秒（候補保存、機械QA、固定ドラム合成を含む）。座標調整はJSONだけで行い、画像取得やツール作成を繰り返さない。
- 高速化は入力PNGのローカルキャッシュ、設定駆動、ROI限定、固定ドラムの再利用、機械QAの同時実行で行う。補間品質や原寸目視工程は省略しない。
- 候補は `generation-trials/mesh-warp-008-v1/` に隔離し、ユーザー承認までruntimeへ反映しない。
