from netmiko import ConnectHandler
import paramiko
from paramiko.client import SSHClient
from scp import SCPClient
import hashlib


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

location1 = output.find('CPU') + 7
filename = output[location1:]

print(f'\nFile to be copied: {filename}\n Copying file from device to this machine\n')
check_md5 = connection.send_command_expect('show md5 file ' + filename, expect_string=r'available', max_loops=5000, delay_factor=5)

md5_loc1 = check_md5.find('UTC') + 3
remote_md5 = check_md5[md5_loc1:]
print(f'MD5 hash value of file on Router: {remote_md5}')


ssh = SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(device_ip, port=22, username='cisco', password='cisco')

with SCPClient(ssh.get_transport()) as scp:
    scp.get(filename)
    scp.close


md5_hash = hashlib.md5()
with open(filename, "rb") as f:
    # Read and update hash in chunks of 4K
    for byte_block in iter(lambda: f.read(4096), b""):
        md5_hash.update(byte_block)
    md5_local = (md5_hash.hexdigest())
    print(md5_local)

if remote_md5 == md5_local:
    print('MD5 has matched. Download successful')
else:
    print('MD5 has mismatch. Check again')

connection.disconnect()
print('Disconnected from device')
