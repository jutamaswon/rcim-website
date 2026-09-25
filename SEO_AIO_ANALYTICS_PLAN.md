# RCIM SEO, AI visibility, and Google measurement plan

Status: planning. Values, accounts, tags, and ownership must be verified before launch.

## Goals

1. Preserve discoverability of every useful page and document from the old RCIM site.
2. Help prospective students find accurate programme, admission, fee, timetable, and contact information in Thai, with English pages only where approved translations exist.
3. Make factual RCIM content easy for search engines and AI search features to interpret and cite.
4. Measure search visibility, visits, and useful actions without sending personal information to analytics.

## 1. Baseline and migration

- Before launch, record current indexed pages, top search queries/pages, search clicks/impressions, and traffic sources if existing Google access is available.
- Complete the old-to-new URL map from the database, uploads, XML, and live-site inventory. Give each old URL a destination: retained, permanent redirect, or explicitly archived.
- Preserve original publication dates for news and historical documents. Fix broken internal links and missing assets before launch.
- Keep a tested rollback copy of the old site and publish the new site first on a staging URL blocked from indexing.

## 2. Technical SEO

- Serve each important page and news article as complete HTML without requiring JavaScript to reveal the main text.
- Use one clear page title, meta description, H1, and canonical URL per page. Set Thai as the document language; add `hreflang` only for real translated equivalents.
- Build XML sitemap(s) for static pages, news, and important documents; update the news sitemap when an item is published. Exclude drafts, admin URLs, and duplicate pages.
- Allow crawling of public content in `robots.txt`. Keep admin and staging out of search. Do not use robots blocking as a substitute for access control.
- Use permanent redirects for changed URLs and test all old URLs after launch. Link related pages with descriptive text and breadcrumbs.
- Add structured data only where it matches visible content and a supported use case: college/organization identity, breadcrumbs, and news articles as appropriate. Validate it before launch.

## 3. Content for people and AI search

- Give each programme a self-contained page with its official name, degree, location, delivery mode, entry requirements, curriculum summary, fees, application steps, key dates, responsible office, and last-reviewed date. Staff must verify facts before publication.
- Use plain language, descriptive headings, concise answers to common questions, and tables for comparable facts. Keep important information as selectable HTML text, including facts also present in posters or PDFs.
- Name RCIM, the university, and the relevant programme consistently. Link to official source documents and show an owner/contact point for corrections.
- Review AI-drafted text against approved department data. Avoid unverified claims, copied boilerplate, hidden text, and fake FAQ content.
- Do not add an `llms.txt` file or special AI markup merely to seek Google AI inclusion. Google's guidance says ordinary Search eligibility and good SEO remain the basis for AI Overviews and AI Mode; there are no extra technical requirements.

## 4. Image and loading performance

- Keep original approved photos outside GitHub. Generate appropriately sized WebP/AVIF derivatives and a JPEG fallback where needed. Store the source filename, licence/approval, dimensions, and final URL in a media manifest.
- Use `srcset`/`sizes`, explicit width and height, meaningful alt text, and lazy loading below the fold. Load the main visible image promptly rather than lazy loading it.
- Set page-weight and Core Web Vitals targets during the design prototype, then test on mobile network conditions. Avoid autoplay video and large third-party scripts on the landing page.

## 5. Google measurement

- Create or reuse a university-owned **Google Search Console** Domain property for `rcim.in.th`, verify it through DNS, and submit the sitemap. Monitor indexing, crawl errors, search queries/pages, clicks, impressions, and Core Web Vitals.
- Create or reuse a university-owned **Google Analytics 4** property and web data stream. Add one Google tag to public pages and the news templates; exclude admin/staging traffic and configure internal-traffic filtering where possible.
- Define a small set of useful events: application-link click, phone click, email click, programme PDF download, and completed application only if the application system can report it accurately. Do not send names, phone numbers, email addresses, or form contents to GA4.
- Link Search Console and GA4 when account ownership is settled. Use a simple monthly report for organic visits, search visibility, popular programme pages, admissions actions, broken pages, and mobile performance. Check whether current Search Console AI-feature reporting is available in the university account and include it if it is.
- Verify tags and events on staging before launch, then confirm live data and sitemap processing after domain cutover. Decide the site's privacy notice and consent approach with the university before enabling production measurement.

## Acceptance checks

- Every migrated public URL is mapped, and redirects and linked documents work.
- All public templates render meaningful text, titles, canonicals, and relevant metadata in the initial HTML.
- Search Console can fetch the sitemap and inspect representative pages; GA4 receives page views and the agreed non-personal events.
- Mobile performance and accessibility are reviewed on home, programme, personnel, document, and news templates.
- A monthly owner is assigned to review Search Console and GA4 and fix content or technical issues.

## Primary guidance

- [Google Search Essentials](https://developers.google.com/search/docs/essentials)
- [Google AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Google Analytics 4 website setup](https://support.google.com/analytics/answer/14183469?hl=en)
- [Search Console Domain property](https://support.google.com/webmasters/answer/10431861?hl=en)
