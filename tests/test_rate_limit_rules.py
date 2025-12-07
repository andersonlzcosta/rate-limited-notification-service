"""Tests for rate limit rules configuration."""
import pytest
from app.core.notification_rules import RateLimitRule, RateLimitConfig


def test_rate_limit_rule_creation():
    """Test that a RateLimitRule can be created with valid parameters."""
    rule = RateLimitRule(
        type="news",
        max_count=1,
        time_window_seconds=86400  # 1 day
    )
    
    assert rule.type == "news"
    assert rule.max_count == 1
    assert rule.time_window_seconds == 86400


def test_rate_limit_rule_validation():
    """Test that RateLimitRule validates input parameters."""
    # Test that max_count must be positive
    with pytest.raises(ValueError):
        RateLimitRule(
            type="news",
            max_count=0,
            time_window_seconds=86400
        )
    
    # Test that max_count cannot be negative
    with pytest.raises(ValueError):
        RateLimitRule(
            type="news",
            max_count=-1,
            time_window_seconds=86400
        )
    
    # Test that time_window_seconds must be positive
    with pytest.raises(ValueError):
        RateLimitRule(
            type="news",
            max_count=1,
            time_window_seconds=0
        )
    
    # Test that time_window_seconds cannot be negative
    with pytest.raises(ValueError):
        RateLimitRule(
            type="news",
            max_count=1,
            time_window_seconds=-1
        )


def test_rate_limit_config_initialization():
    """Test that RateLimitConfig can be initialized with default rules."""
    config = RateLimitConfig()
    
    # Should have default rules
    assert len(config.rules) > 0


def test_rate_limit_config_default_rules():
    """Test that RateLimitConfig has the correct default rules."""
    config = RateLimitConfig()
    
    # Check Status rule: 2 per minute
    status_rule = config.get_rule("status")
    assert status_rule is not None
    assert status_rule.type == "status"
    assert status_rule.max_count == 2
    assert status_rule.time_window_seconds == 60  # 1 minute
    
    # Check News rule: 1 per day
    news_rule = config.get_rule("news")
    assert news_rule is not None
    assert news_rule.type == "news"
    assert news_rule.max_count == 1
    assert news_rule.time_window_seconds == 86400  # 1 day
    
    # Check Marketing rule: 3 per hour
    marketing_rule = config.get_rule("marketing")
    assert marketing_rule is not None
    assert marketing_rule.type == "marketing"
    assert marketing_rule.max_count == 3
    assert marketing_rule.time_window_seconds == 3600  # 1 hour


def test_rate_limit_config_get_rule():
    """Test that get_rule returns the correct rule for a given type."""
    config = RateLimitConfig()
    
    rule = config.get_rule("status")
    assert rule is not None
    assert rule.type == "status"
    
    # Test with non-existent rule
    rule = config.get_rule("nonexistent")
    assert rule is None


def test_rate_limit_config_add_rule():
    """Test that new rules can be added to the configuration."""
    config = RateLimitConfig()
    
    new_rule = RateLimitRule(
        type="custom",
        max_count=5,
        time_window_seconds=300  # 5 minutes
    )
    
    config.add_rule(new_rule)
    
    retrieved_rule = config.get_rule("custom")
    assert retrieved_rule is not None
    assert retrieved_rule.type == "custom"
    assert retrieved_rule.max_count == 5
    assert retrieved_rule.time_window_seconds == 300


def test_rate_limit_config_add_rule_overwrites_existing():
    """Test that adding a rule with existing type can overwrite when explicitly allowed."""
    config = RateLimitConfig()
    
    # Get original rule
    original_rule = config.get_rule("status")
    assert original_rule.max_count == 2
    
    # Try to add without overwrite - should fail
    new_rule = RateLimitRule(
        type="status",
        max_count=10,
        time_window_seconds=60
    )
    
    with pytest.raises(ValueError, match="already exists"):
        config.add_rule(new_rule, overwrite=False)
    
    # Now add with overwrite=True - should succeed
    config.add_rule(new_rule, overwrite=True)
    
    # Verify it was overwritten
    updated_rule = config.get_rule("status")
    assert updated_rule.max_count == 10


def test_rate_limit_config_add_rule_prevents_accidental_overwrite():
    """Test that add_rule prevents accidental overwrites by default."""
    config = RateLimitConfig()
    
    # Try to add a rule that already exists without overwrite flag
    duplicate_rule = RateLimitRule(
        type="news",  # This already exists
        max_count=5,
        time_window_seconds=300
    )
    
    with pytest.raises(ValueError, match="already exists"):
        config.add_rule(duplicate_rule)  # overwrite defaults to False
