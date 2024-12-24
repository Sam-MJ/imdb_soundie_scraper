import sqlite3

sqlite_statements = [
    "CREATE TABLE movies (movie_id INTEGER PRIMARY KEY, name TEXT NOT NULL, date TEXT NOT NULL, url TEXT NOT NULL);",
    "CREATE TABLE soundies (soundie_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)",
    "CREATE TABLE roles (role_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)",
    """CREATE TABLE soundie_role
    (soundie_id INTEGER REFERENCES soundies(soundie_id),
    role_id INTEGER REFERENCES roles(role_id))""",
    """CREATE TABLE soundie_movie
    (soundie_id INTEGER REFERENCES soundies(soundie_id), movie_id INTEGER REFERENCES movies(movie_id),
    UNIQUE(soundie_id, movie_id))""",
]

conn = sqlite3.connect("imdb/database/imdb.db")

for statement in sqlite_statements:
    conn.execute(statement)

conn.commit()
conn.close()

# duplicate soundies in movie if they end up with multiple roles
# one soundie per movie
# multiple roles per soundie
# multiple movies per soundie
