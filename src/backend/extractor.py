import json
import logging
from typing import Dict, Any, List, Optional
from src.backend.llm_client import LLMClient
from src.models.data_models import Component, Package, Pin

logger = logging.getLogger(__name__)

class ContentExtractor:
    """
    Extracts structured component data from text using an LLM.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def extract_all(self, text_content: str, datasheet_id: int = 1, sections: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Extracts component, package, and pin information from the text content.
        
        Args:
            text_content (str): The full text content of the datasheet (or relevant sections).
            datasheet_id (int): The ID of the datasheet being processed.
            sections (Dict[str, str], optional): Identified sections from IngestionEngine.
            
        Returns:
            Dict[str, Any]: A dictionary containing 'component', 'package', and 'pins' objects/lists.
        """
        
        # Construct the prompt
        
        context_text = ""
        
        if sections:
            # Construct context from relevant sections
            # We prioritize sections that are likely to contain the info we need
            
            # 1. Component Details (usually in Description, Features, or Preamble)
            context_text += "--- COMPONENT DESCRIPTION ---\n"
            context_text += sections.get("description", "") + "\n"
            context_text += sections.get("features", "") + "\n"
            context_text += sections.get("preamble", "")[:2000] + "\n" # Limit preamble
            
            # 2. Package Details
            context_text += "\n--- PACKAGE INFORMATION ---\n"
            context_text += sections.get("package_dimensions", "") + "\n"
            context_text += sections.get("ordering_information", "") + "\n"
            
            # 3. Pin Configuration
            context_text += "\n--- PIN CONFIGURATION ---\n"
            context_text += sections.get("pin_configuration", "") + "\n"
            
            # Add other potentially useful sections if they are small enough?
            # For now, let's stick to these key ones.
            
            logger.info("Using identified sections for LLM context.")
        else:
            # Fallback to raw text truncation
            # Truncate to avoid context window issues if necessary (e.g., 30k chars ~ 7-8k tokens)
            # Qwen 32B usually has 32k context, so 30k chars is safe.
            context_text = text_content[:50000] 
            logger.info("Using raw text content (truncated) for LLM context.")
        
        system_prompt = """You are an expert electronics engineer and data extraction assistant. 
Your task is to extract structured information from a component datasheet.
Output the data strictly in JSON format."""

        user_prompt = f"""Extract the following information from the provided datasheet text:

1. Component Details:
   - Part Number
   - Manufacturer
   - Description

2. Package Details:
   - Package Name (e.g., SOIC-8, TO-220)
   - Package Type (e.g., SOIC, DIP, QFN)
   - Dimensions (width, length, height if available) - approximate or nominal values in mm.

3. Pin Configuration:
   - List of pins with:
     - Pin Number
     - Pin Name
     - Electrical Type (Input, Output, Power, Ground, Bidirectional, Passive, etc.)
     - Description (brief function)

Output JSON Schema:
{{
  "component": {{
    "part_number": "string",
    "manufacturer": "string",
    "description": "string"
  }},
  "package": {{
    "name": "string",
    "package_type": "string",
    "dimensions": {{
      "width": float,
      "length": float,
      "height": float
    }}
  }},
  "pins": [
    {{
      "number": "string",
      "name": "string",
      "electrical_type": "string",
      "description": "string"
    }}
  ]
}}

If a value is not found, use null or an empty string.
Ensure the JSON is valid.

Datasheet Text:
{context_text}
"""

        print("\n--- LLM PROMPT ---")
        print(f"System Prompt:\n{system_prompt}")
        print(f"User Prompt:\n{user_prompt}")
        print("------------------\n")

        try:
            response = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                json_mode=True,
                temperature=0.1
            )
            
            print(f"\n--- LLM RAW RESPONSE ---\n{response}\n------------------------\n")
            
            if isinstance(response, dict) and "error" in response:
                logger.error(f"LLM extraction failed: {response['error']}")
                return {}

            # Parse response into models
            data = response
            
            # Create Component
            comp_data = data.get("component", {})
            component = Component(
                datasheet_id=datasheet_id,
                part_number=comp_data.get("part_number", "Unknown"),
                manufacturer=comp_data.get("manufacturer", "Unknown"),
                description=comp_data.get("description", "")
            )
            
            # Create Package
            pkg_data = data.get("package", {})
            package = Package(
                component_id=0, # Placeholder, will be set after component save in real DB
                name=pkg_data.get("name", "Unknown"),
                package_type=pkg_data.get("package_type", "Unknown"),
                dimensions=pkg_data.get("dimensions", {})
            )
            
            # Create Pins
            pins_data = data.get("pins", [])
            pins = []
            for p in pins_data:
                pins.append(Pin(
                    package_id=0, # Placeholder
                    number=str(p.get("number", "")),
                    name=p.get("name", ""),
                    electrical_type=p.get("electrical_type", "Passive"),
                    description=p.get("description", "")
                ))
                
            return {
                "component": component,
                "package": package,
                "pins": pins,
                "raw_json": data
            }

        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            raise
