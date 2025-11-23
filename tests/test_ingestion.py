import pytest
import os
from src.backend.ingestion import IngestionEngine

@pytest.fixture
def ingestion_engine():
    return IngestionEngine()

def test_identify_sections_markdown(ingestion_engine, tmp_path):
    content = """
# General Description
This is the description.

# Pin Configuration
Pin 1: VCC
Pin 2: GND

# Package Dimensions
Width: 10mm
Height: 10mm
"""
    file_path = tmp_path / "test.md"
    file_path.write_text(content, encoding='utf-8')
    
    result = ingestion_engine.process_file(str(file_path))
    
    assert "sections" in result
    sections = result["sections"]
    assert "pin_configuration" in sections
    assert "package_dimensions" in sections
    assert "Pin 1: VCC" in sections["pin_configuration"]
    assert "Width: 10mm" in sections["package_dimensions"]

def test_process_json(ingestion_engine, tmp_path):
    content = '{"key": "value"}'
    file_path = tmp_path / "test.json"
    file_path.write_text(content, encoding='utf-8')
    
    result = ingestion_engine.process_file(str(file_path))
    
    assert result["raw_data"] == {"key": "value"}

def test_unsupported_format(ingestion_engine):
    with pytest.raises(ValueError):
        ingestion_engine.process_file("test.txt")
