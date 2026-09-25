"""Build a local, resized media directory from the RCIM uploads backup.

Generated media and the manifest are deliberately excluded from GitHub.
Run after extracting the WordPress backup. Only year/month upload paths are
considered; cached Elementor/plugin assets are not website content.
"""

from __future__ import annotations

import io
import json
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

from PIL import Image, ImageOps, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "backup_2026_09_25_12_36_12-f645b106-uploads.zip"
MEDIA = ROOT / "site" / "media"
AUDIT = ROOT / "audit"
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt"}
UPLOAD_PATH = re.compile(r"^\d{4}/\d{2}/")
SIZE_SUFFIX = re.compile(r"-\d+x\d+$")


def safe_destination(name: str) -> Path | None:
    p = PurePosixPath(name)
    if not UPLOAD_PATH.match(name) or ".." in p.parts or "\\" in name:
        return None
    return MEDIA.joinpath(*p.parts)


def is_generated_size(name: str, all_names: set[str]) -> bool:
    path = PurePosixPath(name)
    stem = SIZE_SUFFIX.sub("", path.stem)
    return stem != path.stem and str(path.with_name(stem + path.suffix)) in all_names


def save_webp(image: Image.Image, destination: Path, max_width: int) -> tuple[int, int]:
    copy = image.copy()
    copy.thumbnail((max_width, max_width), Image.Resampling.LANCZOS)
    if copy.mode not in ("RGB", "RGBA"):
        copy = copy.convert("RGBA" if "A" in copy.getbands() else "RGB")
    destination.parent.mkdir(parents=True, exist_ok=True)
    copy.save(destination, format="WEBP", quality=78, method=4)
    return copy.size


def main() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(exist_ok=True)
    old_manifest_file = AUDIT / "media-manifest.json"
    old_manifest = json.loads(old_manifest_file.read_text(encoding="utf-8")) if old_manifest_file.exists() else {}
    manifest: dict[str, dict] = {}
    counts: Counter[str] = Counter()
    failures: list[str] = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        all_names = set(archive.namelist())
        for entry in archive.infolist():
            name = entry.filename
            destination = safe_destination(name)
            if destination is None or entry.is_dir():
                continue
            ext = destination.suffix.lower()
            if ext in IMAGE_EXT:
                if is_generated_size(name, all_names):
                    counts["skipped_existing_wordpress_size"] += 1
                    continue
                try:
                    with archive.open(entry) as source:
                        raw = source.read()
                    with Image.open(io.BytesIO(raw)) as opened:
                        image = ImageOps.exif_transpose(opened)
                        image.load()
                    base = destination.with_suffix("")
                    large = base.with_name(base.name + "-1200.webp")
                    width, height = save_webp(image, large, 1200)
                    small = None
                    if image.width > 640:
                        small = base.with_name(base.name + "-480.webp")
                        save_webp(image, small, 480)
                    manifest[name] = {
                        "kind": "image",
                        "src": "/" + large.relative_to(ROOT / "site").as_posix(),
                        "src_small": "/" + small.relative_to(ROOT / "site").as_posix() if small else None,
                        "width": width,
                        "height": height,
                        "source_bytes": entry.file_size,
                        "optimized_bytes": large.stat().st_size + (small.stat().st_size if small else 0),
                    }
                    counts["images"] += 1
                except (OSError, ValueError, UnidentifiedImageError) as exc:
                    failures.append(f"{name}: {type(exc).__name__}")
            elif ext in DOC_EXT:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, destination.open("wb") as target:
                    shutil.copyfileobj(source, target)
                manifest[name] = {
                    "kind": "document",
                    "src": "/" + destination.relative_to(ROOT / "site").as_posix(),
                    "bytes": entry.file_size,
                }
                counts["documents"] += 1
    for name, value in old_manifest.items():
        if name not in manifest and value.get("recovered_from"):
            manifest[name] = value
    (AUDIT / "media-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AUDIT / "media-failures.txt").write_text("\n".join(failures), encoding="utf-8")
    for key, value in sorted(counts.items()):
        print(f"{key}: {value}")
    print(f"failures: {len(failures)}")


if __name__ == "__main__":
    main()
