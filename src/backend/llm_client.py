import os
import json
import logging
from typing import Dict, Any, Optional, Union
from openai import OpenAI, APIConnectionError, APIStatusError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    """
    Client for communicating with the vLLM service using the OpenAI-compatible API.
    """

    def __init__(self, base_url: str = "http://localhost:8000/v1", model_name: str = "Qwen/Qwen2.5-Coder-32B-Instruct", api_key: str = "sk-antigravity"):
        """
        Initialize the LLM client.

        Args:
            base_url (str): The base URL of the vLLM service.
            model_name (str): The name of the model to use.
            api_key (str): The API key (dummy key for vLLM usually).
        """
        self.base_url = base_url
        self.model_name = model_name
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        logger.info(f"LLMClient initialized with base_url={base_url}, model={model_name}")

    def generate(self, prompt: str, system_prompt: str = None, json_mode: bool = True, temperature: float = 0.1) -> Union[Dict[str, Any], str]:
        """
        Generate a response from the LLM.

        Args:
            prompt (str): The user prompt.
            system_prompt (str, optional): The system prompt. Defaults to a generic helpful assistant prompt if None.
            json_mode (bool): Whether to enforce JSON output. Defaults to True.
            temperature (float): Sampling temperature. Defaults to 0.1 for deterministic output.

        Returns:
            Union[Dict[str, Any], str]: The parsed JSON response or the raw string response.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a helpful AI assistant."})
        
        messages.append({"role": "user", "content": prompt})

        response_format = {"type": "json_object"} if json_mode else None

        try:
            logger.debug(f"Sending request to LLM: {messages}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format=response_format,
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Received response from LLM: {content}")

            if json_mode:
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}. Content: {content}")
                    # Attempt to repair or return raw content if parsing fails? 
                    # For now, raise or return raw to let caller handle.
                    # Let's return a dictionary with error info to be safe.
                    return {"error": "JSONDecodeError", "raw_content": content}
            else:
                return content

        except APIConnectionError as e:
            logger.error(f"The server could not be reached: {e.__cause__}")
            raise
        except APIStatusError as e:
            logger.error(f"Another non-200-range status code was received: {e.status_code}")
            logger.error(e.response)
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise
