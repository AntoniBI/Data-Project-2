CREATE TABLE recursos (
    recurso_id SERIAL PRIMARY KEY,
    servicio VARCHAR(255),
    asignado BOOLEAN DEFAULT FALSE
);


INSERT INTO recursos (servicio) VALUES
('Policía'),
('Policía'),
('Policía'),
('Policía'),
('Policía'),
('Policia'),
('Policia'),
('Policia'),
('Policia'),
('Policia'),
('Policia'),
('Ambulancia'),
('Ambulancia'),
('Ambulancia'),
('Ambulancia'),
('Ambulancia'),
('Ambulancia'),
('Ambulancia'),
('Ambulancia'),
('Ambulancia'),
('Ambulancia'),
('Bombero'),
('Bombero'),
('Bombero'),
('Bombero'),
('Bombero'),
('Bombero'),
('Bombero'),
('Bombero'),
('Bombero'),
('Bombero')