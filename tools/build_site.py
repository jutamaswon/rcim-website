"""Build public static pages from the ignored WordPress audit extract.

The generated HTML is new website content; backups and original media remain local.
"""
from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit

from lxml import html as LH

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
AUDIT = ROOT / "audit"
DOMAIN = "https://www.rcim.in.th"
WP = "http://wordpress.org/export/1.2/"
UPLOAD = re.compile(r"/wp-content/uploads/([^?#]+)")
SIZE = re.compile(r"-\d+x\d+(?=\.[^.]+$)")
BAD_TAGS = {"script", "style", "iframe", "form", "input", "button", "textarea", "select", "noscript", "svg", "canvas"}
ALLOWED_ATTRS = {"href", "src", "srcset", "alt", "title", "width", "height", "loading", "decoding", "class", "id", "colspan", "rowspan", "target", "rel", "aria-label"}
ID_PATHS = {}
ALIASES = {
    "/หลักสูตร/": "/masterdoctor/",
    "/รับรองคุณวุฒิ-หลักสูตรข/": "/masterdoctor/qualifications-certified-rcim/",
    "/หลักสูตร/ปริญญาเอก/d-m/": "/masterdoctor/doctor/dm2/",
    "/apply-online-rcim/apply-online-rcim-doctor/": "/apply-online-rcim/details-doctor/",
    "/apply-online-rcim/apply-online-rcim-master/": "/apply-online-rcim/details-master/",
    "/วิจัย-วิชาการ/ส่งเล่มวิทยานิพนธ์ฉบับสมบูรณ์/": "/masterdoctor/research-academic/ส่งเล่มวิทยานิพนธ์ฉบับ/",
    "/วิจัย-วิชาการ/ส่งเล่มวิทยานิพนธ์ฉบับ/": "/masterdoctor/research-academic/ส่งเล่มวิทยานิพนธ์ฉบับ/",
    "/เกี่ยวกับ-rcim/press-release-rcim/": "/about-rcim/press-release-rcim/",
    "/course-rcim/masterdoctor/": "/masterdoctor/",
    "/doctor/dba2/": "/masterdoctor/doctor/dba2/",
    "/doctor/dm2/": "/masterdoctor/doctor/dm2/",
    "/doctor/dpa2/": "/masterdoctor/doctor/dpa2/",
    "/doctor/phd-eai/": "/masterdoctor/doctor/phd-eai/",
    "/for-students-rcim/student-research-work/": "/for-students-rcim/student-research-work/student-research-results-rcim-2566/",
    "/course-rcim/งานประกันคุณภาพ-แผน-rcim/e-library-rcim/": "/about-rcim/งานประกันคุณภาพ-แผน-rcim/e-library-rcim/",
    "/course-rcim/รับรองคุณวุฒิ-หลักสูตร-rcim/": "/masterdoctor/qualifications-certified-rcim/",
    "/course-rcim/research-academic/student-research-work/": "/for-students-rcim/student-research-work/student-research-results-rcim-2566/",
    "/mainrcim/ความสำเร็จ/ภาพกิจกรรม1/": "/about-rcim/rcim-activities-gallery/",
    "/course-rcim/หลักสูตรปริญญาเอก/d-b-a/": "/masterdoctor/doctor/dba2/",
    "/course-rcim/หลักสูตรปริญญาเอก/d-m/": "/masterdoctor/doctor/dm2/",
    "/course-rcim/หลักสูตรปริญญาเอก/d-p-a2/": "/masterdoctor/doctor/dpa2/",
    "/course-rcim/หลักสูตรปริญญาเอก/ph-d/": "/masterdoctor/doctor/phd-eai/",
    "/course-rcim/หลักสูตรปริญญาโท/m-b-a/": "/masterdoctor/master/mba2/",
    "/course-rcim/หลักสูตรปริญญาโท/m-ed-2/": "/masterdoctor/master/med2/",
    "/course-rcim/หลักสูตรปริญญาโท/m-p-a-2/": "/masterdoctor/master/mpa2/",
    "/course-rcim/หลักสูตรปริญญาโท/mm/": "/masterdoctor/master/mm2/",
    "/16723793/ผลงานวิจัยนักศึกษา": "/for-students-rcim/student-research-work/student-research-results-rcim-2566/",
    "/16723804/ผลงานวิจัย-อาจารย์": "/masterdoctor/research-academic/professors-research-work/",
    "/16723805/วารสาร": "/about-rcim/งานประกันคุณภาพ-แผน-rcim/jibim/",
}


