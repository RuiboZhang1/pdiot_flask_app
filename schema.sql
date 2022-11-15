DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS history;

CREATE TABLE users (
    student_id TEXT NOT NULL PRIMARY KEY,
    password TEXT NOT NULL
);

CREATE TABLE history (
    student_id TEXT NOT NULL PRIMARY KEY,
    activity TEXT NOT NULL,
    start_time TEXT NOT NULL
);
