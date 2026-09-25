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
    "/mainrcim/": "/about-rcim/",
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
        return f'<p><a href="{url}">เปิดเอกสารหรือสื่อประกอบ</a></p>'
    source = re.sub(r"\[embedpress.*?\[/embedpress\][^\]]*\]", embed_link, source or "", flags=re.S | re.I)
    source = re.sub(r"\[/?caption[^\]]*\]", "", source, flags=re.I)
    source = source.replace("[object Object]", "")
    source = source.replace("[__HEYPUBLISHER_SUBMISSION_FORM_GOES_HERE__]", "<p>หากต้องการส่งบทความ กรุณาติดต่อวิทยาลัยเพื่อขอรายละเอียด</p>")
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
           ("สำหรับนักศึกษา", "/for-students-rcim/"), ("ข่าวสาร", "/news/"),
           ("ติดต่อ", "/page-id35/")]
    links = "".join(f'<a href="{u}">{esc(n)}</a>' for n, u in nav)
    home_css = '<link rel="stylesheet" href="/assets/home.css">' if path in ("/", "/masterdoctor/") else ""
    return f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | RCIM</title><meta name="description" content="{esc(description[:158])}"><link rel="canonical" href="{esc(canonical)}"><meta property="og:type" content="{'article' if kind == 'NewsArticle' else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description[:158])}"><meta property="og:url" content="{esc(canonical)}"><link rel="stylesheet" href="/assets/site.css">{home_css}<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")}</script></head><body><a class="skip" href="#main">ข้ามไปยังเนื้อหา</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="/"><img class="brand-mark-image" src="/media/2022/06/Logo-RCIM2019-TH-480.webp" width="52" height="52" alt=""><span><strong>RCIM</strong><small>วิทยาลัยนวัตกรรมการจัดการ</small></span></a><button id="menu-toggle" class="menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false">เมนู</button><nav id="site-nav" aria-label="เมนูหลัก">{links}<a class="nav-apply" href="/apply-online-rcim/">สมัครเรียน <span aria-hidden="true">↗</span></a></nav></div></header><main id="main">{body}</main><footer><div class="wrap footer-grid"><div><a class="footer-brand" href="/">RCIM</a><p>วิทยาลัยนวัตกรรมการจัดการ<br>มหาวิทยาลัยเทคโนโลยีราชมงคลรัตนโกสินทร์</p></div><div><strong>ติดต่อ</strong><p>96 หมู่ 3 ถนนพุทธมณฑลสาย 5<br>ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170</p><a href="tel:+6624416067">02-441-6067</a></div><div><strong>สำรวจเว็บไซต์</strong><a href="/masterdoctor/">หลักสูตร</a><a href="/for-students-rcim/">สำหรับนักศึกษา</a><a href="/news/">ข่าวสาร</a><a href="/page-id35/">ติดต่อ</a></div></div><div class="wrap footer-bottom"><span>© RCIM · มหาวิทยาลัยเทคโนโลยีราชมงคลรัตนโกสินทร์</span></div></footer><script src="/assets/site.js" defer></script></body></html>'''


def write_page(path, markup):
    target = local_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    formatted = LH.tostring(LH.fromstring(markup), encoding="unicode", method="html", pretty_print=True, doctype="<!doctype html>")
    target.write_text("\n".join(line.expandtabs(4).rstrip() for line in formatted.splitlines()) + "\n", encoding="utf-8")


