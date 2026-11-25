# Registry format

`registry.json` is the single file CoreFrame fetches. It is hand-edited (not generated), and
`tools/validate.py` enforces everything below in CI.

```json
{
  "$schema": "https://github.com/RoftCore/coreframe-marketplace/raw/main/registry.schema.json",
  "name": "RoftCore Marketplace",
  "publisher": "RoftCore",
  "repository": "https://github.com/RoftCore/coreframe-marketplace",
  "site": "https://coreframe-marketplace.roftcore.work/",
  "updated": "2026-11-24",
  "extensions": [
    {
      "id": "console",
      "name": "Console",
      "version": "3.1",
      "author": "RoftCore",
      "description": "The machine's own shell on a real PTY.",
      "category": "system",
      "icon": "terminal",
      "platforms": ["windows", "linux"],
      "grid_size": { "w": 5, "h": 4 },
      "download_url": "https://github.com/…/console-3.1/console.zip",
      "versions": [
        { "version": "3.1", "download_url": "https://github.com/…/console-3.1/console.zip" },
        { "version": "3.0", "download_url": "https://github.com/…/console-1.1/console.zip" }
      ]
    }
  ]
}
```

## Root fields

| Field | Required | Meaning |
|---|---|---|
| `$schema` | yes | URL of `registry.schema.json`; must match the schema's `$id` |
| `name` | no | Human name of the marketplace |
| `publisher` | yes | Who publishes this registry, not who wrote the extensions |
| `repository` | no | Where the registry lives |
| `site` | no | The page a user can browse |
| `updated` | no | `YYYY-MM-DD`, the last time an entry changed |
| `extensions` | yes | Non-empty array, see below |

## Extension fields

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `^[a-z0-9][a-z0-9_]*$`. **Must equal the `id` in the extension's own `extension.json`**, or CoreFrame installs it under a name the extension does not use. |
| `name` | yes | Shown on the card and in the marketplace panel |
| `version` | yes | Newest published version. Must equal `versions[0].version`. |
| `author` | yes | Shown in the panel |
| `description` | yes | One sentence; it is what a user reads before installing |
| `category` | yes | Free-form label, used by the site's filters |
| `icon` | no | Feather icon name; the site falls back to a monogram |
| `platforms` | no | `["windows", "linux", "macos"]` |
| `grid_size` | no | `{ "w": n, "h": n }` for the default card |
| `download_url` | yes | `https://…​.zip`. Must equal `versions[0].download_url`. |
| `versions` | yes | Newest first. One entry is fine. |

### Why the flat pair and the array

Older CoreFrame builds read only `version` + `download_url`; newer ones read `versions[]` to draw
the version dropdown. Keeping the flat pair equal to the first array entry is what lets one registry
serve both, which is why `tools/validate.py` fails on a mismatch rather than trusting the editor.

### Version strings

`MAJOR.MINOR` or `MAJOR.MINOR.PATCH`, digits only. `1.1` and `1.1.0` are different strings and sort
differently, so pick one form per extension and stay with it. The array must be sorted newest first:
CoreFrame picks `versions[0]` when nobody asks for a specific version.

### Download URLs

- `https://` only, path ending in `.zip`. The marketplace is served over HTTPS and a mixed-content
  zip is a broken install waiting to happen.
- Must stay stable. Republishing different bytes under the same URL is the one thing a reviewer
  cannot see, which is why `sha256` is recorded next to every URL.
- GitHub Releases are the expected host: `https://github.com/<owner>/<repo>/releases/download/<tag>/<id>.zip`.

### Hashes (`sha256`, `size`)

Both are **generated, never edited by hand**:

```bash
python tools/hash_registry.py --write   # downloads every release, records sha256 + size
python tools/hash_registry.py --check   # CI: fails when an asset stops matching
```

- CoreFrame downloads a release, hashes it and refuses to install when the bytes do not match the
  `sha256` in the registry. The error says so explicitly and nothing is written to disk.
- CI runs `--check` on every push, so a release republished under the same URL turns the build red
  instead of reaching a user.
- The site shows the short hash and the size on each version row; the full value is in the tooltip.

An entry without a hash still installs (the check is skipped), but a submission without one is not
accepted: an unhashed release is a promise, not a check.

## Adding an entry

1. Add the object to `extensions`, **newest first is not required for the list** (the site sorts),
   but keep one entry per `id`.
2. Update `updated`.
3. `python tools/validate.py`.
4. Commit and push. Pages serves it immediately; CoreFrame sees it after its 120 s cache expires.
