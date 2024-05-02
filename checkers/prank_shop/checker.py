#!/usr/bin/env python3

import sys
import socket
import string
import secrets
from typing import Any, Tuple, List
from base64 import b64encode as b, b64decode as bb
import json
import checklib
import requests
import random

def random_username(length: int = None) -> str:
    if length is None:
        length = 10 + secrets.randbelow(20)

    alpha = string.ascii_letters + string.digits

    return ''.join(secrets.choice(alpha) for _ in range(length))



def random_secret(length: int = None) -> str:
    if length is None:
        # length = 32 + secrets.randbelow(64)
        length = 12 + secrets.randbelow(10)

    return secrets.token_urlsafe(length)[:length]


class Checker(checklib.BaseChecker):
    vulns: int = 1
    timeout: int = 20
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.url = 'http://'+self.host+':5643'
    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except self.get_check_finished_exception():
            raise
        except socket.timeout as ex:
            self.cquit(
                checklib.Status.DOWN,
                'timeout error',
                f'timeout error: {ex}',
            )
        except ConnectionError as ex:
            self.cquit(
                checklib.Status.DOWN,
                'connection error',
                f'connection error: {ex}',
            )
        except socket.error as ex:
            self.cquit(
                checklib.Status.MUMBLE,
                'socket error',
                f'socket error: {ex}',
            )

    def check(self):
        username = random_username()
        password = random_secret()

        response = requests.post(self.url+"/users/register",params={"username":username,"password":password})
        if response.status_code!=200:
            self.throw_mumble('failed to register', '')

        headers ={}
        response = requests.post(self.url+'/token',data={"username":username,"password":password})
        if response.status_code!=200:
            self.throw_mumble('failed to login', '')
        headers["Authorization"] = "Bearer "+response.json()['access_token']

        username2 = random_username()
        password2 = random_secret()
        response = requests.post(self.url+"/users/register",params={"username":username2,"password":password2})
        if response.status_code!=200:
            self.throw_mumble('failed to register', '')

        headers2 ={}
        response = requests.post(self.url+'/token',data={"username":username2,"password":password2})
        if response.status_code!=200:
            self.throw_mumble('failed to login', '')
        headers2["Authorization"] = "Bearer "+response.json()['access_token']

        response = requests.get(self.url+"/users/")
        if response.status_code!=200:
            self.throw_mumble('failed to get users', '')
        users = response.json()
        su = 0
        for i in users:
            su += i['username'] in (username,username2)
        if su !=2:
            self.throw_mumble('failed to get users', 'i cant see registred users')
        description=random_username()
        response = requests.post(self.url+'/users/me/items',json={"name":random_secret(),"price":random.randint(1,400),"description":description},headers=headers)
        if response.status_code!=200:
            self.throw_mumble('failed to create prank', '')
        item = response.json()
        item_id = item['item_id']

        response = requests.get(self.url+f"/items/{item_id}",headers=headers)
        if response.status_code!=200:
            self.throw_mumble('failed GET /items/item_id', '')
        self.assert_eq(response.json(), item, "result /items/item_id != created item", checklib.Status.MUMBLE)

        result = requests.patch(self.url+f"/users/{item['owner']}/items/{item_id}",headers=headers2,params={"price":int(item['price'])})
        if result.status_code!=200:
            self.throw_mumble('failed buy prank', result.content.decode())

        response = requests.get(self.url+'/users/me/items', headers=headers2)
        if response.status_code!=200:
            self.throw_mumble('failed list pranks', response.content.decode())
        for item in response.json():
            if item['description']==description:
                break
        else:
            self.throw_mumble('no such prank after buy in /users/me/items', '')

        self.cquit(checklib.Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        username = random_username()
        password = random_secret()

        response = requests.post(self.url+"/users/register",params={"username":username,"password":password})
        if response.status_code!=200:
            self.throw_mumble('failed to register', '')

        headers ={}
        response = requests.post(self.url+'/token',data={"username":username,"password":password})
        if response.status_code!=200:
            self.throw_mumble('failed to login', '')
        headers["Authorization"] = "Bearer "+response.json()['access_token']

        response= requests.post(self.url+'/users/me/items',json={"name":"FLAG","price":random.randint(500*10000,500*30000),"description":flag},headers=headers)
        if response.status_code!=200:
            self.throw_corrupt('failed to upload flag', '')
        item = response.json()
    
        self.cquit(
            checklib.Status.OK,
            public=json.dumps({"prank_id":item['item_id']}),
            private=self.store_flag_id(username, password, item['item_id']),
        )

    def get(self, flag_id: str, flag: str, vuln: str):
        username, password,item_id = self.load_flag_id(flag_id)
        item_id = int(item_id)

        headers ={}
        response = requests.post(self.url+'/token',data={"username":username,"password":password})
        if response.status_code!=200:
            self.throw_mumble('failed to login', '')
        headers["Authorization"] = "Bearer "+response.json()['access_token']
        
        response = requests.get(self.url+f'/items/{item_id}',headers=headers)
        if response.status_code!=200:
            self.throw_mumble('failed to get flag prank', '')
        item = response.json()

        self.assert_eq(item['description'], flag, "Flag prank content is invalid", checklib.Status.CORRUPT)

        self.cquit(checklib.Status.OK)

    def throw_mumble(self, message: str, reason: Any):
        self.cquit(
            checklib.Status.MUMBLE,
            message,
            f'{message}: {repr(reason)[:128]}',
        )

    def throw_corrupt(self, message: str, reason: Any):
        self.cquit(
            checklib.Status.CORRUPT,
            message,
            f'{message}: {repr(reason)[:128]}',
        )

    def store_flag_id(self, username: str, password:str, item_id: int) -> str:
        return f'{username} {password} {item_id}'
    
    def load_flag_id(self, flag_id: str) -> Tuple[str, str]:
        return flag_id.split()



if __name__ == "__main__":
    host = sys.argv[2]
    checker = Checker(host)

    try:
        action = sys.argv[1]
        arguments = sys.argv[3:]

        checker.action(action, *arguments)
    except checker.get_check_finished_exception():
        checklib.cquit(
            checklib.Status(checker.status),
            checker.public,
            checker.private,
        )
