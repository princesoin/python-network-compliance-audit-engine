from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader
import yaml

# Load the template file. 

with open ("/home/princesoin/netlab/repo/inventory/devices.yml") as file:
    inventory = yaml.safe_load(file)

with open("/home/princesoin/netlab/repo/inventory/platforms.yml") as file:
    platform_inv = yaml.safe_load(file)
    
# Establish variable for device connection details which netmiko uses later.

device_connection = inventory["ceos1"]["connection"]

platform = device_connection["device_type"]

device_error = platform_inv[platform]["error_handling"]

# Establish variable for the vars template data which jinja2 will use.

device_template_data = inventory["ceos1"]["vars"]

# Link to the template enviornment (root folder)

template_env = Environment(loader = FileSystemLoader("/home/princesoin/netlab/repo/templates/eos"))

# Link to the actual template file and create a new variable. 

server_template = template_env.get_template("servers.j2")

# Render the output of the yaml data linked with the jinja template. Final variable. 

rendered_data = server_template.render(device_template_data)

# Print out the rendered file and ensure it looks how is expected. 

# print(rendered_data)

# Establish connection to the switch using netmiko (Use Yaml). 

net_connect = ConnectHandler(**device_connection)
net_connect.enable()
server_config = rendered_data.splitlines()
output = net_connect.send_config_set(server_config, **device_error)
save_output = net_connect.save_config()
print(output)
net_connect.disconnect()