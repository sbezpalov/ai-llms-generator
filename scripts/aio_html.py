#!/usr/bin/env python3
"""Linear-time extraction of homepage signals for aio-lint (no network).

Page content is untrusted. Backtracking regular expressions, and html.parser
on older Python releases, go quadratic on hostile markup, so this module scans
with bounded `str.find` windows instead: every character is visited a bounded
number of times whatever the input looks like.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass

JSONLD_MIME = "application/ld+json"
INVALID_JSONLD = "(invalid-json)"
# A start tag longer than this is treated as text, which bounds every scan.
MAX_TAG_CHARS = 8 * 1024
MAX_TEXT_CHARS = 1024
MAX_HEADING_WINDOW_CHARS = 4 * 1024
MAX_JSONLD_BLOCKS = 50

TAG_NAME_RE = re.compile(r"(title|h1|link|meta|script|style)(?=[\s/>])", re.IGNORECASE)
# Elements whose content is raw text: markup inside them is not markup.
RAW_TEXT_CLOSERS = {
    name: re.compile(f"</{name}", re.IGNORECASE) for name in ("title", "script", "style")
}
HEADING_CLOSE_RE = re.compile(r"</h1", re.IGNORECASE)
INNER_TAG_RE = re.compile(r"<[^<>]*>")
QUOTES = "\"'"


@dataclass(frozen=True)
class PageSignals:
    title: str | None
    h1: str | None
    canonical: str | None
    has_meta_description: bool
    jsonld_blocks: tuple[str, ...]


def _is_jsonld(type_attr: str) -> bool:
    return type_attr.split(";", 1)[0].strip().lower() == JSONLD_MIME


def _clean_text(raw: str) -> str:
    return " ".join(html.unescape(raw).split())


def _skip_spaces(source: str, index: int) -> int:
    while index < len(source) and source[index].isspace():
        index += 1
    return index


def _read_value(source: str, index: int) -> tuple[str, int]:
    """Attribute value starting at index (just after `=`), and the next index."""
    index = _skip_spaces(source, index)
    if index < len(source) and source[index] in QUOTES:
        end = source.find(source[index], index + 1)
        end = len(source) if end == -1 else end
        return source[index + 1 : end], end + 1
    start = index
    while index < len(source) and not source[index].isspace():
        index += 1
    return source[start:index], index


def parse_attributes(source: str) -> dict[str, str]:
    """Attributes of one start tag (text between the tag name and `>`)."""
    attributes: dict[str, str] = {}
    index = 0
    while index < len(source):
        if source[index].isspace() or source[index] == "/":
            index += 1
            continue
        start = index
        while index < len(source) and not source[index].isspace() and source[index] not in "=/":
            index += 1
        name = source[start:index].lower()
        value = ""
        after_name = _skip_spaces(source, index)
        if after_name < len(source) and source[after_name] == "=":
            value, index = _read_value(source, after_name + 1)
        if name:
            attributes.setdefault(name, html.unescape(value))
        elif index == start:
            index += 1
    return attributes


def _heading_text(text: str, start: int) -> str:
    window = text[start : start + MAX_HEADING_WINDOW_CHARS]
    close = HEADING_CLOSE_RE.search(window)
    if close:
        inner = INNER_TAG_RE.sub(" ", window[: close.start()])
    else:
        # Unclosed heading: keep its leading text only, so later markup still counts.
        inner = window.split("<", 1)[0]
    return _clean_text(inner)[:MAX_TEXT_CHARS]


def page_signals(html_text: str) -> PageSignals:
    title: str | None = None
    h1: str | None = None
    canonical: str | None = None
    has_meta_description = False
    jsonld_blocks: list[str] = []
    position = 0
    while True:
        tag_start = html_text.find("<", position)
        if tag_start == -1:
            break
        position = tag_start + 1
        if html_text.startswith("<!--", tag_start):
            comment_end = html_text.find("-->", tag_start + 4)
            if comment_end == -1:
                break
            position = comment_end + 3
            continue
        name_match = TAG_NAME_RE.match(html_text, tag_start + 1)
        if not name_match:
            continue
        tag_end = html_text.find(">", name_match.end(), tag_start + MAX_TAG_CHARS)
        if tag_end == -1:
            continue
        name = name_match.group(1).lower()
        position = tag_end + 1

        if name in RAW_TEXT_CLOSERS:
            close = RAW_TEXT_CLOSERS[name].search(html_text, position)
            content_end = close.start() if close else len(html_text)
            if name == "title" and title is None:
                title_end = min(content_end, position + MAX_TEXT_CHARS)
                title = _clean_text(html_text[position:title_end])
            elif name == "script" and len(jsonld_blocks) < MAX_JSONLD_BLOCKS:
                attributes = parse_attributes(html_text[name_match.end() : tag_end])
                if _is_jsonld(attributes.get("type", "")):
                    jsonld_blocks.append(html_text[position:content_end])
            position = content_end
        elif name == "h1":
            if h1 is None:
                h1 = _heading_text(html_text, position)
        else:
            attributes = parse_attributes(html_text[name_match.end() : tag_end])
            if name == "link" and canonical is None:
                rel_tokens = attributes.get("rel", "").lower().split()
                if "canonical" in rel_tokens and attributes.get("href", "").strip():
                    canonical = attributes["href"].strip()
            elif name == "meta" and "content" in attributes:
                if attributes.get("name", "").strip().lower() == "description":
                    has_meta_description = True

    return PageSignals(title, h1, canonical, has_meta_description, tuple(jsonld_blocks))


def _node_types(node: object) -> list[str]:
    if isinstance(node, list):
        return [found for item in node for found in _node_types(item)]
    if not isinstance(node, dict):
        return []
    declared = node.get("@type")
    values = declared if isinstance(declared, list) else [declared]
    types = [value for value in values if isinstance(value, str)]
    graph = node.get("@graph")
    if isinstance(graph, list):
        types.extend(_node_types(graph))
    return types


def jsonld_types(blocks: tuple[str, ...]) -> list[str]:
    """@type values across JSON-LD blocks; INVALID_JSONLD marks unparsable ones."""
    types: list[str] = []
    for raw in blocks:
        if not raw.strip():
            continue
        try:
            types.extend(_node_types(json.loads(raw)))
        except (ValueError, RecursionError):
            # ValueError covers JSONDecodeError and the int-digits limit.
            types.append(INVALID_JSONLD)
    return types
