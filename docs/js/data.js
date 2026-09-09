// Fetches manifest.json and per-set data files from /data.
// Uses a simple in-memory cache so navigating between sections of a
// page (or re-rendering) doesn't re-fetch a set file it already has.

const DATA_PATH = "data"; // sibling folder inside /docs

const _setCache = {};

async function loadManifest() {
  const res = await fetch(`${DATA_PATH}/manifest.json`);
  if (!res.ok) throw new Error("Could not load manifest.json");
  return res.json();
}

async function loadSet(setId) {
  if (_setCache[setId]) return _setCache[setId];
  const res = await fetch(`${DATA_PATH}/sets/${setId}.json`);
  if (!res.ok) throw new Error(`Could not load set: ${setId}`);
  const data = await res.json();
  _setCache[setId] = data;
  return data;
}

async function loadAllSets(manifest) {
  const all = [];
  for (const s of manifest) {
    const entries = await loadSet(s.set_id);
    all.push(...entries);
  }
  return all;
}

function mostRecentSet(manifest) {
  return manifest.reduce((latest, s) => {
    if (!latest) return s;
    return (s.release_date || "") > (latest.release_date || "") ? s : latest;
  }, null);
}
