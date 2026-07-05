"""Translates pydantic-ai's internal run events into a small, stable shape.

Callers (the backend's SSE endpoint) get a plain `ProgressEvent` per tool
call/result — e.g. "opening https://example.com" — without needing to import
or understand pydantic-ai's message/event types directly.
"""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable, Callable
from typing import Any

from pydantic import BaseModel
from pydantic_ai import RunContext, messages as _messages


class ProgressEvent(BaseModel):
    """A single step of agent progress, safe to serialize straight to a client."""

    type: str  # "tool_call" | "tool_result"
    tool: str
    detail: str | None = None


# Common Playwright MCP tool argument keys worth surfacing to the user.
_DETAIL_ARG_KEYS = ("url", "selector", "text")


def describe_event(event: Any) -> ProgressEvent | None:
    """Map one pydantic-ai run event to a `ProgressEvent`, or `None` to skip it."""
    if isinstance(event, _messages.FunctionToolCallEvent):
        return ProgressEvent(
            type="tool_call",
            tool=event.part.tool_name,
            detail=_summarize_args(event.part.args),
        )
    if isinstance(event, _messages.FunctionToolResultEvent):
        tool = getattr(event.part, "tool_name", "tool")
        return ProgressEvent(type="tool_result", tool=tool)
    return None


def _summarize_args(args: Any) -> str | None:
    if isinstance(args, dict):
        for key in _DETAIL_ARG_KEYS:
            if key in args:
                return str(args[key])
    return None


OnProgress = Callable[[ProgressEvent], Awaitable[None]]


def wrap_progress_handler(on_progress: OnProgress | None):
    """Build a pydantic-ai `event_stream_handler` that forwards mapped events.

    Returns `None` (i.e. no streaming overhead) if `on_progress` is `None`.
    """
    if on_progress is None:
        return None

    async def handler(_ctx: RunContext[Any], events: AsyncIterable[Any]) -> None:
        async for event in events:
            progress = describe_event(event)
            if progress is not None:
                await on_progress(progress)

    return handler
