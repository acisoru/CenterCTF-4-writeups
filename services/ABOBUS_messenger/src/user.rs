use curve25519_dalek::{RistrettoPoint, Scalar};
use rusqlite::{Connection, Result, Error as SqliteError, named_params};

#[derive(Debug)]
pub struct Person{
    pub id: u32,
    pub username: String,
    pub private_key: [u8;16],
    pub description: String,
    pub is_logined: bool
}
impl Person{
    
    pub fn new(conn: &mut Connection, username: &String, private_key: &[u8;16], description: &String) -> Result<()>{
        let tx = conn.transaction()?;
        tx.execute("INSERT INTO Users (username, private_key,description) VALUES (?, ?, ?)", 
            (username, private_key, description)
        )?;
        tx.commit()?;
        Ok(())
    }
    pub fn get_by_username(conn: &mut Connection, username: &String)-> Result<Person>{
        let person = conn.query_row("SELECT id, username, private_key,description FROM Users WHERE username = ?;",[username], |row| {
            Ok(Self {
                id: row.get(0)?,
                username: row.get(1)?,
                private_key: row.get(2)?,
                description: row.get(3)?,
                is_logined: false,
            })
        })?;
        Ok(person)
    }

}