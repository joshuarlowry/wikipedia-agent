"""Pydantic models for structured fact output in JSON mode."""

from enum import Enum
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


class EntityType(str, Enum):
    person = "person"
    place = "place"
    event = "event"
    idea = "idea"


class EntityModel(BaseModel):
    """Catalog of discovered people, places, events, or ideas."""

    id: str
    name: str
    description: str
    type: EntityType
    source_ids: List[str]


class RelationModel(BaseModel):
    """Relationships between cataloged entities."""

    from_entity: str
    to_entity: str
    description: str
    date: Optional[str] = None
    source_ids: List[str]


class IterationModel(BaseModel):
    """Iterative search results for a given query."""

    query: str
    summary: str
    sources: List[SourceModel]


class FactOutput(BaseModel):
    """
    Final structured output for JSON mode.

    The JSON must include:

        {
            "query": str,
            "sources": [SourceModel, ...],
            "facts": [FactModel, ...],
            "people": [EntityModel, ...],
            "places": [EntityModel, ...],
            "events": [EntityModel, ...],
            "ideas": [EntityModel, ...],
            "relations": [RelationModel, ...],
            "iterations": [IterationModel, ...],
            "summary": str
        }
    """

    query: str
    sources: List[SourceModel]
    facts: List[FactModel]
    people: List[EntityModel] = Field(default_factory=list)
    places: List[EntityModel] = Field(default_factory=list)
    events: List[EntityModel] = Field(default_factory=list)
    ideas: List[EntityModel] = Field(default_factory=list)
    relations: List[RelationModel] = Field(default_factory=list)
    iterations: List[IterationModel] = Field(default_factory=list)
    summary: Optional[str] = None


