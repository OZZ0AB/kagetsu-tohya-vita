#!/usr/bin/env python3
"""Export Kagetsu Tohya's native runtime and source for public release."""
import argparse
import json
from pathlib import Path
import re
import shutil
import tarfile
from prepare_github_release import copy_tree, sha256
from prepare_ux0_bundles import vpk_identity

REPOSITORY = 'kagetsu-tohya-vita'
VERSION = '01.01'
TAG = 'v1.01'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('publish/kagetsu-release'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if root / 'publish' not in output.parents or output.exists():
        raise ValueError('Choose a new folder under publish/; prior exports are preserved')
    vpk = root / 'build/KagetsuTohyaVita-Release.vpk'
    identity = vpk_identity(vpk)
    if (identity['TITLE_ID'], identity['TITLE'], identity['APP_VER']) != ('KAGET0001', 'Kagetsu Tohya', VERSION):
        raise ValueError('Unexpected release VPK identity')
    repository = output / REPOSITORY
    assets = output / 'release-assets'
    repository.mkdir(parents=True)
    assets.mkdir()
    for name in ('.gitignore', 'CMakeLists.txt', 'LICENSE', 'THIRD_PARTY.md', 'CHANGELOG.md'):
        shutil.copy2(root / name, repository / name)
    for name in ('assets', 'diagnostics', 'docs', 'scripts', 'engine/license', 'engine/src/onsjh', 'engine/src/common'):
        copy_tree(root / name, repository / name)
    shutil.copy2(root / 'engine/UPSTREAM.md', repository / 'engine/UPSTREAM.md')
    (repository / 'releases').mkdir()
    shutil.copy2(root / 'releases/kagetsu-release.md', repository / 'releases/kagetsu-release.md')
    cmake = (repository / 'CMakeLists.txt').read_text()
    old = 'set(TSUKIHIME_EDITION "original" CACHE STRING'
    if cmake.count(old) != 1:
        raise ValueError('Cannot identify the default build profile')
    (repository / 'CMakeLists.txt').write_text(cmake.replace(old, 'set(TSUKIHIME_EDITION "kagetsu-tohya" CACHE STRING'))
    readme = (root / 'docs/KAGETSU_TOHYA.md').read_text()
    readme = readme.replace('[BUILDING.md](BUILDING.md)', '[BUILDING.md](docs/BUILDING.md)')
    readme = readme.replace('[THIRD_PARTY.md](../THIRD_PARTY.md)', '[THIRD_PARTY.md](THIRD_PARTY.md)')
    download = ('![Kagetsu Tohya LiveArea artwork](assets/kagetsu-tohya-livearea/bg.png)\n\n'
                '## Download\n\n'
                'Download [KagetsuTohyaVita-Release.vpk](https://github.com/OZZ0AB/kagetsu-tohya-vita/releases/latest/download/KagetsuTohyaVita-Release.vpk) from the [latest release](https://github.com/OZZ0AB/kagetsu-tohya-vita/releases/latest). Corresponding source and checksums accompany the VPK. Supply the game data from your own compatible English PC copy.\n\n')
    readme = readme.replace('## Install\n', download + '## Install\n', 1)
    readme = readme.replace('## Build\n', '## Build\n\nThis repository selects `kagetsu-tohya` by default. Shared sources retain the original Tsukihime and Plus Disc build profiles.\n', 1)
    readme += ('\n## Related ports\n\n'
               '- [Tsukihime Vita](https://github.com/OZZ0AB/tsukihime-vita)\n'
               '- [Tsukihime Plus Disc Vita](https://github.com/OZZ0AB/tsukihime-plus-disc-vita)\n')
    (repository / 'README.md').write_text(readme)
    with (repository / 'THIRD_PARTY.md').open('a') as notices:
        notices.write('\n## Kagetsu Tohya\n\n'
                      'Kagetsu Tohya and its artwork are TYPE-MOON works. The English data tested here credits Lunacy and the original translation contributors, chaoskaiser72 for the unofficial 0.5.3 compatibility update, and Forte, Quizerno, and Fbates for the 2022 revision. Those game, translation, font, and music files are supplied locally by the player. The LiveArea art is resized from the English title image; its original rights remain separate from the runtime license.\n\n'
                      'The native Kagetsu build profile, layout helpers, startup checks, documentation, and packaging scripts accompany the shared runtime changes under GPL-2.0-or-later. The Plus Disc adaptation in these shared sources is documented separately in docs/PLUS_DISC.md.\n')
    forbidden = {'.nsa', '.sar', '.xp3', '.ogg', '.wav', '.ttf', '.exe', '.dll', '.vpk', '.ks', '.tjs', '.pyc', '.zip'}
    private = {'.git', '.aws', '.codex', '.agents', '.vitasdk', 'build', 'tools', 'Tsukihime', 'Tsukihime Plus Disc', 'Kagetsu Tohya', '__pycache__'}
    emoji = re.compile('[\U0001F000-\U0001FAFF\u2600-\u27BF]')
    for path in repository.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(repository)
        if path.suffix.lower() in forbidden or path.name in {'nscript.dat', 'plus-disc-data.json'} or private.intersection(relative.parts):
            raise ValueError('Unexpected private/game file in source: ' + str(relative))
        if path.suffix == '.md':
            text = path.read_text()
            if emoji.search(text) or '/home/bashar/' in text or '/media/bashar/' in text:
                raise ValueError('Private path or emoji in public documentation: ' + str(relative))
    shutil.copy2(vpk, assets / vpk.name)
    source = assets / 'KagetsuTohyaVita-Release-source.tar.gz'
    with tarfile.open(source, 'w:gz') as archive:
        archive.add(repository, arcname='KagetsuTohyaVita-Release-source')
    files = (assets / vpk.name, source)
    (assets / 'SHA256SUMS').write_text(''.join(f'{sha256(path)}  {path.name}\n' for path in files))
    manifest = {'repository_name': REPOSITORY, 'release_tag': TAG, 'app_version': VERSION,
                'title_id': 'KAGET0001', 'upstream_commit': '01955d7c1a4ecdff4245aa6e3fc08fd64625e4a9',
                'source_files': sum(p.is_file() for p in repository.rglob('*')),
                'release_assets': [{'name': p.name, 'bytes': p.stat().st_size, 'sha256': sha256(p)} for p in files]}
    (output / 'release-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
