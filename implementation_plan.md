# Phase 2: Backend Logic & LLM Integration

## Goal Description
Implement the core backend logic for the MinerU to KiCAD Component Generator. This includes the client for communicating with the LLM (vLLM), the ingestion engine for parsing MinerU output, the correction logger for the active learning loop, and the Docker Compose configuration for the AI services.

## User Review Required
> [!IMPORTANT]
> This phase establishes the connection to the LLM and the data ingestion pipeline. Ensure the vLLM service is reachable as configured in `docker-compose.yml`.

## Proposed Changes

### Backend Components

#### [NEW] [llm_client.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/src/backend/llm_client.py)
- Implement `LLMClient` class.
- Use `openai` python package or `requests` to interact with vLLM's OpenAI-compatible API.
- Methods:
    - `__init__(self, base_url="http://localhost:8000/v1", model_name="Qwen/Qwen2.5-Coder-32B-Instruct")`
    - `generate(self, prompt: str, system_prompt: str = None, json_mode: bool = True) -> Dict | str`
    - Handle connection errors and JSON parsing errors.

#### [NEW] [ingestion.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/src/backend/ingestion.py)
- Implement `IngestionEngine` class.
- Methods:
    - `process_file(self, file_path: str) -> Dict`
    - Parse MinerU Markdown/JSON output.
    - Identify sections (Pin Config, Dimensions, etc.) using heuristics (regex/keywords) as per `doc/llm_workflow.md`.

#### [NEW] [correction_logger.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/src/backend/correction_logger.py)
- Implement `CorrectionLogger` class.
- Dependency: `DBManager`
- Methods:
    - `log_correction(self, prompt: str, original_output: str, user_corrected_output: str)`
    - Insert entry into `correction_log` table via `DBManager`.

### Model Setup

#### [NEW] Download Model
- **Action**: Download `Qwen/Qwen2.5-Coder-32B-Instruct` to the shared model directory.
- **Command**:
    ```bash
    huggingface-cli download Qwen/Qwen2.5-Coder-32B-Instruct --local-dir /data/projects/ai/huggingface/models/Qwen/Qwen2.5-Coder-32B-Instruct
    ```

### Docker Configuration

#### [NEW] [docker-compose.yml](file:///data/home/mgreger/proj/pdf2comp-antigravity/docker/docker-compose.yml)
- Services:
    - `llm-service`: vLLM container.
        - Image: `vllm/vllm-openai:latest`
        - Command: `--model /models/Qwen/Qwen2.5-Coder-32B-Instruct --api-key sk-xxxx --host 0.0.0.0`
        - Ports: `8000:8000`
        - Volumes:
            - `/data/projects/ai/huggingface/models:/models`
        - Environment:
            - `HF_HOME=/models/cache`
        - Deploy: GPU resources.
    - `trainer-service`: Unsloth container.
        - Image: `unsloth/unsloth-notebook:latest`
        - Volumes:
            - `/data/projects/ai/huggingface/models:/models`
            - `./src:/app/src`
            - `./data:/app/data`

## Verification Plan

### Automated Tests
- Create unit tests for the new backend components.
- `tests/test_llm_client.py`: Mock the API response and verify `LLMClient` handles it correctly.
- `tests/test_ingestion.py`: Feed sample MinerU output and verify `IngestionEngine` parses it correctly.
- `tests/test_correction_logger.py`: Verify `CorrectionLogger` calls `DBManager` correctly.

### Manual Verification
1.  **Docker**: Run `docker-compose up -d` and verify `llm-service` starts (assuming GPU is available, otherwise verify configuration syntax).
2.  **LLM Client**: Run a small script to ping the `llm-service` (if running) or mock server.
3.  **Ingestion**: Run `IngestionEngine` against a sample MinerU file (if available) or a dummy file.
