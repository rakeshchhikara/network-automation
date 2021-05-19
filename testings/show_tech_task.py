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
prompt = connection.find_prompt()
hostname = prompt[12:-1]
print(f'Generating show techs on device {hostname}. Please wait...')
output = connection.send_command_expect('show tech-support', expect_string=r'available', max_loops=5000, delay_factor=5)
print(output)

connection.disconnect()
print('Disconnected from device')
