# Author: Rakesh Kumar
# Usage: Generate various show-techs on IOS-XR routers and upload to Cisco TAC Case.
# Version: 3

from netmiko import ConnectHandler, file_transfer
import getpass
import requests
from requests.auth import HTTPBasicAuth
import colorama
from colorama import Fore
colorama.init(autoreset=True)


url = 'https://cxd.cisco.com/home/'
sr_username = input(f"Enter SR number: ")
sr_token = input(f"Enter Upload Token: ")

# Take user input for Device IP and run show tech command.
device_ip = input(f'Enter device ip: ')
username = input(f'Enter your username for device Login: ')
password = getpass.getpass(prompt='Enter device Password: ')


lines = []
while True:
    line = input(f'Enter command: ')
    if line:
        lines.append(line)
    else:
        break
text = '\n'.join(lines)

local_files = []

print(f'\nShow tech of these commands will be taken: {Fore.BLUE}{lines}\n')

device = {
    'device_type': 'cisco_xr',
    'host': device_ip,
    'username': username,
    'password': password,
    'port': 22,  # optional, default 22
    'verbose': True  # optional, default False
}

connection = ConnectHandler(**device)
prompt = connection.find_prompt()
prompt_strip = prompt.find(':') + 1
hostname = prompt[prompt_strip:-1]

for user_cmd in lines:
    print(f'\n{Fore.GREEN}Generating "{user_cmd}" on device {hostname}. Please wait...\n')
    output = connection.send_command(user_cmd, expect_string=r'available', max_loops=50000, delay_factor=5)
    print(output)

    # Store show-tech file name on device in 'filename' variable.
    location1 = output.find('showtech-')
    filename = output[location1:-1]
    filename = filename.strip()

    print(f'{Fore.BLUE}Now transferring file...{filename}\n')

    try:
        transfer_dict = file_transfer(
            connection,
            source_file=filename, file_system='harddisk:/showtech',
            dest_file=filename, direction='get', overwrite_file=True)
        print(f'{Fore.MAGENTA} File Download status: {transfer_dict}')

        x = transfer_dict.get("file_transferred")
        y = transfer_dict.get('file_verified')

        if x and y is True:
            local_files.append(filename)

    except EOFError:
        print(f'{Fore.LIGHTRED_EX}EOF error occurred while transferring file - {filename}. Please check')

connection.disconnect()
print(f'\n{Fore.RED}Disconnected from device')

print(f'{Fore.GREEN}Following files generated and downloaded\n{local_files}')

print(f'Now following files will be transferred to Case - {sr_username} : \"{local_files}\"')

uploaded_files = list()

for file in local_files:

    auth = HTTPBasicAuth(sr_username, sr_token)
    filename = file

    f = open(filename, 'rb')
    r = requests.put(url + filename, f, auth=auth, verify=False)
    r.close()
    f.close()
    if r.status_code == 201:
        print(f"{Fore.GREEN}File - {filename} Uploaded Successfully")
        uploaded_files.append(filename)

print(f"{Fore.GREEN}Following files successfully transferred to Case.\n{uploaded_files}")
