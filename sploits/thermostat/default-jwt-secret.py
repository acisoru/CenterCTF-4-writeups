#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta
import jwt

addr = "127.0.0.1"
port = 8000
url = "http://" + addr + ":" + str(port)
session = requests.session()
response = session.get(url+"/api/v1/profile")
user_id = response.json()[0]["ID"]
username = response.json()[0]["username"]
role = "user" #default
exp = int((datetime.now() + timedelta(minutes = 10)).timestamp())
encoded_jwt = jwt.encode({"id": user_id, "role": role, "sub":username, "exp":exp}, "super_secret", algorithm="HS256")
session.cookies.set("token",encoded_jwt)
response = session.get(url+"/api/v1/thermostat")
print(response.json())
