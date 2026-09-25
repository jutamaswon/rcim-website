# RCIM migration status — 25 September 2026

## Local build

- 73 published WordPress pages and 185 published news posts are generated as static HTML at their original URL paths.
- A new responsive homepage, historical news archive, sitemap, robots rules, canonical metadata, and a news-only PHP/MariaDB editor are built locally.
- 605 images have optimized WebP copies. Their source images total about 322 MB; the generated WebP files total about 26 MB. Another 201 public documents are retained as downloads. All media stays outside GitHub and must be uploaded separately.
- The verifier reports zero missing generated pages and zero broken **local** links. PHP syntax has been parsed for all 11 PHP files.
- A separate live-site check returned HTTP 200 for all 258 migrated public page and post URLs. This confirms URL coverage, not word-for-word or image-level equivalence.

## Open migration gaps

- 121 public media references remain unresolved. The supplied uploads ZIP omits several upload years; some missing files return 404 on the current RCIM site. The exact URLs and recovery results are in ignored `audit/` reports for staff review.
- Content that depended on WordPress plugins needs visual review. The build converts embedded documents/media to direct links where possible and logs plugin-dependent records in `audit/plugin-dependent-content.json`.
- Staff must verify current personnel, programme, form, admissions, and contact facts. Old announcements retain their historical dates.
- The PHP news workflow is syntax checked but cannot be tested end to end until MariaDB/PHP staging is available.
- Hosting credentials, publication approval, Search Console ownership, and GA4 ID are not yet available, so the site is not deployed or monitored by Google.

The migration is a reviewable local build, not a claim that every old asset or plugin feature is present. Use `DEPLOYMENT_CHECKLIST.md` for the remaining staging and launch steps.
