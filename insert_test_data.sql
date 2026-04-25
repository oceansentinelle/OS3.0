-- Script d'insertion de données de test Ocean Sentinel
-- Stations: BARAG_PROXY et ARCACHON_EYRAC
-- Paramètres: TEMP, PSAL, DOX2, PH_TOTAL

-- Insertion données BARAG_PROXY (COAST-HF - MESURÉ)
INSERT INTO validated_measurements (
    station_id, timestamp_utc, variable, value, unit, 
    quality_score, validation_status, data_source, data_status
) VALUES
-- Température (normale)
('BARAG_PROXY', NOW() - INTERVAL '10 minutes', 'TEMP', 18.5, '°C', 
 0.95, 'valid', 'COAST-HF Ifremer', 'measured'),

-- Salinité (normale)
('BARAG_PROXY', NOW() - INTERVAL '10 minutes', 'PSAL', 32.8, 'PSU', 
 0.92, 'valid', 'COAST-HF Ifremer', 'measured'),

-- Oxygène dissous (CRITIQUE - HYPOXIE)
('BARAG_PROXY', NOW() - INTERVAL '10 minutes', 'DOX2', 135.0, 'µmol/kg', 
 0.88, 'valid', 'COAST-HF Ifremer', 'measured'),

-- pH (CRITIQUE - ACIDIFICATION - INFÉRÉ)
('BARAG_PROXY', NOW() - INTERVAL '28 minutes', 'PH_TOTAL', 7.65, '', 
 0.75, 'valid', 'Sentinel-3 OLCI', 'inferred');

-- Insertion données ARCACHON_EYRAC (Hub'Eau - MESURÉ)
INSERT INTO validated_measurements (
    station_id, timestamp_utc, variable, value, unit, 
    quality_score, validation_status, data_source, data_status
) VALUES
-- Température (normale)
('ARCACHON_EYRAC', NOW() - INTERVAL '1 hour', 'TEMP', 19.2, '°C', 
 0.90, 'valid', 'Hub''Eau BRGM', 'measured'),

-- Salinité (WARNING - proche seuil)
('ARCACHON_EYRAC', NOW() - INTERVAL '1 hour', 'PSAL', 16.5, 'PSU', 
 0.85, 'valid', 'Hub''Eau BRGM', 'measured'),

-- Oxygène dissous (normale - SIMULÉ)
('ARCACHON_EYRAC', NOW() - INTERVAL '2 hours', 'DOX2', 185.0, 'µmol/kg', 
 0.65, 'valid', 'MARS3D Ifremer', 'simulated'),

-- pH (normale)
('ARCACHON_EYRAC', NOW() - INTERVAL '1 hour', 'PH_TOTAL', 7.92, '', 
 0.88, 'valid', 'Hub''Eau BRGM', 'measured');

-- Vérification
SELECT 
    station_id,
    variable,
    value,
    unit,
    data_status,
    data_source,
    timestamp_utc
FROM validated_measurements
ORDER BY station_id, variable;
