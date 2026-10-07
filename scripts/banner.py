from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader
import yaml

with open("/home/princesoin/netlab/repo/inventory/devices.yml") as file:
    inventory = yaml.safe_load(file)

device = inventory["ceos1"]["connection"]

device_template = inventory["ceos1"]["vars"]

template_env = Environment(loader=FileSystemLoader("/home/princesoin/netlab/repo/templates/eos"))

banner_template = template_env.get_template("banner.j2")

rendered_output = banner_template.render(device_template)

net_connect = ConnectHandler(**device)
net_connect.enable()
banner_config = rendered_output.splitlines()
print(banner_config)
output = net_connect.send_config_set(banner_config)
save_output = net_connect.save_config()
print(output)
net_connect.disconnect()

#    "device2" : {
#    "hostname" : "srl1",
#    "site" : "lab",
#    "contact" : "testemail@email"
#},
# "device3" : {
#    "hostname" : "srl2",
#    "site" : "lab",
#    "contact" : "testemail@email"
#},
#}
