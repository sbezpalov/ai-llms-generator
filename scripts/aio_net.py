#!/usr/bin/env python3
"""SSRF-aware https fetching for aio-lint (stdlib only).

Each hop is resolved once, every resolved address is checked, and the
connection is pinned to a checked address, so a second DNS answer cannot move
it elsewhere. Environment proxies are never used. Redirects are followed by
hand so every hop goes through the same checks.
"""

from __future__ import annotations

import http.client
import ipaddress
import socket
import ssl
import threading
import time
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

USER_AGENT = (
    "aio-lint/1.0 (+https://github.com/sbezpalov/ai-llms-generator; research)"
)
HTTPS_PORT = 443
MAX_REDIRECTS = 3
DEFAULT_TIMEOUT = 10.0
# Whole-fetch budget (all hops and the body) as a multiple of the socket timeout.
TOTAL_TIMEOUT_FACTOR = 3
READ_CHUNK_BYTES = 16 * 1024
MAX_CONNECT_ADDRESSES = 4
DEADLINE_MESSAGE = "total fetch time exceeded"
REDIRECT_CODES = frozenset({301, 302, 303, 307, 308})
FALLBACK_CHARSET = "utf-8"
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/plain,text/html,application/json;q=0.9,*/*;q=0.1",
    "Accept-Encoding": "identity",
    "Connection": "close",
}
# Special-purpose ranges that ipaddress still reports as globally routable.
EXTRA_BLOCKED_NETWORKS = (
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
)


@dataclass(frozen=True)
class FetchResult:
    url: str
    status_code: int | None
    body: str | None
    error: str | None = None
    final_url: str | None = None


@dataclass(frozen=True)
class _Hop:
    """One request: either a final result or the next URL to follow."""

    result: FetchResult | None = None
    next_url: str | None = None


def is_public_ip(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    if ip.version == 6:
        embedded = ip.ipv4_mapped or ip.sixtofour
        if embedded is not None:
            return is_public_ip(str(embedded))
        if ip.is_site_local:
            return False
    if any(ip in network for network in EXTRA_BLOCKED_NETWORKS):
        return False
    return ip.is_global and not (
        ip.is_multicast
        or ip.is_reserved
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_unspecified
    )


def resolve_public_ips(url: str, *, allow_hosts: set[str] | None = None) -> list[str]:
    """Validate an https URL and return its resolved, all-public addresses."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"only https URLs are allowed: {url}")
    if parsed.username or parsed.password:
        raise ValueError(f"URL credentials are forbidden: {url}")
    if parsed.port not in (None, HTTPS_PORT):
        raise ValueError(f"non-default HTTPS ports are forbidden: {url}")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError(f"missing host: {url}")
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError(f"localhost targets are forbidden: {url}")
    if allow_hosts is not None and host not in allow_hosts:
        raise ValueError(f"redirect/host not on allow-list: {host}")

    try:
        infos = socket.getaddrinfo(host, HTTPS_PORT, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed for {host}: {exc}") from exc
    ips = list(dict.fromkeys(info[4][0] for info in infos))
    if not ips:
        raise ValueError(f"DNS resolution returned no addresses for {host}")
    for ip in ips:
        if not is_public_ip(ip):
            raise ValueError(f"resolved to non-public IP {ip} for {host}")
    return ips


def assert_safe_https_url(url: str, *, allow_hosts: set[str] | None = None) -> None:
    resolve_public_ips(url, allow_hosts=allow_hosts)


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Dials one pre-validated address; TLS still verifies the hostname."""

    def __init__(self, host: str, pinned_ip: str, *, timeout: float) -> None:
        self._tls_context = ssl.create_default_context()
        super().__init__(host, HTTPS_PORT, timeout=timeout, context=self._tls_context)
        self._pinned_ip = pinned_ip

    def connect(self) -> None:
        sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        try:
            self.sock = self._tls_context.wrap_socket(sock, server_hostname=self.host)
        except BaseException:
            sock.close()
            raise


def open_connection(host: str, ip: str, timeout: float) -> PinnedHTTPSConnection:
    return PinnedHTTPSConnection(host, ip, timeout=timeout)


def _remaining(deadline: float) -> float:
    """Seconds left in the whole-fetch budget; raises once it is spent."""
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError(DEADLINE_MESSAGE)
    return remaining


def _connect_pinned(
    host: str, ips: list[str], timeout: float, deadline: float
) -> http.client.HTTPSConnection:
    last_error: OSError | None = None
    for ip in ips[:MAX_CONNECT_ADDRESSES]:
        try:
            connection = open_connection(host, ip, min(timeout, _remaining(deadline)))
            connection.connect()
        except TimeoutError:
            raise
        except OSError as exc:
            last_error = exc
            continue
        return connection
    raise last_error or OSError(f"no address to connect to for {host}")


def _read_capped(
    response: http.client.HTTPResponse, max_bytes: int, deadline: float, truncate: bool
) -> bytes | None:
    """Read the body; when it exceeds max_bytes return its head (truncate) or None."""
    chunks: list[bytes] = []
    total = 0
    while True:
        _remaining(deadline)
        chunk = response.read1(READ_CHUNK_BYTES)
        if not chunk:
            return b"".join(chunks)
        total += len(chunk)
        if total > max_bytes:
            return b"".join(chunks) if truncate else None
        chunks.append(chunk)


def decode_body(raw: bytes, charset: str | None) -> str:
    try:
        return raw.decode(charset or FALLBACK_CHARSET, errors="replace")
    except LookupError:
        return raw.decode(FALLBACK_CHARSET, errors="replace")


def _abort(connection: http.client.HTTPSConnection) -> None:
    """Wake a blocked read once the whole-fetch budget is spent."""
    sock = getattr(connection, "sock", None)
    if sock is None:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass  # already closed: nothing left to interrupt


def _fetch_hop(
    current: str,
    *,
    max_bytes: int,
    timeout: float,
    allow_hosts: set[str],
    deadline: float,
    truncate: bool,
) -> _Hop:
    _remaining(deadline)
    ips = resolve_public_ips(current, allow_hosts=allow_hosts)
    parsed = urlparse(current)
    target = (parsed.path or "/") + (f"?{parsed.query}" if parsed.query else "")
    connection = _connect_pinned(parsed.hostname or "", ips, timeout, deadline)
    # Socket timeouts are per operation; the watchdog bounds slow-drip headers too.
    watchdog = threading.Timer(_remaining(deadline), _abort, [connection])
    watchdog.daemon = True
    watchdog.start()
    try:
        connection.request("GET", target, headers=REQUEST_HEADERS)
        response = connection.getresponse()
        status = response.status
        if status in REDIRECT_CODES:
            location = response.getheader("Location")
            if not location:
                return _Hop(
                    FetchResult(current, status, None, "redirect without Location", current)
                )
            return _Hop(next_url=urljoin(current, location))
        raw = _read_capped(response, max_bytes, deadline, truncate)
        if raw is None:
            return _Hop(
                FetchResult(current, status, None, f"body exceeds {max_bytes} bytes", current)
            )
        charset = response.headers.get_content_charset()
        body = decode_body(raw, charset) if raw or status == 200 else None
        return _Hop(FetchResult(current, status, body, final_url=current))
    finally:
        watchdog.cancel()
        connection.close()


def fetch_https(
    url: str,
    *,
    max_bytes: int,
    timeout: float,
    origin_host: str,
    truncate: bool = False,
) -> FetchResult:
    """GET a public https URL, staying on origin_host across redirects.

    A body over max_bytes is an error unless truncate is set, in which case
    only its head is returned (enough to probe a link).
    """
    allow_hosts = {origin_host.lower()}
    deadline = time.monotonic() + timeout * TOTAL_TIMEOUT_FACTOR
    current = url
    try:
        for _ in range(MAX_REDIRECTS + 1):
            hop = _fetch_hop(
                current,
                max_bytes=max_bytes,
                timeout=timeout,
                allow_hosts=allow_hosts,
                deadline=deadline,
                truncate=truncate,
            )
            if hop.result is not None:
                result = hop.result
                return FetchResult(
                    url, result.status_code, result.body, result.error, result.final_url
                )
            current = hop.next_url or current
    except (OSError, ValueError, http.client.HTTPException) as exc:
        error = DEADLINE_MESSAGE if time.monotonic() >= deadline else str(exc)
        return FetchResult(url=url, status_code=None, body=None, error=error)
    return FetchResult(
        url=url,
        status_code=None,
        body=None,
        error=f"too many redirects (>{MAX_REDIRECTS})",
    )
