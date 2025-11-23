# Walkthrough - Phase 2: Backend Logic & LLM Integration

## Changes Implemented

### Backend Components
- **`src/backend/llm_client.py`**: Implemented `LLMClient` to communicate with vLLM via OpenAI-compatible API. Handles JSON parsing and error logging.
- **`src/backend/ingestion.py`**: Implemented `IngestionEngine` to parse MinerU output (Markdown/JSON) and identify key sections using heuristics.
- **`src/backend/correction_logger.py`**: Implemented `CorrectionLogger` to log user corrections to the database for active learning.

### Infrastructure
- **`docker/docker-compose.yml`**: Created Docker Compose configuration for `llm-service` (vLLM) and `trainer-service` (Unsloth). Configured to use the shared model directory.
- **`doc/setup.md`**: Added setup instructions including virtual environment usage.

### Model Setup
- Downloaded `Qwen/Qwen2.5-Coder-32B-Instruct` to `/data/projects/ai/huggingface/models/Qwen/Qwen2.5-Coder-32B-Instruct`.

## Verification Results

### Automated Tests
Ran `pytest` on the new backend components.

**Summary**:
- `tests/test_llm_client.py`: **PASSED** (Mocked API calls)
- `tests/test_ingestion.py`: **PASSED** (Markdown parsing)
- `tests/test_correction_logger.py`: **PASSED** (Database logging)

### Manual Verification
- **Model Download**: Verified file existence and size.
- **Docker Config**: Verified syntax and volume mappings (static check).

## Next Steps
- Proceed to **Phase 3: GUI Implementation**.
- Start the Docker services to verify full integration (requires GPU availability).
