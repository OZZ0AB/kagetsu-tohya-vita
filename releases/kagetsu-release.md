# Kagetsu Tohya Vita Release

A native PS Vita port built with VitaSDK and ONScripter-JH. It reads compatible English PC NScripter files directly; no script conversion, VNDS player, Windows executable, or emulator is required.

## Included

- Native Vita controls, touch input, auto mode, skip, and text history.
- English word wrapping and page-overflow pauses.
- L-trigger dialogue sizes of 20, 22, 24, and 26 pixels, applied on the next page.
- Main and compact dialogue windows fitted to the screen.
- Twenty English save/load slots with readable timestamps and checked writes.
- The game's internal day/progression save slot.
- Dedicated bubble and LiveArea artwork based on the English title screen.
- Separate application and data/save folders from Tsukihime and Plus Disc.

## Installation

1. Install `KagetsuTohyaVita-Release.vpk` with VitaShell. Install over the existing Kagetsu Tohya test bubble when updating.
2. Copy `nscript.dat`, `arc.nsa`, `arc1.nsa`, `default.ttf`, and the entire `CD` folder from your compatible English PC game into `ux0:data/kagetsu_tohya/game/`.
3. Launch **Kagetsu Tohya**. **Circle** confirms or advances; **Triangle** opens the menu, including save/load/history.

Use the active `nscript.dat` from the English PC folder. Copy files directly into `game/`, without another nested `Game/` folder. The supplied edition has tracks `track02.ogg` through `track18.ogg`.

Existing test data and saves use the same paths. The title ID is `KAGET0001`, internal app version `01.01`. Saves are in `ux0:data/kagetsu_tohya/save/`.

## Release files

- `KagetsuTohyaVita-Release.vpk`: installable native runtime.
- `KagetsuTohyaVita-Release-source.tar.gz`: corresponding source, build files, checks, and documentation.
- `SHA256SUMS`: VPK and source checksums.

The project owner reported no issues during initial Vita testing. The native build and host script/archive/layout/save checks passed. A complete playthrough has not been performed. This release retains the tested runtime code and updates the application name/version for publication.

See the [README](https://github.com/OZZ0AB/kagetsu-tohya-vita#readme) for full instructions, controls, troubleshooting, credits, and licensing. Game files, translation, font, and music come from your own compatible copy. The included local bundle tool can package those files into a ux0-ready ZIP on your computer.
