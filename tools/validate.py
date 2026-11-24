#!/usr/bin/env python3
"""Validate registry.json before it reaches CoreFrame.

    python tools/validate.py

Exit 1 on the first class of problem, listing every offender: CoreFrame reads
this file from a URL with no schema validation, so a typo here is a broken
marketplace for every user.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / 'registry.json'
SCHEMA = ROOT / 'registry.schema.json'

ID_RE = re.compile(r'^[a-z0-9][a-z0-9_]*$')
VERSION_RE = re.compile(r'^\d+\.\d+(\.\d+)?$')

errors = []


def fail(message):
    errors.append(message)


def semver(value):
    return tuple(int(part) for part in str(value).split('.'))


def main():
    try:
        data = json.loads(REGISTRY.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        print(f'registry.json is not valid JSON: {exc}')
        return 1

    for key in ('$schema', 'publisher', 'extensions'):
        if key not in data:
            fail(f'missing root key: {key}')
    if not isinstance(data.get('extensions'), list) or not data['extensions']:
        fail('extensions must be a non-empty array')
        report()
        return 1

    seen = set()
    for index, ext in enumerate(data['extensions']):
        where = f'extensions[{index}]'
        if not isinstance(ext, dict):
            fail(f'{where}: not an object')
            continue
        ext_id = ext.get('id')
        if not ext_id or not ID_RE.match(str(ext_id)):
            fail(f'{where}: id must match {ID_RE.pattern} (got {ext_id!r})')
        elif ext_id in seen:
            fail(f'{where}: duplicate id {ext_id!r}')
        else:
            seen.add(ext_id)
            where = f'{ext_id}'
        for key in ('name', 'version', 'author', 'description', 'category', 'download_url'):
            if not ext.get(key):
                fail(f'{where}: missing {key}')
        if ext.get('version') and not VERSION_RE.match(str(ext['version'])):
            fail(f'{where}: version {ext["version"]!r} is not N.N or N.N.N')

        versions = ext.get('versions')
        if not isinstance(versions, list) or not versions:
            fail(f'{where}: versions[] must be a non-empty array')
            continue
        seen_versions = set()
        for v_index, item in enumerate(versions):
            v_where = f'{where} versions[{v_index}]'
            version = item.get('version')
            url = item.get('download_url')
            if not version or not VERSION_RE.match(str(version)):
                fail(f'{v_where}: version {version!r} is not N.N or N.N.N')
            elif version in seen_versions:
                fail(f'{v_where}: duplicate version {version!r}')
            else:
                seen_versions.add(version)
            if not url or not str(url).startswith('https://') or not str(url).endswith('.zip'):
                fail(f'{v_where}: download_url must be an https .zip (got {url!r})')
        if versions and str(versions[0].get('version')) != str(ext.get('version')):
            fail(f'{where}: flat version {ext.get("version")!r} is not versions[0] '
                 f'{versions[0].get("version")!r} (older CoreFrame builds read the flat pair)')
        if versions and ext.get('download_url') != versions[0].get('download_url'):
            fail(f'{where}: flat download_url differs from versions[0].download_url')
        listed = [semver(v.get('version')) for v in versions if VERSION_RE.match(str(v.get('version')))]
        if listed != sorted(listed, reverse=True):
            fail(f'{where}: versions[] must be newest first (got {[v.get("version") for v in versions]})')

    updated = data.get('updated')
    if updated and not re.match(r'^\d{4}-\d{2}-\d{2}$', str(updated)):
        fail(f'updated must be YYYY-MM-DD (got {updated!r})')

    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    if schema.get('$id') != data.get('$schema'):
        fail(f'$schema points at {data.get("$schema")!r} but registry.schema.json declares '
             f'{schema.get("$id")!r}')

    return report()


def report():
    if not errors:
        data = json.loads(REGISTRY.read_text(encoding='utf-8'))
        total = sum(len(e.get('versions') or []) for e in data['extensions'])
        print(f'registry.json OK: {len(data["extensions"])} extensions, {total} versions')
        return 0
    print(f'{len(errors)} problem(s):')
    for message in errors:
        print(f'  - {message}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
