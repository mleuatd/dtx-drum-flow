# FORMAL INVENTORY RECONCILIATION — TERM-B

Generated: 2026-09-19T20:16:00+09:00
Task: OTHER-001
Authority checked: latest GitHub main immediately before write.

## Result

The runtime inventory is ahead of ACTION_KEY_ASSET_MAP.json for three actionKeys. The formal PNG files exist on main and asset_inventory.json maps hit/rebound frames, while ACTION_KEY_ASSET_MAP.json still marks them NEW_IMAGE_REQUIRED / ABSENT / runtimeMapped=false.

| actionKey | hit | rebound | discrepancy |
|---|---|---|---|
| BD+HT:RF/R | character-assets/layers/character/combo/bd_ht_rf_r_hit_refresh.png | character-assets/layers/character/combo/bd_ht_rf_r_rebound_refresh.png | ACTION_KEY_ASSET_MAP stale |
| LT+SN:R/L | character-assets/layers/character/combo/lt_sn_r_l_hit_refresh.png | character-assets/layers/character/combo/lt_sn_r_l_rebound_refresh.png | ACTION_KEY_ASSET_MAP stale |
| BD+HT:RF/L | character-assets/layers/character/combo/bd_ht_rf_l_hit_refresh.png | character-assets/layers/character/combo/bd_ht_rf_l_rebound_refresh.png | ACTION_KEY_ASSET_MAP stale |

## Repository existence evidence

- BD+HT:RF/R hit blob: 9b8728e28efcff35d472a61695cc9353ef39b70f
- BD+HT:RF/R rebound blob: 5a35d3c70d66f616d583add35ee926257bec9be0
- LT+SN:R/L hit blob: 2647dd2ded23f8e43ea2dfef0aa7088c2379e86c
- LT+SN:R/L rebound blob: 08bd9b500669c50aeeb9aaede5a508e105557b6f
- BD+HT:RF/L hit blob: 4ca619edb2d745200739b8d6302d20fbcc05e56c
- BD+HT:RF/L rebound blob: 2edfea860d220dd20c389b7a65f7a0ffcccf7128

## Disposition

Do not regenerate these six PNGs merely because ACTION_KEY_ASSET_MAP.json says they are absent. Reconcile metadata from asset_inventory/runtime evidence first. No formal PNG was modified by TERM-B.

SN:L formal hit remains protected by TERM-A and was not modified.
