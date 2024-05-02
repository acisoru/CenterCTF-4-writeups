CREATE TABLE Users (
            id          INTEGER PRIMARY KEY,
            username    TEXT NOT NULL UNIQUE,
            password  TEXT NOT NULL,
            balance integerunsigned NOT NULL
        );
CREATE TABLE Items (
            item_id INTEGER PRIMARY KEY,
            owner INTEGER NOT NULL,
            price integerunsigned NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        );