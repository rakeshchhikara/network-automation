import pandas

config_data = pandas.read_csv("snmp_config_file.csv", header=0)
hostnames = list(config_data.hostname)
ip_s = list(config_data.ip)
config_data = list(config_data.config_command)

print(hostnames)
print(ip_s)
print(config_data)