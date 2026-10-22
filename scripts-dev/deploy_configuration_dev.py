"""Deployment: renders Jinja templates and pushes the config to devices.

Unlike the audit, this program changes device configuration.
"""

from netmiko import ConnectHandler
import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path

def load_yaml(path):
    """Loads a YAML file such as the inventory or platforms file.

    Args:
        path (str): Location of the YAML file.

    Returns:
        dict: The parsed contents of the file.

    Raises:
        FileNotFoundError: If no file exists at `path`.
        yaml.YAMLError: If the file is not valid YAML.
    """

    try:
        with open(path, 'r') as file:
           yaml_file = yaml.safe_load(file)
           return yaml_file
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Could not load {path}: file missing or invalid YAML")
        raise(e)

def render_config(device_vars, template_dir, template_name):
    """Renders a Jinja template into a list of config lines.

    Args:
        device_vars (dict): The device's `vars` block, used as template data.
        template_dir (str): Folder containing the platform's templates.
        template_name (str): Template file name, e.g. "servers.j2".

    Returns:
        list[str]: The rendered config with blank lines removed.

    Raises:
        jinja2.TemplateNotFound: If the template is missing from `template_dir`.
    """

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
    """Opens a Netmiko SSH session to a device.

    Args:
        connection (dict): Netmiko connection details from the inventory.

    Returns:
        netmiko.BaseConnection: The open session.
    """

    net_connect = ConnectHandler(**connection) 
    return net_connect

def send_config(net_connect, config_lines, error_handling):
    """Pushes config lines to a device.

    Args:
        net_connect (netmiko.BaseConnection): An open session.
        config_lines (list[str]): Config commands to send.
        error_handling (dict): Extra keyword arguments for `send_config_set`,
            such as the platform's error pattern.

    Returns:
        str: The device's output while applying the config.
    """
    
    net_connect.enable()    
    return net_connect.send_config_set(config_lines, **error_handling)

ROOT_DIR = Path(__file__).resolve().parent.parent

INVENTORY_PATH = ROOT_DIR / "inventory" / "devices.yml"
PLATFORMS_PATH = ROOT_DIR / "inventory" / "platforms.yml"

def main():
    """Renders and pushes config to every device in the inventory."""
    
    inventory = load_yaml(INVENTORY_PATH)
    platforms = load_yaml(PLATFORMS_PATH )

    for host, attributes in inventory.items():
        device_type = attributes["connection"]["device_type"]
        platform = platforms[device_type]
        template_dir = ROOT_DIR / platform["template_dir"]
        final_config_lines = render_config(attributes["vars"], str(template_dir), "servers.j2")
        final_error_handling = platform["error_handling"]

        with connect_device((attributes["connection"])) as conn:
            output = send_config(conn, final_config_lines, final_error_handling)
            print(output)

if __name__ == "__main__":
    main()