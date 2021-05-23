from __future__ import print_function, unicode_literals

from netmiko import ConnectHandler, file_transfer


cisco = {'device_type': 'cisco_xr',
         'host': '123.100.1.101',
         'username': 'cisco',
         'password': 'cisco',
         }

source_file = 'put.tgz'
dest_file = 'put.tgz'
direction = 'put'
file_system = 'harddisk:'

# Create the Netmiko SSH connection
ssh_conn = ConnectHandler(**cisco)
transfer_dict = file_transfer(
    ssh_conn,
    source_file=source_file,
    dest_file=dest_file, file_system=file_system, direction=direction, overwrite_file=True)
print(transfer_dict)
pause = input("Hit enter to continue: ")
