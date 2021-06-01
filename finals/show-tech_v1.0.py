# Author: Rakesh Kumar (rakeshk6@cisco.com)
# Usage: THIS SCRIPT WILL RUN SHOW-TECHS ON IOS-XR DEVICE AND THEN WILL COPY THE SHOW-TECH FILE TO LOCAL MACHINE.
# ALSO IT WILL CHECK AND VERIFY REMOTE AND LOCAL(COPIED) FILE MD5 HASH VALUES.
# FINALLY IT WILL UPLOAD THE DOWNLOADED FILES TO TAC CASE.
# version 1

from netmiko import ConnectHandler
import paramiko
from scp import SCPClient
import hashlib
import getpass
import urllib3
import requests
from requests.auth import HTTPBasicAuth

# Get user input for TAC case details to upload files.
url = 'https://cxd.cisco.com/home/'
urllib3.disable_warnings()
sr_username = input("Enter SR number: ")
sr_token = input("Enter Upload Token: ")

# Take user input for Device IP and Credentials.
device_ip = input('Enter device ip: ')
username = input('Enter your username for device Login: ')
password = getpass.getpass(prompt='Enter device Password: ')

# Get input from user for show tech commands to be run on device.
# Note, just Hit Enter if there is no more command for input.
lines = []
while True:
    line = input('Enter command: ')
    if line:
        lines.append(line)
    else:
        break
text = '\n'.join(lines)

local_files = []  # List to store file names.

print(f'\nShow tech of these commands with be taken: {lines}\n')

# Device details dict for connecting to device.
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
    print(f'\nGenerating "{user_cmd}" on device {hostname}. Please wait...\n')
    output = connection.send_command(user_cmd, max_loops=50000, delay_factor=5)
    print(output)

    if "Invalid input" in output:
        print(f'Entered command - "{user_cmd}" is Invalid. Please re-check correct command.\n{120 * "#"}')
    else:
        # Store show-tech file name and path on device in 'filename' variable.
        file_start_loc = output.find('/harddisk')
        file_end_loc = output.find('.tgz') + 4
        filename = output[file_start_loc:file_end_loc]

        # Check md5 hash value of file on Router
        check_md5 = connection.send_command_expect('show md5 file ' + filename, max_loops=5000, delay_factor=5)

        remote_md5 = check_md5[28:]

        # Copying file from Router to local machine. Using paramiko and scp client libraries
        print(f'\nFile to be copied: {filename}\n\nCopying file from device to this machine\n')


        # Using Paramiko library to create underlying channel for SCP.
        def create_ssh_client(server, port, user, pass1):
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server, port, user, pass1)
            return client


        try:
            ssh = create_ssh_client(device_ip, port=22, user=username, pass1=password)
            scp = SCPClient(ssh.get_transport())
            scp.get(filename)
        except Exception as e:
            print(f'Some Exception occurred. Exception detail:', e)
        else:
            print(f'File "{filename}" copied to local machine\n\nNow calculating md5 hash of local file.\n')

            local_file_name = filename[20:]  # Grabbing only name of file. Stripped path.

            # Calculating MD5 hash value of local file
            md5_hash = hashlib.md5()
            with open(local_file_name, "rb") as f:
                # Read and update hash in chunks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
                md5_local = (md5_hash.hexdigest())

            print(f'\nMD5 hash of remote file on {hostname}: {remote_md5}')
            print(f'MD5 hash of local file: {md5_local}\n')

            if remote_md5 == md5_local:
                print(f'MD5 has matched. Download successful.\n{120 * "#"}')
                local_files.append(local_file_name)
            else:
                print(f'MD5 has mismatch. Check again.\n{120 * "#"}')

connection.disconnect()
print(f'Disconnected from device - {hostname}')

print(f'\nShow tech of all commands completed and downloaded to local machine\n')

print(f'Now following files will be transferred to Case: "{local_files}"')

for file in local_files:

    auth = HTTPBasicAuth(sr_username, sr_token)
    filename = file

    f = open(filename, 'rb')
    print(f'\nUploading file - "{filename}" to TAC Case\n')
    r = requests.put(url + filename, f, auth=auth, verify=False)
    r.close()
    f.close()
    if r.status_code == 201:
        print(f'File - "{filename}" Uploaded Successfully to case.')
    else:
        print(f'File - "{filename}" upload to case Failed.')

print("\n Script executed. Please look for errors in logs, if any.\nThanks for using !!!")
