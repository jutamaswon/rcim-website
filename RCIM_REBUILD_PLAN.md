# RCIM website rebuild plan

Status: local build in progress. A replacement site has been generated locally but has not been published. See `README.md` and ignored `audit/verification.json` for current findings.

GitHub scope: the new website source and its new database schema/migrations only. Historical WordPress records, backups, the KU reference, secrets, and images remain outside GitHub. See `README.md`, `.gitignore`, and `SEO_AIO_ANALYTICS_PLAN.md`.

## What has been checked

- Current public site: <https://www.rcim.in.th/>. The homepage and its menu were inspected on 25 September 2026.
- Supplied export: `WordPress.2026-09-25.xml` (9.3 MB). It contains 73 published page records and 453 attachment records, but no `post` records. Sixty-six page records contain `_elementor_data`; 69 have non-empty rendered-content fields. Attachment records give URLs, not the actual image or document bytes. These counts describe the export, not the entire live site.
- Supplied backups: `backup_2026_09_25_12_36_12-f645b106-db.sql.gz` (compressed database) and `backup_2026_09_25_12_36_12-f645b106-uploads.zip` (uploads). The database has 95 tables, including WordPress posts and post metadata. The ZIP has 2,415 entries (about 693 MB uncompressed), including images and 127 PDFs. Its `hestia/` and `elementor/` directories are inside uploads; this is not a full theme or plugin backup.
- Google Drive folder: [Website](https://drive.google.com/drive/folders/18gfeYqdvD5RWEDMGRF57wVxWKibOQBKq) was created in My Drive. It is currently empty.
- Current hosting supplied by RCIM: RH-Sun shared hosting for `www.rcim.in.th`, with 100 GB SSD, unmetered advertised bandwidth, PHP 5.2–8.5, MariaDB 10, and cPanel support for a persistent Node.js/Express app on Node 18 or newer. The host does **not** permit `npm install` over SSH/Terminal. CPU 850% and RAM 11 GB are package allocations, not measured site performance. Quoted annual price is THB 10,190 before 7% VAT.
- Previous KU project: `kuweb/` in this project folder. It has static public pages and a PHP/MySQL content workflow for news, testimonials, and research. It is a reference for content operations, not a final RCIM architecture decision.
- Requested methods: GitHub Spec Kit for written requirements, plan, tasks, and verification; UI UX Pro Max for a design system and interface review.

## Capture method

Use an `.mhtml` copy as an optional visual snapshot of each important public page. It is useful for later inspection, but cannot establish that all pages, PDF files, images, menus, and external destinations were captured. The required archive is a URL and asset inventory plus original files and extracted page content. Use the database backup for the fuller WordPress content and Elementor post metadata, the uploads ZIP for original media and documents, and the XML as a comparison source. Check all of these against the rendered site. Record capture date, source URL, page title, content type, status, and checksum for each item. Preserve the original URL even when the new URL changes.

The in-app Browser did not provide an `.mhtml` export during this planning session; no `.mhtml` files are claimed as saved.

## Phase 1 — Inventory and preserve the old site

1. Parse the database backup in a controlled local extraction. Inventory published posts, pages, custom post types, Elementor widget data, menus, taxonomy, redirects if stored, and media references. Do not publish database user records, credentials, or private settings.
2. Inventory and checksum the uploads ZIP without assuming it contains the theme or plugins. Map database media references to the actual files, including PDFs and personnel photos.
3. Parse the supplied WordPress XML as a cross-check. Its 73 pages and 453 attachment references are a partial subset of the available backup.
4. Crawl the public site independently, including menus, pagination, news categories, galleries, personnel, programmes, student forms, and PDF downloads. Compare the live inventory with the database, uploads ZIP, and XML. If an Elementor kit later becomes available, use it as an additional source, not as a prerequisite.
5. Save each source URL in a content register with its type, title, department or owner, last visible update, target URL, asset links, capture status, and review status. Keep original HTML or text and original downloaded files. Save MHTML for important pages where supported.
6. Check duplicate and outdated pages separately. Keep historical content in the migration register; decide its new placement or an intentional redirect with an RCIM content owner.

**Gate:** Every discovered public URL and downloadable file has an inventory row. Unreachable URLs are listed as exceptions, not silently excluded.

## Phase 2 — Department content collection in Google Drive

Use the created `Website` folder as the parent for the proposed migration folders (to be created when the department structure is agreed):

```text
Website/
  00-Inventory-and-status/
  01-College-and-governance/
  02-Programmes-and-admissions/
  03-Personnel/
  04-Students-and-forms/
  05-Research-and-publications/
  06-News-and-activities/
  07-Quality-and-plans/
  08-Alumni/
  09-Contact-and-campuses/
  90-Original-site-archive/
```

Each department folder gets a short structured intake template for page title, Thai and English text where applicable, responsible staff member, approval status, desired publication date, source URL, and linked images/documents. Personnel entries need name, title, department, public contact details, biography, photograph, image caption/alt text, and confirmation that the photo may be published. Staff supply facts and files in Google Drive; they do not edit website code. The site owner uses AI assistance to create or update the corresponding static HTML, reviews the change, and uploads the finished files. Restrict staff access by their existing university permissions.

**Gate:** Each department confirms its assigned rows and explicitly marks missing items, revisions, or approved archival decisions.

## Phase 3 — Specify and design

Use Spec Kit's constitution, specification, technical plan, task list, and convergence review. Include content completeness, accessibility, mobile use, performance, SEO, and editorial workflow as acceptance criteria. Use UI UX Pro Max to establish RCIM colours, Thai typography, spacing, navigation, responsive patterns, and accessible components. Review prototypes with staff and student users before page implementation.

**Gate:** RCIM signs off the site map, content model, design system, and publishing workflow.

## Phase 4 — Build

Build most public pages as plain static HTML and CSS, following the easy-to-understand structure of the KU site. Personnel, programme, college, student, and document pages are updated from staff-supplied structured data with AI assistance, then reviewed and deployed as files. Keep JavaScript small and avoid a site-wide framework or Node runtime.

Build a small, single-purpose PHP/MariaDB headless CMS for news only. Its protected admin form manages title, date, category, summary, body, cover image, attachments, draft/published status, and URL slug. It stores news in MariaDB and exposes a simple JSON endpoint if needed; public news listing and article pages render HTML on the server so text and metadata are available without JavaScript. Keep news administration separate from the static pages. Use a currently supported PHP version available on the host, proper password hashing, session protection, CSRF protection, image/file validation, and database backups. The KU project's news workflow can guide the interface, but its old PHP 5.4 implementation must be modernized.

Optimize approved images into responsive derivatives before deploying them to the website; retain originals outside GitHub. Use responsive sizes and lazy loading, cache static files, and avoid large third-party embeds above the fold. Provide semantic headings, descriptive links, keyboard navigation, Thai language metadata, page titles and descriptions, canonical URLs, XML sitemap, robots rules, and appropriate structured data. Keep original document links working or redirect them to their verified new locations. Follow `SEO_AIO_ANALYTICS_PLAN.md` for content, redirects, Google Search Console, and GA4 measurement.

**Gate:** Core pages work on desktop and mobile; a site owner can update a static page from a staff submission and publish a news item without developer tools; the agreed performance and accessibility checks pass.

## Phase 5 — Prove migration completeness

Compare the old-site inventory with the new site row by row: page text, personnel, images, PDFs, forms, dates, links, and redirects. Run an automated URL/link check and manual review of representative pages from every section. Publish a discrepancy report with owner and resolution. Preserve historical dates; do not silently change old announcements into current announcements.

**Gate:** Every inventory row is marked migrated, intentionally redirected, or archived with written approval; no unresolved critical content gaps or broken links remain.

## Phase 6 — Launch and maintain

Back up the old site and final content register, establish analytics/search-console ownership, stage the new site, then switch the domain after acceptance. Monitor errors, broken links, indexing, and performance after launch. Keep the Google Drive register as the editorial source archive and document the staff update process.

## Initial RCIM content areas observed

The public menu currently exposes college information and governance, executives/faculty/personnel, press releases, activity galleries, newsletters, alumni, eight master's and doctoral programme pages, admissions, quality/plans, research, student downloads and calendar, and contact details. This is only an initial menu inventory; the full crawl in Phase 1 determines the final page and file count.

## Information needed before implementation

- The database and uploads backups are present. A theme/plugin backup is not required for content extraction; if any content comes from plugin-only configuration, identify it in the live-site comparison.
- The Google Drive account or shared drive where migration folders should be created, plus department editors and approvers.
- cPanel/file deployment method, domain/DNS owner, and whether the current site must remain publicly available during the rebuild. Confirm which PHP versions are actually selectable for this account and what backup/restore access is available.
- Current official RCIM branding and who can approve personnel photos and programme facts.
