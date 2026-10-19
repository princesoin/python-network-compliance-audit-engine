"""Audit collector: connects to each device, saves its config, runs the checks."""

from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException
import yaml
from checks import run_checks
import json

def load_yaml(path):
    """Loads a YAML file such as the inventory or platforms file.

    Args:
        path (str): Location of the YAML file.

    Returns:
        dict: The parsed contents of the file.

    Raises:
        FileNotFoundError: If no file exists at `path`.
    """
    
    try:
        with open(path) as file:
            imported_file = yaml.safe_load(file)
        return imported_file
    except FileNotFoundError as e:
        print(f"Could not find specfied yaml at {path}")
        raise e

def connect_device(connection):
    """Opens a Netmiko SSH session to a device.

    Args:
        connection (dict): Netmiko connection details from the inventory
            (device_type, host, username, password).

    Returns:
        netmiko.BaseConnection: The open session.

    Raises:
        NetmikoTimeoutException: If the device does not respond.
        NetmikoAuthenticationException: If the login is rejected.
    """

    connect_device = ConnectHandler(**connection) # ** Is used to unpack the connection dictionary. i.e. it will be read as device_type : nokia_srl, host : clab-dev-topology-srl1 etc. 
    return connect_device

def audit_result(hostname, results):
    """Prints a PASS or FAIL line for each check result.

    Args:
        hostname (str): Device label used in the output line.
        results (dict[str, list[str]]): Maps check name to its findings.
    """

    for check_name, findings in results.items():
        if findings:
            print(f"[{hostname}] FAIL {check_name}: {findings}")
        else:
            print(f"[{hostname}] PASS {check_name}")

# def save_output(hostname, output):
#     """Saves the collected config to `<hostname>.running_config.txt`.

#     Args:
#         hostname (str): Device label used in the file name.
#         output (str): Config text to write.
#     """

#     with open(f"{hostname}.running_config.txt", "w", encoding="utf-8") as file:

#         file.write(output)

def send_command(establish_conn, command):
    """Runs one show command on an open session.

    Args:
        establish_conn (netmiko.BaseConnection): An open session.
        command (str): The show command to run.

    Returns:
        str: The command output.
    """

    establish_conn.enable()
    return establish_conn.send_command(command)

def main():
    """Audits every device in the inventory.

    Collects each device's config, saves it, runs the checks and writes
    master_audit_results.json. Devices that time out or reject the login are
    listed as unreachable and skipped.
    """

    inventory = load_yaml("/home/princesoin/netlab/repo/inventory/devices.yml")
    platforms = load_yaml("/home/princesoin/netlab/repo/inventory/platforms.yml")
    unreachable_devices = []
    audit_results_json = []

    for device_name, attributes in inventory.items():
        device_type = attributes["connection"]["device_type"]
        device_hostname = attributes["connection"]["host"]
        platform_vars = platforms[device_type]

        outputs = {}

        try:
            with connect_device(attributes["connection"]) as conn:
                for name, command in platform_vars["collect_command"].items():
                    outputs[name] = send_command(conn, command)
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
            print(f"[{device_hostname}] Could not connect: {e}")
            unreachable_devices.append(device_hostname)
            continue

        # save_output(device_hostname, outputs)
        results = run_checks(outputs, attributes["vars"], device_type) # Runs all Audit checks 1 by 1 on each device.
        audit_result(device_name, results)

        formatted_json_device_data = {
            "hostname": device_name,
            "results": results
        }
        
        audit_results_json.append(formatted_json_device_data)
        
    print("Unreachable devices:", unreachable_devices)

    with open("master_audit_results.json", "w", encoding="utf-8") as json_file:
        json.dump(audit_results_json, json_file)

    print("Audit Files Saved under devices:")
   
if __name__ == "__main__":
    main()