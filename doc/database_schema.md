# Database Schema Design

## Overview
The database will be implemented using **SQLite** for local deployment, with a design that allows easy migration to PostgreSQL if a centralized server is needed later. The schema focuses on two main areas:
1.  **Component Data**: Storing the extracted and verified electronic component information.
2.  **Training Data**: Storing user corrections to fine-tune the LLM.

## Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    DATASHEET ||--|{ COMPONENT : defines
    COMPONENT ||--|{ PACKAGE : has
    PACKAGE ||--|{ PIN : contains
    
    DATASHEET {
        int id PK
        string filename
        string file_hash
        string title
        string revision
        date document_date
        datetime created_at
    }

    COMPONENT {
        int id PK
        int datasheet_id FK
        string part_number
        string description
        string manufacturer
    }

    PACKAGE {
        int id PK
        int component_id FK
        string name
        string package_type
        json dimensions "IPC-7351 dimensions"
        json 3d_model_params "CadQuery params"
    }

    PIN {
        int id PK
        int package_id FK
        string number
        string name
        string electrical_type
        string description
    }

    CORRECTION_LOG {
        int id PK
        string task_type "e.g., PIN_EXTRACTION, PACKAGE_ID"
        text input_context "Prompt/Context sent to LLM"
        json llm_output "Original LLM response"
        json user_corrected_output "Final verified data"
        string model_version
        float confidence_score
        datetime created_at
    }
```

## Table Definitions

### 1. Datasheets
Stores metadata about the processed PDF documents.
- `file_hash`: SHA-256 hash to prevent duplicate processing.

### 2. Components
Represents a specific part number or family described in the datasheet.

### 3. Packages
Details the physical package (footprint) information.
- `dimensions`: JSON field storing key-value pairs for IPC-7351 generation (e.g., `{ "A": 1.0, "A1": 0.05, "D": 3.0, "E": 3.0 }`).
- `3d_model_params`: JSON field for CadQuery generation parameters.

### 4. Pins
Stores the pinout table.
- `electrical_type`: Maps to KiCAD types (Input, Output, Bidirectional, Power Input, etc.).

### 5. CorrectionLog (Critical for LoRA)
This table is the source of truth for fine-tuning.
- **Strategy**: Every time a user modifies the extracted data in the GUI and saves, a record is created here.
- **Structure**:
    - `input_context`: The raw text or JSON structure from MinerU that was used as input to the LLM.
    - `llm_output`: The raw JSON the LLM predicted.
    - `user_corrected_output`: The final JSON after user edits.
- **Usage**: The "LoRA Trainer" tool will query this table to create `(prompt, completion)` pairs for training.

## Data Flow for Corrections
1. **Extraction**: App sends `input_context` to LLM -> gets `llm_output`.
2. **UI**: User sees `llm_output` populated in forms.
3. **Edit**: User changes "Pin 1 Type" from "Input" to "Power".
4. **Save**: App saves the final state to `Pins` table AND writes a row to `CorrectionLog` with the diff.
