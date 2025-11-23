# Task: Phase 3 - GUI Implementation

## Context
You are the implementation agent for the "MinerU to KiCAD Component Generator" project. Your goal in this phase is to build the Qt6 (PySide6) desktop application.

## Resources
- **Architecture**: `doc/architecture.md`
- **GUI Architecture**: `doc/gui_architecture.md`
- **Implementation Plan**: `implementation_plan.md`
- **Task List**: `task.md`

## Instructions
1.  **Read the Resources**: Understand the GUI layout and interaction flow.
2.  **Main Window**:
    - Implement `src/gui/main_window.py`.
    - Create the 3-pane layout (Project Tree, PDF Viewer, Data Editor) using `QSplitter`.
3.  **PDF Viewer**:
    - Implement `src/gui/pdf_viewer.py`.
    - Create `PdfPageWidget` using `PyMuPDF` (fitz) to render pages to `QImage`.
    - Implement the highlighting mechanism (drawing rectangles over specific coordinates).
4.  **Editors**:
    - Implement `src/gui/editors/component_editor.py` (Form layout).
    - Implement `src/gui/editors/package_editor.py` (Dimensions table + placeholder for 3D view).
    - Implement `src/gui/editors/pin_editor.py` (Table view with custom delegates for Pin Type).
5.  **Update Task List**:
    - Mark the corresponding items in `task.md` as completed (`[x]`).

## Deliverables
- `src/gui/main_window.py`
- `src/gui/pdf_viewer.py`
- `src/gui/editors/component_editor.py`
- `src/gui/editors/package_editor.py`
- `src/gui/editors/pin_editor.py`
- Updated `task.md`
