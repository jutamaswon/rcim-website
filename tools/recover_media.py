"""Recover publicly linked assets absent from the supplied uploads ZIP.

Run locally with network permission. Files and the manifest stay ignored by Git.
"""
from __future__ import annotations

import io
import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
SITE = ROOT / "site"
MANIFEST = AUDIT / "media-manifest.json"
LIMIT = 30 * 1024 * 1024
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt"}


def recover(url):
    parsed = urlsplit(url)
    if parsed.hostname not in ("www.rcim.in.th", "rcim.in.th") or "/wp-content/uploads/" not in parsed.path:
        return (url, None, "unsupported")
    name = unquote(parsed.path.split("/wp-content/uploads/", 1)[1])
    parts = Path(name).parts
    if len(parts) < 3 or ".." in parts or not parts[0].isdigit() or not parts[1].isdigit():
        return (url, None, "unsafe-path")
    ext = Path(name).suffix.lower()
    if ext not in IMAGE_EXT | DOC_EXT:
        return (url, None, "unsupported-type")
    target_url = "https://www.rcim.in.th/wp-content/uploads/" + quote(name, safe="/")
    request = Request(target_url, headers={"User-Agent": "RCIM content migration/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            if int(response.headers.get("Content-Length") or 0) > LIMIT:
                return (url, None, "too-large")
            data = response.read(LIMIT + 1)
            mime = response.headers.get("Content-Type", "")
        if len(data) > LIMIT:
            return (url, None, "too-large")
        if ext in IMAGE_EXT:
            if not mime.startswith("image/"):
                return (url, None, "wrong-content-type")
            with Image.open(io.BytesIO(data)) as opened:
                image = ImageOps.exif_transpose(opened)
                image.load()
            image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            base = SITE / "media" / name
            large = base.with_suffix("").with_name(base.stem + "-1200.webp")
            large.parent.mkdir(parents=True, exist_ok=True)
            image.save(large, "WEBP", quality=78, method=4)
            small = None
            if image.width > 640:
                thumb = image.copy()
                thumb.thumbnail((480, 480), Image.Resampling.LANCZOS)
                small = base.with_suffix("").with_name(base.stem + "-480.webp")
                thumb.save(small, "WEBP", quality=78, method=4)
            value = {"kind":"image", "src":"/"+large.relative_to(SITE).as_posix(), "src_small":"/"+small.relative_to(SITE).as_posix() if small else None, "width":image.width, "height":image.height, "source_bytes":len(data), "optimized_bytes":large.stat().st_size+(small.stat().st_size if small else 0), "recovered_from":url}
        else:
            if ext == ".pdf" and not data.startswith(b"%PDF"):
                return (url, None, "invalid-pdf")
            if mime.startswith("text/html"):
                return (url, None, "html-instead-of-document")
            dest = SITE / "media" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            value = {"kind":"document", "src":"/"+dest.relative_to(SITE).as_posix(), "bytes":len(data), "recovered_from":url}
        return (url, (name, value), "recovered")
    except HTTPError as exc:
        return (url, None, f"http-{exc.code}")
    except (URLError, TimeoutError, OSError, UnidentifiedImageError, ValueError) as exc:
        return (url, None, type(exc).__name__)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    urls = [u for u in (AUDIT / "missing-media.txt").read_text(encoding="utf-8").splitlines() if u]
    previous_file = AUDIT / "media-recovery-results.json"
    outcomes = json.loads(previous_file.read_text(encoding="utf-8")) if previous_file.exists() else {}
    urls = [u for u in urls if u not in outcomes]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(recover, url) for url in urls]
        for index, future in enumerate(as_completed(futures), 1):
            url, item, status = future.result()
            outcomes[url] = status
            if item:
                name, value = item
                manifest[name] = value
            if index % 50 == 0:
                print(f"checked {index}/{len(urls)}", flush=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (AUDIT / "media-recovery-results.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(dict(Counter(outcomes.values())))


if __name__ == "__main__":
    main()
