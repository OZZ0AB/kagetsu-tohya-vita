#!/usr/bin/env python3
"""Package locally supplied data and native VPKs into separate ux0-ready ZIPs."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import zipfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def vpk_identity(path):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip():
            raise ValueError('Invalid VPK: ' + path.name)
        data = archive.read('sce_sys/param.sfo')
    _, _, keys, values, count = struct.unpack_from('<5I', data)
    fields = {}
    for i in range(count):
        key, _, size, _, offset = struct.unpack_from('<HHIII', data, 20 + i * 16)
        name = data[keys + key:data.index(b'\0', keys + key)].decode()
        if name in ('TITLE_ID', 'APP_VER', 'TITLE'):
            fields[name] = data[values + offset:values + offset + size].rstrip(b'\0').decode()
    return fields


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', choices=('all', 'tsukihime', 'plus-disc', 'kagetsu-tohya'), default='all')
    parser.add_argument('--tsukihime', type=Path, default=Path('Tsukihime/Game'))
    parser.add_argument('--plus-disc', type=Path, default=Path('build/plus-disc-data/game'))
    parser.add_argument('--kagetsu-tohya', type=Path, default=Path('Kagetsu Tohya/Game'))
    parser.add_argument('--output', type=Path, default=Path('build/ux0-ready'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if root / 'build' not in output.parents:
        raise ValueError('Choose an output folder inside project-local build/')
    output.mkdir(parents=True, exist_ok=True)
    games = [
        ('tsukihime', 'Tsukihime', 'TSUKI0001', '01.06', 'TsukihimeVita-01.06.vpk',
         'TsukihimeVita-ux0-ready.zip', args.tsukihime,
         ['nscript.dat', 'arc.sar', 'arc.nsa', 'arc1.nsa', 'default.ttf'] +
         [f'CD/track{i:02}.ogg' for i in range(1, 11)]),
        ('plus-disc', 'Tsukihime Plus Disc', 'TSUPL0001', '01.01', 'TsukihimePlusDiscVita-Release.vpk',
         'TsukihimePlusDiscVita-ux0-ready.zip', args.plus_disc, None),
        ('kagetsu-tohya', 'Kagetsu Tohya', 'KAGET0001', '01.01', 'KagetsuTohyaVita-Release.vpk',
         'KagetsuTohyaVita-ux0-ready.zip', args.kagetsu_tohya,
         ['nscript.dat', 'arc.nsa', 'arc1.nsa', 'default.ttf'] +
         [f'CD/track{i:02}.ogg' for i in range(2, 19)]),
    ]
    for key, title, title_id, version, vpk_name, zip_name, source, names in games:
        if args.game not in ('all', key):
            continue
        final = output / zip_name
        if final.exists():
            raise ValueError('Existing bundle preserved: ' + str(final))
        source = source.resolve()
        vpk = root / 'build' / vpk_name
        identity = vpk_identity(vpk)
        if identity['TITLE_ID'] != title_id or identity['APP_VER'] != version:
            raise ValueError('Unexpected VPK identity for ' + title)
        data_dir = {'tsukihime': 'tsukihime', 'plus-disc': 'tsukihime_plus_disc',
                    'kagetsu-tohya': 'kagetsu_tohya'}[key]
        if names is None:
            manifest = json.loads((source / 'plus-disc-data.json').read_text())
            script = bytes(c ^ 0x84 for c in (source / 'nscript.dat').read_bytes())
            if hashlib.sha256(script).hexdigest() != manifest['script_sha256']:
                raise ValueError('Plus Disc script hash mismatch')
            names = ['nscript.dat', 'default.ttf', 'plus-disc-data.json']
            for item in manifest['media'].values():
                relative = PurePosixPath(item['path'])
                if relative.is_absolute() or '..' in relative.parts or relative.parts[0] != 'media':
                    raise ValueError('Invalid media path')
                media = source / relative
                if media.stat().st_size != item['bytes'] or digest(media) != item['sha256']:
                    raise ValueError('Plus Disc media hash mismatch')
                names.append(str(relative))
        entries = {vpk.name: vpk}
        for name in sorted(set(names)):
            file = source / name
            if file.is_symlink() or not file.is_file() or not file.stat().st_size:
                raise ValueError('Missing or unexpected game file: ' + str(file))
            entries[f'data/{data_dir}/game/{name}'] = file
        notes_name = f'Install-{data_dir}.txt'
        notes = (f'{title} Vita installation\n\n'
                 '1. Extract this ZIP at the ROOT of ux0: using VitaShell or your computer.\n'
                 f'2. Install {vpk.name} with VitaShell.\n'
                 f'3. Launch {title}.\n\n'
                 f'Game files: ux0:data/{data_dir}/game/\n'
                 f'Saves: ux0:data/{data_dir}/save/\n'
                 f'Title ID: {title_id}; app version: {version}\n\n'
                 'Circle confirms/advances. Triangle opens the game menu.\n'
                 'L cycles four dialogue sizes; changes apply at the next page.\n\n'
                 'This local bundle contains data from your supplied game copy.\n'
                 'It does not contain or replace save files. When updating, preserve\n'
                 'the existing save folder and merge the data folders.\n')
        temporary = output / (zip_name + '.partial')
        if temporary.exists():
            raise ValueError('Interrupted bundle found; rename it before retrying: ' + str(temporary))
        inventory = []
        with zipfile.ZipFile(temporary, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, path in entries.items():
                archive.write(path, name)
                inventory.append({'path': name, 'bytes': path.stat().st_size, 'sha256': digest(path)})
            archive.writestr(notes_name, notes)
            inventory.append({'path': notes_name, 'bytes': len(notes.encode()),
                              'sha256': hashlib.sha256(notes.encode()).hexdigest()})
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() or len(archive.namelist()) != len(inventory):
                raise ValueError('Bundle integrity check failed')
            for item in inventory:
                h = hashlib.sha256()
                with archive.open(item['path']) as file:
                    for block in iter(lambda: file.read(1024 * 1024), b''):
                        h.update(block)
                if h.hexdigest() != item['sha256']:
                    raise ValueError('Bundle payload mismatch: ' + item['path'])
        temporary.rename(final)
        result = {'name': zip_name, 'game': title, 'title_id': title_id,
                  'app_version': version, 'bytes': final.stat().st_size,
                  'sha256': digest(final), 'entries': inventory}
        (output / (zip_name + '.json')).write_text(json.dumps(result, indent=2) + '\n')
        print(f'{zip_name}: {final.stat().st_size} bytes, {len(inventory)} checked files', flush=True)
    manifests = [json.loads(path.read_text()) for path in sorted(output.glob('*-ux0-ready.zip.json'))]
    (output / 'SHA256SUMS').write_text(''.join(f"{m['sha256']}  {m['name']}\n" for m in manifests))


if __name__ == '__main__':
    main()
