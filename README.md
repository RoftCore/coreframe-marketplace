# RoftCore Marketplace

The official extension marketplace for **CoreFrame**: a static site (GitHub Pages) plus the
`registry.json` that CoreFrame fetches.

- **Site (canonical):** <https://coreframe-marketplace.roftcore.work/>
- **Registry (what CoreFrame reads):** `https://coreframe-marketplace.roftcore.work/registry.json`
- **Until the custom domain is live:** <https://roftcore.github.io/coreframe-marketplace/>

### Custom domain

`coreframe-marketplace.roftcore.work` is served by GitHub Pages, so DNS points at the Pages host,
not at an IP:

| Type | Name | Content | Proxy |
|---|---|---|---|
| CNAME | `coreframe-marketplace` | `explotador72.github.io` | **DNS only** (grey cloud) while the certificate is issued |

Then set it in the repository: *Settings → Pages → Custom domain*, tick **Enforce HTTPS** once the
certificate is ready (a few minutes), and commit a `CNAME` file containing the domain. The site
derives its own registry URL from the address bar, so nothing else has to change when the domain
goes live.

## How CoreFrame uses it

CoreFrame reads the registry from one URL and renders a **Marketplace** panel: name, version,
description and, when an extension has more than one published version, a dropdown to install an
older one. It only reads `extensions[].id`, `.name`, `.version`, `.download_url` and `.versions[]`;
everything else is for the site and for humans.

The URL is `MARKETPLACE_URL` in `coreframe/config.py` and can be overridden per install in
`coreframe.json`:

```json
{ "marketplace_url": "https://example.org/my-registry.json" }
```

So anyone can run a mirror or their own marketplace, and pointing CoreFrame at it is one key.

## How an extension gets listed

There is no upload form and no account. Only the maintainer edits `registry.json`, and every
submission is reviewed first:

1. **Publish a release** with the packaged `.zip` (CoreFrame → Package, or any zip whose root
   folder contains `extension.json`). Use a stable tag and an `https://` URL that ends in `.zip`.
2. **Open a submission issue** — [Submit an extension](https://github.com/RoftCore/coreframe-marketplace/issues/new?template=submission.yml).
   The form asks for the id, author, description, category and the release URL.
3. **Review** against [`docs/VERIFY.md`](docs/VERIFY.md). A submission that fails gets a comment
   saying exactly what to change; nothing is published silently.
4. **The registry is updated** and the extension appears on the site and in CoreFrame within the
   cache window (CoreFrame caches the registry for 120 seconds).

New versions of an already listed extension follow the same path. Old versions stay in
`versions[]`, newest first, so users can pin or roll back.

## Working on it locally

```bash
python -m http.server 8000          # then open http://127.0.0.1:8000
python tools/validate.py            # registry invariants (CI runs this too)
```

The site is plain HTML/CSS/JS on purpose: no build step means the file GitHub serves is the file
you reviewed.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `assets/` | The marketplace page |
| `registry.json` | The data CoreFrame reads |
| `registry.schema.json` | JSON Schema for that file |
| `docs/FORMAT.md` | Registry contract and field reference |
| `docs/VERIFY.md` | What "verified" means here: the review checklist |
| `tools/validate.py` | Enforces the contract; CI fails on a broken registry |
| `.github/ISSUE_TEMPLATE/submission.yml` | The submission form |

## License

GPL-3.0-or-later, same as CoreFrame. The registry data may be mirrored freely; if you run a mirror,
keep the `publisher` field honest.
