class BlogAIError(Exception):
    """Base class for all errors raised by this package."""


class BlogGenerationError(BlogAIError):
    """Raised when the model fails to produce a usable, valid draft."""
