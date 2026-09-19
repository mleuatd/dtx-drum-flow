import fs from "node:fs/promises";

const base = "character-assets/prototypes/luna_say_maybe_16m";
const paths = process.argv.slice(2);
if (!paths.length) throw new Error("usage: node tools/validate-character-import-staging.mjs <staging.json> [...]");

const readJson = async p => JSON.parse(await fs.readFile(p, "utf8"));
const map = await readJson(base + "/ACTION_KEY_ASSET_MAP.json");

for (const path of paths) {
  const s = await readJson(path);
  const required = ["assetKey","actionKey","runtimeKey","dropboxPath","githubPath","part","phase","sourceSha256","sha256","width","height","status"];
  for (const k of required) if (s[k] === undefined || s[k] === null || s[k] === "") throw new Error(`${path}: missing ${k}`);
  if (!["hit","rebound"].includes(s.phase)) throw new Error(`${path}: invalid phase ${s.phase}`);
  if (!/^[a-f0-9]{64}$/i.test(s.sourceSha256) || !/^[a-f0-9]{64}$/i.test(s.sha256)) throw new Error(`${path}: invalid SHA256`);
  if (s.sourceSha256.toLowerCase() !== s.sha256.toLowerCase()) throw new Error(`${path}: sourceSha256 != sha256; normalization is not allowed in schemaVersion 2`);
  if (!String(s.dropboxPath).startsWith("/ChatGPT/dtx-drum-flow/")) throw new Error(`${path}: Dropbox path outside project root`);
  if (!String(s.githubPath).startsWith("character-assets/layers/character/")) throw new Error(`${path}: githubPath outside character layer root`);
  if (Number(s.width) !== 1448 || Number(s.height) !== 1086) throw new Error(`${path}: expected 1448x1086`);
  if (!["READY_TO_IMPORT","IMPORTED"].includes(s.status)) throw new Error(`${path}: invalid status ${s.status}`);

  const entry = map.entries.find(x => x.actionKey === s.actionKey);
  if (!entry) throw new Error(`${path}: unknown actionKey ${s.actionKey}`);
  const expectedPath = s.phase === "hit" ? entry.hitAsset : entry.reboundAsset;
  if (expectedPath !== s.githubPath) throw new Error(`${path}: githubPath mismatch; expected ${expectedPath}`);
  const expectedRuntime = entry.limbAwareRuntimeKey || entry.runtimeKey;
  if (expectedRuntime !== s.runtimeKey) throw new Error(`${path}: runtimeKey mismatch; expected ${expectedRuntime}`);
  if (entry.neverUse) throw new Error(`${path}: actionKey is marked neverUse`);

  console.log(JSON.stringify({ path, status: "VALID", actionKey: s.actionKey, phase: s.phase, githubPath: s.githubPath, sha256: s.sha256 }));
}
