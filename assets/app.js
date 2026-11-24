// Renders registry.json. No framework, no build step: GitHub Pages serves this
// file as-is, and the only data source is the registry CoreFrame reads.
(() => {
  'use strict';

  const REPO = 'Explotador72/coreframe-marketplace';
  // Derived from the address bar, so the site is identical on the Pages host and on
  // the custom domain, and the URL the page offers is always the one it was served from.
  const PAGE = location.origin + location.pathname.replace(/[^/]*$/, '');
  const REGISTRY_URL = PAGE + 'registry.json';

  const $ = (id) => document.getElementById(id);
  const state = { data: null, category: 'all', query: '', sort: 'name' };

  const esc = (value) => String(value == null ? '' : value)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

  const monogram = (name) => {
    const clean = String(name || '?').replace(/[^A-Za-z0-9 ]/g, '').trim();
    const words = clean.split(/\s+/).filter(Boolean);
    if (!words.length) return '?';
    return words.length > 1 ? (words[0][0] + words[1][0]) : words[0].slice(0, 2);
  };

  function renderStats(registry) {
    const exts = registry.extensions || [];
    $('count-ext').textContent = exts.length;
    $('count-ver').textContent = exts.reduce((n, e) => n + (e.versions || []).length, 0);
    $('updated').textContent = registry.updated || '—';
    $('registry-url').textContent = REGISTRY_URL;
    $('submit-link').href = `https://github.com/${REPO}/issues/new?template=submission.yml`;
  }

  function renderChips(registry) {
    const seen = new Map();
    for (const ext of registry.extensions || []) {
      const key = String(ext.category || 'general');
      seen.set(key, (seen.get(key) || 0) + 1);
    }
    const chips = [['all', 'All', (registry.extensions || []).length]];
    for (const [key, count] of [...seen.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
      chips.push([key, key, count]);
    }
    $('categories').innerHTML = chips.map(([key, label, count]) =>
      `<button type="button" class="chip${key === state.category ? ' active' : ''}" data-cat="${esc(key)}">` +
      `${esc(label)} <span class="mono">${count}</span></button>`).join('');
    $('categories').querySelectorAll('.chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        state.category = chip.dataset.cat;
        renderChips(registry);
        renderGrid();
      });
    });
  }

  function matches(ext) {
    if (state.category !== 'all' && String(ext.category) !== state.category) return false;
    if (!state.query) return true;
    const hay = [ext.id, ext.name, ext.description, ext.author, ext.category]
      .join(' ').toLowerCase();
    return state.query.split(/\s+/).filter(Boolean).every((word) => hay.includes(word));
  }

  function versionKey(value) {
    return String(value).split('.').map((n) => parseInt(n, 10) || 0);
  }

  function sorted(list) {
    const copy = list.slice();
    if (state.sort === 'author') {
      copy.sort((a, b) => String(a.author).localeCompare(String(b.author)) ||
        String(a.name).localeCompare(String(b.name)));
    } else if (state.sort === 'updated') {
      copy.sort((a, b) => {
        const x = versionKey(a.version);
        const y = versionKey(b.version);
        for (let i = 0; i < 3; i++) if ((y[i] || 0) !== (x[i] || 0)) return (y[i] || 0) - (x[i] || 0);
        return String(a.name).localeCompare(String(b.name));
      });
    } else {
      copy.sort((a, b) => String(a.name).localeCompare(String(b.name)));
    }
    return copy;
  }

  function card(ext) {
    const versions = (ext.versions && ext.versions.length)
      ? ext.versions
      : [{ version: ext.version, download_url: ext.download_url }];
    const platforms = (ext.platforms || []).map((p) => `<span class="pill">${esc(p)}</span>`).join('');
    const rows = versions.map((v) => `
      <div class="version-row">
        <span>${esc(v.version)}</span>
        <a href="${esc(v.download_url)}" rel="noopener" title="Download the .zip">download</a>
      </div>`).join('');

    return `
      <article class="card">
        <div class="card-head">
          <div class="avatar" aria-hidden="true">${esc(monogram(ext.name))}</div>
          <div class="card-title">
            <h2 class="card-name">${esc(ext.name)}</h2>
            <p class="card-sub">by ${esc(ext.author)} · <span class="mono">${esc(ext.id)}</span></p>
          </div>
          <span class="badge latest">v${esc(ext.version)}</span>
        </div>
        <p class="card-desc">${esc(ext.description)}</p>
        <div class="card-meta">
          <span class="pill">${esc(ext.category || 'general')}</span>
          ${platforms}
        </div>
        <div class="versions">${rows}</div>
      </article>`;
  }

  function renderGrid() {
    const registry = state.data;
    if (!registry) return;
    const list = sorted((registry.extensions || []).filter(matches));
    $('grid').innerHTML = list.map(card).join('');
    $('empty').hidden = list.length > 0;
  }

  function wire() {
    $('search').addEventListener('input', (event) => {
      state.query = event.target.value.trim().toLowerCase();
      renderGrid();
    });
    $('sort').addEventListener('change', (event) => {
      state.sort = event.target.value;
      renderGrid();
    });
    $('copy-url').addEventListener('click', async (event) => {
      const button = event.currentTarget;
      try {
        await navigator.clipboard.writeText(REGISTRY_URL);
      } catch (_) {
        const range = document.createRange();
        range.selectNodeContents($('registry-url'));
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        document.execCommand('copy');
      }
      const label = button.textContent;
      button.textContent = 'Copied';
      button.classList.add('done');
      setTimeout(() => { button.textContent = label; button.classList.remove('done'); }, 1400);
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === '/' && document.activeElement !== $('search')) {
        event.preventDefault();
        $('search').focus();
      }
    });
  }

  async function boot() {
    wire();
    try {
      const response = await fetch('registry.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`registry.json: HTTP ${response.status}`);
      state.data = await response.json();
    } catch (error) {
      $('grid').innerHTML = `<p class="empty">Could not load the registry: ${esc(error.message)}</p>`;
      return;
    }
    renderStats(state.data);
    renderChips(state.data);
    renderGrid();
  }

  boot();
})();
