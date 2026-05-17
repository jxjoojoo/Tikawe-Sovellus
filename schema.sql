CREATE TABLE Users (
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE,
	password_hash TEXT,
);

CREATE TABLE Recipes (
	id INTEGER PRIMARY KEY,
	name TEXT UNIQUE,
	user_id INTEGER REFERENCES Users,
	time INTEGER,
	description TEXT
);

CREATE TABLE Ingredients (
	id INTEGER PRIMARY KEY,
	recipe_id INTEGER REFERENCES Recipes,
	name TEXT,
	amount TEXT
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
	value INTEGER
);

CREATE TABLE Comments (
	id INTEGER PRIMARY KEY,
	recipe_id INTEGER REFERENCES Recipes,
	user_id INTEGER REFERENCES Users,
	comment_str TEXT
);

CREATE TABLE Images (
	id INTEGER PRIMARY KEY,
	recipe_id INTEGER REFERENCES Recipes,
	image BLOB
);
