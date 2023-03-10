USE people;

CREATE TABLE persons
(
    id serial PRIMARY KEY,
    surname varchar(255) NOT NULL,
    biography text NOT NULL
);

CREATE TABLE reviews
(
    id serial PRIMARY KEY,
    review text NOT NULL,
    person_id int REFERENCES persons(id)
);

