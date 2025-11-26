"""News aggregation agent using LangChain and DeepSeek."""

import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI

from .tools import create_search_tool, create_content_extractor_tool
from .memory import NewsMemory
from .chains import ResearchChain

logger = logging.getLogger(__name__)


class NewsAgent:
    """LangChain agent for news aggregation and analysis."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.7,
        search_tool: str = "duckduckgo",
        max_results: int = 10,
        max_iterations: int = 3
    ):
        """
        Initialize the news agent.
        """
        # Initialize LLM with DeepSeek
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature
        )
        
        # Initialize components
        self.search_tool = create_search_tool(search_tool, max_results)
        self.content_tool = create_content_extractor_tool()
        self.memory = NewsMemory()
        self.chain = ResearchChain(self.llm)
        
        self.max_iterations = max_iterations
        
        logger.info(f"NewsAgent initialized with {search_tool} search tool")
    
    def search_news(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Search for news based on the given prompt, using context from memory.
        """
        logger.info(f"Searching for news: {prompt}")
        
        try:
            # 1. Get context from memory
            context = self.memory.get_context(prompt)
            
            # 2. Generate refined search query
            search_query = self.chain.generate_search_query(prompt, context)
            
            # 3. Execute search
            search_results = self.search_tool.func(search_query)
            
            # 4. Parse results
            articles = self._parse_search_results(search_results, prompt)
            
            logger.info(f"Found {len(articles)} articles using query: {search_query}")
            return articles
            
        except Exception as e:
            logger.error(f"Error in news search: {e}")
            return [{
                'title': 'Error in Search',
                'snippet': f'Unable to retrieve news: {str(e)}',
                'url': 'N/A',
                'source': 'Error'
            }]
            
    def analyze_results(self, prompt: str, articles: List[Dict[str, Any]]) -> str:
        """
        Analyze results using the research chain and save to memory.
        """
        # Get context again (or pass it through, but fetching is cheap)
        context = self.memory.get_context(prompt)
        
        # Analyze
        analysis = self.chain.analyze_results(prompt, articles, context)
        
        # Save to memory
        self.memory.add_report(prompt, analysis)
        
        return analysis
    
    def _parse_search_results(self, results: str, prompt: str) -> List[Dict[str, Any]]:
        """
        Parse search results into structured article format.
        
        Args:
            results: Raw search results string
            prompt: Original search prompt
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        # DuckDuckGo returns results in a specific format
        # Split by common delimiters and try to extract articles
        if not results or len(results.strip()) == 0:
            return [{
                'title': 'No Results',
                'snippet': f'No news found for: {prompt}',
                'url': 'N/A',
                'source': 'Search'
            }]
        
        # Simple parsing - try to extract multiple results
        # Results are typically separated by newlines or specific markers
        lines = results.split('\n')
        current_article = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_article and 'title' in current_article:
                    articles.append(current_article)
                    current_article = {}
                continue
            
            # Check if line contains URL
            if 'http' in line.lower():
                # Extract URL
                url_start = line.find('http')
                url_end = line.find(' ', url_start)
                if url_end == -1:
                    url_end = len(line)
                url = line[url_start:url_end].strip()
                
                if current_article and 'title' in current_article:
                    articles.append(current_article)
                
                current_article = {
                    'url': url,
                    'source': 'Web',
                    'title': line[:url_start].strip() if url_start > 0 else 'News Article',
                }
            elif 'title' not in current_article:
                # First non-URL line is likely title
                current_article['title'] = line
            else:
                # Subsequent lines are snippet
                if 'snippet' not in current_article:
                    current_article['snippet'] = line
                else:
                    current_article['snippet'] += ' ' + line
        
        # Add last article if any
        if current_article and 'title' in current_article:
            articles.append(current_article)
        
        # Ensure all articles have required fields
        for article in articles:
            if 'url' not in article:
                article['url'] = 'N/A'
            if 'source' not in article:
                article['source'] = 'Web'
            if 'snippet' not in article:
                article['snippet'] = article.get('title', '')[:200]
            if 'title' not in article:
                article['title'] = 'Untitled Article'
        
        # If no articles were parsed, create one from the raw results
        if not articles:
            articles = [{
                'title': f'News about: {prompt}',
                'snippet': results[:500] if len(results) > 500 else results,
                'url': 'N/A',
                'source': 'Search Results'
            }]
        
        return articles[:10]  # Limit to 10 articles

