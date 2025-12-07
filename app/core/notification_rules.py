"""Rate limit rules configuration."""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class RateLimitRule:
    
    type: str
    max_count: int
    time_window_seconds: int
    
    def __post_init__(self):
        if self.max_count <= 0:
            raise ValueError(f"max_count must be positive, got {self.max_count}")
        
        if self.time_window_seconds <= 0:
            raise ValueError(
                f"time_window_seconds must be positive, got {self.time_window_seconds}"
            )


class RateLimitConfig:
    """Manages rate limit rules for different notification types."""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        # Status: 2 notifications per minute
        self.add_rule(RateLimitRule(
            type="status",
            max_count=2,
            time_window_seconds=60  # 1 minute
        ), overwrite=True)
        
        # News: 1 notification per day
        self.add_rule(RateLimitRule(
            type="news",
            max_count=1,
            time_window_seconds=86400  # 1 day (24 * 60 * 60)
        ), overwrite=True)
        
        # Marketing: 3 notifications per hour
        self.add_rule(RateLimitRule(
            type="marketing",
            max_count=3,
            time_window_seconds=3600  # 1 hour (60 * 60)
        ), overwrite=True)
    
    def get_rule(self, notification_type: str) -> Optional[RateLimitRule]:
        return self.rules.get(notification_type)
    
    def add_rule(self, rule: RateLimitRule, overwrite: bool = False) -> None:
        if rule.type in self.rules and not overwrite:
            raise ValueError(
                f"Rule for type '{rule.type}' already exists. "
                f"Set overwrite=True to replace it."
            )
        self.rules[rule.type] = rule
