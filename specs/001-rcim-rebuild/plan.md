# Implementation plan

- `tools/`: local import, media preparation, static build, and audit.
- `audit/`: ignored private inventories and verification reports.
- `site/`: deployable static pages and small PHP news application.
- `site/media/`: separately deployed and ignored by GitHub.
- `database/`: new news schema only.

Build static pages from public backup records; use WordPress XML for exact page paths. Preserve post slug paths and original dates. Convert year/month upload images to WebP, keeping documents at stable local paths. Use PHP 8.1+ and MariaDB 10 for new news, with no Node dependency on the host. Validate record counts, links, media, representative pages, and the PHP workflow on staging.
