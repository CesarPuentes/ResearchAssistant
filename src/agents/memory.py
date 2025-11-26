"""Memory management for the news agent."""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class NewsMemory:
    """
    Manages long-term memory for the news agent.
    Persists report summaries to a JSON file to provide context for future runs.
    """
    
    def __init__(self, memory_file: str = "data/memory.json", max_entries: int = 10):
        """
        Initialize memory manager.
        
        Args:
            memory_file: Path to the JSON memory file
            max_entries: Maximum number of past reports to keep
        """
        self.memory_file = Path(memory_file)
        self.max_entries = max_entries
        self.memory_data = self._load_memory()
        
        # Ensure directory exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _load_memory(self) -> List[Dict[str, Any]]:
        """Load memory from file."""
        if not self.memory_file.exists():
            return []
            
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            return []
            
    def save_memory(self):
        """Save memory to file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            
    def add_report(self, prompt: str, summary: str, timestamp: Optional[str] = None):
        """
        Add a new report summary to memory.
        
        Args:
            prompt: The search prompt used
            summary: The generated summary/analysis
            timestamp: ISO format timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        entry = {
            "timestamp": timestamp,
            "prompt": prompt,
            "summary": summary
        }
        
        # Add to beginning of list
        self.memory_data.insert(0, entry)
        
        # Trim to max entries
        if len(self.memory_data) > self.max_entries:
            self.memory_data = self.memory_data[:self.max_entries]
            
        self.save_memory()
        
    def get_context(self, prompt: str, limit: int = 3) -> str:
        """
        Get relevant context from past reports.
        
        Args:
            prompt: Current search prompt (to filter relevant memory)
            limit: Max number of past entries to return
            
        Returns:
            String containing context from previous runs
        """
        # Simple filtering: if the prompt is similar or if we just want recent context
        # For now, we'll return the most recent entries regardless of prompt
        # to establish a timeline of what the user has seen.
        
        if not self.memory_data:
            return "No previous reports found."
            
        context_parts = []
        for i, entry in enumerate(self.memory_data[:limit]):
            context_parts.append(
                f"--- Report from {entry['timestamp']} ---\n"
                f"Topic: {entry['prompt']}\n"
                f"Summary: {entry['summary'][:500]}..." # Truncate for context window
            )
            
        return "\n\n".join(context_parts)
