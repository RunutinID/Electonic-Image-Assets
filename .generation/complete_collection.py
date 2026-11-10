from __future__ import annotations
import argparse, concurrent.futures, json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(r"D:\Runutin\Module Development\Media\Electonic Image Assets")
RAW, BASE = ROOT / "Raw Image", ROOT / "base"
WORK = ROOT / ".generation"
PLUGIN = Path(r"C:\Users\FIRDAUS\AppData\Roaming\kimi-desktop\daimon-share\daimon\runtime\kimi-code\home\plugins\managed\image_generation")
PYTHONW = Path(r"C:\Users\FIRDAUS\AppData\Roaming\kimi-desktop\daimon-bundle\runtime\python\cpython-3.12\pythonw.exe")
STYLE = BASE / "Sensor" / "DHT11 Sensor.png"
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
ALIASES = {"Arduino UNO WiFi Rev 2": "Arduino UNO Rev 2 WiFi"}

def output_rel(raw: Path) -> Path:
    rel = raw.relative_to(RAW).with_suffix(".webp")
    if rel.parts[:2] == ("Microcontrol", "ESP32 Boards"):
        rel = Path("Microcontrol", "ESP32", *rel.parts[2:])
    return rel

def items():
    stems = {p.stem for p in BASE.rglob("*") if p.suffix.lower() in EXTS}
    result = []
    for raw in sorted(RAW.rglob("*")):
        if raw.suffix.lower() not in EXTS:
            continue
        name = ALIASES.get(raw.stem, raw.stem)
        if name not in stems and not (BASE / output_rel(raw)).exists():
            result.append(raw)
    return result

def load(name, default):
    path = WORK / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

def save(name, data):
    (WORK / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def run(command):
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")

def upload_one(raw):
    result = run([str(PYTHONW), "-u", str(PLUGIN / "scripts/image_generation_tool.py"), "image-to-url", "--image-path", str(raw)])
    match = re.search(r"https://\S+", result.stdout)
    if result.returncode or not match:
        return str(raw), None, (result.stdout + result.stderr).strip()
    return str(raw), match.group(0), None

def upload():
    urls = load("urls.json", {})
    all_items = items() + [STYLE]
    to_upload = [p for p in all_items if str(p) not in urls]
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for i, (key, url, error) in enumerate(pool.map(upload_one, to_upload), 1):
            print(f"[{i}/{len(to_upload)}] {'OK' if url else 'ERROR'} {Path(key).name}", flush=True)
            if url:
                urls[key] = url
                save("urls.json", urls)
            if error:
                errors.append({"file": key, "error": error})
    save("upload-errors.json", errors)
    print(f"Uploaded: {len(to_upload)-len(errors)}; errors: {len(errors)}")
    return bool(errors)

def prompt(raw):
    name = raw.stem
    return (
        f"Create a reference-guided photorealistic isometric 3D product render of the exact electronic component named {name}, using the first reference image for physical identity and the second reference image only for visual style. "
        "Completely remove and ignore all store watermarks, seller logos, promotional text, badges, retail banners, URLs, prices, packaging, hands, and background clutter. "
        "Match the exact Runutin base style: one isolated component centered on a seamless solid warm cream background, elevated 30-45 degree orthographic corner isometric view, component rotated diagonally, top surface and two side profiles visible, photorealistic Octane studio render, soft subtle ambient-occlusion contact shadow. "
        "Faithfully preserve the exact physical geometry, PCB color, chips, connectors, pin count, displays, cables, labels, and readable technical silkscreen of this specific reference. Do not substitute another model or invent extra parts. "
        "85mm macro lens feel, deep focus f/8, sharp realistic FR-4, plastic and metal materials, soft studio softbox lighting, centered square composition. "
        "No pure white background, gradients, floor reflections, watermark, promotional text, text overlay, barcode, price tag, hands, desk, clutter, messy wires, lens flare, distortion, warped pins, low-poly, cartoon, flat vector, or glitch."
    )

def launch(batch):
    urls = load("urls.json", {})
    pending = [p for p in items() if str(p) in urls]
    selected = pending[batch*20:(batch+1)*20]
    jobs = []
    for i, raw in enumerate(selected, batch*20):
        out = BASE / output_rel(raw).with_suffix(".png")
        out.parent.mkdir(parents=True, exist_ok=True)
        report = WORK / f"launch-{i:03}.txt"
        command = [str(PYTHONW), "-u", str(PLUGIN / "scripts/image_generation_launch.py"), "generate",
                   "--description", prompt(raw), "--size", "1024x1024", "--background", "opaque",
                   "--reference-image", urls[str(raw)], "--reference-image", urls[str(STYLE)],
                   "--output", str(out)]
        with report.open("w", encoding="utf-8") as handle:
            result = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, text=True)
        text = report.read_text(encoding="utf-8", errors="replace")
        log = re.search(r"Job log:\s*(.+)", text)
        pid = re.search(r"Job PID file:\s*(.+)", text)
        job = {"index": i, "raw": str(raw), "output": str(out), "report": str(report), "returncode": result.returncode}
        if log and pid:
            job.update(log=log.group(1).strip(), pid=pid.group(1).strip())
        else:
            job["error"] = text
        jobs.append(job)
        print(f"[{i+1}] {'LAUNCHED' if log and pid else 'ERROR'} {raw.stem}", flush=True)
    save(f"jobs-{batch}.json", jobs)

