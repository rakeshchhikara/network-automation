# Author: Rakesh Kumar
# Usage: THIS SCRIPT WILL RUN SHOW-TECHS ON IOS-XR DEVICE AND THEN WILL COPY THE SHOW-TECH FILE TO LOCAL MACHINE.
# ALSO IT WILL CHECK AND VERIFY REMOTE AND LOCAL(COPIED) FILE MD5 HASH VALUES.
# FINALLY IT WILL UPLOAD THE DOWNLOADED FILES TO TAC CASE.
# version 2

import time
import os
from netmiko import ConnectHandler
import paramiko
from scp import SCPClient
import hashlib
import getpass
import urllib3
import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper


def initial_func(user_prompt):
    lines = []
    while True:
        line = input(user_prompt)

        if line:
            lines.append(line)
        else:
            break

    print(f'\nNow connecting to device...')
    connection = ConnectHandler(**device)
    prompt = connection.find_prompt()
    prompt_strip = prompt.find(':') + 1
    hostname = prompt[prompt_strip:-1]
    return connection, prompt, hostname, lines


def run_cmd():
    print(f'\nGenerating "{user_cmd}" on device {hostname}. Please wait...\n')
    output = connection.send_command(user_cmd, max_loops=50000, delay_factor=5)

    if ('%' in output) or ('syntax error' in output):
        print(f'Entered command - "{user_cmd}" is Invalid. Please re-check correct command.\n{120 * "#"}')
    else:
        print(output)
        # Store show-tech file name and path on device in 'filename' variable.
        file_start_loc = output.find('/harddisk')
        file_end_loc = output.find('.tgz') + 4
        filename = output[file_start_loc:file_end_loc]
        return filename


def retrieve_file(port):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(device_ip, port, username, password)
    try:
        scp = SCPClient(client.get_transport())
        scp.get(filename)
    except Exception as e:
        print(f'Some Exception occurred while retrieving file to local machine. Exception detail:', e)
    else:
        print(f'\nFile "{filename}" copied to local machine\n')
        local_file_name = filename[20:]  # Grabbing only name of file. Stripped path.
        return local_file_name


def remote_md5_check():
    try:
        print(f'Calculating md5 hash of file "{filename}" on device... please wait.')
        check_md5 = connection.send_command_expect('show md5 file ' + filename, max_loops=5000, delay_factor=5)

        remote_md5 = check_md5[28:]
    except Exception as err:
        print(f'Some exception occurred while performing remote md5 check', err)
    else:
        return remote_md5


