import fs from "node:fs/promises";

const base = "character-assets/prototypes/luna_say_maybe_16m";
const [actionKey, phase, dropboxPath, sha256, outArg] = process.argv.slice(2);

if (!actionKey || !["hit","rebound"].includes(phase) || !dropboxPath || !sha256) {
  throw new Error("usage: node tools/build-character-import-staging.mjs <ACTION_KEY> <hit|rebound> <DROPBOX_PATH> <SHA256> [OUT.json]");
}
if (!/^[a-f0-9]{64}$/i.test(sha256)) throw new Error("SHA256 must be 64 hex chars");
if (!dropboxPath.startsWith("/ChatGPT/dtx-drum-flow/")) throw new Error("Dropbox path must stay under /ChatGPT/dtx-drum-flow/");

const readJson = async p => JSON.parse(await fs.readFile(p, "utf8"));
const map = await readJson(base + "/ACTION_KEY_ASSET_MAP.json");
const entry = map.entries.find(x => x.actionKey === actionKey);
if (!entry) throw new Error("unknown actionKey " + actionKey);
if (entry.neverUse) throw new Error("actionKey is marked neverUse: " + actionKey);

const githubPath = phase === "hit" ? entry.hitAsset : entry.reboundAsset;
if (!githubPath) throw new Error(`missing ${phase} asset path for ${actionKey}`);

const parts = actionKey.split(":");
const instruments = parts[0].split("+");
const limbs = (parts[1] || "").split("/");
const part = instruments.join("+");
const limb = limbs.join("/");

const safe = s => s.toLowerCase()
  .replace(/\+/g, "_")
  .replace(/[:/]/g, "_")
  .replace(/[^a-z0-9_]+/g, "_")
  .replace(/^_+|_+$/g, "");

const assetKey = `${safe(actionKey)}_${phase}`;
const out = {
  schemaVersion: 2,
  assetKey,
  actionKey,
  runtimeKey: entry.limbAwareRuntimeKey || entry.runtimeKey,
  dropboxPath,
  githubPath,
  part,
  limb,
  phase,
  measureRange: [entry.firstMeasure ?? null, entry.lastMeasure ?? null],
  occurrenceCount: entry.occurrenceCount ?? null,
  sourceSha256: sha256.toLowerCase(),
  sha256: sha256.toLowerCase(),
  width: 1448,
  height: 1086,
  status: "READY_TO_IMPORT",
  generatedBy: "tools/build-character-import-staging.mjs"
};

const dest = outArg || `character-assets/staging/${assetKey}.json`;
await fs.mkdir(dest.split("/").slice(0, -1).join("/"), { recursive: true });
await fs.writeFile(dest, JSON.stringify(out, null, 2) + "\n");
console.log(JSON.stringify({ dest, actionKey, phase, dropboxPath, githubPath, sha256: out.sha256 }, null, 2));
