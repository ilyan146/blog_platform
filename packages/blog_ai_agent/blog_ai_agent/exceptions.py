class BlogAIError(Exception):
    """Base class for all errors raised by this package."""


class BlogGenerationError(BlogAIError):
    """Raised when the model fails to produce a usable, valid draft."""


class BlogResearchError(BlogAIError):
    """Raised when the researcher agent fails to gather grounding context."""
