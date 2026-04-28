CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
);

CREATE TABLE Recipes (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    user_id INTEGER REFERENCES Users,
    items TEXT,
    description TEXT
);

CREATE TABLE Classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);
    
CREATE TABLE Recipe_classes (
    id INTEGER PRIMARY KEY,
    recipe_id REFERENCES Recipes,
    title TEXT,
    time INTEGER
);


    

