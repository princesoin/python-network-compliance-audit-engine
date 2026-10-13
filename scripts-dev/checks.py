
def check_ntp(output, device_vars):
    expected = device_vars.get("ntp_servers", [])
    missing = []
    for server in expected:
        if server not in output:
            missing.append(server)
    return missing

ALL_CHECKS = {
    "ntp_check": check_ntp,
    # "logging": check_logging,
    # "telnet": check_telnet,
}

def run_checks(output, device_vars):
    results = {}
    for check_name, check_function in ALL_CHECKS.items():
        results[check_name] = check_function(output, device_vars)
    return results