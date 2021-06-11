# Author: Rakesh Kumar
# Usage: This script has Five options that user can choose.
# To run show tech commands in "Global mode" and upload file/s to TAC case Choose: 1
# To run show tech commands in "Admin mode" and upload file/s to TAC case Choose:  2
# To upload already generated or saved file/s to TAC case Choose:                  3
# To run Only SHOW commands , capture output to file and upload it to TAC case Choose: 4
# To upload existing file on Local machine/JumpHost to TAC case: 5
# version 1.0

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

    if ('^' in output) or ('syntax error' in output) or ('Incomplete command' in output):
        print(f'Entered command - "{user_cmd}" is Invalid or Incomplete. Please re-check correct command.\n{120 * "#"}')
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

    if ('^' in output) or ('syntax error' in output) or ('Incomplete command' in output):
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
    for filename in local_files:
        try:
            print(f'\nUploading file -"{filename}" to TAC case')
            auth = HTTPBasicAuth(sr_username, sr_token)
            file_size = os.stat(filename).st_size
            with open(filename, "rb") as f:
                with tqdm(total=file_size, unit="KB", unit_scale=True, unit_divisor=1024) as t:
                    wrapped_file = CallbackIOWrapper(t.update, f, "read")
                    requests.put(url + filename, auth=auth, data=wrapped_file)
        except Exception as err:
            print(f'Some error occurred while uploading file - "{filename}" to TAC case', err)


prompt_choices = '''

#################################################################################################
# Version 1.0                                                                                   #
# Purpose: This Script can help Engineers/Customers to automate gathering TAC requested DATA    #
  for IOS-XR devices. The could include various show tech in Global/Admin mode or simple        #
  Show commands outputs.                                                                        #
                                                                                                #
  User need to supply the information to script based on Task chosen and this Script will       #
  generate the data and upload to TAC case.                                                     #
                                                                                                #
  Note: This script is designed for IOS-XR devices but user can tweak it for any platform.      #
                                                                                                #
#################################################################################################

==================================================================================
Please select the Task number from below List and Enter as your choice on Prompt.
==================================================================================

To run show tech commands in "Global mode" and upload file/s to TAC case Choose: 1
To run show tech commands in "Admin mode" and upload file/s to TAC case Choose:  2
To upload already generated or saved file/s to TAC case Choose:                  3
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

failed_list = []

if get_choice == 1:
    print(f'\nEnter one show tech command per line. Once all show tech commands entered,\n'
          f'just Hit Enter key to execute script\n')
    user_prompt = 'Enter show tech command(Only Global mode): '
    t = initial_func(user_prompt)
    (connection, prompt, hostname, lines) = t

    for user_cmd in lines:
        filename = run_cmd()
        if filename is None:
            failed_list.append(user_cmd)
            continue
        remote_md5 = remote_md5_check()
        local_file_name = retrieve_file('22')
        md5_local = local_md5_check()
        if md5_local is None:
            failed_list.append(user_cmd)
        md5_compare()

    print(f'List of local files: {local_files}')

    upload_2_sr()
    print(f'\n{20*"#"}\nList of failed commands, if any: {failed_list}')

elif get_choice == 2:
    print(f'\nEnter one Admin mode show tech command per line. Once all show tech commands entered,\n'
          f'just Hit Enter key to execute script\n')
    user_prompt = 'Enter command (ONLY admin mode commands without admin keyword): '
    t = initial_func(user_prompt)
    (connection, prompt, hostname, lines) = t

    loc1 = prompt.find('/CPU')
    active_processor = prompt[5:loc1]

    for user_cmd in lines:
        filename = run_cmd_admin()
        if filename is None:
            failed_list.append(user_cmd)
            continue
        remote_md5 = remote_md5_check()
        local_file_name = retrieve_file('22', )
        md5_local = local_md5_check()
        if md5_local is None:
            failed_list.append(user_cmd)
        md5_compare()

    print(f'List of local files: {local_files}')

    upload_2_sr()
    print(f'\n{20*"#"}\nList of failed commands, if any: {failed_list}')

elif get_choice == 3:
    print(f'\nEnter filename with complete path on Device in each line. Once all files are entered,\n'
          f'just Hit Enter key to execute script\n')

    user_prompt = 'Enter filename with complete path: '
    t = initial_func(user_prompt)
    (connection, prompt, hostname, lines) = t

    for filename in lines:
        local_file_name = retrieve_file('22')
        if local_file_name is None:
            failed_list.append(filename)
            continue
        remote_md5 = remote_md5_check()
        md5_local = local_md5_check()
        if md5_local is None:
            failed_list.append(filename)
        md5_compare()

    print(f'List of local files: {local_files}')
    upload_2_sr()
    print(f'\n{20*"#"}\nList of failed files, if any: {failed_list}')

elif get_choice == 4:
    print(f'\nEnter Show command per line. Once all files are entered,\n'
          f'just Hit Enter key to execute script\n')

    user_prompt = 'Enter Show Command: '
    t = initial_func(user_prompt)
    (connection, prompt, hostname, lines) = t

    time_str = time.strftime("-%d%m%Y-%H%M%S-")
    log_filename = hostname + time_str + 'logs.txt'
    local_files.append(log_filename)

    with open(log_filename, 'w') as logs:
        for cmd in lines:
            print(f'Now running command - {cmd}')
            output = connection.send_command(cmd, max_loops=50000, delay_factor=5, strip_command=False,
                                             strip_prompt=False)
            logs.write(f'{prompt}{output}\n{100 * "#"}\n')
            if '^' in output:
                failed_list.append(cmd)

    print(f'File will be uploaded to case - {local_files}')
    upload_2_sr()
    print(f'\n{20*"#"}\nList of failed commands, if any: {failed_list}')

elif get_choice == 5:
    print(f'\nEnter Local filename in each line. Once all files are entered,\n'
          f'just Hit Enter key to execute script\n')

    user_prompt = input('Enter Local file name(same working directory): ')
    local_files.append(user_prompt)
    upload_2_sr()
else:
    print("Choose Option only from 1 to 5")

print('\n\n#######  Thanks for using this Script.  ########\n')
