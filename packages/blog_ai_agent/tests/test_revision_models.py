from blog_ai_agent.models import ResearchNotes, RevisionBrief


def test_revision_brief_renders_prompt_with_links() -> None:
    brief = RevisionBrief(
        draft_text="My draft about async Python.",
        links=["https://example.com/asyncio"],
    )
    prompt = brief.to_prompt()
    assert "My draft about async Python." in prompt
    assert "https://example.com/asyncio" in prompt


def test_revision_brief_renders_prompt_without_links() -> None:
    brief = RevisionBrief(draft_text="Just my own notes.")
    prompt = brief.to_prompt()
    assert prompt == "Author's draft:\nJust my own notes."


def test_research_notes_render_prompt_with_facts_and_sources() -> None:
    notes = ResearchNotes(
        summary="Asyncio has matured a lot since 3.11.",
        key_facts=["TaskGroups landed in 3.11"],
        sources=["https://example.com/asyncio"],
    )
    prompt = notes.to_prompt()
    assert "Asyncio has matured a lot since 3.11." in prompt
    assert "- TaskGroups landed in 3.11" in prompt
    assert "https://example.com/asyncio" in prompt


def test_research_notes_render_minimal_prompt() -> None:
    notes = ResearchNotes(summary="No links were supplied.")
    assert notes.to_prompt() == "Research notes: No links were supplied."
