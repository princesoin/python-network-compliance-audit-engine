# General Imports 
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException
import yaml
from checks import run_checks
import json

# Function to load in YAML files, i.e. Inventory, Platforms. Converts Yaml Key: value pairs into Dict. 
def load_yaml(path):
    try:
        with open(path) as file:
            imported_file = yaml.safe_load(file)
        return imported_file
    except FileNotFoundError as e:
        print(f"Could not find specfied yaml at {path}")
        raise e

# Function to Connect to device. 
def connect_device(connection):
    connect_device = ConnectHandler(**connection) # ** Is used to unpack the connection dictionary. i.e. it will be read as device_type : nokia_srl, host : clab-dev-topology-srl1 etc. 
    return connect_device

# Print a PASS or FAIL line for every check.
def audit_result(hostname, results):
    for check_name, findings in results.items():
        if findings:
            print(f"[{hostname}] FAIL {check_name}: {findings}")
        else:
            print(f"[{hostname}] PASS {check_name}")

# Save the collected config to a file named after the device.
def save_output(hostname, output):
    with open(f"{hostname}.running_config.txt", "w", encoding="utf-8") as file:
        file.write(output)

# Send show configuration comand to device. 
def send_command(establish_conn, command):
    establish_conn.enable()
    return establish_conn.send_command(command)

# Main. 
def main():
    inventory = load_yaml("/home/princesoin/netlab/repo/inventory/devices.yml")
    platforms = load_yaml("/home/princesoin/netlab/repo/inventory/platforms.yml")
    unreachable_devices = []
    audit_results_json = []

    for host, attributes in inventory.items():
        device_type = attributes["connection"]["device_type"]
        device_hostname = attributes["connection"]["host"]
        platform_vars = platforms[device_type]

        try:
            with connect_device(attributes["connection"]) as conn:
                output = send_command(conn, platform_vars["collect_command"])
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
            print(f"[{device_hostname}] Could not connect: {e}")
            unreachable_devices.append(device_hostname)
            continue

        save_output(device_hostname, output)

        results = run_checks(output, attributes["vars"], device_type) # Runs all Audit checks 1 by 1 on each device.
        
        audit_result(device_hostname, results)

        formatted_json_device_data = {
            "hostname": device_hostname,
            "results": results
        }
        
        audit_results_json.append(formatted_json_device_data)
        
    print("Unreachable devices:", unreachable_devices)

    with open(f"master_audit_results.json", "w", encoding="utf-8") as json_file:
        json.dump(audit_results_json, json_file)

    print(f"Audit Files Saved under devices:")
   
if __name__ == "__main__":
    main()