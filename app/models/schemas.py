"""
Pydantic models for request validation and response serialization.

Strict schemas ensure that malformed payloads are rejected at the API
boundary, long before any business logic runs.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class TextAnalysisRequest(BaseModel):
    """Incoming payload for the ``POST /api/v1/analyze-text`` endpoint."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=1_000_000,
        description="Raw text to analyse. Must be between 1 and 1 000 000 characters.",
    )
    top_n: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of most-frequent words to return (after stop-word removal).",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The quick brown fox jumps over the lazy dog. The dog barked back.",
                "top_n": 5,
            }
        }


# ---------------------------------------------------------------------------
# Response sub-models
# ---------------------------------------------------------------------------

class WordFrequency(BaseModel):
    """A single word and its occurrence count."""

    word: str
    count: int


class TextMetrics(BaseModel):
    """Basic quantitative metrics about the input text."""

    character_count: int = Field(..., description="Total number of characters (including spaces).")
    word_count: int = Field(..., description="Total number of whitespace-delimited tokens.")
    sentence_count: int = Field(..., description="Estimated sentence count (split on .!?).")
    average_word_length: float = Field(..., description="Mean character length of all tokens.")


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class TextAnalysisResponse(BaseModel):
    """Full analysis result returned by the service layer."""

    metrics: TextMetrics
    top_words: list[WordFrequency] = Field(
        ...,
        description="Top-N most frequent words (stop words excluded), ordered by count descending.",
    )
    word_frequencies: dict[str, int] = Field(
        ...,
        description="Complete word → count mapping (stop words excluded).",
    )
