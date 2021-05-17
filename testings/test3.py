import time     # Importing time module to check total runtime.
import pandas   # Importing pandas module to convert csv rows to individual lists based on first row headers.
from netmiko import ConnectHandler  # netmiko for connecting and configuring device
import getpass

# Capturing start time
start = time.time()

# Converting csv rows to individual lists based on first row headers.
config_data = pandas.read_csv("snmp_config_file.csv", header=0)
hostnames = list(config_data.hostname)
ip_s = list(config_data.ip)
config_data = list(config_data.config_command)

password = getpass.getpass(prompt="Enter device password: ")

# iterating both lists at same time.
for ip,config in zip(ip_s,config_data):
    device = {
           'device_type': 'cisco_xr',
           'host': ip,
           'username': 'cisco',
           'password': password,
           'port': 22,             # optional, default 22
           'verbose': True         # optional, default False
           }

    connection = ConnectHandler(**device)

    prompt = connection.find_prompt()
    hostname = prompt[12:-1]
    print(f'Starting Configuring Device - {hostname}\n')
    output = connection.send_config_set(config)
    connection.commit()
    print(output)
    print(f'closing connection to {hostname}\n\n{80 * "#"}')
    connection.disconnect()


end = time.time()
print(f'Total execution time:{end-start}')