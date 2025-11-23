import logging
import json
from typing import Dict, Any
from ..database.db_manager import DBManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorrectionLogger:
    """
    Logger for the active learning loop.
    Stores prompt, original output, and user correction in the database.
    """

    def __init__(self, db_manager: DBManager):
        """
        Initialize the CorrectionLogger.

        Args:
            db_manager (DBManager): The database manager instance.
        """
        self.db = db_manager

    def log_correction(self, prompt: str, original_output: str, user_corrected_output: str) -> None:
        """
        Log a correction to the database.

        Args:
            prompt (str): The prompt sent to the LLM.
            original_output (str): The original output from the LLM (can be JSON string or raw text).
            user_corrected_output (str): The corrected output from the user (should be JSON string).
        """
        try:
            # Ensure outputs are strings
            if not isinstance(original_output, str):
                original_output = json.dumps(original_output)
            if not isinstance(user_corrected_output, str):
                user_corrected_output = json.dumps(user_corrected_output)

            query = """
                INSERT INTO correction_log (input_context, llm_output, user_correction)
                VALUES (?, ?, ?)
            """
            self.db.execute_query(query, (prompt, original_output, user_corrected_output))
            logger.info("Correction logged successfully.")
            
        except Exception as e:
            logger.error(f"Failed to log correction: {e}")
            raise
