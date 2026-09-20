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
   1. 同一actionの監査PASS済み兄弟phaseを土台に、関節ランドマークと打点を使って連続メッシュ変形する
   2. 承認済み既存PNGから、関節でつながった意味単位を同一変形場で再構成する
   3. 独立した微小ゴミに限り、決定論的な透明化・局所補修を行う
5. 顔、髪、衣装、カメラ、固定ドラム、対象外の手足は変更しない。人物全体の生成・再配置は行わない。
6. 1448×1086 RGBA、alpha、対象外差分、手足数、腰→脚→足→ペダルの連続性、余分なスティック・矩形スプライスの有無を確認する。
7. 候補・固定ドラム合成・比較画像・QA・設定JSONを独立試験場所へ保存する。承認前に正式runtimeを上書きしない。
8. 原寸PNGの直接リンクを提示し、ユーザー目視確認で停止する。承認前に他画像へ横展開しない。

## 失敗時の切替規則

- 局所消去で新しい切断線や矩形境界が出たら、その案は正式反映しない。
- 2回続けて同じ方式が失敗したら、同一actionのPASS済み兄弟phaseまたは別の承認済みドナーへ切り替える。
- 機械QAだけで完了扱いにせず、原寸実画像の目視確認を必須とする。

## 008 代表試験と標準化

- 対象: `008_bd_rf_hit.png`
- runtime: `character-assets/layers/character/bd/hit_rf.png`
- 監査異常: 両脚の間の第3脚・ブーツ状残留、腰・スカート下端から脚への分断、矩形スプライス
- 正常土台: 同一actionで監査PASSの `character-assets/layers/character/bd/rebound_rf.png`
- 正常土台SHA-256: `6a4fe9c5f2d56adf88fd020ef84bf1d975d9a4e6ecf5d002e5db00a329b0b660`
- 現runtimeは破綻除去用の暫定代替として保存し、hit/rebound差を復元するメッシュ変形候補とは分離する
- 採用方式: 正常土台の右脚を、`hip -> knee -> ankle -> boot -> BD pedal`の関節連続性を保ったままreboundからhitへ変形する
- 同一変形場: 身体輪郭、衣服輪郭、チェック柄、スカート裾、脚、ブーツ、alpha
- 固定領域: 顔、頭髪、両腕、両手、スティック、左脚、椅子、対象外透明領域
- 候補保存先: `character-assets/generation-trials/mesh-warp-008-v1/`
- 標準化ゲート: 候補生成 -> 軽量QA -> 対象外差分QA -> 固定ドラム合成 -> 原寸視覚QA -> ユーザー確認
- 横展開順: `008 -> 010 -> 014 -> 028 -> 032`
- 横展開条件: 2026-09-21指示以降は、他frameも candidate / QA / review / GitHub保存まで1件ずつ展開可。runtime反映は各画像のユーザー承認まで禁止
- 禁止: reboundの単純コピー、矩形貼り付け、足だけの平行移動、第3脚だけの消去、完全新規AI生成、承認前のruntime上書き

## 008 メッシュ変形試験（runtime未反映）

- 実装: `tools/character_layers/build_mesh_warp_pose.py`
- 設定: `character-assets/generation-trials/mesh-warp-008-v1/008_mesh_config.json`
- 入力は監査PASS済みの `rebound_rf.png`。右脚のROIだけを薄板スプラインで連続変形する。
- 顔・髪・腕・左脚・固定ドラムは変形しない。ドラムは別の固定レイヤーとして確認用画像だけに合成する。
- 形状、線、チェック柄、alphaを同じ写像で同時に変形し、矩形パーツ貼付けを禁止する。
- 境界固定点をROI四辺に置き、右脚だけを対象にして境界の不連続を防止する。
- 再生成の実測は1.77秒（候補保存、機械QA、固定ドラム合成を含む）。座標調整はJSONだけで行う。
- 高速化は入力PNGのローカルキャッシュ、設定駆動、ROI限定、固定ドラムの再利用、機械QAの同時実行で行う。補間品質や原寸目視工程は省略しない。
- 候補は `generation-trials/mesh-warp-008-v1/` に隔離し、ユーザー承認までruntimeへ反映しない。


## 008高速再生成標準（2026-09-21）

008成功方式の再生成は `tools/character_layers/run_visual_repair_trial.py` を標準入口とする。

- 入力PNGはSHA-256で固定し、同一セッションでは `.cache/visual-repair/` を再利用する。キャッシュ自体はGit管理しない。
- 1コマンドで config検証 -> mesh warp -> machine QA -> fixed drum合成 -> formal/review分離 -> before/after -> timing -> manifest を生成する。
- formal candidateは1448×1086 RGBA lossless PNG、reviewは別ファイルのlossless WebPとする。
- machine QA FAIL時は候補を登録候補一覧に入れない。
- `visualQaRequired=true` を維持し、機械PASSだけではVERIFIEDまたはruntime昇格にしない。
- runtime pathと010／014／028／032その他のframeは安全チェックで登録対象から除外する。
- 008のユーザー承認状態は `PENDING` のままとし、承認前のruntime上書きは禁止する。他frameのtrial横展開は1件ずつ許可する。
- 仕様更新時はGitHub最新版blob SHAを取得した上で、その最新版に今回分だけ追記する。


## 全身自然さを含む横展開（2026-09-21）

新規frameでは `character-assets/config/mesh_warp_frame_template_v1.json` を複製して専用JSONを作る。Python本体へのframe別分岐は禁止。

normal source選定では、脚・腕など単一点の近さより、腰→骨盤→体幹→肩→脚→足先までの流れが自然で目標姿勢に近い正常画像を優先する。兄弟phaseが監査FAILなら、そのままnormal sourceへ採用しない。

視覚QAでは局所の形だけでなく、腰と脚、骨盤と体幹、体幹と肩、上下半身の一体感、重心、演奏動作の流れ、服の柄と輪郭の整合を確認する。これらは人間確認用メタデータであり、重い自動探索・自動スコアリング・反復最適化は標準工程へ追加しない。

次候補の010（BD+RC hit）は、同一actionの011 reboundも右手スティック重複でFAILのため、011を無条件にnormal sourceへ使わない。全身の流れが近く監査PASSの別ドナーを先に選定してから専用JSONを作る。
