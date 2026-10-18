from check_modules.ntp_check import check_ntp
# Runs checks in order. 

ALL_CHECKS = {
    "ntp_check": { 
        "function": check_ntp,
        "description": "An accurate and consistent time source is used for event logging.",
        "why": "",
        "ism_control": "ISM-0988",
        "fix": "",
    }
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

def run_checks(output, device_vars, device_type):
    results = {}
    for check_name, check_info in ALL_CHECKS.items():
        check_function = check_info.get("function")
        results[check_name] = check_function(output, device_vars, device_type)
    return results