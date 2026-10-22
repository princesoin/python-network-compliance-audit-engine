
def extract_firmware_nokia(output): 
    found_firmware_verison = []

    for line in output.splitlines():
        words = line.split()
        if words[:2] == ["Software", "Version"]:
            software_version = words[3]
            found_firmware_verison.append(software_version)
        # if words[:2] == ["Build", "Number"]:
        #     build_version = words[3]
        #     found_firmware_verison.append(build_version)

    return found_firmware_verison


def extract_firmware_fortinet(output):
    found_firmware_verison = []

    for line in output.splitlines():
        words = line.split()
        if words[:2] == ["Version:", "FortiGate-ARM64-KVM"]:
            software_version = words[2]
            found_firmware_verison.append(software_version)

    return found_firmware_verison

def extract_firmware_arista(output):
    found_firmware_verison = []

    for line in output.splitlines():
        words = line.split()
        if words[:3] == ["Software", "image", "version:"]:
            software_version = words[3]
            found_firmware_verison.append(software_version)

    return found_firmware_verison

FIRMWARE_EXTRACTOR = {
    "arista_eos" : extract_firmware_arista,
    "nokia_srl" : extract_firmware_nokia,
    "fortinet" : extract_firmware_fortinet
}

def check_firmware(output, device_vars, device_type):
    findings = []
    expected = []

    extractor = FIRMWARE_EXTRACTOR.get(device_type)

    if extractor is None:
        raise ValueError(f"No {device_type} in extractor")
    
    configured = extractor(output)
    
    for entry in device_vars.get("firmware_version", []):
        expected.append(entry.split()[0])

    for server in expected:
        if server not in configured:
            findings.append(f"Missing firmware version {server}")

    for server in configured:
        if server not in expected:
            findings.append(f"Unexpected firmware version {server}")
    
    return findings