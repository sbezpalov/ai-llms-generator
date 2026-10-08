"""SSRF guards and pinned fetching in aio_net (no real network)."""

from __future__ import annotations

import os
import socket
import unittest
from email.message import Message
from unittest import mock

import aio_net

PUBLIC_IP = "93.184.216.34"
HOST = "site.example"


def addrinfo(*ips: str) -> list[tuple]:
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443)) for ip in ips]


class FakeResponse:
    def __init__(
        self,
        status: int = 200,
        body: bytes = b"",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self.headers = Message()
        for name, value in (headers or {}).items():
            self.headers[name] = value
        self._remaining = body

    def getheader(self, name: str, default: str | None = None) -> str | None:
        return self.headers.get(name, default)

    def read1(self, amount: int) -> bytes:
        chunk, self._remaining = self._remaining[:amount], self._remaining[amount:]
        return chunk


class FakeConnection:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.requested: list[str] = []
        self.closed = False

    def connect(self) -> None:
        return None

    def request(self, method: str, target: str, headers: dict[str, str]) -> None:
        self.requested.append(target)

    def getresponse(self) -> FakeResponse:
        return self.response

    def close(self) -> None:
        self.closed = True


class FetchHarness(unittest.TestCase):
    """Patches DNS and the connection factory; records what was dialled."""

    def start(self, responses: list[FakeResponse], dns: list[list[tuple]] | None = None):
        self.dialled: list[tuple[str, str]] = []
        self.connections: list[FakeConnection] = []
        pending = list(responses)

        def open_connection(host: str, ip: str, timeout: float) -> FakeConnection:
            self.dialled.append((host, ip))
            connection = FakeConnection(pending.pop(0))
            self.connections.append(connection)
            return connection

        answers = list(dns) if dns else None

        def getaddrinfo(host: str, port: int, **kwargs: object) -> list[tuple]:
            if answers is None:
                return addrinfo(PUBLIC_IP)
            return answers.pop(0)

        for target, replacement in (
            ("aio_net.open_connection", open_connection),
            ("aio_net.socket.getaddrinfo", getaddrinfo),
        ):
            patcher = mock.patch(target, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    def fetch(self, url: str = f"https://{HOST}/llms.txt", max_bytes: int = 1024):
        return aio_net.fetch_https(url, max_bytes=max_bytes, timeout=5.0, origin_host=HOST)


class IsPublicIpTests(unittest.TestCase):
    def test_accepts_globally_routable_addresses(self) -> None:
        for ip in (PUBLIC_IP, "1.1.1.1", "2606:4700:4700::1111"):
            with self.subTest(ip=ip):
                self.assertTrue(aio_net.is_public_ip(ip))

    def test_rejects_internal_and_special_purpose_addresses(self) -> None:
        for ip in (
            "127.0.0.1",
            "10.0.0.1",
            "172.16.0.1",
            "192.168.1.1",
            "169.254.169.254",
            "100.64.0.1",
            "100.100.100.200",
            "192.0.0.9",
            "192.88.99.1",
            "198.18.0.1",
            "0.0.0.0",
            "224.0.0.1",
            "240.0.0.1",
            "::1",
            "::",
            "fe80::1",
            "fec0::1",
            "fd00:ec2::254",
            "::ffff:127.0.0.1",
            "::ffff:10.0.0.1",
            "2002:7f00:1::",
            "2002:a00:1::",
            "64:ff9b::7f00:1",
        ):
            with self.subTest(ip=ip):
                self.assertFalse(aio_net.is_public_ip(ip))


class ResolvePublicIpsTests(unittest.TestCase):
    def resolve(self, url: str, ips: tuple[str, ...] = (PUBLIC_IP,), **kwargs: object):
        with mock.patch("aio_net.socket.getaddrinfo", return_value=addrinfo(*ips)):
            return aio_net.resolve_public_ips(url, **kwargs)

    def test_returns_validated_addresses(self) -> None:
        self.assertEqual(self.resolve(f"https://{HOST}/"), [PUBLIC_IP])

    def test_refuses_unsafe_urls(self) -> None:
        for url in (
            f"http://{HOST}/",
            f"https://user:secret@{HOST}/",
            f"https://{HOST}:8443/",
            "https://localhost/",
            "https://app.localhost/",
            "https:///nohost",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.resolve(url)

    def test_refuses_when_any_resolved_address_is_internal(self) -> None:
        with self.assertRaises(ValueError):
            self.resolve(f"https://{HOST}/", ips=(PUBLIC_IP, "10.0.0.5"))

    def test_refuses_hosts_outside_the_allow_list(self) -> None:
        with self.assertRaises(ValueError):
            self.resolve("https://other.example/", allow_hosts={HOST})


class FetchHttpsTests(FetchHarness):
    def test_returns_body_and_dials_the_validated_address(self) -> None:
        self.start([FakeResponse(200, b"# Title\n")])

        result = self.fetch()

        self.assertEqual((result.status_code, result.body, result.error), (200, "# Title\n", None))
        self.assertEqual(self.dialled, [(HOST, PUBLIC_IP)])
        self.assertEqual(self.connections[0].requested, ["/llms.txt"])
        self.assertTrue(self.connections[0].closed)

    def test_follows_same_host_redirect_with_fresh_validation(self) -> None:
        self.start(
            [
                FakeResponse(301, headers={"Location": "/new/llms.txt"}),
                FakeResponse(200, b"ok"),
            ]
        )

        result = self.fetch()

        self.assertEqual(result.body, "ok")
        self.assertEqual(result.final_url, f"https://{HOST}/new/llms.txt")
        self.assertEqual(len(self.dialled), 2)

    def test_refuses_redirect_to_another_host(self) -> None:
        self.start([FakeResponse(302, headers={"Location": "https://evil.example/x"})])

        result = self.fetch()

        self.assertIsNone(result.body)
        self.assertIn("allow-list", result.error)
        self.assertEqual(len(self.dialled), 1)

    def test_refuses_redirect_to_plain_http(self) -> None:
        self.start([FakeResponse(302, headers={"Location": f"http://{HOST}/x"})])

        self.assertIn("only https", self.fetch().error)

    def test_refuses_when_dns_answer_turns_internal_on_a_later_hop(self) -> None:
        self.start(
            [FakeResponse(301, headers={"Location": "/again"})],
            dns=[addrinfo(PUBLIC_IP), addrinfo("169.254.169.254")],
        )

        result = self.fetch()

        self.assertIn("non-public", result.error)
        self.assertEqual(self.dialled, [(HOST, PUBLIC_IP)])

    def test_stops_after_too_many_redirects(self) -> None:
        self.start(
            [FakeResponse(301, headers={"Location": "/loop"})] * (aio_net.MAX_REDIRECTS + 1)
        )

        self.assertIn("too many redirects", self.fetch().error)

    def test_reports_redirect_without_location(self) -> None:
        self.start([FakeResponse(301)])

        self.assertEqual(self.fetch().error, "redirect without Location")

    def test_rejects_body_over_the_size_cap(self) -> None:
        self.start([FakeResponse(200, b"x" * 2048)])

        result = self.fetch(max_bytes=1024)

        self.assertIsNone(result.body)
        self.assertIn("exceeds 1024 bytes", result.error)

    def test_unknown_charset_falls_back_to_utf8(self) -> None:
        self.start(
            [FakeResponse(200, "héllo".encode(), {"Content-Type": "text/plain; charset=nope"})]
        )

        result = self.fetch()

        self.assertEqual((result.body, result.error), ("héllo", None))

    def test_keeps_status_of_error_responses(self) -> None:
        self.start([FakeResponse(404, b"")])

        result = self.fetch()

        self.assertEqual((result.status_code, result.body, result.error), (404, None, None))

    def test_gives_up_when_total_deadline_has_passed(self) -> None:
        self.start([FakeResponse(200, b"slow")])

        clock = iter([0.0, 0.0, 0.0])
        with mock.patch("aio_net.time.monotonic", lambda: next(clock, 1000.0)):
            result = self.fetch()

        self.assertIn("total fetch time", result.error)

    def test_does_not_dial_once_the_deadline_has_passed(self) -> None:
        self.start([FakeResponse(200, b"late")])

        clock = iter([0.0])
        with mock.patch("aio_net.time.monotonic", lambda: next(clock, 1000.0)):
            result = self.fetch()

        self.assertIn("total fetch time", result.error)
        self.assertEqual(self.dialled, [])

    def test_tries_a_bounded_number_of_addresses(self) -> None:
        many = [f"93.184.216.{n}" for n in range(1, 20)]
        self.start([], dns=[addrinfo(*many)])

        def refuse(host: str, ip: str, timeout: float) -> FakeConnection:
            self.dialled.append((host, ip))
            raise OSError("unreachable")

        with mock.patch("aio_net.open_connection", refuse):
            result = self.fetch()

        self.assertEqual(result.error, "unreachable")
        self.assertEqual(len(self.dialled), aio_net.MAX_CONNECT_ADDRESSES)

    def test_ignores_proxy_environment(self) -> None:
        self.start([FakeResponse(200, b"ok")])

        with mock.patch.dict(os.environ, {"HTTPS_PROXY": "http://10.0.0.1:3128"}):
            self.fetch()

        self.assertEqual(self.dialled, [(HOST, PUBLIC_IP)])


class PinnedConnectionTests(unittest.TestCase):
    def test_connects_to_the_pinned_address_not_the_hostname(self) -> None:
        dialled: list[tuple[str, int]] = []

        def create_connection(address: tuple[str, int], timeout: float) -> socket.socket:
            dialled.append(address)
            raise OSError("stop before TLS")

        connection = aio_net.open_connection(HOST, PUBLIC_IP, 5.0)
        with mock.patch("aio_net.socket.create_connection", create_connection):
            with self.assertRaises(OSError):
                connection.connect()

        self.assertEqual(dialled, [(PUBLIC_IP, 443)])
        self.assertEqual(connection.host, HOST)


if __name__ == "__main__":
    unittest.main()
