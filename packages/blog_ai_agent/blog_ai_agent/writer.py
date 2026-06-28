"""The Pydantic AI agent that writes blog posts via Azure AI Foundry.

`BlogWriter` wraps a single configured agent. It is constructed once (it holds
an HTTP client to Azure) and reused for every request.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.providers.azure import AzureProvider

try:  # pydantic-ai >= 0.0.x renamed OpenAIModel -> OpenAIChatModel
    from pydantic_ai.models.openai import OpenAIChatModel
except ImportError:  # pragma: no cover - older versions
    from pydantic_ai.models.openai import OpenAIModel as OpenAIChatModel

from blog_ai_agent.exceptions import BlogGenerationError
from blog_ai_agent.models import (
    MAX_WORDS,
    MIN_WORDS,
    TARGET_READ_MINUTES,
    BlogBrief,
    BlogDraft,
)

SYSTEM_PROMPT = f"""\
You are a senior editor who writes engaging, accurate blog posts.

Every post you write MUST:
- Be a {TARGET_READ_MINUTES}-minute read: between {MIN_WORDS} and {MAX_WORDS} words.
- Be valid GitHub-flavored Markdown with a clear structure: a short intro,
  2-4 `##` sections, and a brief conclusion. Do NOT include an H1 title in the
  body (the title is a separate field).
- Open with a hook, stay on topic, and respect the requested tone and audience.
- Be factual. Do not invent statistics, quotes, or sources.

Return your answer strictly in the required structured format.
"""


@dataclass(frozen=True)
class AzureConfig:
    """Connection details for an Azure AI Foundry deployment."""

    endpoint: str
    api_key: str
    deployment: str
    api_version: str = "2024-10-21"


class BlogWriter:
    """Generates validated `BlogDraft`s from a `BlogBrief`."""

    def __init__(self, config: AzureConfig) -> None:
        model = OpenAIChatModel(
            config.deployment,
            provider=AzureProvider(
                azure_endpoint=config.endpoint,
                api_version=config.api_version,
                api_key=config.api_key,
            ),
        )
        self._agent: Agent[None, BlogDraft] = Agent(
            model,
            output_type=BlogDraft,
            system_prompt=SYSTEM_PROMPT,
        )

    async def write(self, brief: BlogBrief) -> BlogDraft:
        """Run the agent. Raises `BlogGenerationError` on any failure."""
        try:
            result = await self._agent.run(brief.to_prompt())
        except Exception as exc:  # noqa: BLE001 - normalize SDK/model errors
            raise BlogGenerationError(str(exc)) from exc
        return result.output
