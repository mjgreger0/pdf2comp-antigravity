import pytest
from unittest.mock import MagicMock
from src.backend.correction_logger import CorrectionLogger

@pytest.fixture
def mock_db():
    return MagicMock()

def test_log_correction(mock_db):
    logger = CorrectionLogger(mock_db)
    logger.log_correction("prompt", "original", "corrected")
    
    mock_db.execute_query.assert_called_once()
    args = mock_db.execute_query.call_args[0]
    assert "INSERT INTO correction_log" in args[0]
    assert args[1] == ("prompt", "original", "corrected")

def test_log_correction_json(mock_db):
    logger = CorrectionLogger(mock_db)
    logger.log_correction("prompt", {"key": "val"}, {"key": "val2"})
    
    mock_db.execute_query.assert_called_once()
    args = mock_db.execute_query.call_args[0]
    # Check that dicts were converted to json strings
    assert args[1] == ("prompt", '{"key": "val"}', '{"key": "val2"}')
