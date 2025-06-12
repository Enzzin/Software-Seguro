"""
Testes simples para utils/user_agent_parser.py
"""

from utils.user_agent_parser import parse_user_agent


def test_parse_desktop_chrome():
    ua_str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
    info = parse_user_agent(ua_str)
    assert info["browser"] == "Chrome"
    assert info["os"] == "Windows"
    assert info["device_type"] == "desktop"
    assert info["is_bot"] is False


def test_parse_mobile_safari():
    ua_str = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    )
    info = parse_user_agent(ua_str)
    assert info["browser"] == "Mobile Safari"
    assert info["device_type"] == "mobile"
