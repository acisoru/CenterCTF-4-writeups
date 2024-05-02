CREATE TABLE Users (
            id          INTEGER PRIMARY KEY,
            username    TEXT NOT NULL UNIQUE,
            private_key  BLOB NOT NULL,
            description  TEXT NOT NULL
        );  
CREATE TABLE Files (
            file_id          INTEGER PRIMARY KEY,
            owner INTEGER NOT NULL,
            content BLOB NOT NULL
        );