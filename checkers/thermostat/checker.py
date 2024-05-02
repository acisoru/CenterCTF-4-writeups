#!/usr/bin/env python3

import sys
import requests

from checklib import *
from example_lib import *
import random, string, json, base64


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 5
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

    def check(self):
        session = get_initialized_session()
        username, password = rnd_username(), rnd_password()
        flag = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        self.mch.register(session, username, password)
        self.mch.login(session, username, password, Status.MUMBLE)
        thermostat_id = self.mch.create_thermostat(session, flag)
        self.mch.update_thermostat(session, thermostat_id, flag)
        self.mch.check_profile(session)
        self.mch.check_profiles(session)
        self.mch.check_my_thermostats(session)
        value = self.mch.get_thermostat(session, thermostat_id, Status.CORRUPT)
        self.assert_eq(value, flag, "Flag value is invalid", Status.CORRUPT)
        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        username, password = rnd_username(), rnd_password()
        self.mch.register(session, username, password)
        self.mch.login(session, username, password, Status.MUMBLE)
        thermostat_id = self.mch.create_thermostat(session, flag)
        self.mch.update_thermostat(session, thermostat_id, flag)
        self.cquit(Status.OK, f"{thermostat_id}", f"{username}:{password}:{thermostat_id}")

    def get(self, flag_id: str, flag: str, vuln: str):
        data = {}
        data["username"], data["password"], data["thermostat_id"] = flag_id.split(':')
        s = get_initialized_session()
        self.mch.login(s, data["username"], data["password"], Status.CORRUPT)
        value = self.mch.get_thermostat(s, data["thermostat_id"], Status.CORRUPT)
        self.assert_eq(value, flag, "Flag value is invalid", Status.CORRUPT)
        self.cquit(Status.OK)

if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
