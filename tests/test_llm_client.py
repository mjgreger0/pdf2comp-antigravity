import pytest
from unittest.mock import MagicMock, patch
from src.backend.llm_client import LLMClient

@pytest.fixture
def mock_openai():
    with patch('src.backend.llm_client.OpenAI') as mock:
        yield mock

def test_llm_client_initialization(mock_openai):
    client = LLMClient(base_url="http://test:8000/v1", model_name="test-model")
    mock_openai.assert_called_once_with(base_url="http://test:8000/v1", api_key="sk-antigravity")
    assert client.model_name == "test-model"

def test_generate_json(mock_openai):
    mock_instance = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"key": "value"}'
    mock_instance.chat.completions.create.return_value = mock_response

    client = LLMClient()
    response = client.generate("test prompt", json_mode=True)
    
    assert response == {"key": "value"}
    mock_instance.chat.completions.create.assert_called_once()

def test_generate_text(mock_openai):
    mock_instance = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "plain text response"
    mock_instance.chat.completions.create.return_value = mock_response

    client = LLMClient()
    response = client.generate("test prompt", json_mode=False)
    
    assert response == "plain text response"

def test_generate_json_error(mock_openai):
    mock_instance = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "invalid json"
    mock_instance.chat.completions.create.return_value = mock_response

    client = LLMClient()
    response = client.generate("test prompt", json_mode=True)
    
    assert "error" in response
    assert response["error"] == "JSONDecodeError"
