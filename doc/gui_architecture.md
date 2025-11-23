# GUI Architecture Design

## 1. Technology Stack
- **Framework**: `PySide6` (Qt 6.x bindings for Python).
- **PDF Rendering**: `PyMuPDF` (fitz) rendering to `QImage`/`QPixmap`.
    - *Rationale*: Provides fast, pixel-perfect rendering and easy coordinate mapping for drawing bounding boxes (highlights) over the PDF.
- **3D Visualization**: `PyVistaQt` (`QtInteractor`).
    - *Rationale*: Easy integration of VTK visualization into Qt for displaying generated 3D models.

## 2. Main Window Layout
The application uses a standard 3-pane layout managed by `QSplitter` for resizability.

### 2.1 Left Pane: Project Explorer (`QTreeView`)
- Displays the structure of the loaded project.
- **Hierarchy**:
    - Datasheet (Root)
        - Component A
            - Package X
            - Package Y
        - Component B

### 2.2 Center Pane: Document Workspace
- **PDF Viewer Widget**:
    - Custom `QWidget` subclass.
    - **Features**:
        - Zoom/Pan support.
        - **Highlight Layer**: Draws semi-transparent rectangles over coordinates extracted from MinerU (e.g., highlighting the specific row in a table where a pin is defined).
        - **Navigation**: "Go to Page" and "Find" functionality.
- **Log/Status Panel** (Bottom, Collapsible):
    - Shows LLM processing status, validation errors, and generation logs.

### 2.3 Right Pane: Data Editor (`QScrollArea`)
- Context-sensitive editor based on selection in the Project Explorer.

#### View A: Component Editor
- Fields: Part Number, Manufacturer, Description, Datasheet Link.
- **Actions**: "Re-extract with LLM", "Save Corrections".

#### View B: Package Editor
- **Dimensions Table**: `QTableView` for editing A, A1, D, E, etc.
- **3D Preview**: Small `PyVista` widget showing the live-updated 3D model based on dimensions.

#### View C: Pinout Editor
- **Pin Table**: `QTableView` with columns: Number, Name, Electrical Type, Description.
- **Features**:
    - Dropdown for "Electrical Type" (Input, Output, Power, etc.).
    - Bulk edit capabilities.
    - "Add/Remove Pin" buttons.

## 3. Interaction Flow
1.  **Load**: User opens a directory. `ProjectModel` parses JSON and populates the Tree.
2.  **Select**: User selects "Pinout" for "ADS1013".
3.  **Highlight**: The PDF Viewer automatically scrolls to the page containing the pin table and highlights the bounding box (from MinerU metadata).
4.  **Edit**: User notices "Pin 2" is "NC" but should be "Alert". User edits the Pin Table.
5.  **Validate**: Real-time validation checks (e.g., duplicate pin numbers) show red borders.
6.  **Save**: User clicks Save.
    - Data is written to SQLite.
    - `CorrectionLog` is updated (triggering the "Active Learning" loop).

## 4. Custom Widgets
- `PdfPageWidget`: Handles rendering a single PDF page `QImage` and painting overlays.
- `PinTypeDelegate`: Custom `QStyledItemDelegate` for rendering color-coded pin type dropdowns in the table.
