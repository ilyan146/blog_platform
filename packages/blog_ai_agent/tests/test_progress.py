from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ToolCallPart,
    ToolReturnPart,
)

from blog_ai_agent.progress import describe_event


def test_describe_tool_call_event_surfaces_url_arg() -> None:
    event = FunctionToolCallEvent(
        part=ToolCallPart(tool_name="browser_navigate", args={"url": "https://example.com"})
    )
    progress = describe_event(event)
    assert progress is not None
    assert progress.type == "tool_call"
    assert progress.tool == "browser_navigate"
    assert progress.detail == "https://example.com"


def test_describe_tool_call_event_without_known_arg_has_no_detail() -> None:
    event = FunctionToolCallEvent(part=ToolCallPart(tool_name="some_tool", args={"count": 3}))
    progress = describe_event(event)
    assert progress is not None
    assert progress.detail is None


def test_describe_tool_result_event() -> None:
    event = FunctionToolResultEvent(
        part=ToolReturnPart(tool_name="browser_navigate", content="page loaded")
    )
    progress = describe_event(event)
    assert progress is not None
    assert progress.type == "tool_result"
    assert progress.tool == "browser_navigate"


def test_describe_event_ignores_unrelated_events() -> None:
    assert describe_event(object()) is None
