"""Pydantic models for structured fact output in JSON mode."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SourceModel(BaseModel):
    """Metadata about a source article used in structured output."""

    id: str = Field(..., description="Stable identifier for the source (e.g. source_1)")
    title: str
    url: str
    last_modified: str
    word_count: int


class FactModel(BaseModel):
    """A single fact extracted from sources, used in structured output."""

    fact: str
    source_ids: List[str]
    category: Literal["definition", "history", "application", "technical", "other"]


class FactOutput(BaseModel):
    """
    Final structured output for JSON mode.

    The JSON must include:

    {
        "query": str,
        "sources": [SourceModel, ...],
        "facts": [FactModel, ...],
        "summary": str
    }
    """

    query: str
    sources: List[SourceModel]
    facts: List[FactModel]
    summary: Optional[str] = None


