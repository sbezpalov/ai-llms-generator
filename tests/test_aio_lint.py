"""Layer scoring and report rendering in aio_lint (offline)."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path
from unittest import mock

import aio_lint
from aio_net import FetchResult

FIXTURES = Path(__file__).resolve().parents[1] / "examples" / "aio-lint-fixtures"


def page(body: str) -> FetchResult:
    return FetchResult(url="https://site.example/", status_code=200, body=body)


def run_cli(*argv: str) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
        code = aio_lint.main(list(argv))
    return code, stdout.getvalue()


class ScoreL0Tests(unittest.TestCase):
    def test_ok_when_all_signals_present(self) -> None:
        layer = aio_lint.score_l0(
            page(
                "<title>T</title><h1>H</h1>"
                '<link href="https://site.example/" rel="canonical">'
                '<meta content="d" name="description">'
            )
        )

        self.assertEqual(layer.status, "ok")
        self.assertTrue(layer.details["has_canonical"])

    def test_fails_without_title_or_h1(self) -> None:
        self.assertEqual(aio_lint.score_l0(page("<h1>H</h1>")).status, "fail")

    def test_truncates_untrusted_canonical(self) -> None:
        layer = aio_lint.score_l0(
            page(f'<title>T</title><h1>H</h1><link rel="canonical" href="{"a" * 5000}">')
        )

        canonical = next(item for item in layer.evidence if item.startswith("canonical: "))
        self.assertLessEqual(len(canonical), 220)


def robots(body: str | None, status: int | None = 200, error: str | None = None) -> FetchResult:
    return FetchResult("https://site.example/robots.txt", status, body, error)


class ScoreL1Tests(unittest.TestCase):
    def test_ok_with_absolute_sitemap(self) -> None:
        layer = aio_lint.score_l1(robots("User-agent: *\nAllow: /\nSitemap: https://site.example/s.xml\n"))

        self.assertEqual(layer.status, "ok")
        self.assertEqual(layer.details["sitemaps"], ["https://site.example/s.xml"])

    def test_trailing_comments_and_crlf_are_ignored(self) -> None:
        body = "User-agent: GPTBot # training\r\nDisallow: /\r\nSitemap: https://site.example/s.xml # map\r\n"

        layer = aio_lint.score_l1(robots(body))

        self.assertEqual(layer.details["ai_user_agents"], ["GPTBot"])
        self.assertEqual(layer.details["sitemaps"], ["https://site.example/s.xml"])

    def test_relative_sitemap_does_not_count(self) -> None:
        layer = aio_lint.score_l1(robots("User-agent: *\nSitemap: /sitemap.xml\n"))

        self.assertEqual((layer.status, layer.details["sitemaps"]), ("weak", []))
        self.assertTrue(any("non-absolute" in item for item in layer.evidence))

    def test_llms_note_is_detected_only_inside_comments(self) -> None:
        with_note = aio_lint.score_l1(robots("# see https://site.example/llms.txt\nUser-agent: *\n"))
        without_note = aio_lint.score_l1(robots("# hello\nUser-agent: *\nDisallow: /llms.txt\n"))

        self.assertTrue(any("llms.txt comment" in item for item in with_note.evidence))
        self.assertFalse(any("llms.txt comment" in item for item in without_note.evidence))

    def test_status_follows_rfc_9309(self) -> None:
        for status, expected, phrase in (
            (404, "weak", "allow-all"),
            (403, "weak", "allow-all"),
            (500, "fail", "disallow"),
            (503, "fail", "disallow"),
        ):
            with self.subTest(status=status):
                layer = aio_lint.score_l1(robots(None, status))
                self.assertEqual(layer.status, expected)
                self.assertIn(f"HTTP {status}", layer.evidence[0])
                self.assertIn(phrase, layer.evidence[0])

    def test_recognizes_newer_ai_tokens_case_insensitively(self) -> None:
        layer = aio_lint.score_l1(robots("User-agent: meta-externalagent\nDisallow: /\nUser-agent: Applebot-Extended\nDisallow: /\n"))

        self.assertEqual(layer.details["ai_user_agents"], ["Applebot-Extended", "meta-externalagent"])

    def test_fetch_error_fails(self) -> None:
        self.assertEqual(aio_lint.score_l1(robots(None, None, "timed out")).status, "fail")


class ScoreL2Tests(unittest.TestCase):
    def llms(self, body: str | None, status: int | None = 200) -> FetchResult:
        return FetchResult("https://site.example/llms.txt", status, body)

    def test_error_status_with_curated_looking_body_is_not_ok(self) -> None:
        layer = aio_lint.score_l2(self.llms("# S\n> d\n## A\n- [A](https://x.example/a)\n", 500))

        self.assertEqual((layer.status, layer.details["classification"]), ("weak", "unavailable"))
        self.assertIn("HTTP 500", " ".join(layer.evidence))
        self.assertNotIn("https_links", layer.details)

    def test_missing_file_fails(self) -> None:
        self.assertEqual(aio_lint.score_l2(self.llms(None, 404)).status, "fail")

    def test_unavailable_gets_its_own_action(self) -> None:
        fetches = {
            "html": page("<title>T</title><h1>H</h1>"),
            "robots": robots("User-agent: *\nSitemap: https://site.example/s.xml\n"),
            "llms": self.llms(None, 503),
        }

        report = aio_lint.audit_from_fetches("https://site.example/", "live", fetches)

        self.assertTrue(any("HTTP 503" in action for action in report.top_actions))
        self.assertFalse(any("Create a curated" in action for action in report.top_actions))


class CheckLinksTests(unittest.TestCase):
    LLMS = (
        "# S\n\n> d\n\n## Docs\n\n"
        "- [Ok](https://site.example/ok/): fine\n"
        "- [Gone](https://site.example/gone/): broken\n"
        "- [Md](https://site.example/page.md): real markdown\n"
        "- [Fake](https://site.example/fake.md): html in disguise\n"
        "- [Ext](https://other.example/x): external\n"
    )
    RESPONSES = {
        "https://site.example/ok/": (200, "<html>ok</html>"),
        "https://site.example/gone/": (404, None),
        "https://site.example/page.md": (200, "# Page\n\nText"),
        "https://site.example/fake.md": (200, "  <!DOCTYPE html><html>Not found</html>"),
    }

    def check(self, body: str | None = None) -> dict:
        requested: list[str] = []

        def fake_fetch(url: str, **kwargs: object) -> FetchResult:
            requested.append(url)
            status, text = self.RESPONSES[url]
            return FetchResult(url, status, text)

        with mock.patch("aio_lint.fetch_https", fake_fetch):
            report = aio_lint.check_links(body or self.LLMS, origin_host="site.example", timeout=1.0)
        self.requested = requested
        return report

    def test_reports_broken_fake_markdown_and_external_links(self) -> None:
        report = self.check()

        self.assertEqual(report["checked"], 4)
        self.assertEqual(report["ok"], 2)
        self.assertEqual(report["broken"], [{"url": "https://site.example/gone/", "reason": "HTTP 404"}])
        self.assertEqual(
            report["not_markdown"], ["https://site.example/fake.md"]
        )
        self.assertEqual(report["external_skipped"], 1)
        self.assertNotIn("https://other.example/x", self.requested)

    def test_checks_a_bounded_number_of_links(self) -> None:
        many = "## A\n" + "".join(
            f"- [P{n}](https://site.example/ok/?n={n})\n" for n in range(aio_lint.MAX_LINK_CHECKS + 10)
        )
        with mock.patch.dict(self.RESPONSES, {
            f"https://site.example/ok/?n={n}": (200, "ok") for n in range(aio_lint.MAX_LINK_CHECKS + 10)
        }):
            report = self.check(many)

        self.assertEqual(report["checked"], aio_lint.MAX_LINK_CHECKS)
        self.assertEqual(report["not_checked"], 10)

    def test_problem_links_downgrade_a_curated_file(self) -> None:
        llms = FetchResult("https://site.example/llms.txt", 200, self.LLMS)

        layer = aio_lint.score_l2(llms, link_report=self.check())

        self.assertEqual(layer.status, "weak")
        self.assertTrue(any(item.startswith("link_check: 2 ok, 1 broken, 1 not markdown") for item in layer.evidence))
        self.assertEqual(layer.details["link_check"]["external_skipped"], 1)

    def test_clean_links_keep_a_curated_file_ok(self) -> None:
        body = "# S\n\n> d\n\n## Docs\n\n- [Ok](https://site.example/ok/): fine\n"
        llms = FetchResult("https://site.example/llms.txt", 200, body)

        self.assertEqual(aio_lint.score_l2(llms, link_report=self.check(body)).status, "ok")

    def test_fixture_mode_rejects_link_checks(self) -> None:
        code, _ = run_cli("--fixture", str(FIXTURES / "curated-site"), "--check-links")

        self.assertEqual(code, 2)


class AuditLiveInputTests(unittest.TestCase):
    def test_refuses_inputs_it_would_otherwise_silently_rewrite(self) -> None:
        for target in ("https://user:pw@example.com", "example.com:8443/a", "https://", "ftp://example.com"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                aio_lint.audit_live(target, timeout=1.0)


class ScoreL3Tests(unittest.TestCase):
    def test_ok_for_recognized_types(self) -> None:
        layer = aio_lint.score_l3(
            page('<script type="application/ld+json">{"@type": "Organization"}</script>')
        )

        self.assertEqual(layer.status, "ok")

    def test_fails_when_every_block_is_invalid(self) -> None:
        layer = aio_lint.score_l3(page('<script type="application/ld+json">{oops</script>'))

        self.assertEqual((layer.status, layer.evidence), ("fail", ["JSON-LD present but invalid JSON"]))

    def test_leftover_placeholders_downgrade_to_weak(self) -> None:
        for leftover in ("TODO_REPLACE_ORGANIZATION_NAME", "https://example.com/"):
            block = json.dumps({"@type": "Organization", "name": "Acme", "url": leftover})
            with self.subTest(leftover=leftover):
                layer = aio_lint.score_l3(page(f'<script type="application/ld+json">{block}</script>'))
                self.assertEqual(layer.status, "weak")
                self.assertTrue(any("placeholder" in item for item in layer.evidence))

    def test_fails_without_blocks(self) -> None:
        self.assertEqual(aio_lint.score_l3(page("<p>x</p>")).status, "fail")


class RenderMarkdownTests(unittest.TestCase):
    def render(self, canonical: str) -> str:
        html = f'<title>T</title><h1>H</h1><link rel="canonical" href="{canonical}">'
        fetches = {
            "html": page(html),
            "robots": FetchResult("https://site.example/robots.txt", 404, None),
            "llms": FetchResult("https://site.example/llms.txt", 404, None),
        }
        return aio_lint.render_markdown(
            aio_lint.audit_from_fetches("https://site.example/", "live", fetches)
        )

    def test_untrusted_text_cannot_break_out_of_its_table_cell(self) -> None:
        report = self.render("x\n| injected | row |\n::error::boom\n<img src=x>`code`\\")

        l0_rows = [line for line in report.splitlines() if line.startswith("| L0 ")]
        self.assertEqual(len(l0_rows), 1)
        self.assertEqual(l0_rows[0].count("|"), 4)
        self.assertNotIn("\\", l0_rows[0])
        self.assertNotIn("<img", report)
        self.assertFalse(any(line.startswith("::") for line in report.splitlines()))

    def test_plain_evidence_stays_readable(self) -> None:
        self.assertIn("canonical: https://site.example/", self.render("https://site.example/"))


class CliTests(unittest.TestCase):
    def test_curated_fixture_reports_markdown_links(self) -> None:
        code, out = run_cli("--fixture", str(FIXTURES / "curated-site"), "--json", "--strict")

        details = json.loads(out)["layers"]["L2"]["details"]
        self.assertEqual(code, 0)
        self.assertEqual((details["classification"], details["markdown_links"]), ("curated", 1))

    def test_dump_fixture_fails_strict(self) -> None:
        code, out = run_cli("--fixture", str(FIXTURES / "dump-site"), "--json", "--strict")

        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["layers"]["L2"]["details"]["classification"], "dump")

    def test_refuses_plain_http_target(self) -> None:
        code, _ = run_cli("http://example.com")

        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
