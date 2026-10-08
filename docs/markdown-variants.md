# Publishing Markdown variants of pages

Optional site-side work. A curated `llms.txt` is useful with plain HTML links;
Markdown variants only make the linked pages cheaper for an agent to read. They
do not promise crawling, citations, or rankings.

## What the proposal asks for

From [llmstxt.org](https://llmstxt.org/):

- A clean Markdown version of a page at the same URL, either with `.md`
  appended (`/guide.html` → `/guide.html.md`) or with the extension replaced
  (`/guide.md`). For URLs without a file name: `index.html.md` or `index.md`
  (`/about/` → `/about/index.html.md`).
- Two link relations to make them discoverable:
  `rel="alternate" type="text/markdown"` points from a page to its Markdown
  version, and `rel="describedby"` points to the `llms.txt` that covers it.
  Both work as an HTML `<link>` or as an HTTP `Link:` header.

```html
<link rel="alternate" type="text/markdown" href="https://example.com/guide.html.md">
<link rel="describedby" href="https://example.com/llms.txt">
```

## Rules for a variant worth linking

1. **Same content** as the HTML page — the article body, not a stub, and not
   the navigation, cookie banner, or comments.
2. **Same origin** as the page and the `llms.txt`.
3. Served as `text/markdown; charset=utf-8` (or `text/plain`), status `200`.
   A missing variant must return `404`, not the HTML "not found" page with
   `200` — that soft 404 is the usual way a broken variant slips into a file.
4. Point search engines at the HTML page so the variant is not indexed as a
   duplicate: send `Link: <https://example.com/guide.html>; rel="canonical"`
   with the Markdown response.
5. Public content only. A variant is another public URL: do not expose drafts
   or pages that require a login.

## By platform

**Static site generators.** The simplest case: the page already has a Markdown
source. Add a build step that writes it next to the generated HTML under the
variant name (`guide/index.html.md` beside `guide/index.html`), stripped of
front matter and template shortcodes. Check the output file, not the source.

**Web server.** Make sure `.md` files get a text media type and UTF-8. For
nginx:

```nginx
location ~ \.md$ {
    types { }
    default_type text/markdown;
    charset utf-8;
    charset_types text/markdown;
}
```

**WordPress and other CMSs.** Core WordPress does not serve Markdown versions
of posts. It takes a plugin or custom code that renders the post content to
Markdown at the variant URL. Whatever you use, verify the result with the
checks below before linking it — and note that an SEO plugin's auto-generated
`llms.txt` is a separate feature (see
[replace-rank-math-llms.md](replace-rank-math-llms.md)).

## Verify before linking

```bash
curl -sS -o /dev/null -w "%{http_code} %{content_type}\n" https://example.com/guide.html.md
```

Expect `200 text/markdown; charset=utf-8`. Then open the body and confirm it
is Markdown with the page's content.

After the variants are in `llms.txt`, the linter can probe every same-origin
link and flags `.md` links that answer with HTML:

```bash
python scripts/aio_lint.py https://example.com --check-links
```

See [aio-lint.md](aio-lint.md).
