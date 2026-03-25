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
    description TEXT
);
    
CREATE TABLE Ingredients (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFERENCES Recipes,
    items TEXT
); 

