# Task: Phase 5 - Integration & Testing

## Context
You are the implementation agent for the "MinerU to KiCAD Component Generator" project. Your goal in this phase is to integrate all components and verify the full workflow.

## Resources
- **Architecture**: `doc/architecture.md`
- **Implementation Plan**: `implementation_plan.md`
- **Task List**: `task.md`

## Instructions
1.  **Read the Resources**: Review the full system architecture.
2.  **Integration**:
    - Ensure the GUI correctly calls the Backend (Ingestion, LLM) and Generators.
    - Verify that "Save" in the GUI triggers the `CorrectionLogger`.
3.  **End-to-End Tests**:
    - Implement `tests/test_e2e.py`.
    - Create a test that simulates the full flow: Parse -> Extract -> Correct -> Generate.
    - Mock the LLM responses for deterministic testing.
4.  **Run Script**:
    - Create `scripts/run_app.sh` to launch the application (setting up PYTHONPATH, etc.).
5.  **Manual Verification**:
    - If possible, run the application and verify a sample datasheet.
6.  **Update Task List**:
    - Mark the corresponding items in `task.md` as completed (`[x]`).

## Deliverables
- `tests/test_e2e.py`
- `scripts/run_app.sh`
- Updated `task.md`
