from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError as exc:
    missing = exc.name or "dependency"
    raise SystemExit(
        f"Missing Python package: {missing}\n"
        "Install dependencies with: pip install -r requirements.txt"
    ) from exc


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_BASE_DIR = ROOT_DIR / "base"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "background_removed"


def output_is_current(source_path: Path, output_path: Path) -> bool:
    if not output_path.exists():
        return False

    return output_path.stat().st_mtime >= source_path.stat().st_mtime


def color_distance(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
    return max(abs(left[index] - right[index]) for index in range(3))


def estimate_background_color(image: Image.Image) -> tuple[int, int, int]:
    width, height = image.size
    pixels = image.load()
    corners = [
        pixels[0, 0][:3],
        pixels[width - 1, 0][:3],
        pixels[0, height - 1][:3],
        pixels[width - 1, height - 1][:3],
    ]
    return tuple(round(sum(color[index] for color in corners) / len(corners)) for index in range(3))


def build_background_mask(image: Image.Image, tolerance: int) -> Image.Image:
    width, height = image.size
    pixels = image.load()
    background = estimate_background_color(image)
    mask = Image.new("L", image.size, 0)
    mask_pixels = mask.load()
    queue: deque[tuple[int, int]] = deque()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if mask_pixels[x, y]:
            continue

        if color_distance(pixels[x, y][:3], background) > tolerance:
            continue

        mask_pixels[x, y] = 255

        if x > 0:
            queue.append((x - 1, y))
        if x < width - 1:
            queue.append((x + 1, y))
        if y > 0:
            queue.append((x, y - 1))
        if y < height - 1:
            queue.append((x, y + 1))

    return mask


def remove_background_from_png(
    source_path: Path,
    output_path: Path,
    tolerance: int,
    feather: float,
) -> None:
    with Image.open(source_path) as image:
        result = image.convert("RGBA")

    background_mask = build_background_mask(result, tolerance)

    if feather > 0:
        background_mask = background_mask.filter(ImageFilter.GaussianBlur(feather))

    alpha = result.getchannel("A")
    new_alpha = Image.new("L", result.size, 255)
    new_alpha_pixels = new_alpha.load()
    alpha_pixels = alpha.load()
    mask_pixels = background_mask.load()

    width, height = result.size
    for y in range(height):
        for x in range(width):
            new_alpha_pixels[x, y] = max(0, alpha_pixels[x, y] - mask_pixels[x, y])

    result.putalpha(new_alpha)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)


def remove_background_tree(
    base_dir: Path = DEFAULT_BASE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    tolerance: int = 35,
    feather: float = 1.2,
    force: bool = False,
) -> tuple[int, int]:
    if not base_dir.is_dir():
        raise FileNotFoundError(f"Base folder not found: {base_dir}")

    processed = 0
    skipped = 0

    for source_path in sorted(base_dir.rglob("*.png")):
        relative_path = source_path.relative_to(base_dir)
        output_path = output_dir / relative_path

        if not force and output_is_current(source_path, output_path):
            skipped += 1
            continue

        remove_background_from_png(
            source_path=source_path,
            output_path=output_path,
            tolerance=tolerance,
            feather=feather,
        )
        processed += 1

    return processed, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Remove plain/near-plain backgrounds from every PNG in base/ and "
            "write the same folder structure to background_removed/."
        )
    )
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--tolerance",
        type=int,
        default=35,
        help="Background color tolerance from 0 to 255. Default: 35",
    )
    parser.add_argument(
        "--feather",
        type=float,
        default=1.2,
        help="Soft edge blur radius in pixels. Default: 1.2",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate all PNG files, including outputs that are already current.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not 0 <= args.tolerance <= 255:
        raise SystemExit("--tolerance must be between 0 and 255")
    if args.feather < 0:
        raise SystemExit("--feather must be 0 or greater")

    processed, skipped = remove_background_tree(
        base_dir=args.base_dir,
        output_dir=args.output_dir,
        tolerance=args.tolerance,
        feather=args.feather,
        force=args.force,
    )

    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
