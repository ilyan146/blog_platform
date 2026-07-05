"""The 'revise my own draft' flow: research author-supplied links, then
rewrite into a 5-minute read. Streamed over SSE; nothing is persisted here
\u2014 the client explicitly saves the result via POST /api/drafts/from-revision.
"""

import asyncio
import json
import re
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from blog_ai_agent import (
    BlogAIError,
    BlogResearcher,
    BlogWriter,
    ProgressEvent,
    RevisionBrief,
    revise_with_research,
)

from app.ai import get_researcher, get_writer
from app.dependencies import CurrentUser
from app.models.schemas import RevisionRequest

router = APIRouter(prefix="/api/revisions", tags=["revisions"])

Researcher = Annotated[BlogResearcher, Depends(get_researcher)]
Writer = Annotated[BlogWriter, Depends(get_writer)]

# Links are simply pasted inline in the author's text, not a separate field.
_URL_RE = re.compile(r"https?://\S+")


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/stream")
async def stream_revision(
    body: RevisionRequest, user: CurrentUser, researcher: Researcher, writer: Writer
):
    brief = RevisionBrief(draft_text=body.draft_text, links=_URL_RE.findall(body.draft_text)[:10])

    async def event_source():
        queue: asyncio.Queue[dict | None] = asyncio.Queue()

        async def on_progress(event: ProgressEvent) -> None:
            await queue.put(event.model_dump())

        async def run() -> None:
            try:
                draft = await revise_with_research(researcher, writer, brief, on_progress=on_progress)
                await queue.put({"type": "done", **draft.model_dump()})
            except BlogAIError as exc:
                await queue.put({"type": "error", "message": str(exc)})
            finally:
                await queue.put(None)  # sentinel: stop the stream

        task = asyncio.create_task(run())
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield _sse(item)
        finally:
            task.cancel()

    return StreamingResponse(event_source(), media_type="text/event-stream")
