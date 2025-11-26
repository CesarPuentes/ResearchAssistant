"""Research chains for the news agent."""

import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class ResearchChain:
    """
    Orchestrates the research process using a chain of reasoning.
    1. Strategize: Generate optimal search queries.
    2. Filter: Select relevant articles (implicit in search/analysis).
    3. Analyze: Synthesize findings with context.
    """
    
    def __init__(self, llm: ChatOpenAI):
        """
        Initialize the research chain.
        
        Args:
            llm: Configured ChatOpenAI instance
        """
        self.llm = llm
        
    def generate_search_query(self, prompt: str, context: str) -> str:
        """
        Generate a refined search query based on prompt and context.
        """
        messages = [
            SystemMessage(content=(
                "You are a research strategist. Your goal is to create the most effective "
                "web search query to find new information about a topic.\n"
                "Consider the user's prompt and the context of what we already know.\n"
                "Return ONLY the search query string, nothing else."
            )),
            HumanMessage(content=(
                f"User Prompt: {prompt}\n\n"
                f"Context (Previous Reports):\n{context}\n\n"
                "Generate a search query to find the latest updates or missing details."
            ))
        ]
        
        try:
            response = self.llm.invoke(messages)
            query = response.content.strip().replace('"', '')
            logger.info(f"Generated search query: {query}")
            return query
        except Exception as e:
            logger.error(f"Error generating search query: {e}")
            return prompt  # Fallback to original prompt
            
    def analyze_results(self, prompt: str, articles: List[Dict[str, Any]], context: str) -> str:
        """
        Analyze search results and generate a report, considering context.
        """
        # Format articles for the LLM
        articles_text = "\n\n".join([
            f"Title: {a.get('title', 'N/A')}\n"
            f"Source: {a.get('source', 'N/A')}\n"
            f"URL: {a.get('url', 'N/A')}\n"
            f"Content: {a.get('snippet', 'N/A')}"
            for a in articles
        ])
        
        messages = [
            SystemMessage(content=(
                "You are a professional news analyst. Your task is to write a comprehensive update report.\n"
                "1. Focus on NEW information found in the articles.\n"
                "2. Reference the 'Previous Context' to show continuity or changes.\n"
                "3. If the new articles just repeat the context, state that there are no significant updates.\n"
                "4. Cite sources (titles/publications) in your analysis."
            )),
            HumanMessage(content=(
                f"Topic: {prompt}\n\n"
                f"Previous Context:\n{context}\n\n"
                f"New Search Results:\n{articles_text}\n\n"
                "Write the analysis report:"
            ))
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error analyzing results: {e}")
            return "Error generating analysis."
