
def extract_ntp_nokia(output):
    found_servers = []
    for line in output.splitlines():
        words = line.split()
        if words[3:5] == ["ntp", "server"]:
            nokia_server_address = words[5]
            nokia_stripped_address = nokia_server_address.strip('"')
            found_servers.append(nokia_stripped_address)
    return found_servers

def extract_ntp_fortinet(output):
    found_servers = []
    for line in output.splitlines():
        words = line.split()
        if words[:2] == ["set", "server"] and len(words) >= 3:
            fgt_server_address = words[2]
            fgt_stripped_address = fgt_server_address.strip('"')
            found_servers.append(fgt_stripped_address)
    return found_servers

def extract_ntp_arista(output):
    found_servers = []
    for line in output.splitlines():
        words = line.split()
        if words[:2] == ["ntp", "server"]:
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
            findings.append(f"Unexpected NTP server {server}")
    
    return findings

# if __name__ == "__main__":
#     fgt_sample = """config system ntp
#     set ntpsync enable
#     set type custom
#     config ntpserver
#         edit 1
#             set server "10.0.0.211"
#         next
#     end
# end"""
#     nokia_sample = """set / system clock timezone 
# set / system ntp admin-state enable
# set / system ntp network-instance mgmt
# set / system ntp server "10.0.0.233"
# commit now
# """
#     arista_sample = """clock timezone
# ntp server "10.0.0.23"
# logging host "10.0.0.10"
# """

#     print(extract_ntp_fortinet(fgt_sample))
#     print(extract_ntp_nokia(nokia_sample))
#     print(extract_ntp_arista(arista_sample))