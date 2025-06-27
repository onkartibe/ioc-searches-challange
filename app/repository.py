from typing import Dict, List
from app.models import DataEntry

class InMemoryRepository:
    """
    In-memory repository for storing DataEntry objects.
    Not thread-safe; for demo/testing only.
    """
    def __init__(self):
        self.storage: Dict[str, DataEntry] = {}

    def add(self, entry: DataEntry) -> bool:
        """
        Add a DataEntry if not a duplicate (value, tags, type).
        Returns True if added, False if duplicate.
        """
        normalized_tags = tuple(sorted(t.lower() for t in entry.tags))
        for e in self.storage.values():
            if (
                e.value == entry.value and
                tuple(sorted(t.lower() for t in e.tags)) == normalized_tags and
                e.type == entry.type
            ):
                return False
        self.storage[entry.id] = entry
        return True

    def search(self, value: str, tags: List[str], limit: int) -> List[DataEntry]:
        """
        Search for entries matching value and tags (case-insensitive).
        Returns up to 'limit' results.
        """
        results = []
        tags_lower = [t.lower() for t in tags]
        for entry in self.storage.values():
            if entry.value != value:
                continue
            entry_tags = [t.lower() for t in entry.tags]
            if tags_lower and not all(tag in entry_tags for tag in tags_lower):
                continue
            results.append(entry)
            if len(results) >= limit:
                break
        return results