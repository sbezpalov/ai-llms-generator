"""Linear-time homepage signal extraction in aio_html."""

from __future__ import annotations

import time
import unittest

import aio_html

HOSTILE_INPUT_BYTES = 512 * 1024
HOSTILE_BUDGET_SECONDS = 5.0


class PageSignalsTests(unittest.TestCase):
    def test_extracts_core_signals(self) -> None:
        html = (
            "<html><head><title> My  Site </title>"
            '<link rel="canonical" href="https://site.example/">'
            '<meta name="description" content="About the site">'
            "</head><body><h1>Hello <em>world</em></h1></body></html>"
        )

        signals = aio_html.page_signals(html)

        self.assertEqual(signals.title, "My Site")
        self.assertEqual(signals.h1, "Hello world")
        self.assertEqual(signals.canonical, "https://site.example/")
        self.assertTrue(signals.has_meta_description)

    def test_attribute_order_and_quoting_do_not_matter(self) -> None:
        html = (
            "<link href=https://site.example/ rel=canonical />"
            "<META CONTENT='x' NAME='Description'>"
        )

        signals = aio_html.page_signals(html)

        self.assertEqual(signals.canonical, "https://site.example/")
        self.assertTrue(signals.has_meta_description)

    def test_reports_missing_signals(self) -> None:
        signals = aio_html.page_signals("<p>nothing here</p>")

        self.assertIsNone(signals.title)
        self.assertIsNone(signals.h1)
        self.assertIsNone(signals.canonical)
        self.assertFalse(signals.has_meta_description)
        self.assertEqual(signals.jsonld_blocks, ())

    def test_ignores_markup_inside_comments(self) -> None:
        signals = aio_html.page_signals("<!-- <title>Old</title> --><title>New</title>")

        self.assertEqual(signals.title, "New")

    def test_ignores_non_canonical_links(self) -> None:
        html = '<link rel="alternate" href="/feed"><link rel="stylesheet canonical" href="/c">'

        self.assertEqual(aio_html.page_signals(html).canonical, "/c")

    def test_collects_jsonld_blocks_with_loose_type_attribute(self) -> None:
        html = (
            '<script type="application/ld+json">{"@type": "WebSite"}</script>'
            "<script type=application/ld+json>{\"@type\": \"Person\"}</script>"
            '<script type="Application/LD+JSON; charset=utf-8">{"@type": "Article"}</script>'
            '<script type="text/javascript">var x = {"@type": "Nope"};</script>'
        )

        blocks = aio_html.page_signals(html).jsonld_blocks

        self.assertEqual(aio_html.jsonld_types(blocks), ["WebSite", "Person", "Article"])

    def test_unclosed_heading_does_not_hide_later_jsonld(self) -> None:
        html = '<h1>Open<script type="application/ld+json">{"@type": "WebSite"}</script>'

        signals = aio_html.page_signals(html)

        self.assertEqual(signals.h1, "Open")
        self.assertEqual(aio_html.jsonld_types(signals.jsonld_blocks), ["WebSite"])

    def test_markup_inside_scripts_and_styles_is_not_markup(self) -> None:
        html = (
            "<script>document.write('<title>Fake</title><h1>Fake</h1>');</script>"
            "<style>/* <link rel=canonical href=/fake> */</style>"
            "<title>Real &amp; true</title><h1>Real</h1>"
        )

        signals = aio_html.page_signals(html)

        self.assertEqual((signals.title, signals.h1, signals.canonical), ("Real & true", "Real", None))

    def test_entities_in_attribute_values_are_decoded(self) -> None:
        html = '<link rel="canonical" href="https://site.example/?a=1&amp;b=2">'

        self.assertEqual(aio_html.page_signals(html).canonical, "https://site.example/?a=1&b=2")

    def test_hostile_markup_is_parsed_in_bounded_time(self) -> None:
        for name, unit in (
            ("canonical", '<link rel="canonical" '),
            ("meta", '<meta name="description" '),
            ("script", '<script type="application/ld+json">'),
            ("title", "<title>"),
            ("open-quote", '<a b="'),
            ("open-quote-link", '<link rel="'),
            ("angle", "<h1><"),
            ("comment", "<!--"),
            ("closed-links", "<link a=b>"),
        ):
            hostile = unit * (HOSTILE_INPUT_BYTES // len(unit))
            with self.subTest(pattern=name):
                started = time.monotonic()
                aio_html.page_signals(hostile)
                self.assertLess(time.monotonic() - started, HOSTILE_BUDGET_SECONDS)


class JsonldTypesTests(unittest.TestCase):
    def test_reads_string_and_list_types(self) -> None:
        blocks = ('{"@type": "Organization"}', '{"@type": ["Article", "BlogPosting"]}')

        self.assertEqual(
            aio_html.jsonld_types(blocks), ["Organization", "Article", "BlogPosting"]
        )

    def test_expands_graph_inside_a_top_level_list(self) -> None:
        blocks = ('[{"@type": "Organization"}, {"@graph": [{"@type": "WebSite"}]}]',)

        self.assertEqual(aio_html.jsonld_types(blocks), ["Organization", "WebSite"])

    def test_keeps_node_type_alongside_its_graph(self) -> None:
        blocks = ('{"@type": "WebPage", "@graph": [{"@type": "Person"}]}',)

        self.assertEqual(aio_html.jsonld_types(blocks), ["WebPage", "Person"])

    def test_ignores_non_string_types_and_scalars(self) -> None:
        blocks = ('{"@type": {"a": 1}}', '{"@type": 123}', '"just a string"', "  ")

        self.assertEqual(aio_html.jsonld_types(blocks), [])

    def test_marks_invalid_json(self) -> None:
        self.assertEqual(aio_html.jsonld_types(("{not json",)), [aio_html.INVALID_JSONLD])

    def test_oversized_number_is_invalid_not_fatal(self) -> None:
        block = '{"@type": "Organization", "n": ' + "9" * 5000 + "}"

        self.assertIn(aio_html.jsonld_types((block,)), ([aio_html.INVALID_JSONLD], ["Organization"]))

    def test_survives_pathologically_nested_json(self) -> None:
        nested = "[" * 100_000 + "]" * 100_000

        self.assertEqual(aio_html.jsonld_types((nested,)), [aio_html.INVALID_JSONLD])


if __name__ == "__main__":
    unittest.main()