def load_records():
    return [json.loads(line) for line in (AUDIT / "db-public-records.jsonl").open(encoding="utf-8") if line.strip()]


def page_urls():
    result = {}
    tree = ET.parse(ROOT / "WordPress.2026-09-25.xml")
    for item in tree.findall("channel/item"):
        if item.findtext(f"{{{WP}}}post_type") == "page" and item.findtext(f"{{{WP}}}status") == "publish":
            result[item.findtext(f"{{{WP}}}post_id")] = unquote(urlsplit(item.findtext("link") or "").path) or "/"
    return result


def local_path(url):
    path = unquote(urlsplit(url).path)
    if path == "/":
        return SITE / "index.html"
    return SITE.joinpath(*[part for part in path.strip("/").split("/") if part]) / "index.html"


def text_only(source):
    try:
        return " ".join(LH.fromstring(f"<div>{source}</div>").text_content().split())
    except Exception:
        return re.sub(r"<[^>]+>", " ", source)


def media_lookup(url, media):
    match = UPLOAD.search(url)
    if not match:
        return None
    name = unquote(match.group(1))
    return media.get(name) or media.get(SIZE.sub("", name))


def clean_content(source, media, missing):
    def embed_link(match):
        found = re.search(r"https?://[^\s'\"\[\]]+", match.group(0))
        if not found:
            return ""
        url = html.escape(found.group(0), quote=True)
        return f'<p><a href="{url}">เปิดเอกสารหรือสื่อที่ฝังไว้จากเว็บไซต์เดิม</a></p>'
    source = re.sub(r"\[embedpress.*?\[/embedpress\][^\]]*\]", embed_link, source or "", flags=re.S | re.I)
    source = re.sub(r"\[/?caption[^\]]*\]", "", source, flags=re.I)
    source = source.replace("[object Object]", "")
    source = source.replace("[__HEYPUBLISHER_SUBMISSION_FORM_GOES_HERE__]", "<p>แบบฟอร์มส่งบทความจากเว็บไซต์เดิมอยู่ระหว่างตรวจสอบ กรุณาติดต่อวิทยาลัย</p>")
    try:
        root = LH.fragment_fromstring(source or "", create_parent="div")
    except Exception:
        root = LH.Element("div")
        root.text = text_only(source or "")
    for el in list(root.iter()):
        tag = el.tag.lower() if isinstance(el.tag, str) else ""
        if tag == "iframe":
            src = el.get("src", "")
            if "pdf-viewer-for-elementor" in src:
                src = parse_qs(urlsplit(src).query).get("file", [src])[0]
            found = media_lookup(src, media) if UPLOAD.search(src) else None
            if found:
                src = found["src"]
            elif UPLOAD.search(src):
                missing.add(src)
            if src.startswith("https://"):
                link = LH.Element("a", href=src)
                link.text = "เปิดสื่อภายนอก"
                el.addnext(link)
            elif src.startswith("/media/"):
                link = LH.Element("a", href=src)
                link.text = "เปิดเอกสาร"
                el.addnext(link)
        if tag in BAD_TAGS:
            el.drop_tree()
            continue
        for key in list(el.attrib):
            if key.lower() not in ALLOWED_ATTRS or key.lower().startswith("on"):
                del el.attrib[key]
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            el.tag = "h2" if tag in ("h1", "h2", "h3") else "h3"
        if tag in ("img", "a"):
            key = "src" if tag == "img" else "href"
            url = el.get(key, "")
            if "pdf-viewer-for-elementor" in url:
                url = parse_qs(urlsplit(url).query).get("file", [url])[0]
                el.set(key, url)
            if url.lower().startswith(("javascript:", "data:")):
                el.attrib.pop(key, None)
                continue
            if UPLOAD.search(url):
                found = media_lookup(url, media)
                if found:
                    el.set(key, found["src"])
                    if tag == "img":
                        el.set("width", str(found["width"]))
                        el.set("height", str(found["height"]))
                        el.set("loading", "lazy")
                        el.set("decoding", "async")
                        if found.get("src_small"):
                            el.set("srcset", f'{found["src_small"]} 480w, {found["src"]} 1200w')
                            el.set("sizes", "(max-width: 640px) 100vw, 800px")
                        if not el.get("alt"):
                            el.set("alt", "ภาพประกอบเนื้อหา RCIM")
                else:
                    missing.add(url)
            elif urlsplit(url).hostname in ("www.rcim.in.th", "rcim.in.th"):
                parsed = urlsplit(url)
                query = parse_qs(parsed.query)
                wp_id = (query.get("p") or query.get("page_id") or [None])[0]
                if wp_id in ID_PATHS:
                    el.set(key, ID_PATHS[wp_id])
                else:
                    el.set(key, unquote(parsed.path) + ("?" + parsed.query if parsed.query else ""))
            if tag == "a" and el.get("href", "").startswith("/"):
                old = unquote(urlsplit(el.get("href")).path).lower()
                if old in ALIASES:
                    el.set("href", ALIASES[old])
            if tag == "img" and el.get("src", "").startswith("/images/editor/"):
                missing.add(el.get("src"))
                el.drop_tree()
                continue
        if tag == "a" and el.get("target") == "_blank":
            el.set("rel", "noopener noreferrer")
        if tag == "img" and not el.get("alt"):
            el.set("alt", "ภาพประกอบเนื้อหา RCIM")
    return "".join(LH.tostring(child, encoding="unicode", method="html") for child in root)


