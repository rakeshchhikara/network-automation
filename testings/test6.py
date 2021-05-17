import time  # Importing time module to check total runtime.
import pandas  # Importing pandas module to convert csv rows to individual lists based on first row headers.
from netmiko import ConnectHandler  # for connecting and configuring device
import getpass
import threading


def connect_2_device(device,config,host_name):
    connection = ConnectHandler(**device)

    prompt = connection.find_prompt()
    hostname = prompt[12:-1]
    if hostname == host_name:
        print(f'Starting Configuring Device - {hostname}\n')
        output = connection.send_config_set(config)
        connection.commit()
        print(output)
        print(f'Device configured successfully. Closing connection to {hostname}\n\n{80 * "#"}')
        connection.disconnect()
        output_file.write(output + '\n')
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

# password = getpass.getpass(prompt="Enter device password: ")

output_file = open("output_file.txt", 'a+')

threads = list()

# iterating both lists at same time.
for ip, config, host_name in zip(ip_s, config_data, hostnames):
    device = {
        'device_type': 'cisco_xr',
        'host': ip,
        'username': 'cisco',
        'password': 'cisco',
        'port': 22,  # optional, default 22
        'verbose': True  # optional, default False
    }
    th = threading.Thread(target=connect_2_device, args=(device,config,host_name))
    threads.append(th)

for th in threads:
    th.start()

for th in threads:
    th.join()


output_file.close()
end = time.perf_counter()
print(f'Total execution time {round(end-start,2)}')
