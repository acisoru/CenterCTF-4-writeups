import requests
from checklib import *

PORT = 8000

class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}'

    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.port = PORT

    def register(self, session: requests.Session, username: str, password: str):
        session.post(self.url + "/api/v1/register", json={"username":username, "password":password})

    def login(self, session: requests.Session, username: str, password: str, status: Status):
        session.post(self.url + "/api/v1/login", json={"username":username, "password":password})

    def check_profile(self, session: requests.Session):
        response = session.get(self.url + "/api/v1/profile/me")
        data = self.c.get_json(response, "Invalid response on personal profile endpoint")

    def check_profiles(self, session: requests.Session):
        response = session.get(self.url + "/api/v1/profile")
        data = self.c.get_json(response, "Invalid response on profiles list endpoint")

    def check_my_thermostats(self, session: requests.Session):
        response = session.get(self.url + "/api/v1/thermostat")
        data = self.c.get_json(response, "Invalid response on thermostat lists endpoint")

    def create_thermostat(self, session: requests.Session, flag: str):
        url = f'{self.url}/api/v1/thermostat'
        response = session.post(url, json={
            "commentary": flag,
        })
        data = self.c.get_json(response, "Invalid response on create_thermostat")
        self.c.assert_eq(type(data), dict, "Invalid response on create_thermostat")
        self.c.assert_in("ID", data, "Invalid response on create_thermostat")
        self.c.assert_eq(type(data["ID"]), int, "Invalid response on create_thermostat")
        self.c.assert_in("temperature", data, "Invalid response on create_thermostat")
        self.c.assert_eq(type(data["temperature"]), float, "Invalid response on create_thermostat")
        self.c.assert_in("commentary", data, "Invalid response on create_thermostat")
        self.c.assert_eq(type(data["commentary"]), str, "Invalid response on create_thermostat")
        return data["ID"]

    def update_thermostat(self, session: requests.Session, thermostat_id: int, flag: str):
        url = f'{self.url}/api/v1/thermostat/{thermostat_id}'
        response = session.put(url, json={
            "temperature": 13.37,
            "commentary": flag,
        })
        data = self.c.get_json(response, "Invalid response on update thermostat endpoint")

    def get_thermostat(self, session: requests.Session, thermostat_id: int, status: Status) -> str:
        url = f'{self.url}/api/v1/thermostat/{thermostat_id}'
        response = session.get(url)
        data = self.c.get_json(response, "Invalid response on get_thermostat")
        self.c.assert_eq(type(data), dict, "Invalid response on get_thermostat")
        self.c.assert_in("ID", data, "Invalid response on get_thermostat")
        self.c.assert_eq(type(data["ID"]), int, "Invalid response on get_thermostat")
        self.c.assert_in("temperature", data, "Invalid response on get_thermostat")
        self.c.assert_eq(type(data["temperature"]), float, "Invalid response on get_thermostat")
        self.c.assert_in("commentary", data, "Invalid response on get_thermostat")
        self.c.assert_eq(type(data["commentary"]), str, "Invalid response on get_thermostat")
        return data["commentary"]
