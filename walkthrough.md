# Output Generation Walkthrough

This document details the implementation of the KiCAD file generators.

## Implemented Generators

### 1. Symbol Generator
- **File**: `src/generators/symbol_generator.py`
- **Functionality**: Generates `.kicad_sym` files.
- **Features**:
    - Automatic pin grouping (Left: Input/Passive, Right: Output, Top/Bottom: Power).
    - Dynamic symbol body sizing based on pin count.
    - Standard KiCAD properties (Reference, Value, Footprint, Datasheet).

### 2. Footprint Generator
- **File**: `src/generators/footprint_generator.py`
- **Functionality**: Generates `.kicad_mod` files.
- **Features**:
    - Supports QFN/QFP (Quad) and SOIC/SOP (Dual Row) packages.
    - Calculates pad dimensions using simplified IPC-7351B formulas.
    - Generates Courtyard and Silk Screen layers.

### 3. Model Generator
- **File**: `src/generators/model_generator.py`
- **Functionality**: Generates 3D models (`.step`).
- **Status**: **Requires `cadquery` library.**
- **Features**:
    - Parametric generation for Box, QFN, and SOIC shapes.
    - Exports STEP files for mechanical integration.

## Verification Results

Ran `tests/verify_generators.py` in the virtual environment.

```
[Symbol Generator]
PASS: Header found

[Footprint Generator]
PASS: Header found

[Model Generator]
PASS: Model generated in test_output
PASS: STEP file exists
```

> [!NOTE]
> The `ModelGenerator` requires `cadquery` to be installed in the environment (`pip install cadquery`). This has been installed and verified.

## LLM Extraction Implementation
- **File**: `src/backend/extractor.py`
- **Functionality**: Extracts structured component data from text using LLM.
- **Integration**:
    - `MainWindow` now initializes `ContentExtractor`.
    - `process_with_llm` retrieves content (from `.md` or `.json` if available) and calls `extractor.extract_all`.
    - Populates `Component`, `Package`, and `Pin` models with extracted data.
- **Verification**:
    - Verified via `tests/test_e2e.py` which mocks the LLM response and asserts data population.

## Context Handling Optimization
- **Goal**: Prevent LLM context window overflow by selectively feeding relevant sections.
- **Implementation**:
    - `IngestionEngine` (`src/backend/ingestion.py`) now identifies sections (Pin Configuration, Package Dimensions, etc.) using regex heuristics.
    - `ContentExtractor` (`src/backend/extractor.py`) constructs a focused prompt using these sections instead of the raw full text.
    - `MainWindow` (`src/gui/main_window.py`) orchestrates the flow by passing identified sections to the extractor.
- **Verification**:
    - `tests/test_context_handling.py` verifies that sections are correctly identified and passed to the LLM prompt.
    - Test passed: `tests/test_context_handling.py .. [100%]`
