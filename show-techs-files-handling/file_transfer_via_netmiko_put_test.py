# This script is to transfer file from IOS_XR router to local machine via file_transfer function of Netmiko library.

from netmiko import ConnectHandler, file_transfer

cmd_output = '''
Sun May 23 09:56:18.956 UTC
++ Show tech start time: 2021-May-23.095620.UTC ++
Sun May 23 09:56:24 UTC 2021 Waiting for gathering to complete
..................................
Sun May 23 09:58:36 UTC 2021 Compressing show tech output
Show tech output available at 0/0/CPU0 : /net/node0_0_CPU0/harddisk:/showtech/showtech-generic-2021-May-23.095620.UTC.tgz
'''

location1 = cmd_output.find('harddisk')
file_name = cmd_output[location1:-1]
#location2 = location1 + 10
#dst_file = cmd_output[location2:-1]

print(file_name)
#print(dst_file)
#quit(1)


cisco = {'device_type': 'cisco_xr',
         'host': '123.100.1.101',
         'username': 'cisco',
         'password': 'cisco',
         }

source_file = file_name
dest_file = 'xyz.tgz'
direction = 'put'
file_system = '/'

# Create the Netmiko SSH connection
ssh_conn = ConnectHandler(**cisco)
transfer_dict = file_transfer(
    ssh_conn, file_system=file_system,
    source_file=source_file,
    dest_file=dest_file, direction=direction, overwrite_file=True)
print(transfer_dict)
pause = input("Hit enter to continue: ")
