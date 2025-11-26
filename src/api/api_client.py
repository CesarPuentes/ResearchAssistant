"""DeepSeek API client implementation."""

import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Client for interacting with DeepSeek API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        Initialize DeepSeek API client.
        
        Args:
            api_key: DeepSeek API key
            base_url: Base URL for DeepSeek API
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize OpenAI client with DeepSeek endpoint
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        logger.info(f"DeepSeek client initialized with model: {model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send a chat completion request to DeepSeek.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Response content as string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Received response from DeepSeek: {content[:100]}...")
            return content
            
        except Exception as e:
            logger.error(f"Error in DeepSeek API call: {e}")
            raise
    
    def analyze_news(self, news_data: List[Dict[str, Any]]) -> str:
        """
        Analyze and summarize news articles using DeepSeek.
        
        Args:
            news_data: List of news article dictionaries
            
        Returns:
            Analyzed and summarized news report
        """
        # Format news data for analysis
        news_text = "\n\n".join([
            f"Title: {article.get('title', 'N/A')}\n"
            f"Source: {article.get('source', 'N/A')}\n"
            f"URL: {article.get('url', 'N/A')}\n"
            f"Snippet: {article.get('snippet', 'N/A')}"
            for article in news_data
        ])
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional news analyst. Your task is to analyze news articles "
                    "and create a comprehensive, well-structured report. Focus on key insights, "
                    "trends, and important developments. Organize the information logically and "
                    "highlight the most significant points."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Please analyze the following news articles and create a comprehensive report:\n\n"
                    f"{news_text}\n\n"
                    f"Provide a structured summary with:\n"
                    f"1. Executive Summary\n"
                    f"2. Key Developments\n"
                    f"3. Detailed Analysis\n"
                    f"4. Sources and References"
                )
            }
        ]
        
        return self.chat_completion(messages)
    
    def create_aggregate_summary(self, reports: List[str]) -> str:
        """
        Create an aggregate summary from multiple reports.
        
        Args:
            reports: List of previous report texts
            
        Returns:
            Aggregate summary
        """
        combined_reports = "\n\n---\n\n".join([
            f"Report {i+1}:\n{report}"
            for i, report in enumerate(reports)
        ])
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional news analyst creating an aggregate report. "
                    "Your task is to synthesize multiple news reports into a comprehensive "
                    "overview, identifying trends, recurring themes, and the overall narrative "
                    "across the time period covered."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Please create an aggregate summary from these multiple reports:\n\n"
                    f"{combined_reports}\n\n"
                    f"Provide:\n"
                    f"1. Overview of the time period covered\n"
                    f"2. Major trends and developments\n"
                    f"3. Key insights across all reports\n"
                    f"4. Conclusion and outlook"
                )
            }
        ]
        
        return self.chat_completion(messages)
