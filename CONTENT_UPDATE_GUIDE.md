# Updating RCIM content

The public college pages are plain HTML in `site/`. The site owner reviews staff information and updates the relevant HTML file with AI assistance. The staff member does not need to edit code.

## Staff submission template

Copy this into a document in the relevant department folder in Google Drive:

```text
Department:
Page title:
Existing page URL (if updating one):
Responsible staff member:
Reviewed/approved by:
Requested publication date:
Last fact-check date:
Thai text (headings and paragraphs):
English text (if available):
Related links and official sources:
Documents to attach (file names and short descriptions):
Images to attach (file names, captions, alt text, and permission to publish):
What changed from the old page:
```

For a personnel profile, also supply the public name, title, department, office, public contact method, short biography, and approved portrait. Do not include private contact details. An owner should check current roles and image permission before publishing.

## Owner workflow

1. Save the approved text and media in the department's Google Drive folder. Keep originals there.
2. Resize public images to WebP. Put deployment copies under `site/media/`; that directory is intentionally outside GitHub.
3. Ask AI to update only the target page HTML. Provide the approved text and exact image path. Review the change against the staff submission.
4. Check the page on a phone and desktop, including links, document downloads, headings, and image alt text.
5. Commit the HTML/CSS change to GitHub and upload the changed files and media to hosting.

For **new news**, use `/admin/` instead of editing HTML. Save a draft first, review it, then publish. Historical news generated from the backup remains static and retains its original dates.

The parent [Website](https://drive.google.com/drive/folders/18gfeYqdvD5RWEDMGRF57wVxWKibOQBKq) folder exists. Department subfolders and access rights will be set up when staff owners and permissions are supplied.
