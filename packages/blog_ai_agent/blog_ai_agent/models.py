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
