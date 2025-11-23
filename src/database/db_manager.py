import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime

class DBManager:
    def __init__(self, db_path: str = "pdf2comp.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Creates a database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_db(self, schema_path: str = "src/database/schema.sql"):
        """Initializes the database using the provided schema file."""
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        conn = self.get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()

    def execute_query(self, query: str, params: Tuple = ()) -> int:
        """Executes a query (INSERT, UPDATE, DELETE) and returns the last row id."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns all results as a list of dictionaries."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Executes a SELECT query and returns a single result as a dictionary."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def log_correction(self, 
                       task_type: str, 
                       input_context: str, 
                       llm_output: Dict[str, Any], 
                       user_corrected_output: Dict[str, Any],
                       model_version: str = "v1",
                       confidence_score: float = 1.0) -> int:
        """
        Logs a user correction to the database for active learning.
        Handles JSON serialization of the output fields.
        """
        query = """
            INSERT INTO correction_log 
            (task_type, input_context, llm_output, user_corrected_output, model_version, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            task_type,
            input_context,
            json.dumps(llm_output),
            json.dumps(user_corrected_output),
            model_version,
            confidence_score
        )
        
        return self.execute_query(query, params)
