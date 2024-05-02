#!/usr/bin/env python3

import sys
import socket
import string
import secrets
from typing import Any, Tuple, List
from base64 import b64encode as b, b64decode as bb
import json
import checklib

import api


def random_username(length: int = None) -> str:
    if length is None:
        length = 10 + secrets.randbelow(20)

    alpha = string.ascii_letters + string.digits

    return ''.join(secrets.choice(alpha) for _ in range(length))



def random_secret(length: int = None) -> str:
    if length is None:
        length = 32 + secrets.randbelow(64)

    return secrets.token_urlsafe(length)[:length]


class Checker(checklib.BaseChecker):
    vulns: int = 1
    timeout: int = 20
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)

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

    def check(self): # TODO: need to test it on real infra
        username = random_username()
        description = random_secret()

        with api.connect(self.host) as client:
            proof, successful = client.register(
                username.encode(),
                description.encode(),
            )
            if not successful:
                self.throw_mumble('failed to register', '')
            proof_decoded = bb(proof)
            
            self.assert_eq(len(proof_decoded), 224, "Invalid proof format", checklib.Status.CORRUPT)

            # client.logout()
            # client.exit()

        with api.connect(self.host) as client:
            successful = client.login(
                username.encode(),
                proof,
            )
            if not successful:
                # if b'failed to login' in response:
                #     self.throw_mumble('user does not exist', response)

                self.throw_mumble('failed to login', '')

            # client
            # if not response.endswith(secret.encode()):
            #     self.throw_mumble('invalid secret', response)
            arr = []
            for i in range(1+secrets.randbelow(5)):
                plaintext1 = ' '.join(random_secret() for i in range(2+secrets.randbelow(10)))
                file_id,successful = client.upload_file(plaintext1,)

                if not successful:
                    self.throw_corrupt('invalid encryption', '')

                decrypted, successful = client.get_decrypted_file(file_id,)
                if (not successful) or plaintext1+' '*(16-(len(plaintext1)%16))!=decrypted:
                    self.throw_corrupt('invalid encryption', '')
                    
                arr.append((file_id, decrypted))
        
            lst = client.list_files()
            if lst !=arr:
                self.throw_corrupt('list_files doesnot work', '')

            client.logout()
            # client.exit()

        self.cquit(checklib.Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        username = random_username()
        description = "created_by_checker lol kekv P I V O "+username
        with api.connect(self.host) as client:
            proof,successful = client.register(
                username.encode(),
                description.encode(),
            )
            if not successful:
                # if b'user already exists' in response:
                # self.throw_mumble('user already exists', response)
                self.throw_mumble('failed to register','')

            successful = client.login(
                username.encode(),
                proof,
            )
            if not successful:
                # if b'user does not exist' in response:
                #     self.throw_corrupt('user does not exist', response)

                self.throw_mumble('failed to login', '')

            file_id,successful = client.upload_file(flag)
            if not successful:
                self.throw_mumble('failed to upload flag','')

            # client.exit()


        self.cquit(
            checklib.Status.OK,
            public=json.dumps({"username":username,"file_id": file_id}),
            private=self.store_flag_id(username, proof.decode(), file_id),
        )

    def get(self, flag_id: str, flag: str, vuln: str):
        username, proof,file_id = self.load_flag_id(flag_id)
        file_id = int(file_id)

        with api.connect(self.host) as client:
            successful = client.login(
                username.encode(),
                proof.encode(),
            )
            if not successful:
                # if b'user does not exist' in response:
                #     self.throw_corrupt('user does not exist', response)

                self.throw_mumble('failed to login', '')

            # if not response.endswith(flag.encode()):
            #     self.throw_corrupt('invalid secret', response)
            dec,successful = client.get_decrypted_file(file_id)
            if not successful:
                self.throw_mumble('failed to get file', '')
            
            self.assert_eq(dec.strip(), flag, "File content is invalid", checklib.Status.CORRUPT)
            
            client.logout()
            # client.exit()

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

    def store_flag_id(self, username: str, proof: str, file_id: int) -> str:
        return f'{username} {proof} {file_id}'
    
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