def document(title, description, path, body, *, kind="WebPage", modified=None, published=None):
    esc = html.escape
    canonical = DOMAIN + quote(path, safe="/%")
    schema = {"@context": "https://schema.org", "@type": kind, "headline": title,
              "url": canonical, "publisher": {"@type": "CollegeOrUniversity", "name": "วิทยาลัยนวัตกรรมการจัดการ มทร.รัตนโกสินทร์", "url": DOMAIN}}
    if modified:
        schema["dateModified"] = modified[:10]
    if published and kind == "NewsArticle":
        schema["datePublished"] = published[:10]
    nav = [("เกี่ยวกับวิทยาลัย", "/about-rcim/"), ("หลักสูตร", "/masterdoctor/"),
           ("นักศึกษา", "/for-students-rcim/"), ("ข่าวสาร", "/news/"),
           ("สมัครเรียน", "/apply-online-rcim/"), ("ติดต่อ", "/page-id35/")]
    links = "".join(f'<a href="{u}">{esc(n)}</a>' for n, u in nav)
    home_css = '<link rel="stylesheet" href="/assets/home.css">' if path == "/" else ""
    return f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | RCIM</title><meta name="description" content="{esc(description[:158])}"><link rel="canonical" href="{esc(canonical)}"><meta property="og:type" content="{'article' if kind == 'NewsArticle' else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description[:158])}"><meta property="og:url" content="{esc(canonical)}"><link rel="stylesheet" href="/assets/site.css">{home_css}<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")}</script></head><body><a class="skip" href="#main">ข้ามไปยังเนื้อหา</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="/"><img class="brand-mark-image" src="/media/2022/06/Logo-RCIM2019-TH-480.webp" width="52" height="52" alt=""><span><strong>RCIM</strong><small>วิทยาลัยนวัตกรรมการจัดการ</small></span></a><button id="menu-toggle" class="menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false">เมนู</button><nav id="site-nav" aria-label="เมนูหลัก">{links}</nav></div></header><main id="main">{body}</main><footer><div class="wrap footer-grid"><div><strong>RCIM</strong><p>วิทยาลัยนวัตกรรมการจัดการ<br>มหาวิทยาลัยเทคโนโลยีราชมงคลรัตนโกสินทร์</p></div><div><p>96 หมู่ 3 ถนนพุทธมณฑลสาย 5 ต.ศาลายา อ.พุทธมณฑล จ.นครปฐม 73170</p><p>โทร. 0-2441-6067 · 092-442-8000</p></div></div></footer><script src="/assets/site.js" defer></script></body></html>'''


