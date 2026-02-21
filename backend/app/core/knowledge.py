"""
Simple in-memory knowledge base for agent training.

This is a minimal implementation to support the AgentEngine training flow.
"""
from typing import Any, Dict, List, Optional


class KnowledgeBase:
    """In-memory knowledge storage keyed by agent id."""

    def __init__(self) -> None:
        self._entries: Dict[int, List[Dict[str, Any]]] = {}

    async def initialize(self) -> None:
        """Initialize the knowledge base (no-op for in-memory)."""
        return None

    async def add_knowledge(self, agent_id: int, entry: Dict[str, Any]) -> None:
        """Add a knowledge entry for an agent."""
        self._entries.setdefault(agent_id, []).append(entry)

    async def get_knowledge(self, agent_id: int) -> List[Dict[str, Any]]:
        """Get all knowledge entries for an agent."""
        return self._entries.get(agent_id, [])

    async def search_knowledge(self, agent_id: int, query: str) -> List[Dict[str, Any]]:
        """Search knowledge entries for an agent containing the query string."""
        entries = self._entries.get(agent_id, [])
        return [entry for entry in entries if query.lower() in str(entry).lower()]

    async def remove_knowledge(self, agent_id: int, entry_id: Optional[str] = None) -> None:
        """Remove knowledge entries for an agent. If entry_id is provided, remove only that entry."""
        if agent_id not in self._entries:
            return
        
        if entry_id:
            self._entries[agent_id] = [
                entry for entry in self._entries[agent_id]
                if entry.get('id') != entry_id
            ]
        else:
            del self._entries[agent_id]

    async def cleanup(self) -> None:
        """Clean up all in-memory knowledge."""
        self._entries.clear()
