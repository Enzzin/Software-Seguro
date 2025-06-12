"""
Testes para utils/ip_utils.py
– Sem chamadas externas: requests.get é simulado.
"""

import types, builtins
import ipaddress
from utils import ip_utils


class DummyReq:
    def __init__(self, headers=None, remote_addr="203.0.113.1"):
        self.headers    = headers or {}
        self.remote_addr = remote_addr


def test_get_real_ip_prefers_public_header():
    req = DummyReq(
        headers={"X-Forwarded-For": "198.51.100.5, 10.0.0.3"},
        remote_addr="192.168.1.10"
    )
    assert ip_utils.get_real_ip(req) == "198.51.100.5"


def test_get_real_ip_falls_back_to_remote_addr():
    req = DummyReq(headers={}, remote_addr="198.51.100.99")
    assert ip_utils.get_real_ip(req) == "198.51.100.99"


def test_is_valid_ip():
    assert ip_utils.is_valid_ip("2001:db8::1")
    assert ip_utils.is_valid_ip("8.8.8.8")
    assert not ip_utils.is_valid_ip("999.999.999.999")


def test_anonymize_ipv4():
    assert ip_utils.anonymize_ip("203.0.113.57") == "203.0.113.0"


def test_anonymize_ipv6():
    out = ip_utils.anonymize_ip("2001:db8::abcd:ef12")
    # Últimos 64 bits zerados
    assert out.endswith("::")


def test_get_geolocation_mocked(monkeypatch):
    """Simula ip-api.com para evitar tráfego externo."""
    class _Resp:
        status_code = 200
        def json(self):
            return {
                "status": "success",
                "country": "Example-land",
                "countryCode": "EX",
                "city": "Testville",
                "regionName": "TX",
                "lat": 10.0,
                "lon": 20.0,
            }

    monkeypatch.setattr(ip_utils.requests, "get", lambda *a, **kw: _Resp())
    data = ip_utils.get_geolocation("198.51.100.5")
    assert data["country"] == "EX"
    assert data["city"] == "Testville"