def write_page(path, markup):
    target = local_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    formatted = LH.tostring(LH.fromstring(markup), encoding="unicode", method="html", pretty_print=True, doctype="<!doctype html>")
    target.write_text("\n".join(line.expandtabs(4).rstrip() for line in formatted.splitlines()) + "\n", encoding="utf-8")


def homepage_body(legacy_content, posts):
    features = [
        ("หลักสูตร", "สำรวจหลักสูตรระดับบัณฑิตศึกษา", "/masterdoctor/"),
        ("สมัครเรียน", "ข้อมูลและช่องทางการสมัครเรียน", "/apply-online-rcim/"),
        ("สำหรับนักศึกษา", "ปฏิทิน เอกสาร และแบบฟอร์ม", "/for-students-rcim/"),
        ("เกี่ยวกับวิทยาลัย", "รู้จัก RCIM บุคลากร และงานวิชาการ", "/about-rcim/"),
        ("ข่าวสาร", "ข่าวใหม่และประกาศของวิทยาลัย", "/news/"),
        ("ติดต่อ", "ที่ตั้งและช่องทางติดต่อ", "/page-id35/"),
    ]
    cards = "".join(f'<a class="feature-card" href="{path}"><strong>{name}</strong><span>{desc}</span><b aria-hidden="true">→</b></a>' for name, desc, path in features)
    recent = sorted(posts, key=lambda r: r.get("date", ""), reverse=True)[:3]
    news = "".join(f'<a class="news-card" href="{html.escape(r["path"])}"><time>{html.escape(r.get("date", "")[:10])}</time><strong>{html.escape(r["title"])}</strong><span>อ่านข่าว →</span></a>' for r in recent)
    return f'''<section class="home-hero"><div class="wrap"><span class="eyebrow">มหาวิทยาลัยเทคโนโลยีราชมงคลรัตนโกสินทร์</span><h1>วิทยาลัยนวัตกรรมการจัดการ</h1><p>แหล่งรวมข้อมูลหลักสูตร ข่าวสาร และบริการสำหรับนักศึกษาและผู้สนใจศึกษา</p><div class="hero-actions"><a class="button-light" href="/masterdoctor/">ดูหลักสูตร</a><a class="button-outline" href="/apply-online-rcim/">สมัครเรียน</a></div></div></section><section class="wrap section"><div class="section-head"><span class="eyebrow">ค้นหาข้อมูล</span><h2>สิ่งที่คุณต้องการ</h2></div><div class="feature-grid">{cards}</div></section><section class="home-news"><div class="wrap section"><div class="section-head"><span class="eyebrow">ข่าวสาร</span><h2>ประกาศล่าสุดจากเว็บไซต์เดิม</h2><a href="/news/archive/">ดูข่าวย้อนหลังทั้งหมด →</a></div><div class="news-grid">{news}</div></div></section><section class="wrap section legacy-home"><h2>ข้อมูลจากเว็บไซต์เดิม</h2><div class="prose">{legacy_content}</div></section>'''


