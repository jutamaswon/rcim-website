"""Extract public WordPress content from a local SQL gzip backup.

The output stays under audit/ (ignored by Git). This deliberately excludes
users, options, passwords, sessions, and all other private database tables.
"""

from __future__ import annotations

import gzip
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / "backup_2026_09_25_12_36_12-f645b106-db.sql.gz"
OUT = ROOT / "audit"
INSERT = re.compile(r"^INSERT INTO `(?P<table>[^`]+)` VALUES ")
ESCAPES = {"0": "\0", "b": "\b", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a"}


def parse_row(source: str) -> list[str | None]:
    """Read one mysqldump tuple; strings may contain escaped punctuation."""
    start = source.find("(")
    if start < 0:
        raise ValueError("SQL row has no opening parenthesis")
    values: list[str | None] = []
    token: list[str] = []
    quote: str | None = None
    quoted = False
    i = start + 1
    while i < len(source):
        ch = source[i]
        if quote:
            if ch == "\\" and i + 1 < len(source):
                i += 1
                token.append(ESCAPES.get(source[i], source[i]))
            elif ch == quote:
                if i + 1 < len(source) and source[i + 1] == quote:
                    token.append(quote)
                    i += 1
                else:
                    quote = None
            else:
                token.append(ch)
        elif ch in ("'", '"'):
            quote = ch
            quoted = True
        elif ch == "," or ch == ")":
            value = "".join(token) if quoted else "".join(token).strip()
            values.append(None if not quoted and value.upper() == "NULL" else value)
            token.clear()
            quoted = False
            if ch == ")":
                return values
        else:
            token.append(ch)
        i += 1
    raise ValueError("Unterminated SQL row")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    counts: Counter[str] = Counter()
    public_ids: set[str] = set()

    def rows_for(table: str):
        current_table = ""
        with gzip.open(BACKUP, "rt", encoding="utf-8", errors="replace") as source:
            for line in source:
                match = INSERT.match(line)
                if match:
                    current_table = match.group("table")
                    row_source = line[match.end() :]
                elif current_table and line.startswith("("):
                    row_source = line
                else:
                    if line.rstrip().endswith(";"):
                        current_table = ""
                    continue
                if current_table == table:
                    yield row_source

    with (OUT / "db-public-records.jsonl").open("w", encoding="utf-8") as records:
        for row_source in rows_for("omgnt_posts"):
            row = parse_row(row_source)
            if len(row) != 23:
                raise ValueError(f"Expected 23 post columns, got {len(row)}")
            counts[f"{row[20]}:{row[7]}"] += 1
            if row[7] == "publish" and row[10] == "" and row[20] not in (
                "attachment",
                "nav_menu_item",
                "elementor_library",
            ):
                public_ids.add(row[0] or "")
                item = {
                    "id": row[0],
                    "type": row[20],
                    "title": row[5],
                    "slug": row[11],
                    "date": row[2],
                    "modified": row[14],
                    "parent_id": row[17],
                    "guid": row[18],
                    "content_html": row[4],
                    "excerpt": row[6],
                }
                records.write(json.dumps(item, ensure_ascii=False) + "\n")

    meta_prefix = re.compile(r'^\(\d+,(\d+),["\']_elementor_data["\'],')
    with (OUT / "db-elementor-data.jsonl").open("w", encoding="utf-8") as elementor:
        for row_source in rows_for("omgnt_postmeta"):
            match = meta_prefix.match(row_source[:120])
            if not match or match.group(1) not in public_ids:
                continue
            row = parse_row(row_source)
            if len(row) != 4:
                raise ValueError(f"Expected 4 postmeta columns, got {len(row)}")
            if row[3]:
                elementor.write(
                    json.dumps({"post_id": row[1], "data": row[3]}, ensure_ascii=False)
                    + "\n"
                )
                counts["elementor_meta"] += 1

    (OUT / "db-content-summary.json").write_text(
        json.dumps(dict(sorted(counts.items())), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    for key, count in sorted(counts.items()):
        print(f"{key}: {count}")


if __name__ == "__main__":
    main()
