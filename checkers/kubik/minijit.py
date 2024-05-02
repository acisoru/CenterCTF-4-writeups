import ctypes
import random
import os
from pathlib import Path
BASE_DIR = Path(__file__).absolute().resolve().parent

lib = ctypes.cdll.LoadLibrary(os.path.join(BASE_DIR, "libminijit.so"))

lib.execute_program_c.argtypes = [ctypes.c_char_p]
lib.execute_program_c.restype = ctypes.c_uint64


def generate_program():
    program = f"load_r1 {random.randint(1, 1000)}\n"
    program += f"load_r2 {random.randint(1, 1000)}\n"
    for _ in range(random.randint(0, 95)):
        if random.randint(1, 2) == 1:
            program += f"load_r2 {random.randint(1, 100)}\n"
        operation = random.choice(["add", "sub"])
        program += f"{operation}\n"
    return program


def get_random_code():
    p = generate_program()
    result = lib.execute_program_c(p.encode('utf-8'))

    return p, str(result)
