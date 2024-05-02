#!/usr/bin/env python3
import requests

addr = "127.0.0.1"
port = 8000
url = "http://" + addr + ":" + str(port)
username = "hackername"
password = "hackerpass"
session = requests.session()
try:
    session.post(url+"/api/v1/register", json={"username":username, "password":password})
except Exception as err:
    print(err)
session.post(url+"/api/v1/login", json={"username":username, "password":password})
response = session.get(url+"/api/v1/thermostat/1/history")
print(response.json())
