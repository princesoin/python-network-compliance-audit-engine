"""NTP check: per-platform extractors and the comparison against inventory."""

def extract_ntp_nokia(output):
    """Extracts NTP server addresses from Nokia SR Linux flat config.

    Expects lines such as `set / system ntp server <address>`, where `ntp` and
    `server` sit at word positions 3 and 4 and the address at position 5.

    Args:
        output (str): Config text collected from the device.

    Returns:
        list[str]: Server addresses with surrounding quotes removed.
    """

    found_servers = []
    for line in output.splitlines():
        words = line.split()
        if words[3:5] == ["ntp", "server"] and len(words) > 5:
            nokia_server_address = words[5]
            nokia_stripped_address = nokia_server_address.strip('"')
            found_servers.append(nokia_stripped_address)
        elif words[3:5] == ["ntp", "server"] and len(words) <= 5:
            found_servers.append('')
    return found_servers

def extract_ntp_fortinet(output):
    """Extracts NTP server addresses from FortiOS `show system ntp` output.

    Reads `set server "<address>"` lines and strips the quotes. Other `set`
    lines, such as `set server-mode`, are ignored.

    Args:
        output (str): Config text collected from the device.

    Returns:
        list[str]: Server addresses with surrounding quotes removed.
    """

    found_servers = []
    for line in output.splitlines():
        words = line.split()
        if words[:2] == ["set", "server"] and len(words) >= 3:
            fgt_server_address = words[2]
            fgt_stripped_address = fgt_server_address.strip('"')
            found_servers.append(fgt_stripped_address)
    return found_servers

def extract_ntp_arista(output):
    # TODO: guard short VRF lines
    """Extracts NTP server addresses from Arista EOS config.

    Handles `ntp server <address> [options]` and
    `ntp server vrf <name> <address>`. `no ntp server ...` lines are ignored.

    Args:
        output (str): Config text collected from the device.

    Returns:
        list[str]: Server addresses with surrounding quotes removed.
    """

    found_servers = []
    for line in output.splitlines():
        words = line.split()
        if words[:3] == ["ntp", "server", "vrf"]:
            arista_server_address = words[4]
            arista_stripped_address = arista_server_address.strip('"')
            found_servers.append(arista_stripped_address)
        elif words[:2] == ["ntp", "server"] and len(words) >= 3:
            arista_server_address = words[2]
            arista_stripped_address = arista_server_address.strip('"')
            found_servers.append(arista_stripped_address)
    return found_servers

NTP_EXTRACTORS = {
    "nokia_srl": extract_ntp_nokia,
    "fortinet": extract_ntp_fortinet,
    "arista_eos": extract_ntp_arista
}

def check_ntp(output, device_vars, device_type):
    """Compare NTP servers on the device with the inventory.

    Args:
        output: Saved config text collected from the device.
        device_vars: The device's `vars` block from devices.yml.
        device_type: Platform key, e.g. "nokia_srl" or "fortinet".

    Returns:
        A list of finding strings. An empty list means PASS.

    Raises:
        ValueError: If no extractor exists for device_type.
    """
    
    expected = []
    findings = []
    extractor = NTP_EXTRACTORS.get(device_type)
    if extractor is None:
        raise ValueError(f"No NTP extractor for {device_type}")
    
    configured = extractor(output)

    for entry in device_vars.get("ntp_servers", []):
        expected.append(entry.split()[0])

    for server in expected:
        if server not in configured:
            findings.append(f"Missing NTP Server {server}")

    for server in configured:
        if server not in expected:
            findings.append(f"Unexpected NTP Server {server}")
    
    return findings