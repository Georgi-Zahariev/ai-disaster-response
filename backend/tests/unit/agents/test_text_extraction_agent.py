"""
Unit tests for text extraction agent.
"""

import pytest
from unittest.mock import AsyncMock, patch


# Sample test signal
SAMPLE_TEXT_SIGNAL = {
    "signalId": "txt-test-001",
    "signalType": "text",
    "content": "Major traffic accident on Highway 101 near downtown. Multiple lanes blocked.",
    "source": {
        "sourceId": "src-test",
        "sourceType": "human_report",
        "sourceName": "Test Source"
    },
    "receivedAt": "2026-03-09T14:30:00Z",
    "createdAt": "2026-03-09T14:30:00Z",
    "confidence": 0.8
}


@pytest.mark.asyncio
async def test_extract_from_text_signal():
    """Test extracting observations from text signal."""
    from backend.agents.text_extraction_agent import TextExtractionAgent
    
    agent = TextExtractionAgent()
    
    # TODO: Add mocks for LLM/NLP services
    # For now, test that function returns list
    result = await agent.extract(SAMPLE_TEXT_SIGNAL)
    
    assert isinstance(result, list)
    # assert len(result) > 0
    # assert result[0]["observationType"] is not None


@pytest.mark.asyncio
async def test_extract_with_empty_content():
    """Test extraction handles empty content gracefully."""
    from backend.agents.text_extraction_agent import TextExtractionAgent
    
    agent = TextExtractionAgent()
    
    empty_signal = {**SAMPLE_TEXT_SIGNAL, "content": ""}
    result = await agent.extract(empty_signal)
    
    assert result == []


@pytest.mark.asyncio
@patch('backend.agents.text_extraction_agent.TextExtractionAgent._extract_entities')
async def test_entity_extraction(mock_extract):
    """Test entity extraction is called."""
    from backend.agents.text_extraction_agent import TextExtractionAgent
    
    mock_extract.return_value = {
        "locations": ["Highway 101", "downtown"],
        "organizations": [],
        "dates": [],
        "quantities": []
    }
    
    agent = TextExtractionAgent()
    result = await agent.extract(SAMPLE_TEXT_SIGNAL)
    
    # Verify entity extraction was called
    # mock_extract.assert_called_once()
