-- SQLite Schema for MinerU to KiCAD Component Generator

CREATE TABLE IF NOT EXISTS datasheets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    title TEXT,
    revision TEXT,
    document_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datasheet_id INTEGER NOT NULL,
    part_number TEXT NOT NULL,
    description TEXT,
    manufacturer TEXT,
    FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    package_type TEXT,
    dimensions JSON, -- IPC-7351 dimensions
    model_params JSON, -- CadQuery params (renamed from 3d_model_params to avoid syntax issues)
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id INTEGER NOT NULL,
    number TEXT NOT NULL,
    name TEXT,
    electrical_type TEXT,
    description TEXT,
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS correction_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL, -- e.g., 'PIN_EXTRACTION', 'PACKAGE_ID'
    input_context TEXT NOT NULL, -- Prompt/Context sent to LLM
    llm_output JSON, -- Original LLM response
    user_corrected_output JSON, -- Final verified data
    model_version TEXT,
    confidence_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_datasheets_hash ON datasheets(file_hash);
CREATE INDEX IF NOT EXISTS idx_components_datasheet ON components(datasheet_id);
CREATE INDEX IF NOT EXISTS idx_packages_component ON packages(component_id);
CREATE INDEX IF NOT EXISTS idx_pins_package ON pins(package_id);
