-- CREATE DATABASE Interactive_web;
CREATE TABLE session_6 (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    message VARCHAR(255)
);

CREATE TABLE session_6_images (
    id SERIAL PRIMARY KEY,
    content bytea
);
