CREATE TABLE IF NOT EXISTS vehiculos (
  id_vehiculo SERIAL PRIMARY KEY,
  tipo_vehiculo VARCHAR(50),
  longitud FLOAT,
  latitud FLOAT,
  asignado BOOLEAN
);
