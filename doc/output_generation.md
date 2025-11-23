# Output Generation Strategy

## 1. KiCAD Symbols (`.kicad_sym`)

### 1.1 Generation Logic
- **Library Structure**: One `.kicad_sym` file per Component (containing all its package variants).
- **Symbol Layout**:
    - **Shape**: Rectangular body.
    - **Pin Placement**:
        - **Left**: Inputs, Passive, NC.
        - **Right**: Outputs, Bidirectional, Open Collector.
        - **Top**: Positive Power (VDD, VCC).
        - **Bottom**: Negative Power/Ground (GND, VSS).
    - **Grouping**: Pins are grouped by logical function if metadata is available (e.g., "Port A", "Port B").

### 1.2 Implementation
- **Class**: `SymbolGenerator`
- **Method**: `generate_symbol(component_data, pin_table)`
- **Output**: Writes S-expression text directly.
- **Validation**: Checks for duplicate pin numbers and missing electrical types.

## 2. IPC-7351 Footprints (`.kicad_mod`)

### 2.1 Generation Logic
- **Standard**: IPC-7351B (and C where applicable).
- **Calculations**:
    - Uses standard formulas for Land Pattern calculation based on:
        - **Toe/Heel/Side Fillets** (defined by Density Level: Nominal, Least, Most).
        - **Component Tolerances** (extracted from datasheet).
        - **Fabrication Tolerances** (configurable defaults).
- **Naming Convention**: Generates IPC-compliant names (e.g., `QFN50P300X300X100-10N`).

### 2.2 Implementation
- **Class**: `FootprintGenerator`
- **Library**: Custom Python implementation of IPC formulas (lightweight) or adaptation of existing open-source IPC calculators.
- **Handling Duplicates**: If multiple components share the exact same package dimensions, they map to the same footprint file in the `.pretty` folder.

## 3. 3D Models (`.step`, `.wrl`)

### 3.1 Technology: CadQuery
- **Why**: Parametric, Python-based, robust STEP export (via OpenCASCADE).
- **Workflow**:
    1.  **Select Script**: Based on package type (e.g., `packages/qfn.py`).
    2.  **Inject Parameters**: Pass extracted dimensions (body size, lead length, pitch, etc.) to the script.
    3.  **Generate**: Run script to produce `model.step` and `model.wrl`.
    4.  **Coloring**: `model.wrl` is generated with material colors (Black body, Silver leads) for visual appeal in KiCAD.

### 3.2 Model Storage
- Models are saved to `${KICAD_USER_3DMOD}/<LibraryName>.3dshapes/`.
- Footprints automatically reference this path using `${KICAD_USER_3DMOD}` variable.

## 4. Automation & Batching
- The `GeneratorService` orchestrates the process:
    1.  Validates all data.
    2.  Calls `FootprintGenerator` -> `file.kicad_mod`.
    3.  Calls `ModelGenerator` -> `file.step` + `file.wrl`.
    4.  Calls `SymbolGenerator` -> `file.kicad_sym`.
    5.  Updates metadata in the files (Doc Title, Date, Revision).
