// Handles reading/writing the user's collected card IDs to localStorage.
// This is the "personal collection" -- entirely stored in the browser,
// no server or account needed.

const COLLECTION_KEY = "pokedex_collection_v1";

function getCollection() {
  const raw = localStorage.getItem(COLLECTION_KEY);
  return raw ? new Set(JSON.parse(raw)) : new Set();
}

function saveCollection(set) {
  localStorage.setItem(COLLECTION_KEY, JSON.stringify(Array.from(set)));
}

function isCollected(id) {
  return getCollection().has(id);
}

function toggleCollected(id) {
  const collection = getCollection();
  if (collection.has(id)) {
    collection.delete(id);
  } else {
    collection.add(id);
  }
  saveCollection(collection);
  return collection.has(id);
}
