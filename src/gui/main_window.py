import sys
import os
import asyncio
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget,
                               QFileDialog, QToolBar, QMessageBox, QMenu, QStatusBar, QLabel)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSettings

from src.gui.pdf_viewer import PdfViewer
from src.gui.editors.component_editor import ComponentEditor
from src.gui.editors.package_editor import PackageEditor
from src.gui.editors.pin_editor import PinEditor

from src.backend.ingestion import IngestionEngine
from src.backend.llm_client import LLMClient
from src.backend.extractor import ContentExtractor
from src.backend.correction_logger import CorrectionLogger
from src.database.db_manager import DBManager
from src.models.data_models import Component, Package, Pin, Datasheet

# Generators
from src.generators.symbol_generator import SymbolGenerator
from src.generators.footprint_generator import FootprintGenerator
from src.generators.model_generator import ModelGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinerU to KiCAD Component Generator")
        self.resize(1600, 900)

        # Initialize Settings
        self.settings = QSettings("Antigravity", "MinerU2KiCAD")

        # Initialize Backend Components
        self.db_manager = DBManager("component_data.db") # Use local DB for now
        self.ingestion_engine = IngestionEngine()
        llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
        llm_model = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct")
        self.llm_client = LLMClient(base_url=llm_base_url, model_name=llm_model)
        self.extractor = ContentExtractor(self.llm_client)
        self.correction_logger = CorrectionLogger(self.db_manager)
        
        # Initialize Generators
        self.symbol_gen = SymbolGenerator()
        self.footprint_gen = FootprintGenerator()
        self.model_gen = ModelGenerator()

        # Data State
        self.current_datasheet: Datasheet = None
        self.current_component: Component = None
        self.current_package: Package = None
        self.current_pins: list[Pin] = []
        self.current_file_path: str = None

        # UI Setup
        self._setup_ui()
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()

        # Restore State
        self.load_last_file()

    def _setup_ui(self):
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Main Splitter (Left: Tree, Center: PDF, Right: Editors)
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # 1. Left Pane: Project Tree
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("Project Explorer")
        
        # 2. Center Pane: PDF Viewer
        self.pdf_viewer = PdfViewer()
        
        # 3. Right Pane: Data Editors
        self.editor_tabs = QTabWidget()
        self.component_editor = ComponentEditor()
        self.package_editor = PackageEditor()
        self.pin_editor = PinEditor()
        
        self.editor_tabs.addTab(self.component_editor, "Component")
        self.editor_tabs.addTab(self.package_editor, "Package")
        self.editor_tabs.addTab(self.pin_editor, "Pins")
        
        # Add widgets to splitter
        self.main_splitter.addWidget(self.project_tree)
        self.main_splitter.addWidget(self.pdf_viewer)
        self.main_splitter.addWidget(self.editor_tabs)
        
        # Set initial sizes (approx 20%, 50%, 30%)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 3)
        self.main_splitter.setStretchFactor(2, 2)
        
        main_layout.addWidget(self.main_splitter)

    def _create_actions(self):
        self.open_action = QAction("&Open PDF...", self)
        self.open_action.triggered.connect(self.open_pdf)
        
        self.process_llm_action = QAction("&Process with LLM", self)
        self.process_llm_action.triggered.connect(self.process_with_llm)

        self.generate_action = QAction("&Generate Files", self)
        self.generate_action.triggered.connect(self.generate_files)
        
        self.save_correction_action = QAction("&Save Correction", self)
        self.save_correction_action.triggered.connect(self.save_correction)

    def _create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_correction_action)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)
        
        tools_menu = menu_bar.addMenu("&Tools")
        tools_menu.addAction(self.process_llm_action)
        tools_menu.addAction(self.generate_action)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addAction(self.open_action)
        toolbar.addSeparator()
        toolbar.addAction(self.process_llm_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_correction_action)
        toolbar.addAction(self.generate_action)

    def _create_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

    def update_status(self, message):
        self.status_label.setText(message)
        # Force UI update
        QApplication.processEvents()

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Datasheet PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_datasheet(file_path)

    def load_last_file(self):
        last_file = self.settings.value("last_opened_file")
        if last_file and os.path.exists(last_file):
            self.update_status(f"Restoring last opened file: {last_file}")
            self.load_datasheet(last_file)

    def load_datasheet(self, file_path):
        # 1. Load PDF in Viewer
        self.update_status(f"Loading PDF: {os.path.basename(file_path)}...")
        self.pdf_viewer.load_document(file_path)
        self.update_status(f"Loaded: {os.path.basename(file_path)}. Ready to process.")
        
        # Store file path
        self.current_file_path = file_path
        
        # Save to settings
        self.settings.setValue("last_opened_file", file_path)

        # Initialize current datasheet object
        self.current_datasheet = Datasheet(
            filename=os.path.basename(file_path),
            file_hash="dummy_hash", # TODO: Calculate hash
            title="New Datasheet"
        )
        
        # Clear previous data
        self.current_component = None
        self.current_package = None
        self.current_pins = []
        self.project_tree.clear()

    def process_with_llm(self):
        if not self.current_datasheet or not self.current_file_path:
            QMessageBox.warning(self, "Warning", "Please load a PDF first.")
            return

        self.update_status("Processing with LLM... (This may take a moment)")
        
        try:
            # Check for corresponding .md file (MinerU output)
            md_path = self.current_file_path.replace('.pdf', '.md')
            content = ""
            sections = {}
            
            if os.path.exists(md_path):
                self.update_status(f"Reading content from {os.path.basename(md_path)}...")
                # Use IngestionEngine to process the file
                ingestion_result = self.ingestion_engine.process_file(md_path)
                content = ingestion_result.get("content", "")
                sections = ingestion_result.get("sections", {})
            else:
                # Fallback: Check if there's a JSON file
                json_path = self.current_file_path.replace('.pdf', '.json')
                if os.path.exists(json_path):
                    self.update_status(f"Reading content from {os.path.basename(json_path)}...")
                    ingestion_result = self.ingestion_engine.process_file(json_path)
                    content = str(ingestion_result.get("raw_data", "")) # Convert JSON to string for now
                    sections = ingestion_result.get("sections", {})
                
                if not content:
                    # If no pre-processed content, we can't do much without running MinerU.
                    QMessageBox.warning(self, "Missing Content", 
                                        f"Could not find MinerU output (.md) for {self.current_datasheet.filename}.\n"
                                        "Please run the ingestion script first.\n\n"
                                        "Attempting to proceed with empty content (will likely fail to extract data).")
                    self.update_status("Processing aborted: No content found.")
                    return

            # Call Extractor
            self.update_status("Sending content to LLM...")
            extracted_data = self.extractor.extract_all(content, datasheet_id=1, sections=sections)
            
            if not extracted_data:
                raise Exception("Extraction returned no data.")

            self.current_component = extracted_data.get("component")
            self.current_package = extracted_data.get("package")
            self.current_pins = extracted_data.get("pins")
            
            # DEBUG: Print response
            if self.current_component:
                print(f"Response: {self.current_component.model_dump_json()}")
            print("----------------------")
            
            self.update_ui_from_data()
            self.update_status("LLM Processing Complete.")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to process file: {str(e)}")

    def update_ui_from_data(self):
        if self.current_component:
            # Update Component Editor
            self.component_editor.set_data({
                "part_number": self.current_component.part_number,
                "manufacturer": self.current_component.manufacturer,
                "description": self.current_component.description,
                "datasheet_link": self.current_datasheet.filename if self.current_datasheet else ""
            })
            
        if self.current_package:
            # Update Package Editor
            self.package_editor.set_dimensions(self.current_package.dimensions)
            
        if self.current_pins:
            # Update Pin Editor
            pins_data = []
            for pin in self.current_pins:
                pins_data.append({
                    "number": pin.number,
                    "name": pin.name,
                    "type": pin.electrical_type,
                    "description": pin.description
                })
            self.pin_editor.set_pins(pins_data)
            
        # Update Tree
        self.project_tree.clear()
        if self.current_datasheet:
            root = QTreeWidgetItem(self.project_tree, [self.current_datasheet.filename])
            if self.current_component:
                comp = QTreeWidgetItem(root, [self.current_component.part_number])
                if self.current_package:
                    QTreeWidgetItem(comp, [self.current_package.name])
                QTreeWidgetItem(comp, [f"{len(self.current_pins)} Pins"])
            self.project_tree.expandAll()

    def generate_files(self):
        if not self.current_component:
            QMessageBox.warning(self, "Warning", "No component loaded.")
            return

        try:
            self.update_status("Generating files...")
            # Generate Symbol
            sym_content = self.symbol_gen.generate_symbol(self.current_component, self.current_pins)
            
            # Generate Footprint
            fp_content = self.footprint_gen.generate_footprint(self.current_package)
            
            # Generate Model
            # model_path = self.model_gen.generate_model(self.current_package)
            
            # Save to disk (Mocking save dialog)
            # In real app, ask user where to save
            
            print("Generated Symbol:\n", sym_content)
            print("Generated Footprint:\n", fp_content)
            
            self.update_status("Files generated successfully.")
            QMessageBox.information(self, "Success", "Files generated successfully (printed to console for now).")
            
        except Exception as e:
            self.update_status(f"Generation Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Generation failed: {str(e)}")

    def save_correction(self):
        # Trigger Correction Logger
        # In a real scenario, we'd compare original LLM output with current editor state
        if self.current_component:
            try:
                self.correction_logger.log_correction(
                    prompt="Extract component data",
                    original_output="{}", # Mock original
                    user_corrected_output=self.current_component.model_dump_json()
                )
                self.update_status("Correction logged.")
                QMessageBox.information(self, "Success", "Correction logged.")
            except Exception as e:
                self.update_status(f"Logging Error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to log correction: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