def main():
    records = [r for r in load_records() if r["type"] in ("page", "post")]
    page_paths = page_urls()
    media = json.loads((AUDIT / "media-manifest.json").read_text(encoding="utf-8")) if (AUDIT / "media-manifest.json").exists() else {}
    missing = set()
    manifest = []
    posts = []
    pages = []
    used = set()
    for rec in records:
        path = page_paths.get(rec["id"]) if rec["type"] == "page" else "/" + unquote(rec["slug"].strip("/")) + "/"
        path = path or "/?page_id=" + rec["id"]
        if "?" in path or path in used:
            path = f'/legacy-{rec["type"]}-{rec["id"]}/'
        used.add(path)
        rec["path"] = path
        (posts if rec["type"] == "post" else pages).append(rec)
    ID_PATHS.clear()
    ID_PATHS.update({r["id"]: r["path"] for r in records})
    for rec in records:
        path = rec["path"]
        title = rec["title"].strip() or "RCIM"
        content = clean_content(rec.get("content_html") or "", media, missing)
        child_pages = [p for p in pages if p.get("parent_id") == rec["id"]]
        child_html = ""
        if child_pages:
            child_html = '<section class="related"><h2>หัวข้อที่เกี่ยวข้อง</h2><div class="link-grid">' + "".join(f'<a class="link-card" href="{html.escape(p["path"])}">{html.escape(p["title"])}</a>' for p in child_pages) + '</div></section>'
        if not text_only(content).strip() and not child_pages and not any(tag in content for tag in ("<img", "<a", "<table")):
            content = '<p>หน้านี้อยู่ระหว่างตรวจสอบข้อมูลจากต้นฉบับ กรุณาดูหัวข้ออื่นหรือสอบถามวิทยาลัย</p>'
        date = rec.get("date", "")[:10]
        type_label = "ข่าวย้อนหลัง" if rec["type"] == "post" else "ข้อมูลวิทยาลัย"
        body = f'<div class="page-hero"><div class="wrap"><span class="eyebrow">{type_label}</span><h1>{html.escape(title)}</h1>{f"<time datetime={date}>{date}</time>" if rec["type"] == "post" else ""}</div></div><div class="wrap content-layout"><article class="prose">{content}{child_html}</article></div>'
        if path == "/":
            body = homepage_body(content + child_html, posts)
            title = "วิทยาลัยนวัตกรรมการจัดการ"
        description = text_only(rec.get("content_html") or title)[:158] or title
        write_page(path, document(title, description, path, body, kind="NewsArticle" if rec["type"] == "post" else "WebPage", modified=rec.get("modified"), published=rec.get("date")))
        manifest.append({"id": rec["id"], "type": rec["type"], "title": title, "path": path, "date": date, "lastmod": rec.get("modified", "")[:10], "content_chars": len(text_only(rec.get("content_html") or "")), "rendered_chars": len(text_only(body))})
    latest = sorted(posts, key=lambda r: r.get("date", ""), reverse=True)
    cards = "".join(f'<a class="news-card" href="{html.escape(r["path"])}"><time>{html.escape(r.get("date", "")[:10])}</time><strong>{html.escape(r["title"])}</strong><span>อ่านข่าวย้อนหลัง →</span></a>' for r in latest)
    news_body = '<div class="page-hero"><div class="wrap"><span class="eyebrow">ข่าวและประกาศ</span><h1>ข่าวสาร RCIM</h1><p>ข่าวย้อนหลังจากเว็บไซต์เดิมและข่าวใหม่จากวิทยาลัย</p></div></div><div class="wrap section"><div class="news-grid">' + cards + '</div></div>'
    write_page("/news/archive/", document("ข่าวย้อนหลัง RCIM", "ข่าวและประกาศย้อนหลัง วิทยาลัยนวัตกรรมการจัดการ", "/news/archive/", news_body))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for row in manifest + [{"path": "/news/", "date": "2026-09-25"}, {"path": "/news/archive/", "date": "2026-09-25"}]:
        sitemap.append(f'<url><loc>{html.escape(DOMAIN + quote(row["path"], safe="/%"))}</loc><lastmod>{row.get("lastmod") or row["date"] or "2026-09-25"}</lastmod></url>')
    sitemap.append('</urlset>')
    (SITE / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")
    (SITE / "robots.txt").write_text(f'User-agent: *\nDisallow: /admin/\nSitemap: {DOMAIN}/sitemap.xml\nSitemap: {DOMAIN}/news/sitemap.php\n', encoding="utf-8")
    (AUDIT / "migration-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (AUDIT / "missing-media.txt").write_text("\n".join(sorted(missing)), encoding="utf-8")
    plugin_cases = [{"id": r["id"], "title": r["title"], "path": r["path"], "markers": sorted(set(re.findall(r"\[(?:embedpress|caption|__HEYPUBLISHER)[^\]]*\]|<iframe|<form", r.get("content_html") or "", flags=re.I)))} for r in records]
    (AUDIT / "plugin-dependent-content.json").write_text(json.dumps([r for r in plugin_cases if r["markers"]], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {len(pages)} pages and {len(posts)} historical posts; missing media references: {len(missing)}")


if __name__ == "__main__":
    main()
