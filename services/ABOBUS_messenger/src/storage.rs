use rusqlite::{ Connection, Error as SqliteError, Result};

#[derive(Debug)]
pub struct File{
    pub file_id: u32,
    pub owner: u32,
    pub content: Vec<u8>
}

impl File {
    pub fn get_by_id(conn: &mut Connection, file_id: u32) -> Result<Self>{
        let file = conn.query_row("SELECT owner, content FROM Files WHERE file_id = ?;",[file_id], |row| {
            Ok(Self {
                file_id: file_id,
                owner: row.get(0)?,
                content: row.get(1)?,
            })
        })?;
        Ok(file)
    }

    pub fn list(conn: &mut Connection, owner: u32) -> Result<Vec<Self>,SqliteError>
    {
        let mut stmt = conn.prepare("SELECT file_id,content FROM Files WHERE owner= ?;")?;
        let encrypted_files_iter = stmt.query_map([owner], |row| {
            Ok(Self {
                owner: owner,
                file_id: row.get(0)?,
                content: row.get(1)?,
            })
        })?;
        Ok(encrypted_files_iter.into_iter().filter_map(|s| s.ok()).collect())
    }

    pub fn create(conn: &mut Connection,owner: u32, content: &Vec<u8> ) -> Result<u32, SqliteError>{
        let tx = conn.transaction()?;
        let file_id = tx.query_row("INSERT INTO Files (owner, content) VALUES (?, ?) RETURNING file_id;",(owner, content), |row| {
            Ok(row.get(0)?)
        })?;
        tx.commit()?;
        Ok(file_id)
    }
}