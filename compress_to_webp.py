from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    missing = exc.name or "dependency"
    raise SystemExit(
        f"Missing Python package: {missing}\n"
        "Install dependencies with: pip install -r requirements.txt"
    ) from exc


ROOT_DIR = Path(__file__).resolve().parent

# DEFAULT_BASE_DIR = ROOT_DIR / "base"
# DEFAULT_OUTPUT_DIR = ROOT_DIR / "compressed"

DEFAULT_BASE_DIR = ROOT_DIR / "watermark"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "compressed watermark"

def output_is_current(source_path: Path, output_path: Path) -> bool:
    if not output_path.exists():
        return False

    return output_path.stat().st_mtime >= source_path.stat().st_mtime


def convert_png_to_webp(
    source_path: Path,
    output_path: Path,
    quality: int,
    lossless: bool,
) -> None:
    with Image.open(source_path) as image:
        converted = image.convert("RGBA")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    converted.save(
        output_path,
        "WEBP",
        quality=quality,
        lossless=lossless,
        method=6,
    )


def compress_png_tree(
    base_dir: Path = DEFAULT_BASE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    quality: int = 85,
    lossless: bool = False,
    force: bool = False,
) -> tuple[int, int]:
    if not base_dir.is_dir():
        raise FileNotFoundError(f"Base folder not found: {base_dir}")

    processed = 0
    skipped = 0

    for source_path in sorted(base_dir.rglob("*.png")):
        relative_path = source_path.relative_to(base_dir).with_suffix(".webp")
        output_path = output_dir / relative_path

        if not force and output_is_current(source_path, output_path):
            skipped += 1
            continue

        convert_png_to_webp(
            source_path=source_path,
            output_path=output_path,
            quality=quality,
            lossless=lossless,
        )
        processed += 1

    return processed, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert every PNG in base/ to WebP and write the same folder "
            "structure to compressed/."
        )
    )
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="WebP quality from 1 to 100. Default: 85",
    )
    parser.add_argument(
        "--lossless",
        action="store_true",
        help="Use lossless WebP compression.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate all WebP files, including outputs that are already current.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not 1 <= args.quality <= 100:
        raise SystemExit("--quality must be between 1 and 100")

    processed, skipped = compress_png_tree(
        base_dir=args.base_dir,
        output_dir=args.output_dir,
        quality=args.quality,
        lossless=args.lossless,
        force=args.force,
    )

    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
