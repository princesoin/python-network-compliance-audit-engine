
def check_ntp(output, device_vars):
    keyword = "server"
    configured = []
    expected = []
    findings = []

# NTP Check. 
    for line in output.splitlines():
        if "ntp server" in line:
            words = line.split()
            keyword_index = words.index(keyword)
            if keyword_index + 1 < len(words):
                server_address = words[keyword_index + 1]
                configured.append(server_address)
            else:
                print("The keyword is on the very last line.")

    for entry in device_vars.get("ntp_servers", []):
        expected.append(entry.split()[0])

    for server in expected:
        if server not in configured:
            findings.append(f" missing NTP server {server}")

    for server in configured:
        if server not in expected:
            findings.append(f" unexpected NTP server {server}")

    return findings

#def check_logging():
    ###

# Runs checks in order. 

ALL_CHECKS = {
    "ntp_check": { 
        "function": check_ntp,
        "description": "An accurate and consistent time source is used for event logging.",
        "why": "",
        "ism_control": "ISM-0988",
        "fix": "",
    },
    # "logging": { 
    #         "function": check_logging,
    #         "description": "",
    #         "why": "",
    #         "ism_control": "",
    #         "fix": "",
    #     },
    # "telnet": { 
    #             "function": check_telnet,
    #             "description": "",
    #             "why": "",
    #             "ism_control": "",
    #             "fix": "",
    #         },
}

def run_checks(output, device_vars):
    results = {}
    for check_name, check_info in ALL_CHECKS.items():
        check_function = check_info.get("function")
        results[check_name] = check_function(output, device_vars)
    return results

if __name__ == "__main__":
    fake_config = "ntp ntp server 10.0.0.126\nntp server 10.0.0.127"
    fake_vars = {"ntp_servers": ["10.0.0.126", "10.0.0.200"]}
    print(run_checks(fake_config, fake_vars))