import requests
from requests.auth import HTTPBasicAuth

url = 'https://cxd.cisco.com/home/'
#username = 'SR Number'
#password = 'Upload Token'
username = input("Enter SR number: ")
password = input("Enter Upload Token: ")

auth = HTTPBasicAuth(username, password)
filename = 'OLGPXOLGCICU001-logs_21stMay.txt'

f = open(filename, 'rb')
r = requests.put(url + filename, f, auth=auth, verify=False)
r.close()
f.close()
if r.status_code == 201:
    print("File Uploaded Successfully")
