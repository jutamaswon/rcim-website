# RCIM website replacement specification

## User stories

- A student can find programmes, forms, admissions, announcements, and contact details on a phone.
- A prospective student can read programme information through search without JavaScript.
- An RCIM editor can revise static information from staff submissions and publish new news through a protected form.
- A migration reviewer can compare every legacy public URL against the new site.

## Requirements

1. Preserve 73 published pages and 185 published posts from the September 2026 backup at their original paths where possible.
2. Reproduce public text, links, dates, documents, and optimized images. Log absent or plugin-dependent content.
3. Provide homepage, navigation, article pages, and historical news archive.
4. Provide a PHP/MariaDB news-only admin with draft/publish, title, date, summary, body, cover image, and slug.
5. Provide server-rendered new news pages and a JSON feed.
6. Include sitemap, robots, canonical tags, Organization schema, and responsive images.
7. Keep uploads, backups, KU project, private data, and secrets outside GitHub.

## Acceptance

- Every public page/post ID appears once in the migration manifest.
- Initial HTML contains main content and works without JavaScript.
- Mobile layout and keyboard navigation work.
- Missing media and links are reported.
- New news publication is verified on staging.

Hosting credentials, domain switch, Search Console, GA4, staff Drive access, and official photo/fact approval remain deferred.
