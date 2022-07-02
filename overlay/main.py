import enum
import logging
import re
from pathlib import Path

__version__ = "0.0.1"

import click

from PIL import Image


# hack to get us enum support :), kinda repetitive :|
class Position(str, enum.Enum):
    TOP_LEFT = "top-left"
    TOP = "top"
    TOP_RIGHT = "top-right"
    RIGHT = "right"
    BOTTOM_RIGHT = "bottom-right"
    BOTTOM = "bottom"
    BOTTOM_LEFT = "bottom-left"
    LEFT = 'left'
    CENTER = "center"


@click.command("overlay")
@click.option("--position", "-p", default="top-left", type=click.Choice(Position))
@click.option("--relative-height", "-h", default=None, type=click.FloatRange(0.01, 1),
              help="width as a decimal relative to the base image's width")
@click.option("--relative-width", "-w", default=0.2, type=click.FloatRange(0.01, 1),
              help="width as a decimal relative to the base image's height")
@click.option("--input", "-i", default=Path("."),
              type=click.Path(dir_okay=True, exists=True, file_okay=False, writable=True, path_type=Path),
              help="folder to scan for images to overlay. If unspecified, defaults to current working directory")
@click.option("--overlay", "-o", default=None,
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path),
              help="specifies the image to overlay on the base images. If unspecified, the input folder will be scanned "
                   "for a supported image format with the name \"overlay\"")
@click.option("--in-place", default=False, is_flag=True, help="perform the overlay in place")
@click.option("--verbose", "-v", help="enables debug logging", is_flag=True, default=False)
def main(position: Position, relative_height: float, relative_width: float, input: Path, overlay: Path,
         verbose: bool, in_place: bool):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    logger = logging.getLogger()
    logger.info(f'overlay v{__version__}')

    if not (relative_width or relative_height):
        logger.error("please specify at least one of relative-width, relative-height")

    candidates = []
    SUPPORTED_FORMATS = re.compile("\.(bmp|ico|jpeg|jpg|png|tiff|webp)")
    logger.info(f"scanning input folder '{input.resolve().as_posix()}'")
    for path in input.iterdir():
        if path.is_file() and SUPPORTED_FORMATS.match(path.suffix):
            if path.stem == "overlay":
                if overlay is None:
                    overlay = path
            else:
                candidates.append(path)

    if overlay is None:
        logger.error("overlay image could not be found from input directory")
        exit(-1)
    elif not overlay.exists():
        logger.error(f"specified overlay image '{overlay.absolute().as_posix()}' does not appear to exist")
        exit(-1)

    logger.debug(f"{len(candidates)} image candidates")
    logger.info(f"opening overlay image: {overlay.as_posix()}")
    watermark_img = Image.open(overlay)
    total_transformed = 0
    # we need to resize, then overlay for each image
    overlay_aspect_ratio = watermark_img.width / watermark_img.height
    for img_path in candidates:
        if not in_place:
            new_img_fname = img_path.with_name(f"o_{img_path.stem}{img_path.suffix}")
            if new_img_fname.exists():
                logger.debug(f"skipping {img_path.as_posix()} because {new_img_fname.as_posix()} exists")
                continue
        else:
            new_img_fname = img_path

        img = Image.open(img_path).convert("RGBA")

        if relative_width is None:
            overlay_width = overlay_aspect_ratio * (relative_height * img.height)
        else:
            overlay_width = relative_width * img.width

        if relative_height is None:
            overlay_height = (relative_width * img.width) / overlay_aspect_ratio
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
            overlay_x = img.width - resized_overlay.width

        if position in (Position.TOP_LEFT, Position.TOP, Position.TOP_RIGHT):
            overlay_y = 0
        elif position in (Position.LEFT, Position.CENTER, Position.RIGHT):
            overlay_y = int(img.height / 2 - resized_overlay.height / 2)
        else:  # ie, position in (Position.BOTTOM_LEFT, Position.BOTTOM, Position.BOTTOM_RIGHT):
            overlay_y = img.height - resized_overlay.height

        img.alpha_composite(resized_overlay, (overlay_x, overlay_y))
        img.save(new_img_fname)
        logger.debug(f"saving transformed image: {new_img_fname.as_posix()}")
        total_transformed += 1
    logger.info(f"{total_transformed} images overlayed")


if __name__ == '__main__':
    main()
