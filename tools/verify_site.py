"""Compare generated public URLs and local references with the source inventory."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
AUDIT = ROOT / "audit"


def main():
    manifest = json.loads((AUDIT / "migration-manifest.json").read_text(encoding="utf-8"))
    counts = Counter(row["type"] for row in manifest)
    missing_pages = []
    broken_links = set()
    remaining_wp_media = set()
    for row in manifest:
        path = SITE.joinpath(*[part for part in row["path"].strip("/").split("/") if part]) / "index.html" if row["path"] != "/" else SITE / "index.html"
        if not path.exists():
            missing_pages.append(row["path"])
    for path in SITE.rglob("*.html"):
        if "media" in path.parts:
            continue
        try:
            tree = html.fromstring(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for el in tree.xpath("//*[@href or @src]"):
            for attr in ("href", "src"):
                url = el.get(attr, "")
                if "/wp-content/uploads/" in url:
                    remaining_wp_media.add(url)
                if not url.startswith("/") or url.startswith("//"):
                    continue
                parsed = urlsplit(url)
                target = unquote(parsed.path)
                if target in ("/news/", "/admin/") or target.startswith(("/news/story/", "/api/", "/admin/")):
                    continue
                local = SITE.joinpath(*[part for part in target.strip("/").split("/") if part])
                if target.endswith("/"):
                    local = local / "index.html"
                if not local.exists():
                    broken_links.add((path.relative_to(SITE).as_posix(), url))
    report = {
        "source_public_pages": 73,
        "source_public_posts": 185,
        "generated_pages": counts["page"],
        "generated_posts": counts["post"],
        "missing_generated_pages": missing_pages,
        "missing_media_references": len((AUDIT / "missing-media.txt").read_text(encoding="utf-8").splitlines()),
        "remaining_old_upload_urls": sorted(remaining_wp_media),
        "broken_local_links": [{"source": source, "target": target} for source, target in sorted(broken_links)],
    }
    (AUDIT / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in report.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
