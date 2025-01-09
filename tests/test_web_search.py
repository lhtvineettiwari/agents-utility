import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from src.youtube_tracker.web_search import WebSearcher

@pytest.fixture
def web_searcher():
    return WebSearcher()

@pytest.fixture
def mock_search_response():
    """Mock HTML response for DuckDuckGo search"""
    return """
    <html>
        <div class="result">
            <h2 class="result__title">
                <a href="https://example.com/1">Test Title 1</a>
            </h2>
            <div class="result__snippet">Test Snippet 1</div>
        </div>
        <div class="result">
            <h2 class="result__title">
                <a href="https://example.com/2">Test Title 2</a>
            </h2>
            <div class="result__snippet">Test Snippet 2</div>
        </div>
    </html>
    """

@pytest.fixture
def mock_page_response():
    """Mock HTML response for webpage content"""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <script>var x = 1;</script>
            <div>Test Content</div>
            <style>.test { color: red; }</style>
            <p>More test content</p>
        </body>
    </html>
    """

def test_search_success(web_searcher, mock_search_response, mock_page_response):
    """Test successful search with mocked responses"""
    with patch('requests.get') as mock_get:
        # Mock search response
        mock_search = Mock()
        mock_search.text = mock_search_response
        mock_search.raise_for_status.return_value = None
        
        # Mock page response
        mock_page = Mock()
        mock_page.text = mock_page_response
        mock_page.raise_for_status.return_value = None
        
        # Configure mock to return different responses
        mock_get.side_effect = [mock_search] + [mock_page] * 2  # One search + two page fetches
        
        results = web_searcher.search("test query", num_results=2)
        
        assert len(results) == 2
        assert results[0]['url'] == 'https://example.com/1'
        assert results[0]['title'] == 'Test Title 1'
        assert results[0]['snippet'] == 'Test Snippet 1'
        assert 'Test Content' in results[0]['context']
        assert 'var x = 1' not in results[0]['context']  # Script content should be removed

def test_search_with_empty_response(web_searcher):
    """Test search with empty response"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        results = web_searcher.search("test query")
        assert len(results) == 0

def test_search_with_request_error(web_searcher):
    """Test search with request error"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Test error")
        results = web_searcher.search("test query")
        assert len(results) == 0

def test_get_page_context_success(web_searcher, mock_page_response):
    """Test successful page context extraction"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = mock_page_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        context = web_searcher.get_page_context("https://example.com")
        assert 'Test Content' in context
        assert 'More test content' in context
        assert 'var x = 1' not in context  # Script content should be removed
        assert '.test { color: red; }' not in context  # Style content should be removed

def test_get_page_context_with_error(web_searcher):
    """Test page context extraction with error"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Test error")
        context = web_searcher.get_page_context("https://example.com")
        assert context == ""

def test_search_result_structure(web_searcher, mock_search_response, mock_page_response):
    """Test structure of search results"""
    with patch('requests.get') as mock_get:
        # Mock responses
        mock_search = Mock()
        mock_search.text = mock_search_response
        mock_search.raise_for_status.return_value = None
        
        mock_page = Mock()
        mock_page.text = mock_page_response
        mock_page.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_search] + [mock_page] * 2
        
        results = web_searcher.search("test query", num_results=2)
        
        # Check result structure
        for result in results:
            assert isinstance(result, dict)
            assert all(key in result for key in ['url', 'title', 'snippet', 'context'])
            assert all(isinstance(result[key], str) for key in result)
