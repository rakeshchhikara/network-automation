import time     # Importing time module to check total runtime.
import pandas   # Importing pandas module to convert csv rows to individual lists based on first row headers.
from netmiko import ConnectHandler  # for connecting and configuring device
import getpass

# Capturing start time
start = time.time()

# Converting csv rows to individual lists based on first row headers.
config_data = pandas.read_csv("snmp_config_file.csv", header=0)
hostnames = list(config_data.hostname)
ip_s = list(config_data.ip)
config_data = list(config_data.config_command)

password = getpass.getpass(prompt="Enter device password: ")

output_file = open("output_file.txt", 'a+')

# iterating both lists at same time.
for ip, config, host_name in zip(ip_s, config_data, hostnames):
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
    if hostname == host_name:
        pre_snmp = connection.send_config_set("show run snmp | i location")
        print(f'Starting Configuring Device - {hostname}\n')
        output = connection.send_config_set(config)
        connection.commit()
        post_snmp = connection.send_config_set("show run snmp | i location")
        print(output)
        print(f'Device configured successfully. Closing connection to {hostname}\n\n{80 * "#"}')
        connection.disconnect()
        output_file.write(pre_snmp + output + post_snmp + '\n')
        output_file.write(80 * '#' + '\n')

    else:
        connection.disconnect()
        error1 = f'Hostname mismatch with snmp_config_file. It\'s {hostname} on device but config file has {host_name}'
        output_file.write(error1 + '\n' + 80 * '#' + '\n')
        print(error1)
        print(80 * '#' + '\n')


output_file.close()
end = time.time()
print(f'Total execution time:{end-start}')
