# LLM Integration & LoRA Fine-Tuning Workflow

## 1. LLM Integration Strategy

### 1.1 Model Selection
- **Primary Model**: `Qwen-2.5-Coder-32B-Instruct` (or similar).
    - *Rationale*: Excellent instruction following, strong at structured output (JSON), and capable of reasoning about technical documents.
    - *Serving*: `vLLM` container exposing OpenAI-compatible API.

### 1.2 Prompt Engineering
The system will use a **Multi-Stage Extraction** approach to handle the complexity of datasheets.

#### Stage 1: Document Segmentation (Heuristic + LLM)
- **Input**: MinerU Markdown (`ads1013.md`) + Content List (`ads1013_content_list.json`).
- **Task**: Identify key sections: "Pin Configuration", "Package Dimensions", "Electrical Characteristics".
- **Method**: Regex/Keyword matching first (fast), fallback to LLM if structure is non-standard.

#### Stage 2: Component & Package Extraction
- **Input**: "General Description" and "Ordering Information" sections.
- **Prompt**: "Extract all component part numbers and their associated package types from the following text. Return JSON."
- **Output Schema**:
    ```json
    {
      "components": [
        {"part_number": "ADS1013", "description": "12-Bit ADC..."},
        ...
      ],
      "packages": ["QFN-10", "MSOP-10"]
    }
    ```

#### Stage 3: Pinout Extraction
- **Input**: "Pin Configuration" section (Images + Tables).
- **Prompt**: "Extract the pinout table for package {package_name}. For each pin, identify Number, Name, Type (Input/Output/Power/etc), and Description."
- **Context**: The LLM is given the Markdown table representation from MinerU.

#### Stage 4: Dimension Extraction (The Hard Part)
- **Input**: "Package Dimensions" section.
- **Challenge**: Dimensions are often in complex drawings.
- **Strategy**:
    1.  Provide the text/table data associated with dimensions.
    2.  Ask LLM to map dimensions to IPC-7351 standard parameters (A, A1, b, D, E, e, L, etc.).
    3.  *Future Enhancement*: Use a Vision-Language Model (VLM) like `Qwen-VL` to look at the dimension drawing directly if text is insufficient.

### 1.3 JSON Mode
All LLM calls will enforce **JSON Output** to ensure the application can parse the results reliably.

## 2. LoRA Fine-Tuning Workflow

### 2.1 The "Correction Loop"
The system learns from user corrections. This is the core "Agentic" feature.

1.  **Capture**: When a user corrects an extracted field (e.g., changes Pin 1 from "Input" to "Power"), the application logs:
    -   `Prompt`: The exact text sent to the LLM.
    -   `Completion`: The corrected JSON object (not the original wrong one).
2.  **Accumulate**: These pairs are stored in the `CorrectionLog` table.
3.  **Dataset Generation**: A background job exports `CorrectionLog` entries to a JSONL file:
    ```json
    {"messages": [{"role": "user", "content": "...prompt..."}, {"role": "assistant", "content": "...corrected_json..."}]}
    ```

### 2.2 Training Pipeline
- **Framework**: `Unsloth` (optimized for speed and memory) or `HuggingFace PEFT`.
- **Process**:
    1.  **Trigger**: User clicks "Improve Model" (or auto-scheduled).
    2.  **Container**: Spawns a `trainer` container.
    3.  **Fine-Tune**: Runs LoRA fine-tuning on the base model using the accumulated dataset.
    4.  **Save**: Saves the new LoRA adapter to `/data/projects/ai/huggingface/models/adapters/v1`.
    5.  **Reload**: Signals the `vLLM` service to load the new adapter.

### 2.3 Multi-Manufacturer Adaptability
- The LoRA model will generalize across manufacturers because the training data (user corrections) will naturally cover diverse datasheet formats as the user processes more documents.
- **Active Learning**: The system effectively performs active learning—the user labels the "hard" examples (where the model failed), making the fine-tuning highly efficient.

## 3. Infrastructure
- **Inference**: `vLLM` running on GPU 0.
- **Training**: `Unsloth` running on GPU 1 (when active).
- **Orchestration**: Docker Compose to manage the services.
