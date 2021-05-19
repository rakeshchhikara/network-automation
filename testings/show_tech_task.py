# THIS SCRIPT WILL TAKE SHOW-TECH ON IOS-XR DEVICE AND THEN WILL COPY THE SHOW-TECH FILE TO LOCAL MACHINE.
# ALSO IT WILL CHECK AND VERIFY REMOTE AND LOCAL(COPIED) FILE MD5 HASH VALUES.

from netmiko import ConnectHandler
import paramiko
from paramiko.client import SSHClient
from scp import SCPClient
import hashlib


# Take user input for Device IP and run show tech command.
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
print(f'Generating show techs on device {hostname}. Please wait...\n')
output = connection.send_command_expect('show tech-support', expect_string=r'available', max_loops=5000, delay_factor=5)
print(output)

# Store show-tech file name and path on device in 'filename' variable.
location1 = output.find('/harddisk')
filename = output[location1:-1]

# Check md5 hash value of file on Router
check_md5 = connection.send_command_expect('show md5 file ' + filename, max_loops=5000, delay_factor=5)

md5_loc1 = check_md5.find('UTC') + 4
remote_md5 = check_md5[md5_loc1:]


# Copying file from Router to local machine. Using paramiko and scp client libraries
print(f'\nFile to be copied: {filename}\n\nCopying file from device to this machine\n')

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

ssh = createSSHClient(device_ip, port=22, user="cisco", password='cisco')
scp = SCPClient(ssh.get_transport())
scp.get(filename)

print(f'File {filename} copied successfully to local machine\n\nNow calculating md5 hash of local file.\n')

local_file_name = filename[20:]     # Grabbing only name of file. Stripped path.

# Calculating MD5 hash value of local file
md5_hash = hashlib.md5()
with open(local_file_name, "rb") as f:
    # Read and update hash in chunks of 4K
    for byte_block in iter(lambda: f.read(4096), b""):
        md5_hash.update(byte_block)
    md5_local = (md5_hash.hexdigest())


print(f'\nMD5 hash of remote file on {hostname}: {remote_md5}')
print(f'MD5 hash of local file on {hostname}: {md5_local}\n')

if remote_md5 == md5_local:
    print('MD5 has matched. Download successful')
else:
    print('MD5 has mismatch. Check again')

connection.disconnect()
print(f'Disconnected from device - {hostname}')
