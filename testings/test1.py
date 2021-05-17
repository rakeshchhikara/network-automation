from netmiko import ConnectHandler
from datetime import datetime
import time
import threading  #implements threading in Python
import pandas


# getting the current time as a timestamp
start = time.time()

config_data = pandas.read_csv("snmp_config_file.csv", header=0)
hostnames = list(config_data.hostname)
ip_s = list(config_data.ip)
config-commands = list(config_data.config-command)

# this function backups the config of a router
# this is the target function which gets executed by each thread
def backup(device):
    connection = ConnectHandler(**device)
    print('Entering the enable mode...')
    connection.enable()

    output = connection.send_command('show run')
    # print(output)
    prompt = connection.find_prompt()
    hostname = prompt[0:-1]
    # print(hostname)

    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    filename = f'{hostname}_{year}-{month}-{day}_backup.txt'
    with open(filename, 'w') as backup:
        backup.write(output)
        print(f'Backup of {hostname} completed successfully')
        print('#' * 30)

    print('Closing connection')
    connection.disconnect()



with open('devices.txt') as f:
    devices = f.read().splitlines()

# creating an empty list (it will store the threads)
threads = list()
for ip in devices:
    device = {
           'device_type': 'cisco_ios',
           'host': ip,
           'username': 'u1',
           'password': 'cisco',
           'port': 22,             # optional, default 22
           'secret': 'cisco',      # this is the enable password
           'verbose': True         # optional, default False
           }
    # creating a thread for each router that executes the backup function
    th = threading.Thread(target=backup, args=(device,))
    threads.append(th) # appending the thread to the list

# starting the threads
for th in threads:
    th.start()

# waiting for the threads to finish
for th in threads:
    th.join()

end = time.time()
print(f'Total execution time:{end-start}')