def watch(batch):
    jobs = load(f"jobs-{batch}.json", [])
    def one(job):
        if "log" not in job:
            return job["index"], 1
        report = WORK / f"watch-{job['index']:03}.txt"
        command = [str(PYTHONW), "-u", str(PLUGIN / "scripts/image_generation_watch.py"),
                   "--log-file", job["log"], "--pid-file", job["pid"], "--interval-seconds", "20"]
        with report.open("w", encoding="utf-8") as handle:
            result = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, text=True)
        return job["index"], result.returncode
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        for index, code in pool.map(one, jobs):
            print(f"[{index+1}] {'DONE' if code == 0 else 'FAILED'}", flush=True)

def finalize(batch):
    jobs = load(f"jobs-{batch}.json", [])
    thumbs = []
    for job in jobs:
        raw, output = Path(job["raw"]), Path(job["output"])
        candidates = [p for p in output.parent.glob(output.stem + ".*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
        final = output.with_suffix(".webp")
        try:
            source = final if final.exists() else next(p for p in candidates if p.name.startswith(output.stem + "."))
            with Image.open(source) as im:
                im.verify()
            if source != final:
                with Image.open(source) as im:
                    im.convert("RGB").save(final, "WEBP", quality=92, method=6)
                source.unlink()
            with Image.open(final) as im:
                im.thumbnail((220, 220))
                thumbs.append((raw.stem, im.copy()))
            print(f"OK {final.relative_to(BASE)}")
        except Exception as exc:
            print(f"MISSING/INVALID {raw.stem}: {exc}")
    if thumbs:
        cols, cell_w, cell_h = 5, 250, 255
        rows = (len(thumbs)+cols-1)//cols
        sheet = Image.new("RGB", (cols*cell_w, rows*cell_h), "#faf5ec")
        draw = ImageDraw.Draw(sheet)
        for n, (name, im) in enumerate(thumbs):
            x, y = (n%cols)*cell_w, (n//cols)*cell_h
            sheet.paste(im, (x+(cell_w-im.width)//2, y+5))
            draw.text((x+8, y+228), name[:36], fill="#1a1a1a")
        sheet.save(WORK / f"contact-{batch}.jpg", quality=88)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["audit", "upload", "launch", "watch", "finalize"])
    parser.add_argument("--batch", type=int, default=0)
    args = parser.parse_args()
    WORK.mkdir(exist_ok=True)
    if args.action == "audit":
        missing = items()
        print(f"Missing: {len(missing)}")
        for p in missing:
            print(output_rel(p))
    elif args.action == "upload":
        raise SystemExit(upload())
    elif args.action == "launch":
        launch(args.batch)
    elif args.action == "watch":
        watch(args.batch)
    elif args.action == "finalize":
        finalize(args.batch)

if __name__ == "__main__":
    main()
