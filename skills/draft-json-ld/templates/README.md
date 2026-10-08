# JSON-LD templates

These files are **examples**, not deploy-ready organization facts.

Before publishing:

1. Replace every `TODO_REPLACE_*` value with a fact visible on the public page
   (absolute `https://` URLs, ISO 8601 dates with a timezone).
2. Remove properties whose values are unknown (`…_OR_REMOVE` marks the usual
   candidates); do not guess them. Published JSON-LD must contain no
   `TODO_REPLACE` text — `aio-lint` flags it on the homepage.
3. Keep structured data consistent with the page users can see.
4. Validate generic Schema.org syntax with
   [Schema Markup Validator](https://validator.schema.org/).
5. Use [Google Rich Results Test](https://search.google.com/test/rich-results)
   only for types currently supported by Google.

`FAQPage` and `HowTo` remain Schema.org types, but they are not current Google
rich-result features. Valid markup does not guarantee a rich result, ranking,
citation, or inclusion in an AI answer.
