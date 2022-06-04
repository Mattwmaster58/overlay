import enum
import logging
import re
from pathlib import Path

__version__ = "0.0.1"

import click

from PIL import Image


# hack to get us enum support :), kinda repetitive :|
class Position(str, enum.Enum):
    TOP_LEFT = "tl"
    TOP = "t"
    TOP_RIGHT = "tr"
    RIGHT = "r"
    BOTTOM_RIGHT = "br"
    BOTTOM = "b"
    BOTTOM_LEFT = "bl"
    LEFT = 'l'
    CENTER = "c"


@click.command("overlay")
@click.option("--position", "-p", default="tl", type=click.Choice(Position))
@click.option("--relative-height", "-h", default=None, type=click.FloatRange(0.01, 1))
@click.option("--relative-width", "-w", default=0.2, type=click.FloatRange(0.01, 1))
@click.option("--input", "-i", default=Path("."),
              type=click.Path(dir_okay=True, exists=True, file_okay=False, writable=True, path_type=Path))
@click.option("--watermark", "-w", default=None,
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path))
@click.option("--verbose", "-v", help="enables debug logging", is_flag=True, default=False)
def main(position: Position, relative_height: float, relative_width: float, input: Path, watermark: Path,
         verbose: bool):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    logger = logging.getLogger()
    logger.info(f'overlay v{__version__}')

    if not (relative_width or relative_height):
        logger.error("please specify at least one of relative-width, relative-height")

    candidates = []
    SUPPORTED_FORMATS = re.compile("\.(bmp|ico|jpeg|jpg|png|tiff|webp)")
    for path in input.iterdir():
        logger.info(f"scanning input folder '{input.resolve().as_posix()}'")
        if path.is_file() and SUPPORTED_FORMATS.match(path.suffix):
            if path.stem == "template":
                if watermark is None:
                    watermark = path
            else:
                candidates.append(path)

    logger.debug(f"{len(candidates)} image candidates")
    logger.info(f"opening watermark {watermark.as_posix()}")
    watermark_img = Image.open(watermark)

    # we need to resize, then overlay for each image
    overlay_aspect_ratio = watermark_img.width / watermark_img.height
    for img_path in candidates:
        new_img_fname = img_path.with_stem(f"o_{img_path.stem}")
        if new_img_fname.exists():
            logger.debug(f"skipping {img_path.as_posix()} because {new_img_fname.as_posix()} exists")
            continue

        img = Image.load(img_path)

        if relative_width is None:
            overlay_width = overlay_aspect_ratio * (relative_height * img.height)
        else:
            overlay_width = relative_width * img.width

        if relative_height is None:
            overlay_height = overlay_aspect_ratio * (relative_width * img.width)
        else:
            overlay_height = relative_height * img.height

        resized_overlay = watermark_img.resize((
            int(overlay_width),
            int(overlay_height),
        ))

        if position in (Position.BOTTOM_LEFT, Position.TOP_LEFT, Position.LEFT):
            overlay_x = 0
        elif position in (Position.TOP, Position.CENTER, Position.BOTTOM):
            overlay_x = int(img.width / 2 - resized_overlay.width / 2)
        else:  # ie, position in (Position.RIGHT, Position.BOTTOM_RIGHT, Position.TOP_RIGHT):
            overlay_x = img.width - overlay_width

        if position in (Position.TOP_LEFT, Position.TOP, Position.TOP_RIGHT):
            overlay_y = 0
        elif position in (Position.LEFT, Position.CENTER, Position.RIGHT):
            overlay_y = int(img.height / 2 - resized_overlay.height / 2)
        else:  # ie, position in (Position.BOTTOM_LEFT, Position.BOTTOM, Position.BOTTOM_RIGHT):
            overlay_y = img.height - resized_overlay.height

        img.paste(resized_overlay, (overlay_x, overlay_y))
        img.save(new_img_fname)


if __name__ == '__main__':
    main()
