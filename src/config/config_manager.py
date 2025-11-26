"""Configuration manager for the news aggregation system."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration from environment variables and YAML files."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the YAML configuration file. If None, looks for config.yaml
        """
        # Load environment variables
        load_dotenv()
        
        # Load YAML config if it exists
        self.config_data = {}
        if config_path is None:
            config_path = os.path.join(os.getcwd(), "config.yaml")
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-notation path.
        
        Environment variables take precedence over YAML config.
        
        Args:
            key_path: Dot-notation path (e.g., "deepseek.api_key")
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        # Check environment variable first (convert dot notation to UPPER_SNAKE_CASE)
        env_key = key_path.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Check YAML config
        keys = key_path.split('.')
        value = self.config_data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value if value is not None else default
    
    def validate_required(self) -> tuple[bool, list[str]]:
        """
        Validate that all required configuration values are present.
        
        Returns:
            Tuple of (is_valid, list of missing keys)
        """
        required_keys = [
            "deepseek.api_key",
            "email.from_address",
            "email.password",
        ]
        
        missing = []
        for key in required_keys:
            if not self.get(key):
                missing.append(key)
        
        return len(missing) == 0, missing
    
    @property
    def deepseek_api_key(self) -> str:
        """Get DeepSeek API key."""
        return self.get("deepseek.api_key", "")
    
    @property
    def deepseek_base_url(self) -> str:
        """Get DeepSeek base URL."""
        return self.get("deepseek.base_url", "https://api.deepseek.com/v1")
    
    @property
    def deepseek_model(self) -> str:
        """Get DeepSeek model name."""
        return self.get("deepseek.model", "deepseek-chat")
    
    @property
    def deepseek_temperature(self) -> float:
        """Get DeepSeek temperature."""
        return float(self.get("deepseek.temperature", 0.7))
    
    @property
    def deepseek_max_tokens(self) -> int:
        """Get DeepSeek max tokens."""
        return int(self.get("deepseek.max_tokens", 4000))
    
    @property
    def email_smtp_server(self) -> str:
        """Get email SMTP server."""
        return self.get("email.smtp_server", "smtp.gmail.com")
    
    @property
    def email_smtp_port(self) -> int:
        """Get email SMTP port."""
        return int(self.get("email.smtp_port", 587))
    
    @property
    def email_use_tls(self) -> bool:
        """Get email TLS setting."""
        use_tls = self.get("email.use_tls", True)
        if isinstance(use_tls, str):
            return use_tls.lower() in ('true', '1', 'yes')
        return bool(use_tls)
    
    @property
    def email_from(self) -> str:
        """Get email from address."""
        return self.get("email.from_address", "")
    
    @property
    def email_password(self) -> str:
        """Get email password."""
        return self.get("email.password", "")
    
    @property
    def search_default_tool(self) -> str:
        """Get default search tool."""
        return self.get("search.default_tool", "duckduckgo")
    
    @property
    def search_max_results(self) -> int:
        """Get max search results."""
        return int(self.get("search.max_results", 10))
    
    @property
    def search_depth(self) -> int:
        """Get search depth."""
        return int(self.get("search.search_depth", 3))
    
    @property
    def scheduler_default_interval(self) -> int:
        """Get default scheduler interval in hours."""
        return int(self.get("scheduler.default_interval_hours", 6))
    
    @property
    def scheduler_timezone(self) -> str:
        """Get scheduler timezone."""
        return self.get("scheduler.timezone", "America/New_York")
    
    @property
    def scheduler_max_history_days(self) -> int:
        """Get max history days."""
        return int(self.get("scheduler.max_history_days", 30))
    
    @property
    def log_level(self) -> str:
        """Get log level."""
        return self.get("app.log_level", "INFO")
    
    @property
    def data_dir(self) -> Path:
        """Get data directory path."""
        path = Path(self.get("app.data_dir", "./data"))
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory path."""
        path = Path(self.get("app.logs_dir", "./logs"))
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def database_path(self) -> Path:
        """Get database file path."""
        return Path(self.get("app.database_path", "./data/news_aggregator.db"))
