#!/usr/bin/env python3

import contextlib
from typing import Iterator

# https://github.com/oalieno/mini-pwntools
import minipwn as pwn
import ast
import re

class API:
    def __init__(self, io: pwn.remote):
        self.io = io

    def register(self, username: bytes, description: bytes) ->tuple[bytes, bool]:
        self.io.sendlineafter(b'- logout\n', b'register')

        self.io.sendlineafter(b': ', username)
        self.io.sendlineafter(b': ', description)
        proof = self.io.recvline()
        if b'already exists ;(' in proof:
            return (b'', False)
        else:
            return (proof[len('here is your proof: '):-1], True)


    def login(self, username: bytes, proof: bytes) -> bool:
        self.io.sendlineafter(b'- logout\n', b'login')

        self.io.sendlineafter(b': ', username)
        self.io.sendlineafter(b': ', proof)

        return b'successful login!' in self.io.recvline()
    
    def profile_description(self) -> tuple[bytes, bool]:
        self.io.sendlineafter(b'- logout\n', b'profile_description')
        is_logined = b'Login first :(' not in self.io.recvline()
        return (self.io.recvline().strip(),is_logined)
    
    def logout(self):
        self.io.sendlineafter(b'- logout\n', b'logout')

    def upload_file(self, plaintext: str) -> tuple[int,bool]:
        self.io.sendlineafter(b'- logout\n', b'upload_file')

        self.io.sendlineafter(b': ', plaintext.encode())
        is_logined = b'Login first :(' not in self.io.recvline()
        if not is_logined:
            return (-1, False)

        file_id = self.io.recvline()[len('Your file_id: '):-1]
        return (int(file_id.decode()), True)

    def get_encrypted_file(self, file_id: int) -> tuple[bytes,bool]:
        self.io.sendlineafter(b'- logout\n', b'get_encrypted_file')

        self.io.sendlineafter(b': ', str(file_id).encode())

        line = self.io.recvline()
        if (b'INPUT NUMBER' in line ) or (b'Some sql error' in line):
            return (b'', False)

        enc = line[len('Encrypted file content: '):-1].decode()
        enc = bytes(ast.literal_eval(enc))

        return (enc, True)

    def get_decrypted_file(self, file_id: int) -> tuple[str,bool]:
        self.io.sendlineafter(b'- logout\n', b'get_decrypted_file')

        self.io.sendlineafter(b': ', str(file_id).encode())

        line = self.io.recvline()
        if (b'Decrypted file content' not in line):
            return (b'', False)

        enc = line[len('Decrypted file content: '):-1].decode()
        enc = ast.literal_eval(enc)

        return (enc, True)

    def list_files(self) -> list:
        self.io.sendlineafter(b'- logout\n', b'list_files')

        line = self.io.recvline()
        if b'Login first :(' in line:
            return []

        txt = self.io.recvuntil(b'\nChoose option:\n- register')[:-len(b'\nChoose option:\n- register')].decode().strip('\n').split('\n')
        # print(txt)
        res = []
        for i in range(0,len(txt),2):
            file_id =int(txt[i][len('file_id: '):])
            content = (txt[i+1][len('file_content: '):])
            res.append((file_id, content))

        return res
    


@contextlib.contextmanager
def connect(hostname: str, port: int = 18484) -> Iterator[API]:
    io = pwn.remote(hostname, port)
    api = API(io)

    try:
        yield api
    finally:
        io.s.close()
