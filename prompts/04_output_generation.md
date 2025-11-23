# Task: Phase 4 - Output Generation

## Context
You are the implementation agent for the "MinerU to KiCAD Component Generator" project. Your goal in this phase is to implement the generators for KiCAD files.

## Resources
- **Architecture**: `doc/architecture.md`
- **Output Generation**: `doc/output_generation.md`
- **Implementation Plan**: `implementation_plan.md`
- **Task List**: `task.md`

## Instructions
1.  **Read the Resources**: Understand the KiCAD file formats and generation logic.
2.  **Symbol Generator**:
    - Implement `src/generators/symbol_generator.py`.
    - Create `SymbolGenerator` class to generate `.kicad_sym` (S-expressions).
    - Handle pin grouping and symbol graphics (rectangle, text).
3.  **Footprint Generator**:
    - Implement `src/generators/footprint_generator.py`.
    - Create `FootprintGenerator` class to generate `.kicad_mod`.
    - Implement IPC-7351B formulas for pad stacks based on dimensions.
4.  **3D Model Generator**:
    - Implement `src/generators/model_generator.py`.
    - Create `ModelGenerator` class using `CadQuery`.
    - Implement parametric scripts for common packages (QFN, SOIC, etc.).
    - Ensure it exports both `.step` and `.wrl`.
5.  **Update Task List**:
    - Mark the corresponding items in `task.md` as completed (`[x]`).

## Deliverables
- `src/generators/symbol_generator.py`
- `src/generators/footprint_generator.py`
- `src/generators/model_generator.py`
- Updated `task.md`
