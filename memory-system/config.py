"""
Configuration Management for Memory System
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


DEFAULT_CONFIG = {
    "version": "1.0",
    "database": {
        "path": "data/.memory.db",
        "backup_enabled": True,
        "backup_interval_days": 7,
        "backup_path": "backups/"
    },
    "paths": {
        "entries": "data/entries/",
        "projects": "data/projects/",
        "decisions": "data/decisions/",
        "logs": "data/logs/",
        "reports": "reports/",
        "templates": "templates/"
    },
    "output": {
        "color_enabled": True,
        "date_format": "%Y-%m-%d",
        "datetime_format": "%Y-%m-%d %H:%M",
        "default_view": "table"
    },
    "editor": {
        "default": "vim",
        "template_for_new_entries": "templates/entry_template.md"
    },
    "parsing": {
        "auto_extract_tasks": True,
        "auto_extract_decisions": True,
        "auto_extract_blockers": True,
        "require_approval": True,
        "nlp_backend": "regex"
    },
    "escalation": {
        "enabled": True,
        "levels": [
            {"level": 0, "name": "Identified", "auto_escalate_after_hours": 24},
            {"level": 1, "name": "Acknowledged", "auto_escalate_after_hours": 48},
            {"level": 2, "name": "Escalated", "auto_escalate_after_hours": 72},
            {"level": 3, "name": "Critical", "auto_escalate_after_hours": None}
        ]
    },
    "integrations": {
        "telegram": {
            "enabled": False,
            "bot_token": None
        },
        "openclaw": {
            "enabled": True,
            "auto_parse": True
        }
    }
}


class Config:
    """Configuration manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Load configuration."""
        self.config_path = config_path or self._find_config()
        self._config = self._load()
    
    def _find_config(self) -> str:
        """Find configuration file."""
        # Check for config in standard locations
        locations = [
            "memory-config.json",
            "config.json",
            os.path.expanduser("~/.memory/config.json"),
            "/etc/memory/config.json"
        ]
        
        for loc in locations:
            if Path(loc).exists():
                return loc
        
        # Default location
        return "memory-config.json"
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if Path(self.config_path).exists():
            with open(self.config_path) as f:
                user_config = json.load(f)
            # Merge with defaults
            return self._merge(DEFAULT_CONFIG, user_config)
        
        # Create default config
        import copy
        self.save(DEFAULT_CONFIG)
        return copy.deepcopy(DEFAULT_CONFIG)
    
    def _merge(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config with defaults."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self, config: Optional[Dict] = None) -> None:
        """Save configuration to file."""
        config = config or self._config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()
    
    @property
    def database_path(self) -> str:
        """Get database path."""
        return self.get('database.path', 'data/.memory.db')
    
    @property
    def entries_path(self) -> str:
        """Get entries directory path."""
        return self.get('paths.entries', 'data/entries/')
    
    @property
    def reports_path(self) -> str:
        """Get reports directory path."""
        return self.get('paths.reports', 'reports/')
    
    @property
    def color_enabled(self) -> bool:
        """Check if color output is enabled."""
        return self.get('output.color_enabled', True)
    
    def ensure_directories(self) -> None:
        """Ensure all configured directories exist."""
        paths = [
            self.get('paths.entries'),
            self.get('paths.projects'),
            self.get('paths.decisions'),
            self.get('paths.logs'),
            self.get('paths.reports'),
            self.get('database.backup_path'),
            self.get('paths.templates')
        ]
        
        for path in paths:
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)
