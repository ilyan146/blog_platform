"""The Pydantic AI agent that researches an author's linked sources.

`BlogResearcher` wraps an agent with a Playwright MCP server as its toolset,
so it can navigate to author-supplied links and read their content. It
distills what it finds into `ResearchNotes` for `BlogWriter.revise()` to use
as grounding context. If no links are supplied, it skips the agent run
entirely and returns empty notes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset
from fastmcp.client.transports import StdioTransport

from blog_ai_agent.exceptions import BlogResearchError
from blog_ai_agent.models import ResearchNotes, RevisionBrief
from blog_ai_agent.progress import OnProgress, wrap_progress_handler
from blog_ai_agent.writer import AzureConfig, build_azure_model

RESEARCH_SYSTEM_PROMPT = """\
You are a research assistant preparing grounding context for an editor who
will revise an author's blog draft.

You have browser tools available. For each link the author supplied:
- Navigate to it and read its content.
- Extract only facts and points relevant to the author's draft topic.
- Do not visit any link that isn't in the supplied list, and do not follow
  further links found on a page.

If a link fails to load or is irrelevant, skip it and note that it was
skipped rather than failing the whole task.

Return your findings strictly in the required structured format: a short
summary, a list of discrete key facts, and the list of source URLs you
actually managed to consult.
"""


@dataclass(frozen=True)
class PlaywrightMCPConfig:
    """How to launch the Playwright MCP server as a subprocess."""

    command: str = "npx"
    args: tuple[str, ...] = field(
        default_factory=lambda: ("-y", "@playwright/mcp@latest", "--headless", "--isolated")
    )


class BlogResearcher:
    """Gathers `ResearchNotes` from the links in a `RevisionBrief`."""

    def __init__(self, config: AzureConfig, mcp_config: PlaywrightMCPConfig | None = None) -> None:
        model = build_azure_model(config)
        mcp_config = mcp_config or PlaywrightMCPConfig()
        toolset = MCPToolset(StdioTransport(command=mcp_config.command, args=list(mcp_config.args)))
        self._agent: Agent[None, ResearchNotes] = Agent(
            model,
            output_type=ResearchNotes,
            system_prompt=RESEARCH_SYSTEM_PROMPT,
            toolsets=[toolset],
        )

    async def research(
        self, brief: RevisionBrief, *, on_progress: OnProgress | None = None
    ) -> ResearchNotes:
        """Run the agent. Raises `BlogResearchError` on any failure.

        Skips the agent run (and returns empty notes) if the brief has no
        links \u2014 there's nothing to research.
        """
        if not brief.links:
            return ResearchNotes(summary="No links were supplied; revising from the author's draft alone.")
        try:
            result = await self._agent.run(
                brief.to_prompt(), event_stream_handler=wrap_progress_handler(on_progress)
            )
        except Exception as exc:  # noqa: BLE001 - normalize SDK/MCP errors
            raise BlogResearchError(str(exc)) from exc
        return result.output
