"""Domain models for blog generation.

These are the contract between the application and the agent. The agent is
*required* to return a `BlogDraft`; if it cannot, generation fails loudly.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, computed_field

# A 5-minute read at an average adult reading speed (~225 wpm) is ~1,125 words.
# We give the model a band to aim for rather than an exact number.
WORDS_PER_MINUTE = 225
TARGET_READ_MINUTES = 5
MIN_WORDS = 900
MAX_WORDS = 1300


class BlogTone(str, Enum):
    """Editorial voice the author can request."""

    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    STORYTELLING = "storytelling"


class BlogBrief(BaseModel):
    """What the author asks for. The only input the agent needs."""

    topic: str = Field(min_length=3, max_length=200)
    audience: str = Field(
        default="a general technical audience",
        max_length=200,
        description="Who the post is written for.",
    )
    tone: BlogTone = BlogTone.CONVERSATIONAL
    key_points: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Optional points the author wants covered.",
    )

    def to_prompt(self) -> str:
        """Render the brief as the user-turn prompt for the agent."""
        lines = [
            f"Topic: {self.topic}",
            f"Audience: {self.audience}",
            f"Tone: {self.tone.value}",
        ]
        if self.key_points:
            points = "\n".join(f"- {p}" for p in self.key_points)
            lines.append(f"Key points to cover:\n{points}")
        return "\n".join(lines)


class BlogDraft(BaseModel):
    """The validated output of a generation run."""

    title: str = Field(min_length=3, max_length=120)
    excerpt: str = Field(
        min_length=20,
        max_length=320,
        description="A one-to-two sentence hook shown in listings.",
    )
    body_markdown: str = Field(
        min_length=MIN_WORDS,  # cheap floor; real word check is computed below
        description="The full post body in GitHub-flavored Markdown.",
    )
    tags: list[str] = Field(default_factory=list, max_length=6)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def word_count(self) -> int:
        return len(self.body_markdown.split())

    @computed_field  # type: ignore[prop-decorator]
    @property
    def reading_time_minutes(self) -> int:
        return max(1, round(self.word_count / WORDS_PER_MINUTE))


class RevisionBrief(BaseModel):
    """What the author submits for the 'revise my own draft' flow.

    Unlike `BlogBrief` (a topic to write from scratch), this carries the
    author's own text plus any links they dropped in for extra context.
    """

    draft_text: str = Field(min_length=1, description="The author's own draft or notes.")
    links: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="URLs found in the draft text, to be researched for context.",
    )

    def to_prompt(self) -> str:
        """Render the brief as the user-turn prompt for the researcher/writer agents."""
        lines = [f"Author's draft:\n{self.draft_text}"]
        if self.links:
            links = "\n".join(f"- {link}" for link in self.links)
            lines.append(f"Links the author wants used as context:\n{links}")
        return "\n\n".join(lines)


class ResearchNotes(BaseModel):
    """Grounding context the researcher agent distills from linked sources."""

    summary: str = Field(
        min_length=1,
        description="Condensed synthesis of the linked sources, relevant to the author's draft.",
    )
    key_facts: list[str] = Field(
        default_factory=list,
        max_length=15,
        description="Discrete facts/points worth incorporating into the revision.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="URLs actually consulted (a subset of the links supplied, if some failed).",
    )

    def to_prompt(self) -> str:
        """Render the notes as context for the writer agent's revision prompt."""
        if not self.key_facts and not self.sources:
            return f"Research notes: {self.summary}"
        lines = [f"Research notes:\n{self.summary}"]
        if self.key_facts:
            facts = "\n".join(f"- {fact}" for fact in self.key_facts)
            lines.append(f"Key facts to consider:\n{facts}")
        if self.sources:
            lines.append("Sources consulted:\n" + "\n".join(f"- {src}" for src in self.sources))
        return "\n\n".join(lines)
