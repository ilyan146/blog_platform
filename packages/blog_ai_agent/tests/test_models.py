from blog_ai_agent.models import BlogBrief, BlogDraft, BlogTone


def test_brief_renders_prompt_with_key_points() -> None:
    brief = BlogBrief(
        topic="Async Python",
        audience="backend engineers",
        tone=BlogTone.TECHNICAL,
        key_points=["event loop", "asyncio.gather"],
    )
    prompt = brief.to_prompt()
    assert "Topic: Async Python" in prompt
    assert "Tone: technical" in prompt
    assert "- event loop" in prompt


def test_draft_computes_reading_time() -> None:
    body = " ".join(["word"] * 1125)  # ~5 min at 225 wpm
    draft = BlogDraft(
        title="A Test Post",
        excerpt="A short hook that is long enough to satisfy validation.",
        body_markdown=body,
        tags=["python"],
    )
    assert draft.word_count == 1125
    assert draft.reading_time_minutes == 5
