CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    recipes_added INTEGER DEFAULT 0
);

CREATE TABLE Recipes (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    user_id INTEGER REFERENCES Users,
    items TEXT,
    description TEXT
);

