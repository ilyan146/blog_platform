"""Public API for the blog AI agent.

This package is framework-agnostic: it knows nothing about FastAPI, HTTP, or
databases. It takes a plain `BlogBrief` and returns a validated `BlogDraft`.
"""

from blog_ai_agent.exceptions import BlogAIError, BlogGenerationError, BlogResearchError
from blog_ai_agent.models import BlogBrief, BlogDraft, BlogTone, ResearchNotes, RevisionBrief
from blog_ai_agent.pipeline import revise_with_research
from blog_ai_agent.progress import ProgressEvent
from blog_ai_agent.researcher import BlogResearcher, PlaywrightMCPConfig
from blog_ai_agent.writer import AzureConfig, BlogWriter

__all__ = [
    "AzureConfig",
    "BlogAIError",
    "BlogBrief",
    "BlogDraft",
    "BlogGenerationError",
    "BlogResearcher",
    "BlogResearchError",
    "BlogTone",
    "BlogWriter",
    "PlaywrightMCPConfig",
    "ProgressEvent",
    "ResearchNotes",
    "RevisionBrief",
    "revise_with_research",
]
