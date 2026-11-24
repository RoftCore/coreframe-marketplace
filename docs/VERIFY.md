# Review checklist

"Verified" here means one person read it and ran it. Nothing in this repository claims more than
that, and the README of every listed extension should say so.

## 1. The archive

- [ ] Downloads over `https://` and is a `.zip`.
- [ ] Opens cleanly; the folder that contains `extension.json` is the **only** wrapper, or there is
      no wrapper at all. Anything else installs flattened into the wrong place.
- [ ] No path traversal: no entry with an absolute path or a `..` segment.
- [ ] `extension.json` parses, its `id` matches the registry entry and it points at a `main.py`
      that defines `class Extension`.
- [ ] Reasonable size. A 40 MB extension that says it strips EXIF metadata is suspicious; ask.
- [ ] The release asset is **immutable**: tag or release URL, not a branch, not a raw file that can
      be replaced in place.

## 2. The code

- [ ] Read `main.py` and every file under `static/`. It should be legible; minified or obfuscated
      source is a rejection, not a style note.
- [ ] No network calls to hosts the extension does not need, and no telemetry.
- [ ] No reading outside its own `data_dir` beyond what its permission level allows.
- [ ] No `subprocess` at a level below `system`, no registry writes below `admin`.
- [ ] Anything it downloads later (models, media) is fetched from a documented source.
- [ ] Frontend: `script_scope` is `module` unless there is a reason; no inline `onclick` reaching for
      a module-scoped function.

## 3. The manifest

- [ ] `permissions.level` is the lowest level that actually works. Ask for `user_files` when its
      own `data_dir` would do and it is a rejection.
- [ ] `menu_items` and `widgets` actions exist in `main.py` as methods.
- [ ] `js_modules` / `css_modules` files exist and are declared with their real names.
- [ ] `version` in the manifest matches the version being published.

## 4. What the user sees

- [ ] Install it in a clean `DATA_DIR`, let it load, and open every widget and menu action.
- [ ] Check the console: no exceptions, no failed requests.
- [ ] Uninstall/disable and confirm nothing is left running (no orphan process).
- [ ] Confirm the description in the registry is accurate. A card promising something the extension
      does not do is a rejection even if the code is fine.

## 5. Recording the result

- [ ] Add or update the registry entry, bump `updated`, keep `versions[]` newest first.
- [ ] `python tools/validate.py` passes.
- [ ] Reply to the submission issue saying what was checked and what was found, so the next review
      has a precedent.

If something is wrong, say exactly what and what would fix it. A submission that is closed with
"not accepted" and no reason teaches the author nothing.
