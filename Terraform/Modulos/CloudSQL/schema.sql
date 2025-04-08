CREATE TABLE vehiculos (
    id_vehiculo SERIAL PRIMARY KEY,
    tipo_vehiculo VARCHAR(50) NOT NULL,
    longitud FLOAT NOT NULL,
    latitud FLOAT NOT NULL,
    asignado BOOLEAN DEFAULT FALSE
);
 
-- Insertar un vehículo de ejemplo
INSERT INTO vehiculos (tipo_vehiculo, longitud, latitud, asignado)
VALUES ('Ambulancia', -3.7038, 40.4168, TRUE);