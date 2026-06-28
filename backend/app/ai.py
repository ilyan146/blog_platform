"""Constructs the singleton `BlogWriter` from settings and exposes it as a dep.

The writer holds an HTTP client to Azure, so we build it once at import time
and reuse it across requests.
"""

from blog_ai_agent import BlogWriter
from blog_ai_agent.writer import AzureConfig

from app.config import settings

_writer = BlogWriter(
    AzureConfig(
        endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        deployment=settings.azure_openai_deployment,
        api_version=settings.azure_openai_api_version,
    )
)


def get_writer() -> BlogWriter:
    """FastAPI dependency: the shared blog writer."""
    return _writer
