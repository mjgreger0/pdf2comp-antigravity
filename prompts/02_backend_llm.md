# Task: Phase 2 - Backend Logic & LLM Integration

## Context
You are the implementation agent for the "MinerU to KiCAD Component Generator" project. Your goal in this phase is to implement the backend logic for data ingestion, LLM communication, and the active learning correction loop.

## Resources
- **Architecture**: `doc/architecture.md`
- **LLM Workflow**: `doc/llm_workflow.md`
- **Implementation Plan**: `implementation_plan.md`
- **Task List**: `task.md`

## Instructions
1.  **Read the Resources**: Understand the LLM workflow and how the correction loop works.
2.  **LLM Client**:
    - Implement `src/backend/llm_client.py`.
    - Create a class `LLMClient` that communicates with the vLLM service (OpenAI-compatible API).
    - Implement methods for sending prompts and receiving JSON responses.
    - Ensure it handles JSON parsing and error checking.
3.  **Ingestion Engine**:
    - Implement `src/backend/ingestion.py`.
    - Create a class `IngestionEngine` that parses MinerU output (Markdown/JSON).
    - Implement logic to identify key sections (Pin Config, Dimensions).
4.  **Correction Logger**:
    - Implement `src/backend/correction_logger.py`.
    - Create a class `CorrectionLogger` that interacts with `DBManager`.
    - Implement `log_correction(prompt, original_output, user_corrected_output)` to save data to the `correction_log` table.
5.  **Docker Setup**:
    - Create `docker/docker-compose.yml`.
    - Define services for `llm-service` (vLLM) and `trainer-service` (Unsloth).
    - Configure volumes for model storage.
6.  **Update Task List**:
    - Mark the corresponding items in `task.md` as completed (`[x]`).

## Deliverables
- `src/backend/llm_client.py`
- `src/backend/ingestion.py`
- `src/backend/correction_logger.py`
- `docker/docker-compose.yml`
- Updated `task.md`
