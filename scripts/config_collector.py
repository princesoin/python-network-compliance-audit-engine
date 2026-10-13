# General Imports 
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException
import yaml

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

# Function to Send show configuration comand to device. 
def send_command(establish_conn, command):
    establish_conn.enable()
    return establish_conn.send_command(command)

# Main function. 
def main():
    inventory = load_yaml("/home/princesoin/netlab/repo/inventory/devices.yml")
    platforms = load_yaml("/home/princesoin/netlab/repo/inventory/platforms.yml")

    unreachable_devices = []

    for host, attributes in inventory.items():
        device_types = attributes["connection"]["device_type"]
        device_hostname = attributes["connection"]["host"]
        platform_vars = platforms[device_types]
        ntp_matcher = attributes["vars"]["ntp_servers"]
        show_run_command = platform_vars["collect_command"]
        try:
            with connect_device(attributes["connection"]) as conn:
                output = send_command(conn, show_run_command)

            with open(f"{device_hostname}.running_config.txt", "w", encoding="utf-8") as file:
                new_file = file.write(output)

            for server in ntp_matcher:
                if server in output:
                    print(f"[{device_hostname}] Found server: {server}")
                else:
                    print(f"[{device_hostname}] WARNING: NTP server {server} is missing!")
            
            print(f"Configuration file saved to {device_hostname}.running_config.txt")
       
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
            print(f"Netmiko raised an excetion for {device_hostname}: {e}")
            unreachable_devices.append(device_hostname)
            continue

    print("List of Unreachable devices: ", unreachable_devices)

if __name__ == "__main__":
    main()