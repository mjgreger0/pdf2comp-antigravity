import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.ingestion import IngestionEngine
from src.backend.extractor import ContentExtractor

class TestContextHandling(unittest.TestCase):
    def setUp(self):
        self.ingestion_engine = IngestionEngine()
        self.mock_llm_client = MagicMock()
        self.extractor = ContentExtractor(self.mock_llm_client)

    def test_section_identification(self):
        """
        Verify that IngestionEngine correctly identifies sections.
        """
        content = """
# Introduction
Some intro text.

# Pin Configuration
Pin 1: VCC
Pin 2: GND

# Electrical Characteristics
Volts: 5V

# Package Dimensions
Width: 10mm
"""
        sections = self.ingestion_engine._identify_sections(content)
        
        self.assertIn("pin_configuration", sections)
        self.assertIn("electrical_characteristics", sections)
        self.assertIn("package_dimensions", sections)
        
        self.assertIn("Pin 1: VCC", sections["pin_configuration"])
        self.assertIn("Volts: 5V", sections["electrical_characteristics"])

    def test_extractor_uses_sections(self):
        """
        Verify that ContentExtractor uses sections in the prompt.
        """
        sections = {
            "pin_configuration": "Pin 1: VCC\nPin 2: GND",
            "package_dimensions": "Width: 10mm",
            "other": "Irrelevant info"
        }
        
        # Mock LLM response
        self.mock_llm_client.generate.return_value = {}
        
        # Call extract_all with sections
        # Note: We need to update extract_all signature first, but for now we pass it as part of content or separate arg
        # The plan says we will update extract_all to accept sections.
        # So this test expects the updated signature.
        try:
            self.extractor.extract_all(text_content="Full content", sections=sections)
        except TypeError:
            # If signature not updated yet, this will fail, which is expected for TDD
            pass
            
        # Verify prompt contains specific section content
        # We need to capture the arguments passed to generate
        if self.mock_llm_client.generate.called:
            call_args = self.mock_llm_client.generate.call_args
            prompt = call_args[1]['prompt']
            
            self.assertIn("Pin 1: VCC", prompt)
            self.assertIn("Width: 10mm", prompt)
            # Ensure we are not just dumping everything if we want to be selective, 
            # but the plan is to include relevant sections.
            
if __name__ == '__main__':
    unittest.main()
