# Project Setup

## Prerequisites
- Python 3.10+
- Docker & Docker Compose
- NVIDIA GPU (for local LLM inference)

## Virtual Environment
All Python code should be executed within a virtual environment.

1.  **Create venv**:
    ```bash
    python3 -m venv .venv
    ```

2.  **Activate venv**:
    ```bash
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `requirements.txt` should be generated from installed packages)*

## Docker
To start the AI services:

```bash
cd docker
docker-compose up -d
```
