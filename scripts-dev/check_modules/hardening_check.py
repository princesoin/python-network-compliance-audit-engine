def extract_hardening_arista(output):
    ssh_status = []
    for line in output.splitlines():
        words = line.split()
        if not words:
            continue
        if "SSHD" in words[:2] and "status" in words:
            ssh_status.append(["SSHD Status", words[-1]])
        if words[:2] == ["FIPS", "status:"]:
            ssh_status.append(["FIPS Status", words[2]])
    return ssh_status

def extract_hardening_nokia(output):
    ssh_status = []
    current_block = None

    for line in output.splitlines():
        words = line.split()
        if not words:
            continue
        if words[:2] == ["ssh-server", "mgmt"]:
            current_block = "SSHD Status"

        elif words[0] == "fips-140":
            current_block = "FIPS Status"

        elif words[0] == "admin-state" and current_block is not None:
            ssh_status.append([current_block, words[1]])
            current_block = None

    return ssh_status

def extract_hardening_fortinet(output):
    ssh_status = []
    for line in output.splitlines():
        words = line.split()
        if not words:
            continue
        if "SSH" in words and any("v2" in w for w in words):
            ssh_status.append(["SSHD Status", words[3]])
        if "FIPS-CC" in words or "fips-cc" in words:
            ssh_status.append(["FIPS Status", words[-1]])
    return ssh_status

Hardening_EXTRACTORS = {
    "nokia_srl": extract_hardening_nokia,
    "fortinet": extract_hardening_fortinet,
    "arista_eos": extract_hardening_arista
}

def check_hardening(output, device_vars, device_type):
    """Compare Hardening Settings on the device with the inventory.

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
    extractor = Hardening_EXTRACTORS.get(device_type)

    if extractor is None:
        raise ValueError(f"No Hardening extractor for {device_type}")
    
    configured = extractor(output)

    hardening_vars = device_vars.get('hardening_configuration', {})
    
    expected_mapping = {
        "SSHD Status": hardening_vars.get("sshd_status"),
        "FIPS Status": hardening_vars.get("fips_status")
    }

    expected = [[label, value] for label, value in expected_mapping.items() if value is not None]

    for expected_item in expected:
        if expected_item not in configured:
            findings.append(f"Missing or Incorrect Hardening Setting: {expected_item[0]} (Expected: {expected_item[1]})")

    for configured_item in configured:
        if configured_item not in expected:
            findings.append(f"Unexpected Setting Found active on device: {configured_item[0]}={configured_item[1]}")
    
    return findings