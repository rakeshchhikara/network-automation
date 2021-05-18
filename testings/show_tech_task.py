import csv
from netmiko import ConnectHandler
import getpass

device_ip = input('Enter device ip: ')
# password = getpass.getpass(prompt='Enter device Password: ')

device = {
    'device_type': 'cisco_xr',
    'host': device_ip,
    'username': 'cisco',
    'password': 'cisco',
    'port': 22,  # optional, default 22
    'verbose': True  # optional, default False
}

connection = ConnectHandler(**device)
output = connection.send_command('show tech')
print(output)

connection.disconnect()
print('Disconnected from device')
