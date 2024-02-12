CREATE TABLE theater (
    name           TEXT,
    capacity       INT,
    PRIMARY KEY(name)
);

CREATE TABLE screening (
    screening_id    TEXT DEFAULT (lower(hex(randomblob(16)))),
    start_time      TIME,
    date            DATE,
    theater_name    TEXT,
    IMDB_key        TEXT,
    available_seats INT,
    PRIMARY KEY(screening_id),
    FOREIGN KEY(theater_name) REFERENCES theater(name),
    FOREIGN KEY(IMDB_key) REFERENCES movie(IMDB_key)
);

CREATE TABLE movie (
    IMDB_key       TEXT,
    title          TEXT,
    prod_year      INT,
    running_time   INT,
    PRIMARY KEY(IMDB_key)
);

CREATE TABLE ticket (
    ticket_id      TEXT DEFAULT (lower(hex(randomblob(16)))),
    username       TEXT,
    screening_id   TEXT,
    PRIMARY KEY(ticket_id),
    FOREIGN KEY(username) REFERENCES customer(username),
    FOREIGN KEY(screening_id) REFERENCES screening(screening_id)
);

CREATE TABLE customer (
    username       TEXT,
    full_name      TEXT,
    password       VARCHAR(255) NOT NULL,
    PRIMARY KEY(username)
);

INSERT INTO movie(IMDB_key, title, prod_year, running_time)
VALUES 
("tt0381707", "White Chicks", 2004, 109),
("tt0172495", "Gladiator", 2000, 155),
("tt01111161", "Nyckeln till frihet", 1994, 142),
("tt0109830", "Forrest Gump", 1994, 142),
("tt0377092", "Mean Girls", 2004, 97), 
("tt1160419", "Dune", 2021, 155);


INSERT INTO theater(name, capacity)
VALUES 
("Sergel", 350),
("Råsunda", 150),
("Heron City", 412),
("Scandinavia", 600),
("Kista Galleria", 400); 


INSERT INTO screening(start_time, screening_id, theater_name, IMDB_key)
VALUES 
('2024-02-20 18:00:00', lower(hex(randomblob(16))), "Råsunda", "tt0381707"),
('2024-02-10 17:30:00', lower(hex(randomblob(16))), "Heron City", "tt01111161"),
('2024-02-09 14:30:00', lower(hex(randomblob(16))), "Scandinavia", "tt0377092"),
('2024-02-17 20:00:00', lower(hex(randomblob(16))), "Sergel", "tt1160419");


INSERT INTO customer(username, full_name, password)
VALUES 
("LuddeFnutt", "Ludwig Cederberg",'VonNeumann12'),
("SaraLightSaber", "Sara Saber", 'HACKe13'),
("Gabbecito", "Gabriel Wåhlin",'VAlfalk42');
