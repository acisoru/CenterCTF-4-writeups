extern crate libc;
extern crate libloading;

use std::ffi::OsStr;

use libloading::{Library, Symbol};

pub fn execute_program(program: &str) -> u64 {
    let lib_path = OsStr::new("./libminijit.so");
    let lib = unsafe { Library::new(lib_path) }.unwrap();

    unsafe {
        let func: Symbol<unsafe extern fn(program: *const libc::c_char) -> u64> = lib.get(b"execute_program_c").unwrap();

        let program = std::ffi::CString::new(program).unwrap();
        func(program.as_ptr())
    }
}
