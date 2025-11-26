"""Custom tools for LangChain agents."""

import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SimpleTool:
    """Simple tool wrapper."""
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func


def create_search_tool(tool_name: str = "duckduckgo", max_results: int = 10) -> SimpleTool:
    """
    Create a search tool based on the specified provider.
    
    Args:
        tool_name: Name of the search tool (duckduckgo, google, tavily)
        max_results: Maximum number of results to return
        
    Returns:
        SimpleTool instance
    """
    if tool_name.lower() == "duckduckgo":
        search = DuckDuckGoSearchAPIWrapper(max_results=max_results)
        return SimpleTool(
            name="web_search",
            description=(
                "Search the web for current news and information. "
                "Use this to find recent news articles, updates, and developments. "
                "Input should be a search query string."
            ),
            func=search.run
        )
    else:
        # Placeholder for other search tools
        raise NotImplementedError(f"Search tool '{tool_name}' not yet implemented")


def extract_article_content(url: str) -> str:
    """
    Extract text content from a news article URL.
    
    Args:
        url: URL of the article
        
    Returns:
        Extracted text content
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:5000]  # Limit to first 5000 characters
        
    except Exception as e:
        logger.warning(f"Could not extract content from {url}: {e}")
        return ""


def create_content_extractor_tool() -> SimpleTool:
    """
    Create a tool for extracting content from URLs.
    
    Returns:
        SimpleTool instance
    """
    return SimpleTool(
        name="extract_article",
        description=(
            "Extract the full text content from a news article URL. "
            "Use this when you need to read the full article content. "
            "Input should be a valid URL."
        ),
        func=extract_article_content
    )


def parse_search_results(search_output: str) -> List[Dict[str, str]]:
    """
    Parse search results from DuckDuckGo output into structured format.
    
    Args:
        search_output: Raw search output string
        
    Returns:
        List of article dictionaries
    """
    articles = []
    
    # DuckDuckGo returns results in a specific format
    # This is a simplified parser - adjust based on actual output format
    lines = search_output.split('\n')
    current_article = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_article:
                articles.append(current_article)
                current_article = {}
            continue
        
        # Try to parse title, snippet, and link
        if line.startswith('http'):
            current_article['url'] = line
        elif 'title' not in current_article:
            current_article['title'] = line
        else:
            current_article['snippet'] = current_article.get('snippet', '') + ' ' + line
    
    if current_article:
        articles.append(current_article)
    
    return articles


def format_news_results(articles: List[Dict[str, Any]]) -> str:
    """
    Format news articles into a readable string.
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        Formatted string
    """
    if not articles:
        return "No articles found."
    
    formatted = []
    for i, article in enumerate(articles, 1):
        formatted.append(
            f"{i}. {article.get('title', 'No title')}\n"
            f"   Source: {article.get('source', 'Unknown')}\n"
            f"   URL: {article.get('url', 'N/A')}\n"
            f"   Summary: {article.get('snippet', 'N/A')[:200]}..."
        )
    
    return "\n\n".join(formatted)
