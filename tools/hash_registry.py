#!/usr/bin/env python3
"""Pin every published release to its bytes.

    python tools/hash_registry.py --write    # download each zip, record sha256 + size
    python tools/hash_registry.py --check    # CI: fail if a release changed under us

The registry is hand-edited and reviewed, but a reviewer cannot see a release
asset being replaced in place after the review. These hashes are what CoreFrame
compares before installing, so `--check` turning red means something is wrong
with an asset, not with this repository.
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / 'registry.json'
CHUNK = 1 << 16


def download(url, timeout=60):
    """Return (sha256, size) for a release asset."""
    digest = hashlib.sha256()
    size = 0
    request = urllib.request.Request(url, headers={'User-Agent': 'coreframe-marketplace-hash'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def entries(registry):
    for extension in registry['extensions']:
        for version in extension.get('versions') or []:
            yield extension, version


def check(registry, update):
    failures = []
    changed = 0
    for extension, version in entries(registry):
        url = version.get('download_url')
        label = f"{extension['id']} {version.get('version')}"
        try:
            sha, size = download(url)
        except Exception as exc:
            failures.append(f'{label}: download failed ({exc})')
            continue
        recorded = str(version.get('sha256') or '').lower()
        if update:
            version['sha256'] = sha
            version['size'] = size
            changed += 1
            print(f'{label}: {sha[:16]}… {size} B')
            continue
        if not recorded:
            failures.append(f'{label}: no sha256 in the registry (run --write)')
        elif recorded != sha:
            failures.append(f'{label}: registry says {recorded[:16]}… but the asset is {sha[:16]}…')
        if version.get('size') and int(version['size']) != size:
            failures.append(f'{label}: registry says {version["size"]} B but the asset is {size} B')
    return failures, changed


def main():
    parser = argparse.ArgumentParser(description='Hash and verify every release in registry.json.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write', action='store_true', help='record sha256/size in registry.json')
    group.add_argument('--check', action='store_true', help='verify the recorded hashes')
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    failures, changed = check(registry, update=args.write)

    if args.write:
        REGISTRY.write_text(json.dumps(registry, indent=2) + '\n', encoding='utf-8')
        print(f'recorded {changed} hash(es) in registry.json')
        for failure in failures:
            print(f'  ! {failure}')
        return 1 if failures else 0

    if failures:
        print(f'{len(failures)} problem(s):')
        for failure in failures:
            print(f'  - {failure}')
        return 1
    total = sum(1 for _ in entries(registry))
    print(f'registry hashes OK: {total} release(s) match their recorded sha256')
    return 0


if __name__ == '__main__':
    sys.exit(main())
