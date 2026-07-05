"""Constructs the singleton `BlogWriter`/`BlogResearcher` from settings and
exposes them as FastAPI dependencies.

Both hold long-lived clients (Azure HTTP client, MCP subprocess), so they're
built once at import time and reused across requests.
"""

from blog_ai_agent import BlogResearcher, BlogWriter, PlaywrightMCPConfig
from blog_ai_agent.writer import AzureConfig

from app.config import settings

_azure_config = AzureConfig(
    endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    deployment=settings.azure_openai_deployment,
    api_version=settings.azure_openai_api_version,
)

_writer = BlogWriter(_azure_config)
_researcher = BlogResearcher(
    _azure_config,
    PlaywrightMCPConfig(
        command=settings.playwright_mcp_command,
        args=tuple(settings.playwright_mcp_args),
    ),
)


def get_writer() -> BlogWriter:
    """FastAPI dependency: the shared blog writer."""
    return _writer


def get_researcher() -> BlogResearcher:
    """FastAPI dependency: the shared blog researcher (used by the revise flow)."""
    return _researcher
