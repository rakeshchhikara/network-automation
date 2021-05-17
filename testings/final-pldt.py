# THIS SCRIPT WILL TAKE DATA FROM CSV FILE FOR DEVICE_IP AND RESPECTIVE CONFIG LINE AND THEN WILL CONFIGURE EACH
# DEVICE WHILE MATCHING HOSTNAME ON DEVICE. TAKING ADVANTAGE OF MULTI-THREADING TO SPEED-UP CONFIGURATION.

import time  # Importing time module to check total runtime.
import pandas  # Importing pandas module to convert csv rows to individual lists based on first row headers.
from netmiko import ConnectHandler  # for connecting and configuring device
import getpass          # To supply password securely.
import threading        # Make use of multi-threading to save time.


# This function is connect and configure device.
def connect_2_device(device, config, host_name):
    connection = ConnectHandler(**device)

    prompt = connection.find_prompt()
    hostname = prompt[12:-1]
    if hostname == host_name:
        pre_snmp = connection.send_config_set("show run snmp | i location")
        print(f'Starting Configuring Device - {hostname}\n')
        output = connection.send_config_set(config)
        connection.commit()
        post_snmp = connection.send_config_set("do show run snmp | i location")
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


# Capturing start time
start = time.perf_counter()

# Converting csv rows to individual lists based on first row headers.
config_data = pandas.read_csv("snmp_config_file.csv", header=0)
hostnames = list(config_data.hostname)
ip_s = list(config_data.ip)
config_data = list(config_data.config_command)

# Getting password of device from User
password = getpass.getpass(prompt="Enter device password: ")

# This file will save output of devices configuration or error.
output_file = open("output_file.txt", 'a+')

# Make empty list to store threads.
threads = list()

# iterating both lists at same time.
for ip, config, host_name in zip(ip_s, config_data, hostnames):
    device = {
        'device_type': 'cisco_xr',
        'host': ip,
        'username': 'cisco',
        'password': password,       # Supply device password from getpass module.
        'port': 22,  # optional, default 22
        'verbose': True  # optional, default False
    }

    # Create and store threads of each device in list.
    th = threading.Thread(target=connect_2_device, args=(device, config, host_name))
    threads.append(th)

# Iterate over threads list to start them. Using sleep timer to limit number of threads.
for th in threads:
    th.start()

# Join all threads before moving ahead.
for th in threads:
    th.join()


output_file.close()
end = time.perf_counter()

print(f'Total execution time {round(end-start,2)}')
