# Changelog

## Kagetsu Tohya Release - 2026-11-08

- Publish the tested runtime as `KagetsuTohyaVita-Release.vpk`, with title ID `KAGET0001` and internal version `01.01` for updating the test bubble.
- Retain the test build's runtime code and data/save paths. The project owner reported no issues during initial Vita testing; a complete playthrough remains outstanding.
- Add a local tool to package all three games into separate ux0 installation ZIPs containing their VPK and locally supplied game data.

## Kagetsu Tohya test build - 2026-11-08

- Added a separate `kagetsu-tohya` build profile, `KAGET0001` title ID, and `ux0:data/kagetsu_tohya/` data/save paths.
- Load the supplied English PC NScripter script, NSA archives, font, and OGG CD tracks directly.
- Carry over native controls, English word wrapping, checked saves/timestamps, and the compact twenty-slot save menu.
- Fit the main and compact dialogue windows to the screen with four text sizes (20, 22, 24, 26 pixels) and page-overflow pauses.
- Recognize CD fade commands through the native music fade handler.
- Reserve and initialize a trailing script terminator, fixing an out-of-bounds scan exposed by the LF-only Kagetsu script.
- Add temporary title-screen LiveArea artwork and read-only production reader/layout checks. Vita gameplay testing remains outstanding.

## Plus Disc Release - 2026-11-08

- Fit all twenty save/load slots and their heading within the screen using a scoped, smaller menu font.
- Added the supplied Plus Disc icon, background, and logo to a dedicated LiveArea asset set.
- Deliver the application as `TsukihimePlusDiscVita-Release.vpk`, with internal app version 01.01 and title ID TSUPL0001.

## 1.06 - 2026-10-27

- Repurposed the Vita L trigger to cycle original text size and three larger dialogue sizes (17, 19, 21, and 23 script pixels).
- Apply size changes at the next text page and show the selected size in the bottom margin.
- Adjust line width and page height for enlarged text, adding input pauses before a page would overflow.
- Keep choice buttons and mixed-size backlog pages at the original size.
- Keep the selected size for the current app session; launching the app starts at the original size.

## 1.05 - 2026-10-27

- Wrap single-byte English dialogue at spaces so words that fit on a line are not split at the right edge.
- Preserve scripted line breaks, click waits, page changes, and indentation; keep character wrapping for words longer than a full line.
- Record automatic word breaks for consistent backlog and saved-page redraw.
- English word wrapping was confirmed working on a Vita.

## 1.04 - 2026-10-26

- Added the selected bubble icon, LiveArea background, and launch-panel artwork at the required Vita dimensions.
- Included the working save-menu and timestamp fixes from 1.03.
- Prepared installation instructions, build documentation, and source release materials.

## 1.03 - 2026-10-26

- Replaced unsupported Japanese save-menu glyphs with ASCII labels and confirmation buttons.
- Added a valid display timestamp fallback when file and clock timestamps are unusable.
- Checked save writes, flushes, and closes, and displayed a message on failure.
- Saving and gameplay were confirmed working on a Vita.

## 1.02 - 2026-10-26

- Corrected the executable's filesystem identity for external game-data access.
- Made startup logging optional and added a fallback log location.

## 1.01 - 2026-10-26

- Enabled single-byte English string support.
- Fixed mixed SAR/NSA archive loading and added startup diagnostics.

## 1.00 - 2026-10-26

- Initial native Vita build based on ONScripter-JH.
