# RCIM staging and launch checklist

## Before upload

- Review `audit/verification.json` and resolve or approve all missing content, media, and links.
- Have RCIM staff check personnel names, roles, photos, programmes, forms, admissions dates, and contact details.
- Export the final media directory separately from GitHub and keep a backup.
- Confirm the selected PHP version is 8.1+ and enables PDO MySQL and GD WebP.

## Staging

1. Back up the existing WordPress site and database; keep a rollback path.
2. Create a new MariaDB database and import `database/001_create_news.sql`.
3. Upload `site/` and `site/media/` to an isolated staging web root. Do not copy `audit/`, old backups, or `kuweb/`.
4. Create `site/config.php` from the example with database credentials and a random setup key. Restrict file permissions to the hosting account.
5. Open `/admin/setup.php`, create the first editor, then remove the setup key from config.
6. Publish a test news article with a cover image; verify `/news/`, its article URL, `/api/news.php`, and `/news/sitemap.php`.
7. Check representative static pages, Thai URLs, PDFs, images, mobile menu, keyboard use, and redirects. Verify `.htaccess` rewrite works.
8. Add caching headers for static assets in cPanel and enable HTTPS. Check that administrative pages are not indexed.

## Launch after RCIM approval

- Point the domain to the new web root and test the old URL inventory.
- Create a Search Console Domain property and submit `/sitemap.xml` and `/news/sitemap.php`.
- Create GA4, add its measurement ID, and verify page views and consent requirements with RCIM.
- Monitor 404s, indexing, page speed, and news publishing during the first weeks.

No hosting or Google services are connected by this local build.
