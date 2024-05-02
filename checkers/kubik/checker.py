#!/usr/bin/env python3
import concurrent.futures
import random
import sys
import time

from pathlib import Path

import requests
from checklib import *

from device import Device

BASE_DIR = Path(__file__).absolute().resolve().parent

def do_checks(ip):
    d = Device(ip)
    check_methods = [d.check_mqtt_to_ws_connectivity, d.check_ws_to_mqtt_connectivity, d.check_code_exec_capability]
    check = lambda: random.choice(check_methods)()
    return d.check_ws_to_mqtt_connectivity() and d.check_code_exec_capability() and all(
        [check() for _ in range(random.randint(2, 5))]) and d.check_mqtt_to_ws_connectivity()


def do_multicheck(ip):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(do_checks, ip) for _ in range(random.randint(2, 5))}

        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return all(results)



class Checker(BaseChecker):
    vulns: int = 2
    timeout: int = 5
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        #print(self.host)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests.exceptions.ConnectionError')

    def check(self):
        #assert_eq(do_checks(self.host), True, "Service functionality verification failed", Status.MUMBLE)
        assert_eq(do_multicheck(self.host), True, "Service functionality verification failed", Status.MUMBLE)
        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        d = Device(self.host)

        if vuln == "1":
            self.assert_eq(d.put_flag_1(flag), True, "unable to put flag 1", Status.MUMBLE)
        elif vuln == "2":
            self.assert_eq(d.put_flag_2(flag), True, "unable to put flag 2", Status.MUMBLE)

        self.cquit(Status.OK, private=f"{d.id}")

    def get(self, flag_id: str, flag: str, vuln: str):
        d = Device(self.host, override_id=flag_id)
        if vuln == "1":
            self.assert_eq(d.retrieve_flag_1(), flag, "wrong or missing flag 1", Status.CORRUPT)
        elif vuln == "2":
            self.assert_eq(d.retrieve_flag_2(), flag, "wrong or missing flag 2", Status.CORRUPT)

        self.cquit(Status.OK)


if __name__ == '__main__':
    IP = sys.argv[2]
    #print('check IP:', IP)
    c = Checker(sys.argv[2])
    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
