import requests
import json

ip = '127.0.0.1'
port = 10080

payload = {'key1': 'value1', 'key2': {'key2_1': 'value2_1', 'key2_2': 'value2_2'}}

req_url = 'http://' + str(ip) + ':' + str(port) + '/'
headers = {'Content-type': 'application/json'}
req = requests.post(req_url, data=json.dumps(payload), headers=headers)
print req.text
