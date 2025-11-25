# Phase 5: Integration & Testing Implementation Plan

This plan outlines the integration of all components and the verification of the full workflow for the "MinerU to KiCAD Component Generator" project.

## User Review Required
> [!IMPORTANT]
> The End-to-End test mocks the LLM to ensure deterministic results. Real-world performance depends on the actual LLM (vLLM) which is not tested here.

## Proposed Changes

### Backend
#### [MODIFY] [ingestion.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/src/backend/ingestion.py)
- **Functionality**: Improve section identification to return structured data.
- **Changes**:
    - Update `_identify_sections` to be more robust.
    - Ensure it returns a dictionary with keys like "pin_configuration", "package_dimensions", etc. containing the relevant text.

#### [MODIFY] [extractor.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/src/backend/extractor.py)
- **Functionality**: Use identified sections to construct a focused prompt.
- **Changes**:
    - Update `extract_all` to accept `sections` dictionary.
    - Construct the prompt by including only relevant sections for each extraction task (or all relevant sections if doing one pass).
    - Remove the hardcoded 50k truncation if sections are used, or apply it per section.

#### [MODIFY] [main_window.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/src/gui/main_window.py)
- **Functionality**: Pass sections to the extractor.
- **Changes**:
    - In `process_with_llm`, use `self.ingestion_engine.process_file` to get sections.
    - Pass `sections` to `self.extractor.extract_all`.

### Tests
#### [NEW] [test_context_handling.py](file:///data/home/mgreger/proj/pdf2comp-antigravity/tests/test_context_handling.py)
- **Functionality**: Verifies that the system handles large documents by selecting sections.
- **Steps**:
    1.  Create a large dummy markdown content with distinct sections.
    2.  Run `IngestionEngine` to identify sections.
    3.  Run `ContentExtractor` (mocking LLM) to verify it receives the correct sections in the prompt.

## Verification Plan

### Automated Tests
- Run `pytest tests/test_context_handling.py`.

### Manual Verification
- Open a large datasheet PDF (or corresponding MD).
- Click "Process with LLM".
- Verify in the logs that the prompt contains the specific sections (Pin Configuration, etc.) and not just the first 50k chars.