def homepage_body(posts):
    routes = [
        ("01", "ผู้สนใจสมัครเรียน", "หลักสูตรและขั้นตอนการสมัคร", "/apply-online-rcim/"),
        ("02", "นักศึกษาปัจจุบัน", "บริการ เอกสาร และงานวิจัย", "/for-students-rcim/"),
        ("03", "งานวิจัยและวิชาการ", "ผลงานและข้อมูลวิชาการ", "/masterdoctor/research-academic/"),
    ]
    route_cards = "".join(
        f'<a class="route-card" href="{path}"><span class="route-number">{number}</span>'
        f'<span class="route-copy"><strong>{name}</strong><small>{desc}</small></span>'
        '<span class="route-arrow" aria-hidden="true">↗</span></a>'
        for number, name, desc, path in routes
    )
    programmes = [
        ("บริหารธุรกิจ", "MBA", "/masterdoctor/master/mba2/", "master"),
        ("รัฐประศาสนศาสตร์", "MPA", "/masterdoctor/master/mpa2/", "master"),
        ("ศึกษาศาสตร์", "M.Ed.", "/masterdoctor/master/med2/", "master"),
        ("การจัดการ", "MM", "/masterdoctor/master/mm2/", "master"),
        ("บริหารธุรกิจ", "DBA", "/masterdoctor/doctor/dba2/", "doctor"),
        ("รัฐประศาสนศาสตร์", "DPA", "/masterdoctor/doctor/dpa2/", "doctor"),
        ("บริหารการศึกษาและนวัตกรรม", "Ph.D.", "/masterdoctor/doctor/phd-eai/", "doctor"),
        ("การจัดการ", "DM", "/masterdoctor/doctor/dm2/", "doctor"),
    ]
    def programme_cards(level):
        return "".join(
            f'<a class="programme-card" href="{path}"><span class="programme-code">{code}</span>'
            f'<strong>{name}</strong><span class="card-arrow" aria-hidden="true">↗</span></a>'
            for name, code, path, item_level in programmes if item_level == level
        )
    recent = sorted(posts, key=lambda r: r.get("date", ""), reverse=True)[:3]
    news = "".join(
        f'<a class="news-card" href="{html.escape(r["path"])}"><time datetime="{html.escape(r.get("date", "")[:10])}">{html.escape(r.get("date", "")[:10])}</time>'
        f'<strong>{html.escape(r["title"])}</strong><span>อ่านรายละเอียด <span aria-hidden="true">↗</span></span></a>'
        for r in recent
    )
    return f'''<section class="home-hero" aria-labelledby="home-title">
      <div class="wrap hero-grid"><div class="hero-copy">
      <span class="eyebrow">มหาวิทยาลัยเทคโนโลยีราชมงคลรัตนโกสินทร์</span>
      <h1 id="home-title">วิทยาลัยนวัตกรรม<br>การจัดการ</h1>
      <p>หลักสูตรระดับบัณฑิตศึกษาที่เชื่อมความรู้ การวิจัย และการทำงานจริง</p>
      <div class="hero-actions"><a class="button-primary" href="/masterdoctor/">ดูหลักสูตร <span aria-hidden="true">→</span></a><a class="button-outline" href="/apply-online-rcim/">สมัครเรียน <span aria-hidden="true">→</span></a></div>
      </div><div class="hero-photo" role="img" aria-label="อาคารมหาวิทยาลัยเทคโนโลยีราชมงคลรัตนโกสินทร์"><span>RCIM <b>GRADUATE COLLEGE</b></span></div></div>
    </section>
    <section class="section about-intro" aria-labelledby="about-title"><div class="wrap">
      <div class="section-heading"><span class="eyebrow">เกี่ยวกับวิทยาลัย</span><h2 id="about-title">รู้จัก RCIM</h2><p>พื้นที่เรียนรู้สำหรับผู้ที่ต้องการต่อยอดความรู้และสร้างความก้าวหน้า</p></div>
      <div class="about-two-col"><div class="about-text"><p>วิทยาลัยนวัตกรรมการจัดการ เป็นส่วนหนึ่งของมหาวิทยาลัยเทคโนโลยีราชมงคลรัตนโกสินทร์ เปิดการศึกษาระดับปริญญาโทและปริญญาเอก ด้านการบริหาร การจัดการ และการศึกษา</p><p>ค้นหาข้อมูลหลักสูตร งานวิชาการ บุคลากร และบริการสำหรับนักศึกษาได้จากเว็บไซต์นี้</p><a class="section-link" href="/about-rcim/">เกี่ยวกับวิทยาลัย <span aria-hidden="true">→</span></a></div><div class="about-image"><img src="/media/2022/05/BG-RCIM-2022.10-1200.webp" width="675" height="1200" loading="lazy" decoding="async" alt="ประติมากรรมในพื้นที่มหาวิทยาลัย"><span>RCIM · ศาลายา</span></div></div>
    </div></section>
    <section class="routes-section" aria-labelledby="routes-title"><div class="wrap section"><div class="section-heading"><span class="eyebrow">เริ่มต้นที่นี่</span><h2 id="routes-title">ค้นหาข้อมูลที่คุณต้องการ</h2></div><div class="route-grid">{route_cards}</div></div></section>
    <section class="programmes-section" aria-labelledby="programmes-title"><div class="wrap section"><div class="section-heading"><span class="eyebrow">หลักสูตร RCIM</span><h2 id="programmes-title">หลักสูตรระดับบัณฑิตศึกษา</h2><p>เลือกหลักสูตรที่ตรงกับเป้าหมายของคุณ</p></div>
    <div class="programme-group"><div class="group-heading"><span>01</span><h3>ปริญญาโท</h3></div><div class="programme-grid">{programme_cards('master')}</div></div>
    <div class="programme-group"><div class="group-heading"><span>02</span><h3>ปริญญาเอก</h3></div><div class="programme-grid">{programme_cards('doctor')}</div></div><div class="section-action"><a class="section-link" href="/masterdoctor/">ดูข้อมูลหลักสูตรทั้งหมด <span aria-hidden="true">→</span></a></div></div></section>
    <section class="people-section" aria-labelledby="people-title"><div class="wrap section"><div class="section-heading"><span class="eyebrow">ชุมชน RCIM</span><h2 id="people-title">คณาจารย์และบุคลากร</h2><p>รู้จักผู้สอนและทีมงานของวิทยาลัย</p></div><div class="people-grid"><a class="people-card" href="/about-rcim/structure-rcim/college-professor/"><span class="people-icon">อ</span><strong>คณาจารย์</strong><span>ดูข้อมูลคณาจารย์ →</span></a><a class="people-card" href="/about-rcim/structure-rcim/personnel/"><span class="people-icon">บ</span><strong>บุคลากร</strong><span>ดูข้อมูลบุคลากร →</span></a></div></div></section>
    <section class="home-news" aria-labelledby="news-title"><div class="wrap section"><div class="section-heading"><span class="eyebrow">ข่าวและประกาศ</span><h2 id="news-title">ข่าวสารจากวิทยาลัย</h2><p>ติดตามประกาศและกิจกรรมล่าสุด</p></div><div class="news-grid">{news}</div><div class="section-action"><a class="section-link" href="/news/">ดูข่าวทั้งหมด <span aria-hidden="true">→</span></a></div></div></section>
    <section class="contact-section" aria-labelledby="contact-title"><div class="wrap section"><div class="section-heading"><span class="eyebrow">ติดต่อ RCIM</span><h2 id="contact-title">ติดต่อวิทยาลัย</h2></div><div class="campus-grid"><div class="campus-card"><h3>ศาลายา</h3><p>96 หมู่ 3 ถนนพุทธมณฑลสาย 5 ตำบลศาลายา อำเภอพุทธมณฑล จังหวัดนครปฐม 73170</p><a href="tel:+6624416067">02-441-6067</a><a href="tel:+66924428000">092-442-8000</a><a href="tel:+66924429000">092-442-9000</a></div><div class="campus-card"><h3>วังไกลกังวล</h3><p>ถนนเพชรเกษม ตำบลหนองแก อำเภอหัวหิน จังหวัดประจวบคีรีขันธ์ 77110</p><a href="tel:+66924427000">092-442-7000</a></div></div><div class="section-action"><a class="section-link" href="/page-id35/">ที่ตั้งและช่องทางติดต่อทั้งหมด <span aria-hidden="true">→</span></a></div></div></section>'''