def local_md5_check():
    try:
        print(f'Calculating md5 hash of Local file "{filename}" ... please wait.')
        local_file_name = filename[20:]  # Grabbing only name of file. Stripped path.

        # Calculating MD5 hash value of local file
        md5_hash = hashlib.md5()
        with open(local_file_name, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
            md5_local = (md5_hash.hexdigest())
    except Exception as err:
        print(f'Some exception occurred while performing md5 check on local file', err)
    else:
        return md5_local


def md5_compare():
    print(f'\nMD5 calculated on Device - {remote_md5}')
    print(f'Local md5 calculated: {md5_local}')
    if remote_md5 == md5_local:
        print(f'MD5 has matched. Download successful.\n{120 * "#"}')
        local_files.append(local_file_name)
    else:
        print(f'MD5 has mismatch. Check again.\n{120 * "#"}')


def run_cmd_admin():
    print(f'Entering in Admin mode to generate Admin specific show tech of command - "{user_cmd}"')

    output = connection.send_command('admin', expect_string=r'sysadmin')
    print(output)
    print(f'\nGenerating "{user_cmd}" on device {hostname}. Please wait...\n')
    output = connection.send_command(user_cmd, expect_string=r'sysadmin', max_loops=50000, delay_factor=5)

    if ('%' in output) or ('syntax error' in output):
        print(
            f'Entered command - "{user_cmd}" is Incomplete or Invalid. Please re-check correct command.\n{120 * "#"}')
    else:
        print(output)
        file_start_loc = output.find('/')
        file_end_loc = output.find('.tgz') + 4
        filename = output[file_start_loc:file_end_loc]
        print('\nCopying file to Global mode')
        copy_cmd = f'copy {filename} harddisk:/showtech location 0/{active_processor}/CPU0/VM1'
        copy2global = connection.send_command(copy_cmd, expect_string=r'sysadmin')
        print(f'{copy_cmd}/n{copy2global}')
        connection.send_command('exit', expect_string=r'CPU')
        file_loc = filename.find('showtech-')
        filename = filename[file_loc:]
        filename = '/harddisk:/showtech/' + filename
        return filename


def upload_2_sr():
    try:
        for filename in local_files:
            auth = HTTPBasicAuth(sr_username, sr_token)
            file_size = os.stat(filename).st_size
            with open(filename, "rb") as f:
                with tqdm(total=file_size, unit="KB", unit_scale=True, unit_divisor=1024) as t:
                    wrapped_file = CallbackIOWrapper(t.update, f, "read")
                    requests.put(url + filename, auth=auth, data=wrapped_file)
    except Exception as err:
        print(f'Some error occurred while uploading file to TAC case', err)


prompt_choices = '''
To run show tech commands in "Global mode" and upload file to TAC case Choose: 1
To run show tech commands in "Admin mode" and upload files to TAC case Choose: 2
To upload already generated or saved file to TAC case Choose: 3
To run Only SHOW commands , capture output to file and upload it to TAC case Choose: 4
To upload existing file on Local machine/JumpHost to TAC case: 5
'''

print(prompt_choices)

get_choice = int(input('Enter your Choice: '))

# Get user input for TAC case details to upload files.
url = 'https://cxd.cisco.com/home/'
urllib3.disable_warnings()
sr_username = input("Enter SR number: ")
sr_token = input("Enter Upload Token: ")

device_ip = username = password = str()

if get_choice < 5:
    # Take user input for Device IP and Credentials.
    device_ip = input('Enter device ip: ')
    username = input('Enter your username for device Login: ')
    password = getpass.getpass(prompt='Enter device Password: ')

local_files = []  # List to store file names.

# Device details dict for connecting to device.
device = {
    'device_type': 'cisco_xr',
    'host': device_ip,
    'username': username,
    'password': password,
    'port': 22,  # optional, default 22
    'verbose': True  # optional, default False
}

if get_choice == 1:
    print("\nuser selected option: 1\n")

    user_prompt = 'Enter show tech command: '
    t = initial_func(user_prompt)
    (connection, prompt, hostname, lines) = t

    for user_cmd in lines:
        filename = run_cmd()
        if filename is None:
            continue
        remote_md5 = remote_md5_check()
        local_file_name = retrieve_file('22')
        md5_local = local_md5_check()
        md5_compare()

    print(f'List of local files: {local_files}')

    upload_2_sr()

elif get_choice == 2:
    print("\nuser selected option: 2\n")

    user_prompt = 'Enter command (only admin mode commands without admin keyword): '
    t = initial_func(user_prompt)
    (connection, prompt, hostname, lines) = t

    loc1 = prompt.find('/CPU')
    active_processor = prompt[5:loc1]

    for user_cmd in lines:
        filename = run_cmd_admin()
        if filename is None:
            continue
        remote_md5 = remote_md5_check()
        local_file_name = retrieve_file('22', )
        md5_local = local_md5_check()
        md5_compare()

    print(f'List of local files: {local_files}')

    upload_2_sr()

elif get_choice == 3:
    print("\nUser selected option: 3\n")

    user_prompt = 'Enter filename with complete path: '
    t = initial_func(user_prompt)
    (connection, prompt, hostname, lines) = t

    for filename in lines:
        local_file_name = retrieve_file('22')
        if local_file_name is None:
            continue
        remote_md5 = remote_md5_check()
        md5_local = local_md5_check()
        md5_compare()

    print(f'List of local files: {local_files}')
    upload_2_sr()

elif get_choice == 4:
    print('User Selected option: 4')

    user_prompt = 'Enter Show Command: '
    t = initial_func(user_prompt)
    (connection, prompt, hostname, lines) = t

    time_str = time.strftime("-%d%m%Y-%H%M%S-")
    log_filename = hostname + time_str + 'logs.txt'
    local_files.append(log_filename)

    failed_cmd_list = []

    with open(log_filename, 'w') as logs:
        for cmd in lines:
            print(f'Now running command - {cmd}')
            output = connection.send_command(cmd, max_loops=50000, delay_factor=5, strip_command=False,
                                             strip_prompt=False)
            logs.write(f'{prompt}{output}\n{100 * "#"}\n')
            if '%' in output:
                failed_cmd_list.append(cmd)

    print(f'File will be uploaded to case - {local_files}')
    upload_2_sr()
    print(f'\nFollowing commands are Invalid or Incomplete. Manual check required.\n{failed_cmd_list}')

elif get_choice == 5:
    print('User Selected option: 5')

    user_prompt = input('Enter Local file name(same working directory): ')
    local_files.append(user_prompt)

    upload_2_sr()

else:
    print("Choose Option only from 1 to 5")

print('\n#######  Thanks for using this Script.  ########\n')
