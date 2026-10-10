(()=> {
  const root = document.querySelector("[data-tool-directory]");
  if (!root) return;
  const category = root.dataset.category || "";
  const categoryMeta = {
    "pdf-tools": { label: "PDF", color: "#e53935", bg: "#fff0f0", icon: '<path d="M7 3.75h7l5 5v11.5a1.75 1.75 0 0 1-1.75 1.75h-10.5A1.75 1.75 0 0 1 5 20.25V5.5a1.75 1.75 0 0 1 2-1.75Z"/><path d="M14 4v5h5M8 15h8M8 18h5"/>' },
    "youtube-tools": { label: "YouTube", color: "#e62117", bg: "#fff0ef", icon: '<rect x="3" y="6" width="18" height="12" rx="4"/><path d="m10 9 5 3-5 3z" fill="currentColor" stroke="none"/>' },
    "image-tools": { label: "Image", color: "#7c3aed", bg: "#f4efff", icon: '<rect x="3.5" y="4" width="17" height="16" rx="2.5"/><circle cx="9" cy="9" r="1.5"/><path d="m4 17 5-5 3 3 3-4 5 6"/>' },
    "data-tools": { label: "Data", color: "#087f8c", bg: "#e8fbfc", icon: '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7"/>' },
    "nepal-tools": { label: "Nepal", color: "#2563eb", bg: "#eef5ff", icon: '<path d="m3 17 5-7 3 3 4-7 6 11H3Z"/><path d="m8 10 2 1M14 7l2 1"/>' },
    "laxman-tools": { label: "Laxman", color: "#0f766e", bg: "#e9fbf6", icon: '<path d="M14.7 6.3a5 5 0 0 0-6.4 6.4L3.5 17.5a2.1 2.1 0 0 0 3 3l4.8-4.8a5 5 0 0 0 6.4-6.4l-3 3-3.5-3.5 3.5-3.5Z"/>' }
  };
  const meta = categoryMeta[category] || { label: category.replace(/-tools$/, "").replace(/-/g, " "), color: "#475467", bg: "#f2f4f7", icon: '<circle cx="12" cy="12" r="8"/><path d="M12 8v8M8 12h8"/>' };
  const label = meta.label;
  root.className = "td-page";
  root.innerHTML = `<section class="td-hero"><span class="td-badge">LAXMAN NEPAL · ${label.toUpperCase()} TOOLS</span><h1>Free <span>${label}</span> tools.</h1><p>Browse every tool in this category. Each tool lives in its own folder with a dedicated page and helpful information.</p></section><div class="td-toolsbar"><input class="td-search" type="search" placeholder="Search ${label} tools…" aria-label="Search tools"><span class="td-count" aria-live="polite">Loading tools…</span></div><div class="td-grid"></div><div class="td-empty" hidden>No tools are listed in this category yet.</div><div class="td-error" hidden></div>`;
  const grid = root.querySelector(".td-grid"), search = root.querySelector(".td-search"), count = root.querySelector(".td-count"), empty = root.querySelector(".td-empty"), error = root.querySelector(".td-error");
  let items = [];
  const pretty = s => s.replace(/[-_]+/g, " ").replace(/\b\w/g, m => m.toUpperCase()).replace(/Youtube/g, "YouTube").replace(/Pdf/g, "PDF");
  const icon = `<svg class="td-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${meta.icon}</svg>`;
  function draw() {
    const q = search.value.trim().toLowerCase();
    const shown = items.filter(x => (x.name + " " + x.title + " " + (x.description || "")).toLowerCase().includes(q));
    grid.innerHTML = shown.map(x => {
      const name = String(x.name || "");
      const title = String(x.title || pretty(name));
      const description = String(x.description || ("Free " + label.toLowerCase() + " tool from Laxman Nepal."));
      return `<a class="td-card" href="/${category}/${encodeURIComponent(name)}/"><span class="td-logo" style="--td-icon-color:${meta.color};--td-icon-bg:${meta.bg}">${icon}</span><h2>${title}</h2><p>${description}</p><span class="td-open">Open tool →</span></a>`;
    }).join("");
    count.textContent = shown.length + " tool" + (shown.length === 1 ? "" : "s");
    empty.hidden = shown.length !== 0;
    error.hidden = true;
  }
  async function load() {
    try {
      const r = await fetch("/" + category + "/tools.json", { cache: "no-store" });
      if (!r.ok) throw Error("Could not read local tool catalog");
      const data = await r.json();
      if (!Array.isArray(data)) throw Error("Invalid tool catalog");
      items = data.filter(x => x && typeof x.name === "string").map(x => ({ name: x.name, title: x.title || pretty(x.name), description: x.description || ("Free " + label.toLowerCase() + " tool from Laxman Nepal.") }));
      draw();
    } catch (e) {
      count.textContent = "Catalog unavailable";
      error.textContent = "We couldn't load this tool list right now. Please try again shortly.";
      error.hidden = false;
      empty.hidden = true;
      grid.innerHTML = "";
    }
  }
  search.addEventListener("input", draw);
  load();
})();