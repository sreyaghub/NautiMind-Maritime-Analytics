CREATE TABLE vessels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vessel_name TEXT,
    imo_number TEXT,
    vessel_type TEXT,
    benchmark_speed REAL,
    benchmark_consumption REAL
);

CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vessel_id INTEGER,
    report_date TEXT,
    latitude REAL,
    longitude REAL,
    actual_speed REAL,
    actual_consumption REAL,
    wind_speed REAL,
    wave_height REAL,
    current_speed REAL
);