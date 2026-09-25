# RCIM website rebuild

This repository is for the **new** RCIM website. The intended design is plain static HTML/CSS for most pages and a small PHP/MariaDB CMS for news. Department staff provide structured content in Google Drive; the site owner reviews AI-assisted updates to the static pages.

## Current state

Planning and content audit. The new site has not been built or deployed.

## What belongs in GitHub

- New website source code, templates, and deployment instructions.
- New database **schema and migration files** for the news CMS.
- Site map, content model, SEO/AIO plan, and verification checklist.

## What stays outside GitHub

- Old WordPress database and uploads backups, XML export, and the KU reference site.
- Live database records, account details, configuration secrets, and environment files.
- Images and other media. Final resized images will be kept in the project media store and deployed to the website separately, using stable paths referenced by the HTML.

See [RCIM_REBUILD_PLAN.md](RCIM_REBUILD_PLAN.md) and [SEO_AIO_ANALYTICS_PLAN.md](SEO_AIO_ANALYTICS_PLAN.md).
