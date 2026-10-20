"""Registry of audit checks and the function that runs them in order."""

from check_modules.ntp_check import check_ntp
from check_modules.firmware_check import check_firmware
from check_modules.hardening_check import check_hardening

ALL_CHECKS = {
    "ntp_check": { 
        "function": check_ntp,
        "command": "ntp",
        "description": "An accurate and consistent time source is used for event logging.",
        "why": "",
        "ism_control": "ISM-0988",
        "fix": "",
    },
    
      "firmware_check": { 
        "function": check_firmware,
        "command": "firmware",
        "description": "Requires checking and verifying network device firmware and running configurations against a known good baseline after patching.",
        "why": "",
        "ism_control": "ISM-2161",
        "fix": "",
    },
        "hardening_check": { 
        "function": check_hardening,
        "command": "hardening",
        "description": "All data communicated over network infrastructure must be encrypted using ASD-approved cryptography",
        "why": "",
        "ism_control": "ISM-1781",
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

def run_checks(outputs, device_vars, device_type):
    """Runs every check in ALL_CHECKS against one device.

    Args:
        outputs (dict): Already collected config text strings mapped by command key.
        device_vars (dict): The device's `vars` block from devices.yml.
        device_type (str): Platform key, passed through to each check.

    Returns:
        dict[str, list[str]]: Maps each check name to its list of findings.
    """
    results = {}
    
    for check_name, check_info in ALL_CHECKS.items():
        check_function = check_info["function"]
        command_name = check_info["command"]  
        
        check_output = outputs.get(command_name, "")
        
        results[check_name] = check_function(check_output, device_vars, device_type)
        
    return results