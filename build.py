#!/usr/bin/env python3
"""
Builds the Maybe Panic repository for Kodi 21+.

    python build.py [--uno PATH]

Zips every add-on in addons/, plus Plex Uno from the git checkout at PATH (its committed HEAD, not
the working tree), into zips/<id>/<id>-<version>.zip, then rewrites zips/addons.xml and its .md5
from every zip there - so older versions stay listed, and installable, until their zips are deleted.

A version that's already published isn't rebuilt: if the add-on changed, its version has to be
bumped first, or Kodi would never offer the change.
"""
import argparse
import hashlib
import io
import os
import re
import subprocess
import sys
import tarfile
import zipfile
from xml.etree import ElementTree

ROOT = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.join(ROOT, 'addons')
ZIPS = os.path.join(ROOT, 'zips')

# never shipped, wherever they turn up
SKIP_NAMES = {'.git', '.gitignore', '.gitattributes', '.github', '.idea', '.vscode', '__pycache__',
              '.pytest_cache', 'Thumbs.db', '.DS_Store'}
SKIP_SUFFIXES = ('.pyc', '.pyo')
# Plex Uno's development-only files
UNO_SKIP_TOP = {'tests', 'docs', 'pytest.ini'}


def shipped(rel_path):
    parts = rel_path.replace('\\', '/').split('/')
    return not any(p in SKIP_NAMES for p in parts) and not rel_path.endswith(SKIP_SUFFIXES)


def folder_files(folder):
    """(path in the add-on, bytes) for an add-on folder in addons/"""
    for parent, dirs, names in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_NAMES)
        for name in sorted(names):
            full = os.path.join(parent, name)
            rel = os.path.relpath(full, folder).replace('\\', '/')
            if shipped(rel):
                with open(full, 'rb') as f:
                    yield rel, f.read()


def git_files(checkout):
    """(path in the add-on, bytes) for a git checkout's HEAD"""
    dirty = subprocess.run(['git', '-C', checkout, 'status', '--porcelain', '--untracked-files=no'],
                           capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        print('  note: {} has uncommitted changes; building its HEAD without them'.format(checkout))
    head = subprocess.run(['git', '-C', checkout, 'log', '-1', '--format=%h %s'],
                          capture_output=True, text=True, check=True).stdout.strip()
    print('  from {}'.format(head))
    tar = subprocess.run(['git', '-C', checkout, 'archive', '--format=tar', 'HEAD'],
                         capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        for member in t.getmembers():
            if not member.isfile():
                continue
            if member.name.split('/')[0] in UNO_SKIP_TOP or not shipped(member.name):
                continue
            yield member.name, t.extractfile(member).read()


def addon_info(addon_xml):
    root = ElementTree.fromstring(addon_xml)
    return root.get('id'), root.get('version')


def build(files):
    files = sorted(files)
    addon_xml = dict(files).get('addon.xml')
    if addon_xml is None:
        raise SystemExit('  no addon.xml')
    addon_id, version = addon_info(addon_xml)
    target = os.path.join(ZIPS, addon_id, '{}-{}.zip'.format(addon_id, version))

    if os.path.exists(target):
        with zipfile.ZipFile(target) as z:
            published = {i.filename: i.CRC for i in z.infolist() if not i.is_dir()}
        current = {'{}/{}'.format(addon_id, rel): zipfile.crc32(data) for rel, data in files}
        if published == current:
            print('  {} {}: unchanged'.format(addon_id, version))
            return
        raise SystemExit('  {} {} is already published with different contents: bump its version in '
                         'addon.xml first'.format(addon_id, version))

    os.makedirs(os.path.dirname(target), exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel, data in files:
            z.writestr('{}/{}'.format(addon_id, rel), data)
    print('  {} {}: built ({} files)'.format(addon_id, version, len(files)))


def version_key(version):
    # good enough to put the newest of one add-on's versions first in addons.xml; Kodi sorts for itself
    return [(0, int(p), '') if p.isdigit() else (1, 0, p) for p in re.split(r'[.\-~+]', version)]


def write_index():
    """addons.xml and .md5 from every zip in zips/, plus each add-on's metadata beside its zips"""
    entries = []
    for addon_id in sorted(os.listdir(ZIPS)):
        folder = os.path.join(ZIPS, addon_id)
        if not os.path.isdir(folder):
            continue
        versions = []
        for name in os.listdir(folder):
            if not name.endswith('.zip'):
                continue
            with zipfile.ZipFile(os.path.join(folder, name)) as z:
                xml = z.read('{}/addon.xml'.format(addon_id)).decode('utf-8')
            versions.append((addon_info(xml.encode('utf-8'))[1], name, xml))
        versions.sort(key=lambda v: version_key(v[0]), reverse=True)

        # Kodi shows the newest version's icon and fanart from here, before anything is installed
        newest = os.path.join(folder, versions[0][1])
        with zipfile.ZipFile(newest) as z:
            assets = ['addon.xml'] + [el.text for el in ElementTree.fromstring(
                z.read('{}/addon.xml'.format(addon_id))).iter() if el.tag in ('icon', 'fanart') and el.text]
            for asset in assets:
                data = z.read('{}/{}'.format(addon_id, asset))
                out = os.path.join(folder, asset)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, 'wb') as f:
                    f.write(data)

        for _, _, xml in versions:
            xml = re.sub(r'^\s*<\?xml[^>]*\?>\s*', '', xml).replace('\r\n', '\n').strip()
            entries.append(xml)

    text = '<?xml version="1.0" encoding="UTF-8"?>\n<addons>\n' + '\n\n'.join(entries) + '\n</addons>\n'
    data = text.encode('utf-8')
    with open(os.path.join(ZIPS, 'addons.xml'), 'wb') as f:
        f.write(data)
    with open(os.path.join(ZIPS, 'addons.xml.md5'), 'wb') as f:
        f.write(hashlib.md5(data).hexdigest().encode('ascii'))
    print('addons.xml: {} entries'.format(len(entries)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--uno', metavar='PATH', help="Plex Uno's git checkout (script.plexmod-uno)")
    args = parser.parse_args()

    os.makedirs(ZIPS, exist_ok=True)
    for name in sorted(os.listdir(ADDONS)):
        folder = os.path.join(ADDONS, name)
        if os.path.isfile(os.path.join(folder, 'addon.xml')):
            print(name)
            build(folder_files(folder))
    if args.uno:
        print(os.path.basename(os.path.normpath(args.uno)))
        build(git_files(args.uno))
    write_index()


if __name__ == '__main__':
    sys.exit(main())
