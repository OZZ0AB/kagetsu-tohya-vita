#!/usr/bin/env python3
"""Make temporary Kagetsu Tohya test artwork from a local title image."""
import argparse
from pathlib import Path
from PIL import Image, ImageOps
from prepare_livearea import save_indexed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title", type=Path)
    parser.add_argument("--output", type=Path, default=Path("assets/kagetsu-tohya-livearea"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with Image.open(args.title) as source:
        source = source.convert("RGB")
        if source.size != (640, 480):
            raise ValueError("Expected the 640x480 English title image")
        # Exclude the PC menu and copyright footer from the launch resources.
        art = source.crop((0, 0, 640, 398))
        icon = source.crop((124, 8, 516, 398))
        save_indexed(ImageOps.fit(icon, (128, 128), Image.Resampling.LANCZOS),
                     args.output / "icon0.png")
        for name, size in (("bg.png", (840, 500)), ("startup.png", (280, 158))):
            panel = Image.new("RGB", size, (218, 167, 116))
            fitted = ImageOps.contain(art, size, Image.Resampling.LANCZOS)
            panel.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
            save_indexed(panel, args.output / name)
    (args.output / "template.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<livearea style="a5" format-ver="01.00" content-rev="1">\n'
        '  <livearea-background><image>bg.png</image></livearea-background>\n'
        '  <gate><startup-image>startup.png</startup-image></gate>\n'
        '</livearea>\n')


if __name__ == "__main__":
    main()
