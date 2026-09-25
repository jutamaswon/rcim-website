# RCIM website design

The interface follows UI UX Pro Max guidance for clear hierarchy, navigation, contrast, keyboard use, and responsive layouts. The visual direction is a restrained institutional grid with RCIM pink as the action colour. The supplied public RCIM logo appears in the header; brand approval remains a launch check.

## Page flow

1. Home: purpose and primary action → routes for applicants, students, and researchers → master's and doctoral programmes → news → college and contact.
2. Programme landing: brief introduction → master's courses → doctoral courses → qualification, research, and application links.
3. Inner page: breadcrumb → page title → readable content → related child pages.
4. News archive: search → year groups → compact dated rows. All article links remain in the HTML for search engines and visitors without JavaScript.

## Design tokens

- Text/navy: `#17283a` and `#14263b`.
- RCIM action pink: `#7b194c`; accent: `#a51f62`.
- Warm neutral surface: `#f7f5f2`; border: `#dce1e5`.
- Thai-capable system type: Tahoma, Noto Sans Thai, Arial; body starts at 16 px with 1.75 line height.
- Maximum content width: 1200 px; article width: 900 px.

## Implementation

- Shared rules are in `site/assets/site.css`; home and programme landing rules are in `site/assets/home.css`.
- Navigation and archive search use the small `site/assets/site.js` file. News search is progressive enhancement; links work without it.
- Buttons and menu controls are at least 44 px high, links have visible focus, and the mobile menu exposes its expanded state.
- Generated images use WebP, dimensions, and lazy loading. The home hero uses CSS and text rather than a large decorative download.
- Check 375 px, 768 px, 1024 px, and 1440 px layouts when changing shared styles. Do not allow horizontal scrolling.

## Content rule

Treat this as the RCIM website. Write labels as normal college content. Use descriptive headings and link text. Staff should review programme names, personnel details, dates, and campus contact information before launch.
