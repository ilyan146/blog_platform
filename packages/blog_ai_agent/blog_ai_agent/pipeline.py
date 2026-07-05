"""Two-stage revision pipeline: research the author's links, then rewrite.

Kept separate from `BlogResearcher`/`BlogWriter` so each agent stays focused
and independently testable, while callers (the backend) get one call that
does the full "revise my draft" flow.
"""

from __future__ import annotations

from blog_ai_agent.models import BlogDraft, RevisionBrief
from blog_ai_agent.progress import OnProgress
from blog_ai_agent.researcher import BlogResearcher
from blog_ai_agent.writer import BlogWriter


async def revise_with_research(
    researcher: BlogResearcher,
    writer: BlogWriter,
    brief: RevisionBrief,
    *,
    on_progress: OnProgress | None = None,
) -> BlogDraft:
    """Research `brief.links`, then revise `brief.draft_text` using what was found."""
    notes = await researcher.research(brief, on_progress=on_progress)
    return await writer.revise(brief, notes, on_progress=on_progress)
