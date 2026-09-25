# RCIM website handoff

Updated: 25 September 2026. Use this file to resume the project. The latest website implementation was committed and pushed to the private GitHub repository [jutamaswon/rcim-website](https://github.com/jutamaswon/rcim-website), branch `main`, as `4741b61` (`Apply KU design patterns to RCIM site`).

## Goal and decisions

- Build a **new RCIM website** at `https://www.rcim.in.th`, with static HTML/CSS for ordinary pages and a small PHP/MariaDB CMS only for new news.
- Keep editing simple for a site owner who understands basic PHP and HTML. Staff will supply structured content and personnel photos; AI-assisted edits to static pages are reviewed before publication.
- Use the supplied `kuweb/` project as a layout reference. The current design adapts its navy banner, centered introductions, two-column overview, rounded cards, people section, news, and contact flow, using RCIM colours, copy, URLs, and optimized RCIM images. The KU folder lacks its referenced image assets; no KU images were copied.
- The public website must read as RCIM's own site. Do not show labels such as “ข้อมูลจากเว็บไซต์เดิม”.
- GitHub holds only the new website, its news database schema, and documentation. Do not commit the WordPress database, export, uploads, live data, secrets, or pictures.

## Current build

- `site/` contains 73 published pages and 185 published historical posts at the mapped public URLs, a redesigned homepage, a programme landing page, and a searchable news archive.
- `site/assets/site.css` controls shared pages; `site/assets/home.css` controls the homepage and programme landing; `site/assets/site.js` handles the mobile menu and archive search.
- `tools/build_site.py` regenerates static HTML from the ignored public-content extract and WordPress export. Direct edits to generated HTML may be overwritten by the next build; update the generator for repeatable changes.
- `site/admin/`, `site/news/`, `site/api/`, and `database/001_create_news.sql` provide the news-only PHP/MariaDB CMS. It has not been run against a staging database.
- `site/media/` contains optimized public WebP images and documents. It is ignored by Git and must be transferred separately for staging/deployment.
- The [Google Drive Website folder](https://drive.google.com/drive/folders/18gfeYqdvD5RWEDMGRF57wVxWKibOQBKq) exists. Department/staff subfolders and structured content collection were deferred until the user has that information.

## Last verification

- `tools/verify_site.py`: 73/73 pages and 185/185 posts generated; zero missing generated pages and zero broken local links.
- `node tools/check_php.cjs`: syntax parsed for all 11 PHP files.
- Browser review: homepage and programme page at 375, 768, 1024, and 1440 px; no horizontal overflow. Mobile navigation and archive search worked.
- Prior live URL check returned HTTP 200 for all 258 mapped public page/post URLs. This verifies URL coverage, not full editorial equivalence.
- `audit/verification.json` still reports 121 unresolved media references and 120 references to old upload URLs. The supplied uploads archive omits files from some years; a number of source URLs also return 404. See ignored `audit/missing-media.txt` and `audit/media-recovery-results.json`.

## How to resume locally

1. Open this workspace and read `README.md`, `MIGRATION_STATUS.md`, and `DESIGN_SYSTEM.md`.
2. Check Git status before editing. The last saved state was clean at `4741b61`.
3. For repeatable page changes, edit `tools/build_site.py` and the CSS files, then rebuild with Python 3.12 (Pillow and lxml required): `python tools/build_site.py`.
4. Run `python tools/verify_site.py` and `node tools/check_php.cjs`. On this Windows host, `python` may not be on PATH; the bundled interpreter used here was `C:\Users\wjuta\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
5. Preview with `python -m http.server 8765 --directory site` and open `http://localhost:8765/`. The local Python server displays static pages only; it does not execute the PHP news CMS.
6. Keep `site/media/`, `audit/`, `kuweb/`, `WordPress.2026-09-25.xml`, and `backup_2026_09_25_12_36_12-f645b106-*` out of Git.

## Next work before launch

1. Have RCIM staff review programme descriptions, personnel names/roles/photos, admissions dates, forms, campus contacts, and all pages that depended on Elementor or other plugins.
2. Resolve or explicitly approve the 121 missing media references. Verify image quality and document access on representative pages.
3. Build an isolated staging site on RH-Sun hosting. The chosen architecture needs static hosting, PHP 8.1+, PDO MySQL, GD WebP, MariaDB 10, and Apache rewrite support; it does not require a persistent Node server or `npm install` on hosting.
4. Import `database/001_create_news.sql`, configure `site/config.php` on staging, create the first news editor, and test publish/edit/cover-image/API/sitemap flows end to end.
5. After RCIM approves launch and provides access, set up Search Console and GA4 and follow `SEO_AIO_ANALYTICS_PLAN.md` and `DEPLOYMENT_CHECKLIST.md`.

The site has **not** been deployed to `www.rcim.in.th`. Hosting credentials, Search Console ownership, and a GA4 measurement ID were not available at this checkpoint.
