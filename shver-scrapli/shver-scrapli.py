from scrapli import Scrapli

device = {
    "host": "10.197.199.11",
    "auth_username": "admin",
    "auth_password": "Cisco@123",
    "auth_strict_key": False,
    "platform": "cisco_iosxe",
    "port": 2201,
    "transport_options": {
        "open_cmd":
            ["-o", "KexAlgorithms=+diffie-hellman-group-exchange-sha1", "-o", "Ciphers=+aes256-cbc"]
    }
}
connection = Scrapli(**device)
connection.open()

output = connection.send_command("show version")

print(output.result)
