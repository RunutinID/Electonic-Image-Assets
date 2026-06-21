from __future__ import annotations

import argparse
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

try:
    from PIL import Image
except ImportError as exc:
    missing = exc.name or "dependency"
    raise SystemExit(
        f"Missing Python package: {missing}\n"
        "Install dependencies with: pip install -r requirements.txt"
    ) from exc


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_BASE_DIR = ROOT_DIR / "base"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "watermark"
DEFAULT_LOGO_PATH = ROOT_DIR / "LightRunutinLogo.svg"


def parse_svg_size(logo_path: Path) -> tuple[float, float]:
    root = ElementTree.parse(logo_path).getroot()
    width = root.get("width")
    height = root.get("height")

    if width and height:
        return float(width.replace("px", "")), float(height.replace("px", ""))

    view_box = root.get("viewBox")
    if view_box:
        _, _, view_box_width, view_box_height = view_box.split()
        return float(view_box_width), float(view_box_height)

    raise ValueError(f"SVG size not found: {logo_path}")


def output_is_current(source_path: Path, output_path: Path, logo_path: Path) -> bool:
    """Return True when output exists and is newer than both input assets."""
    if not output_path.exists():
        return False

    output_mtime = output_path.stat().st_mtime
    return (
        output_mtime >= source_path.stat().st_mtime
        and output_mtime >= logo_path.stat().st_mtime
    )


def render_svg_logo_with_cairosvg(logo_path: Path, target_width: int) -> Image.Image:
    import cairosvg

    png_bytes = cairosvg.svg2png(url=str(logo_path), output_width=target_width)
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def browser_candidates() -> list[Path]:
    return [
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]


def render_svg_logo_with_browser(logo_path: Path, target_width: int) -> Image.Image:
    source_width, source_height = parse_svg_size(logo_path)
    target_height = max(1, round(target_width * source_height / source_width))

    browser_path = next((path for path in browser_candidates() if path.exists()), None)
    if browser_path is None:
        raise RuntimeError(
            "Cannot render SVG. Install Microsoft Edge/Google Chrome, or install "
            "Cairo native libraries for CairoSVG."
        )

    svg_uri = logo_path.resolve().as_uri()
    html = (
        "<!doctype html>"
        "<html><head><style>"
        "html,body{margin:0;width:100%;height:100%;background:transparent;overflow:hidden}"
        "img{display:block;width:100%;height:100%;object-fit:contain}"
        "</style></head>"
        f'<body><img src="{svg_uri}"></body></html>'
    )

    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        html_path = temp_path / "logo.html"
        png_path = temp_path / "logo.png"
        html_path.write_text(html, encoding="utf-8")

        command = [
            str(browser_path),
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--default-background-color=00000000",
            f"--window-size={target_width},{target_height}",
            f"--screenshot={png_path}",
            html_path.resolve().as_uri(),
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return Image.open(png_path).convert("RGBA")


def render_svg_logo(logo_path: Path, target_width: int) -> Image.Image:
    try:
        return render_svg_logo_with_cairosvg(logo_path, target_width)
    except Exception:
        return render_svg_logo_with_browser(logo_path, target_width)


def add_watermark(
    source_path: Path,
    output_path: Path,
    logo_path: Path,
    logo_scale: float,
    margin_scale: float,
    opacity: float,
) -> None:
    with Image.open(source_path) as image:
        base_image = image.convert("RGBA")

    watermark_width = max(1, round(base_image.width * logo_scale))
    watermark = render_svg_logo(logo_path, watermark_width)

    if opacity < 1:
        alpha = watermark.getchannel("A")
        alpha = alpha.point(lambda value: round(value * opacity))
        watermark.putalpha(alpha)

    margin = max(1, round(min(base_image.size) * margin_scale))
    position = (
        base_image.width - watermark.width - margin,
        base_image.height - watermark.height - margin,
    )

    base_image.alpha_composite(watermark, position)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    base_image.save(output_path)


def watermark_png_tree(
    base_dir: Path = DEFAULT_BASE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    logo_path: Path = DEFAULT_LOGO_PATH,
    logo_scale: float = 0.22,
    margin_scale: float = 0.04,
    opacity: float = 0.9,
    force: bool = False,
) -> tuple[int, int]:
    if not base_dir.is_dir():
        raise FileNotFoundError(f"Base folder not found: {base_dir}")
    if not logo_path.is_file():
        raise FileNotFoundError(f"Logo file not found: {logo_path}")

    processed = 0
    skipped = 0

    for source_path in sorted(base_dir.rglob("*.png")):
        relative_path = source_path.relative_to(base_dir)
        output_path = output_dir / relative_path

        if not force and output_is_current(source_path, output_path, logo_path):
            skipped += 1
            continue

        add_watermark(
            source_path=source_path,
            output_path=output_path,
            logo_path=logo_path,
            logo_scale=logo_scale,
            margin_scale=margin_scale,
            opacity=opacity,
        )
        processed += 1

    return processed, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Add LightRunutinLogo.svg watermark to every PNG in base/ and write "
            "the same folder structure to watermark/."
        )
    )
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--logo", type=Path, default=DEFAULT_LOGO_PATH)
    parser.add_argument(
        "--logo-scale",
        type=float,
        default=0.22,
        help="Logo width as a fraction of image width. Default: 0.22",
    )
    parser.add_argument(
        "--margin-scale",
        type=float,
        default=0.04,
        help="Bottom/right margin as a fraction of the smaller image side. Default: 0.04",
    )
    parser.add_argument(
        "--opacity",
        type=float,
        default=0.9,
        help="Watermark opacity from 0 to 1. Default: 0.9",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate all PNG files, including outputs that are already current.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not 0 < args.logo_scale <= 1:
        raise SystemExit("--logo-scale must be greater than 0 and no more than 1")
    if not 0 <= args.opacity <= 1:
        raise SystemExit("--opacity must be between 0 and 1")
    if args.margin_scale < 0:
        raise SystemExit("--margin-scale must be 0 or greater")

    processed, skipped = watermark_png_tree(
        base_dir=args.base_dir,
        output_dir=args.output_dir,
        logo_path=args.logo,
        logo_scale=args.logo_scale,
        margin_scale=args.margin_scale,
        opacity=args.opacity,
        force=args.force,
    )

    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
