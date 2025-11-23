"""Fact accumulator for JSON mode - stores facts as LLM discovers them."""

import json
from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class Fact:
    """A single fact extracted from sources."""
    fact: str
    source_ids: List[str]
    category: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return asdict(self)


@dataclass
class Source:
    """Metadata about a source article."""
    id: str
    title: str
    url: str
    last_modified: str
    word_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return asdict(self)


class FactAccumulator:
    """
    Accumulates facts as the LLM discovers them.
    
    The LLM calls record_fact() as it reads through documents,
    and we track all the facts. At the end, we programmatically
    generate the JSON output.
    """
    
    def __init__(self, query: str = ""):
        """Initialize the fact accumulator."""
        self.query = query
        self.facts: List[Fact] = []
        self.sources: List[Source] = []
        self._source_ids_seen = set()
    
    def add_source(self, source_id: str, title: str, url: str, 
                   last_modified: str, word_count: int) -> None:
        """Add a source to the accumulator."""
        if source_id not in self._source_ids_seen:
            self.sources.append(Source(
                id=source_id,
                title=title,
                url=url,
                last_modified=last_modified,
                word_count=word_count
            ))
            self._source_ids_seen.add(source_id)
    
    def record_fact(self, fact: str, source_ids: List[str], category: str) -> str:
        """
        Record a fact discovered by the LLM.
        
        Args:
            fact: The fact or insight discovered
            source_ids: List of source IDs supporting this fact
            category: Category of the fact (definition, history, application, technical, other)
        
        Returns:
            Confirmation message for the LLM
        """
        # Validate category
        valid_categories = ['definition', 'history', 'application', 'technical', 'other']
        if category not in valid_categories:
            category = 'other'
        
        # Ensure source_ids is a list
        if isinstance(source_ids, str):
            source_ids = [source_ids]
        
        # Add the fact
        self.facts.append(Fact(
            fact=fact,
            source_ids=source_ids,
            category=category
        ))
        
        return f"✓ Fact recorded (category: {category}, {len(source_ids)} source(s))"
    
    def get_fact_count(self) -> int:
        """Get the number of facts recorded."""
        return len(self.facts)
    
    def get_source_count(self) -> int:
        """Get the number of sources."""
        return len(self.sources)
    
    def generate_summary(self) -> str:
        """
        Generate a brief summary based on the facts.
        
        For now, this is a placeholder. In the future, we could
        ask the LLM to generate a summary after fact collection.
        """
        if not self.facts:
            return "No facts were extracted from the sources."
        
        # Group facts by category
        categories = {}
        for fact in self.facts:
            cat = fact.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(fact.fact)
        
        # Create a simple summary
        summary_parts = []
        if 'definition' in categories:
            summary_parts.append(categories['definition'][0])
        
        summary_parts.append(
            f"The sources provided {len(self.facts)} facts "
            f"across {len(categories)} categories."
        )
        
        return " ".join(summary_parts)
    
    def to_json(self, include_summary: bool = True) -> str:
        """
        Convert accumulated facts to JSON output.
        
        Args:
            include_summary: Whether to include a summary
        
        Returns:
            JSON string with all data
        """
        result = {
            "query": self.query,
            "sources": [source.to_dict() for source in self.sources],
            "facts": [fact.to_dict() for fact in self.facts],
        }
        
        if include_summary:
            result["summary"] = self.generate_summary()
        
        return json.dumps(result, indent=2)
    
    def clear(self) -> None:
        """Clear all accumulated data."""
        self.facts.clear()
        self.sources.clear()
        self._source_ids_seen.clear()
