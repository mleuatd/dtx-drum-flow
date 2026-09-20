# DTX Drum Flow 人物差分画像・完全統合生成仕様

## 目的
このディレクトリは、Luna Say Maybe 人物差分62枚を再生成する前の唯一の生成仕様正本です。画像生成より先に、共通仕様・動作仕様・個別フレーム差分を固定します。既存62枚は保存対象であり、この仕様作成では上書きしません。

## 正本優先順位
1. ユーザーが明示した HARD 条件
2. GitHub main の FULL_IMAGE_VISUAL_AUDIT_20260920.json
3. GitHub main の asset_inventory.json / character-prototype.js / app.js にある実装ロック
4. PASS画像の実測・視覚測定
5. 062_drum_base.png の測定
6. IK等の派生 SOFT 制約
7. FAIL画像は actionKey・phase・動作意図・カメラ意図だけ参照可能

推定値は絶対値に昇格させません。各座標には source / confidence / tolerance を持たせます。

## 3層継承
共通仕様 → actions/<action>.json → frames/<frame>.json の順で上書きします。個別フレームは差分だけを持ち、共通条件を複製しません。

## 固定事項
- 1448×1086 PNG
- 白黒ラフ線画、黒線、透明背景優先
- 長い青緑〜ミント髪、グレーチェックのロングジャケット、暗色短スカート、黒ショートブーツ
- 4頭身デフォルメ、同一人物
- 背後から左へ回り込む反対肩越し。背中大、顔は画面左に少し、視線右、ドラムは右奥
- 真正面・真横・真後ろ・左右反転は禁止
- 腕2、脚2、手2、スティック2、各手最大1本
- 062ドラムベースを固定別レイヤーとして扱い、人物フレーム内へドラムを再描画しない
- ラフ線は許容するが、人体破綻・残像・余分な線・矩形合成痕・黒塊は許容しない

## 数値の読み方
座標は左上原点、x右、y下。norm は [x/1448, y/1086]。画面角度は +x から時計回りの度数です。
IMPLEMENTATION_LOCK は高確度、MEASURED_* は測定基準、DERIVED_* はSOFT制約です。

## 動作
hit/rebound は同一 actionKey の1セットです。hit は対象打点の許容楕円内、rebound は同じ軌道系で45〜105px（標準70px）離し、スティック角度差は原則12°以内。高速連打でも別ポーズの残像を残しません。

## レイヤー
人物フレームは人物・椅子・2本のスティックだけを全画面座標で持ちます。ドラムは DRUM_GEOMETRY.json に従う固定別レイヤー。人物画像の生成時はドラムベースを位置参照に使いますが、出力人物PNGへ焼き込みません。

## QA
生成前は actionKey / limb / target / positive reference / negative constraint を確認。生成後は自動QAと視覚QAを両方通します。HARD違反は即FAIL。自動計測がSOFT値を超えた場合は、視覚測定誤差か作画ドリフトかを確認してから修復します。

## 参照禁止
FAIL 53枚の破綻部分を正例へ混ぜることは禁止です。REVIEW 1枚も正例へ自動昇格させません。詳細は REFERENCE_POLICY.json と NEGATIVE_CONSTRAINTS.json を参照。

## 次工程ゲート
SELF_CHECK.json の gate が PASS で、全30 action と全62 frame spec が存在する場合のみ、次の再生成工程へ進めます。