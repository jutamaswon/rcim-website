"""Check all migrated public URLs against the currently visible RCIM site."""
from __future__ import annotations

import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"


def check(row):
    path = quote(row["path"], safe="/%")
    request = Request("https://www.rcim.in.th" + path, headers={"User-Agent":"RCIM content migration check/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            status = response.status
            final_url = response.url
            data = response.read(2 * 1024 * 1024)
        try:
            tree = html.fromstring(data)
            for el in tree.xpath("//script|//style|//nav|//footer"):
                el.drop_tree()
            title = " ".join(tree.xpath("//title/text()")[:1]).strip()
            text_chars = len(" ".join(tree.text_content().split()))
        except Exception:
            title, text_chars = "", 0
        return {"id":row["id"],"type":row["type"],"path":row["path"],"status":status,"final_url":final_url,"live_title":title,"live_text_chars":text_chars,"migrated_text_chars":row["content_chars"]}
    except HTTPError as exc:
        status = exc.code
    except (URLError, TimeoutError, OSError) as exc:
        status = type(exc).__name__
    return {"id":row["id"],"type":row["type"],"path":row["path"],"status":status,"migrated_text_chars":row["content_chars"]}


def main():
    rows = json.loads((AUDIT / "migration-manifest.json").read_text(encoding="utf-8"))
    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for index, future in enumerate(as_completed([pool.submit(check, row) for row in rows]), 1):
            results.append(future.result())
            if index % 50 == 0:
                print(f"checked {index}/{len(rows)}", flush=True)
    results.sort(key=lambda x: int(x["id"]))
    (AUDIT / "live-url-comparison.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(dict(Counter(str(row["status"]) for row in results)))


if __name__ == "__main__":
    main()
