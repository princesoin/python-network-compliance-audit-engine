from netmiko import ConnectHandler
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

arista_device =  {
    'device_type' : 'arista_eos',
    'host' : 'clab-dev-topology-ceos1',
    'username' : 'admin',
    'password' : 'admin',
}

device_data = {
    "hostname" : "ceos1",
    "site" : "lab",
    "contact" : "testemail@email"
}

template_env = Environment(loader=FileSystemLoader("/home/princesoin/netlab/repo/templates/eos"))

banner_template = template_env.get_template("banner.j2")

rendered_output = banner_template.render(device_data)

net_connect = ConnectHandler(**arista_device)
net_connect.enable()
banner_config = rendered_output.splitlines()
print(banner_config)
output = net_connect.send_config_set(banner_config)
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
