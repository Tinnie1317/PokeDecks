// Renders an array of card-variant entries into a checkbox grid inside
// the given container element. Each tile is one physical print variant
// (e.g. "Charizard - Holofoil"), not one card -- a card with multiple
// variants gets multiple tiles.

function renderGrid(container, entries) {
  container.innerHTML = "";

  if (entries.length === 0) {
    container.innerHTML = "<p class='empty-message'>No cards to show.</p>";
    return;
  }

  for (const entry of entries) {
    const tile = document.createElement("label");
    tile.className = "card-tile";
    tile.htmlFor = `check-${entry.id}`;

    const checked = isCollected(entry.id);
    if (checked) tile.classList.add("collected");

    tile.innerHTML = `
      <input type="checkbox" id="check-${entry.id}" ${checked ? "checked" : ""} />
      <img src="${entry.image_small || ""}" alt="${entry.name}" loading="lazy" />
      <div class="card-info">
        <div class="card-name">${entry.name}</div>
        <div class="card-set">${entry.set_name} &middot; #${entry.number || "?"}</div>
        <div class="card-variant">${entry.print_variant}</div>
        <div class="card-rarity">${entry.special_variant}</div>
      </div>
    `;

    const checkbox = tile.querySelector("input");
    checkbox.addEventListener("change", () => {
      const nowCollected = toggleCollected(entry.id);
      tile.classList.toggle("collected", nowCollected);
    });

    container.appendChild(tile);
  }
}
