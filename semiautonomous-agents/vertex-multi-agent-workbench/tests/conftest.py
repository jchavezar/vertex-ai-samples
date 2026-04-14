"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use uvloop if available for better async performance."""
    try:
        import uvloop
        return uvloop.EventLoopPolicy()
    except ImportError:
        import asyncio
        return asyncio.DefaultEventLoopPolicy()


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
