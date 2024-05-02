use libc::{memset, mmap, MAP_ANONYMOUS, MAP_PRIVATE, PROT_EXEC, PROT_READ, PROT_WRITE};
use std::mem;
use std::slice;

#[repr(C)]
struct JitMemory {
    memory: *mut u8,
    size: usize,
}

impl JitMemory {
    fn new(size: usize) -> Self {
        let memory = unsafe {
            let ptr = mmap(
                std::ptr::null_mut(),
                size,
                PROT_READ | PROT_WRITE | PROT_EXEC,
                MAP_ANONYMOUS | MAP_PRIVATE,
                -1,
                0,
            ) as *mut u8;

            // Initialize memory with 0x90
            memset(ptr as *mut libc::c_void, 0x90, size);

            ptr
        };

        JitMemory { memory, size }
    }

    fn as_slice(&self) -> &mut [u8] {
        unsafe { slice::from_raw_parts_mut(self.memory, self.size) }
    }
}

fn write_to_memory(memory: &mut [u8], pos: usize, value: &[u8]) {
    for i in 3..7 {
        memory[pos + i] = 0;
    }

    let len = value.len();
    let mut write_enable = false;
    for (i, byte) in value.iter().rev().enumerate() {
        if *byte == 0x00 && !write_enable {
            continue;
        } else {
            write_enable = true;
        }
        memory[pos + 3 + len - 1 - i] = *byte;
    }
}

fn parse_and_compile(program: &str, memory: &mut [u8]) {
    let mut pos = 0;

    for line in program.lines() {
        let words: Vec<&str> = line.split_whitespace().collect();
        match words.get(0) {
            Some(&"load_r1") => {
                let value = words[1].parse::<u64>().unwrap().to_le_bytes();

                memory[pos] = 0x48;
                memory[pos + 1] = 0xC7;
                memory[pos + 2] = 0xC0;

                write_to_memory(memory, pos, &value);
                pos += 7;
            }
            Some(&"load_r2") => {
                let value = words[1].parse::<u64>().unwrap().to_le_bytes();

                memory[pos] = 0x48;
                memory[pos + 1] = 0xC7;
                memory[pos + 2] = 0xC3;
                write_to_memory(memory, pos, &value);

                pos += 7;
            }
            Some(&"add") => {
                memory[pos] = 0x48;
                memory[pos + 1] = 0x01;
                memory[pos + 2] = 0xD8;
                pos += 3;
            }
            Some(&"sub") => {
                memory[pos] = 0x48;
                memory[pos + 1] = 0x29;
                memory[pos + 2] = 0xD8;
                pos += 3;
            }
            _ => {}
        }
    }
}

fn execute_program(program: &str) -> u64 {
    let jit_memory = JitMemory::new(1024);
    let memory = jit_memory.as_slice();
    memory[memory.len() - 1] = 0xC3; // ret

    parse_and_compile(&program, memory);

    #[cfg(feature = "debug_print_memory")]
    {
        for byte in memory.iter() {
            print!("{:02X}", byte);
        }
        println!();
    }

    let executable: extern "C" fn() -> u64 = unsafe { mem::transmute(jit_memory.memory) };
    executable()
}

#[no_mangle]
pub extern "C" fn execute_program_c(program: *const libc::c_char) -> u64 {
    let program = unsafe { std::ffi::CStr::from_ptr(program).to_str().unwrap() };
    execute_program(program)
}

/*fn main() {
    let program = "
    load_r1 12
    load_r2 12
    add
    ";

    let result = execute_program(&program);
    println!("Result: {}", result);
}*/
