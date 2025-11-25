import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import json
from datetime import date

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.models.data_models import Component, Package, Pin

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        # Create a QApplication instance if one doesn't exist
        # We need this for QWidgets to work, even in tests
        if not QApplication.instance():
            # Use offscreen platform for headless testing
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # Patch DBManager to avoid real DB file creation
        self.db_patcher = patch('src.gui.main_window.DBManager')
        self.mock_db = self.db_patcher.start()
        
        # Patch QSettings
        self.settings_patcher = patch('src.gui.main_window.QSettings')
        self.mock_settings_cls = self.settings_patcher.start()
        self.mock_settings = self.mock_settings_cls.return_value
        self.mock_settings.value.return_value = None # Default no last file

        # Initialize Window
        self.window = MainWindow()
        
        # Patch QMessageBox to avoid blocking
        self.msg_patcher = patch('src.gui.main_window.QMessageBox')
        self.mock_msg = self.msg_patcher.start()

        # Mock Backend
        self.window.ingestion_engine = MagicMock()
        self.window.llm_client = MagicMock()
        self.window.extractor = MagicMock() # Mock the Extractor
        self.window.correction_logger = MagicMock()
        
        # Mock Generators
        self.window.symbol_gen = MagicMock()
        self.window.footprint_gen = MagicMock()
        self.window.model_gen = MagicMock()

    def tearDown(self):
        self.db_patcher.stop()
        self.msg_patcher.stop()
        self.settings_patcher.stop()
        # We don't destroy self.app because it might be needed for other tests
        # and QApplication is a singleton.

    def test_full_workflow(self):
        """
        Simulate: Open PDF -> Process with LLM -> Modify -> Generate -> Save Correction
        """
        print("\n--- Starting End-to-End Test ---")
        
        # 1. Simulate Opening PDF
        pdf_path = "/tmp/dummy_datasheet.pdf"
        # Create dummy PDF file if needed by viewer, or mock viewer
        self.window.pdf_viewer.load_document = MagicMock()
        
        print("Step 1: Loading Datasheet...")
        self.window.load_datasheet(pdf_path)
        
        # Verify Datasheet Loaded
        self.assertIsNotNone(self.window.current_datasheet)
        self.assertEqual(self.window.current_datasheet.filename, "dummy_datasheet.pdf")
        
        # Verify Settings Saved
        self.mock_settings.setValue.assert_called_with("last_opened_file", pdf_path)
        print("Verified Last Opened File saved to settings.")
        
        # 2. Simulate LLM Processing
        print("Step 2: Processing with LLM...")
        
        # Mock Extractor Return
        mock_component = Component(
            datasheet_id=1,
            part_number="MOCKED-PART",
            description="Mocked Description",
            manufacturer="Mocked Mfg"
        )
        mock_package = Package(
            component_id=1,
            name="MOCKED-PKG",
            package_type="SOIC",
            dimensions={"width": 5.0}
        )
        mock_pins = [
            Pin(package_id=1, number="1", name="GND", electrical_type="Power")
        ]
        
        self.window.extractor.extract_all.return_value = {
            "component": mock_component,
            "package": mock_package,
            "pins": mock_pins
        }
        
        # We need to mock os.path.exists to simulate MD file existence or bypass it
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', unittest.mock.mock_open(read_data="Mocked Content")) as mock_open:
            
            mock_exists.return_value = True # Pretend MD file exists
            
            self.window.process_with_llm()
            
            # Verify Extractor Called
            self.window.extractor.extract_all.assert_called_once()
            
            # Verify Data Populated
            self.assertIsNotNone(self.window.current_component)
            self.assertEqual(self.window.current_component.part_number, "MOCKED-PART")
            print(f"Verified Component: {self.window.current_component.part_number}")
        
        # 3. Simulate User Modification
        print("Step 3: Modifying Data...")
        self.window.current_component.description = "Updated Description"
        
        # 4. Simulate Generation
        print("Step 4: Generating Files...")
        
        # Mock Generator Returns
        self.window.symbol_gen.generate_symbol.return_value = "(kicad_symbol ...)"
        self.window.footprint_gen.generate_footprint.return_value = "(kicad_footprint ...)"
        
        # Trigger Generation
        self.window.generate_files()
        
        # Verify Generators Called
        self.window.symbol_gen.generate_symbol.assert_called_once()
        self.window.footprint_gen.generate_footprint.assert_called_once()
        print("Verified Generators called.")
        
        # 5. Simulate Save Correction
        print("Step 5: Saving Correction...")
        self.window.save_correction()
        
        # Verify Logger Called
        self.window.correction_logger.log_correction.assert_called_once()
        args = self.window.correction_logger.log_correction.call_args
        self.assertIn("Updated Description", args[1]['user_corrected_output'])
        print("Verified Correction Logged.")
        
        print("--- End-to-End Test Passed ---")

if __name__ == '__main__':
    unittest.main()