def programmes_body():
    groups = [
        ("ปริญญาโท", [
            ("MBA", "บริหารธุรกิจ", "/masterdoctor/master/mba2/"),
            ("MPA", "รัฐประศาสนศาสตร์", "/masterdoctor/master/mpa2/"),
            ("M.Ed.", "ศึกษาศาสตร์", "/masterdoctor/master/med2/"),
            ("MM", "การจัดการ", "/masterdoctor/master/mm2/"),
        ]),
        ("ปริญญาเอก", [
            ("DBA", "บริหารธุรกิจ", "/masterdoctor/doctor/dba2/"),
            ("DPA", "รัฐประศาสนศาสตร์", "/masterdoctor/doctor/dpa2/"),
            ("Ph.D.", "บริหารการศึกษาและนวัตกรรม", "/masterdoctor/doctor/phd-eai/"),
            ("DM", "การจัดการ", "/masterdoctor/doctor/dm2/"),
        ]),
    ]
    sections = []
    for name, items in groups:
        links = "".join(
            f'<a class="programme-card" href="{path}"><span class="programme-code">{code}</span><strong>{label}</strong><span class="card-arrow" aria-hidden="true">↗</span></a>'
            for code, label, path in items
        )
        sections.append(f'<section class="programme-group"><h2>{name}</h2><div class="programme-grid">{links}</div></section>')
    return '''<div class="page-hero"><div class="wrap"><nav class="breadcrumbs" aria-label="ตำแหน่งหน้า"><a href="/">หน้าหลัก</a><span aria-hidden="true">/</span><span>หลักสูตร</span></nav><span class="eyebrow">หลักสูตร RCIM</span><h1>หลักสูตรระดับบัณฑิตศึกษา</h1><p>สำรวจหลักสูตรปริญญาโทและปริญญาเอกของวิทยาลัยนวัตกรรมการจัดการ</p></div></div>''' + '<div class="wrap section programme-landing"><div class="programme-intro"><p>เลือกดูรายละเอียดหลักสูตรที่สนใจ พร้อมข้อมูลคุณวุฒิและช่องทางการสมัครเรียน</p><a href="/apply-online-rcim/">ข้อมูลการสมัครเรียน ↗</a></div>' + "".join(sections) + '<div class="programme-extra"><a href="/masterdoctor/qualifications-certified-rcim/">ข้อมูลการรับรองคุณวุฒิและหลักสูตร ↗</a><a href="/masterdoctor/research-academic/">งานวิจัยและวิชาการ ↗</a></div></div>'


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
            content = '<p>หน้านี้อยู่ระหว่างปรับปรุงข้อมูล กรุณาดูหัวข้ออื่นหรือสอบถามวิทยาลัย</p>'
        date = rec.get("date", "")[:10]
        section = path.strip("/").split("/")[0]
        labels = {"about-rcim": "เกี่ยวกับวิทยาลัย", "masterdoctor": "หลักสูตรและวิชาการ",
                  "for-students-rcim": "สำหรับนักศึกษา", "apply-online-rcim": "การสมัครเรียน",
                  "page-id35": "ติดต่อวิทยาลัย"}
        type_label = "ข่าวสาร" if rec["type"] == "post" else labels.get(section, "ข้อมูล RCIM")
        section_url = "/news/" if rec["type"] == "post" else ("/" + section + "/" if section in labels else "/about-rcim/")
        crumb = f'<nav class="breadcrumbs" aria-label="ตำแหน่งหน้า"><a href="/">หน้าหลัก</a><span aria-hidden="true">/</span><a href="{html.escape(section_url)}">{type_label}</a></nav>'
        if path == section_url:
            crumb = '<nav class="breadcrumbs" aria-label="ตำแหน่งหน้า"><a href="/">หน้าหลัก</a><span aria-hidden="true">/</span><span> ' + type_label + '</span></nav>'
        body = f'<div class="page-hero"><div class="wrap">{crumb}<span class="eyebrow">{type_label}</span><h1>{html.escape(title)}</h1>{f"<time datetime={date}>{date}</time>" if rec["type"] == "post" else ""}</div></div><div class="wrap content-layout"><article class="prose">{content}{child_html}</article></div>'
        if path == "/":
            body = homepage_body(posts)
            title = "วิทยาลัยนวัตกรรมการจัดการ"
        elif path == "/masterdoctor/":
            body = programmes_body()
            title = "หลักสูตรระดับบัณฑิตศึกษา"
        description = text_only(rec.get("content_html") or title)[:158] or title
        write_page(path, document(title, description, path, body, kind="NewsArticle" if rec["type"] == "post" else "WebPage", modified=rec.get("modified"), published=rec.get("date")))
        manifest.append({"id": rec["id"], "type": rec["type"], "title": title, "path": path, "date": date, "lastmod": rec.get("modified", "")[:10], "content_chars": len(text_only(rec.get("content_html") or "")), "rendered_chars": len(text_only(body))})
    latest = sorted(posts, key=lambda r: r.get("date", ""), reverse=True)
    by_year = {}
    for post in latest:
        by_year.setdefault(post.get("date", "")[:4] or "อื่น ๆ", []).append(post)
    groups = []
    for year, items in by_year.items():
        rows = "".join(
            f'<a class="archive-row" href="{html.escape(r["path"])}"><time datetime="{html.escape(r.get("date", "")[:10])}">{html.escape(r.get("date", "")[:10])}</time><strong>{html.escape(r["title"])}</strong><span aria-hidden="true">↗</span></a>'
            for r in items
        )
        groups.append(f'<section class="archive-year"><div class="archive-year-heading"><h2>{year}</h2><span>{len(items)} รายการ</span></div><div class="archive-list">{rows}</div></section>')
    news_body = '<div class="page-hero"><div class="wrap"><nav class="breadcrumbs" aria-label="ตำแหน่งหน้า"><a href="/">หน้าหลัก</a><span aria-hidden="true">/</span><a href="/news/">ข่าวสาร</a></nav><span class="eyebrow">ข่าวสาร RCIM</span><h1>คลังข่าวและประกาศ</h1><p>ค้นหาข่าวและประกาศของวิทยาลัยตามปีที่เผยแพร่</p></div></div><div class="wrap section archive-page"><label class="search-label" for="archive-search">ค้นหาข่าว</label><input id="archive-search" class="archive-search" type="search" placeholder="พิมพ์หัวข้อข่าว" autocomplete="off"><p id="archive-empty" class="archive-empty" hidden>ไม่พบข่าวที่ตรงกับคำค้น</p>' + ''.join(groups) + '</div>'
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
