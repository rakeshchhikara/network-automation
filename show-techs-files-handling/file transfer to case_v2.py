import requests
import urllib3
from requests.auth import HTTPBasicAuth
import logging

logging.basicConfig(level=logging.DEBUG)
urllib3.disable_warnings()

sr_username = input("Enter SR number: ")
sr_password = input("Enter Upload Token: ")

files_list = []
while True:
    line = input('Enter Filename: ')
    if line:
        files_list.append(line)
    else:
        break
text = '\n'.join(files_list)

url = 'https://cxd.cisco.com/home/'

print(f'Following files will be uploaded to SR {sr_username}: {files_list}')

for filename in files_list:
    auth = HTTPBasicAuth(sr_username, sr_password)

    print(f'Now uploading file {filename} to SR {sr_username}...')
    f = open(filename, 'rb')
    r = requests.put(url + filename, f, timeout=(5, 600), auth=auth, verify=False)
    r.close()
    f.close()
    if r.status_code == 201:
        print(f"File \"{filename}\" Uploaded Successfully\n")

print("All files uploaded successfully to Case !!!")
