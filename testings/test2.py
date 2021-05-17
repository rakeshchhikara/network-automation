import time
import pandas
from netmiko import ConnectHandler
import threading

start = time.time()

config_data = pandas.read_csv("snmp_config_file.csv", header=0)
hostnames = list(config_data.hostname)
ip_s = list(config_data.ip)
config_data = list(config_data.config_command)

print(hostnames)
print(ip_s)
print(config_data)

#quit(1)

def configure_device(device):
    connection = ConnectHandler(**device)

    prompt = connection.find_prompt()
    hostname = prompt[12:-1]
    print(f'Starting Configuring Device - {hostname}\n\n')
    output = connection.send_config_set(config_line)
    output1 = connection.commit()
    print(output)
    print(output1)
    print(f'closing connection to {hostname}\n\n{80 *"#"}')
    connection.disconnect()


threads = list()
for ip,config in zip(ip_s,config_data):
    device = {
           'device_type': 'cisco_xr',
           'host': ip,
           'username': 'cisco',
           'password': 'cisco',
           'port': 22,             # optional, default 22
           'verbose': True         # optional, default False
           }
    config_line = config

    # creating a thread for each router which will be configured
    th = threading.Thread(target=configure_device, args=(device,))
    threads.append(th)  # appending the thread to the list

# starting the threads
for th in threads:
    th.start()
    time.sleep(1)

# waiting for the threads to finish
for th in threads:
    th.join()

end = time.time()
print(f'Total execution time:{end-start}')