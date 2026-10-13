# General Imports. 
from netmiko import ConnectHandler
import yaml
from jinja2 import Template, Environment, FileSystemLoader, TemplateNotFound

# Creating a reusable function with error handling for yaml file loading. 

def load_yaml(path):
    try:
        with open(path, 'r') as file:
           yaml_file = yaml.safe_load(file)
           return yaml_file
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Could not load {path}: file missing or invalid YAML")
        raise(e)

def render_config(device_vars, template_dir, template_name):
    try: 
        template_dir = Environment(loader = FileSystemLoader(template_dir))
        template_name = template_dir.get_template(template_name)
        device_vars = template_name.render(device_vars)
        formatted_config = []
        for line in device_vars.splitlines():
            if line.strip():
                formatted_config.append(line)
        return formatted_config
    except TemplateNotFound as e:
        print(f"jinja2 template in specfied path {template_dir}: not found.")
        raise(e)

def connect_device(connection):
    net_connect = ConnectHandler(**connection) 
    return net_connect

def send_config(net_connect, config_lines, error_handling):
    net_connect.enable()    
    return net_connect.send_config_set(config_lines, **error_handling)

def main():
    inventory = load_yaml("/home/princesoin/netlab/repo/inventory/devices.yml")
    platforms = load_yaml("/home/princesoin/netlab/repo/inventory/platforms.yml")

    for host, attributes in inventory.items():
        device_type = attributes["connection"]["device_type"]
        platform = platforms[device_type]
        final_config_lines = render_config(attributes["vars"], platform["template_dir"], "servers.j2")
        final_error_handling = platform["error_handling"]

        with connect_device((attributes["connection"])) as conn:
            output = send_config(conn, final_config_lines, final_error_handling)
            print(output)

if __name__ == "__main__":
    main()