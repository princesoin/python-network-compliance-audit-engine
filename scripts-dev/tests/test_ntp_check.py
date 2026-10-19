import pytest
from check_modules.ntp_check import extract_ntp_fortinet
from check_modules.ntp_check import extract_ntp_arista
from check_modules.ntp_check import extract_ntp_nokia
from check_modules.ntp_check import check_ntp

# Fortinet Platform Tests. 

def test_fortinet_returns_non_IP():
    sample = 'set server test'
    result = extract_ntp_fortinet(sample)
    assert result == ["test"]

def test_fortinet_no_ntp_config():
    sample = ''
    result = extract_ntp_fortinet(sample)
    assert result == []

def test_fortinet_multiple_lines():
    sample = """config system ntp
    set ntpsync enable
    set type custom
    config ntpserver
        edit 1
            set server "10.0.0.50"
        next
    end
    set server-mode enable
    set interface "fortilink"
    end"""
    result = extract_ntp_fortinet(sample)
    assert result == ["10.0.0.50"]

def test_fortinet_returns_empty_no_server():
    sample = 'set server ""'
    result = extract_ntp_fortinet(sample)
    assert result == [""]

def test_fortinet_returns_server_without_quotes():
    sample = 'set server "10.0.0.211"'
    result = extract_ntp_fortinet(sample)
    assert result == ["10.0.0.211"]

def test_wrong_server_fortinet():
    output = "set server 10.0.0.50"
    device_vars = {"ntp_servers": ["10.0.0.55"]}
    result = check_ntp(output, device_vars, "fortinet")
    assert result == ['Missing NTP Server 10.0.0.55', 'Unexpected NTP Server 10.0.0.50']

def test_correct_server_fortinet():
    output = "set server 10.0.0.22"
    device_vars = {"ntp_servers": ["10.0.0.22"]}
    result = check_ntp(output, device_vars, "fortinet")
    assert result == []

# Arista Platform Tests. 

def test_arista_returns_server_vrf():
    sample = """ntp server 10.0.0.126 prefer
            ntp server vrf MGMT 10.0.0.127
            no ntp server 10.0.0.99"""
    result = extract_ntp_arista(sample)
    assert result == ["10.0.0.126", "10.0.0.127"]

def test_arista_returns_nothing():
    sample = "ntp server"
    result = extract_ntp_arista(sample)
    assert result == []

def test_arista_returns_word_value():
    sample = "ntp server test"
    result = extract_ntp_arista(sample)
    assert result == ["test"]

def test_arista_returns_word_value_multiple():
    sample = "ntp server ntp server"
    result = extract_ntp_arista(sample)
    assert result == ["ntp"]

def test_wrong_server_arista():
    output = "ntp server 10.0.0.126 prefer"
    device_vars = {"ntp_servers": ["10.0.0.55"]}
    result = check_ntp(output, device_vars, "arista_eos")
    assert result == ['Missing NTP Server 10.0.0.55', 'Unexpected NTP Server 10.0.0.126']

def test_correct_server_arista():
    output = "ntp server 10.0.0.99"
    device_vars = {"ntp_servers": ["10.0.0.99"]}
    result = check_ntp(output, device_vars, "arista_eos")
    assert result == []

# Nokia Platform Tests. 

def test_nokia_returns_server_multiple_lines():
    sample = """set / system ntp admin-state enable
    set / system ntp network-instance mgmt
    set / system ntp server 10.0.0.55
    set / system ntp server 10.0.0.33
    """
    result = extract_ntp_nokia(sample)
    assert result == ["10.0.0.55", "10.0.0.33"]

def test_nokia_returns_empty_value():
    sample = "set / system ntp server"
    result = extract_ntp_nokia(sample)
    assert result == ['']

def test_nokia_returns_word_value():
    sample = "set / system ntp server test"
    result = extract_ntp_nokia(sample)
    assert result == ['test']

def test_nokia_returns_invalid_config():
    sample = "set / system ntp server 10.0.0.56 10.0.0.88"
    result = extract_ntp_nokia(sample)
    assert result == ['10.0.0.56']

def test_wrong_server_nokia():
    output = "set / system ntp server 10.0.0.56"
    device_vars = {"ntp_servers": ["10.0.0.55"]}
    result = check_ntp(output, device_vars, "nokia_srl")
    assert result == ['Missing NTP Server 10.0.0.55', 'Unexpected NTP Server 10.0.0.56']

def test_correct_server_nokia():
    output = "set / system ntp server 10.0.0.56"
    device_vars = {"ntp_servers": ["10.0.0.56"]}
    result = check_ntp(output, device_vars, "nokia_srl")
    assert result == []

# Vendor Neutral Platform Tests. 

def test_unknown_platform_raises():
    with pytest.raises(ValueError):
        check_ntp("anything", {}, "banana")