# Phase 5: Integration & Testing Implementation Plan

This plan outlines the integration of all components and the verification of the full workflow for the "MinerU to KiCAD Component Generator" project.

## User Review Required
> [!IMPORTANT]
> The End-to-End test mocks the LLM to ensure deterministic results. Real-world performance depends on the actual LLM (vLLM) which is not tested here.

## Proposed Changes

### Integration
#### [MODIFY] [main_window.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/src/gui/main_window.py)
- **Functionality**: Connect GUI to Backend and Generators.
- **Changes**:
    - Add `IngestionEngine` and `LLMClient` initialization.
    - Implement "Open PDF" action to trigger ingestion.
    - Implement "Generate" action to trigger generators.
    - Implement "Save Correction" to trigger `CorrectionLogger`.

### Tests
#### [NEW] [test_e2e.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/tests/test_e2e.py)
- **Class**: `TestEndToEnd`
- **Functionality**: Simulates the full workflow.
- **Steps**:
    1.  Mock `LLMClient` responses.
    2.  Run `IngestionEngine` on a sample file.
    3.  Simulate data extraction and population of models.
    4.  Simulate user modification of data.
    5.  Run Generators (`SymbolGenerator`, `FootprintGenerator`, `ModelGenerator`).
    6.  Verify output files exist and contain expected data.

### Scripts
#### [NEW] [run_app.sh](file:///data/home/mgreger/proj/pdf2comp-antigravity/scripts/run_app.sh)
- **Functionality**: Sets up environment and launches the application.
- **Content**:
    - Set `PYTHONPATH`.
    - Run `python src/gui/main_window.py`.

## Verification Plan

### Automated Tests
- Run `pytest tests/test_e2e.py`.

### Manual Verification
- Run `scripts/run_app.sh`.
- Open a PDF (if available).
- Verify UI elements populate (using dummy data if LLM is not running).
