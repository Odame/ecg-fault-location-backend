CREATE TABLE pole (
                pole_id INTEGER NOT NULL,
                pole_number VARCHAR NOT NULL,
                lat NUMERIC(9,6) NOT NULL,
                long NUMERIC(9,6) NOT NULL,
                CONSTRAINT pole_pk PRIMARY KEY (pole_id),
                CONSTRAINT pole_pole_number_unique UNIQUE (pole_number)
);

INSERT INTO pole (pole_number, lat, long) VALUES 
('POLE_0', 100.123456, 101.123456),
('POLE_1', 101.123456, 102.123456),
('POLE_2', 102.123456, 103.123456),
('POLE_3', 103.123456, 104.123456),
('POLE_4', 104.123456, 105.123456),
('POLE_5', 105.123456, 106.123456),
('POLE_6', 106.123456, 107.123456),
('POLE_7', 107.123456, 108.123456),
('POLE_8', 108.123456, 109.123456),
('POLE_9', 109.123456, 110.123456);