import pytest
from check_modules.ntp_check import extract_ntp_fortinet
from check_modules.ntp_check import extract_ntp_arista
from check_modules.ntp_check import check_ntp

def test_fortinet_returns_server_without_quotes():
    sample = 'set server "10.0.0.211"'
    result = extract_ntp_fortinet(sample)
    assert result == ["10.0.0.211"]

def test_unknown_platform_raises():
    with pytest.raises(ValueError):
        check_ntp("anything", {}, "banana")

def test_arista_returns_server_vrf():
    sample = """ntp server 10.0.0.126 prefer
            ntp server vrf MGMT 10.0.0.127
            no ntp server 10.0.0.99"""
    result = extract_ntp_arista(sample)
    assert result == ["10.0.0.126", "10.0.0.127"]