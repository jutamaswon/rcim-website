# RCIM website rebuild

This repository is for the **new** RCIM website. The intended design is plain static HTML/CSS for most pages and a small PHP/MariaDB CMS for news. Department staff provide structured content in Google Drive; the site owner reviews AI-assisted updates to the static pages.

## Current state

A local build is in `site/`: 73 legacy pages, 185 historical posts, a news archive, and a small PHP/MariaDB editor for new news. It is **not deployed**. The ignored `audit/` folder holds migration and verification reports. Media is stored separately in ignored `site/media/`.

## Build locally

Use Python 3.12 with Pillow and lxml. The import scripts read the supplied private backups but only create public content outputs:

1. Run `python tools/extract_wp_public.py` to extract published records from the SQL backup into ignored `audit/`.
2. Run `python tools/prepare_media.py` to resize backup images and copy public documents into ignored `site/media/`.
3. If internet access is available, run `python tools/build_site.py`, `python tools/recover_media.py`, then `python tools/build_site.py` again to recover public assets missing from the backup.
4. Run `python tools/verify_site.py` and review `audit/verification.json`, `audit/missing-media.txt`, and `audit/media-recovery-results.json`.

For an optional PHP syntax check, run `npm install --no-save --no-package-lock --prefix .tooling php-parser` followed by `node tools/check_php.cjs`. The `.tooling/` directory is ignored.

The static pages are generated HTML files and can be edited directly. To make repeatable changes, update the source data or generator and rebuild. `site/assets/site.css` controls the shared look.

## News setup on hosting

The server needs PHP **8.1 or newer** with PDO MySQL, GD WebP, and MariaDB 10. Upload the contents of `site/` to the web root and upload `site/media/` separately. Import `database/001_create_news.sql` into a new database. Copy `site/config.example.php` to `site/config.php` on hosting, fill in database credentials and a long random setup key, then open `/admin/setup.php` once to create the first editor. Remove the setup key from the config after the first editor exists. Visit `/admin/login.php` to publish new news. Keep `site/config.php` and all media outside GitHub.

New news uses `/news/`; historical articles retain their old slug URLs and are listed at `/news/archive/`. Apache rewrite support is needed for `/news/story/<slug>/`. If it is unavailable, use `/news/article.php?slug=<slug>` until routing is configured.

The hostname, Search Console, GA4, and domain switch remain deferred until account access and RCIM content review are available. See `DEPLOYMENT_CHECKLIST.md`.

## What belongs in GitHub

- New website source code, templates, and deployment instructions.
- New database **schema and migration files** for the news CMS.
- Site map, content model, SEO/AIO plan, and verification checklist.

## What stays outside GitHub

- Old WordPress database and uploads backups, XML export, and the KU reference site.
- Live database records, account details, configuration secrets, and environment files.
- Images and other media. Final resized images will be kept in the project media store and deployed to the website separately, using stable paths referenced by the HTML.

See [RCIM_REBUILD_PLAN.md](RCIM_REBUILD_PLAN.md) and [SEO_AIO_ANALYTICS_PLAN.md](SEO_AIO_ANALYTICS_PLAN.md).
