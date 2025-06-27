from app.models import SubmitRequest, DataEntry, EntryType
import re
import uuid
from typing import List, Optional

class DataService:
    """
    Service layer for handling data submission and search.
    """

    _IP_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
    _DOMAIN_REGEX = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,}$")
    _MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")
    _SHA1_REGEX = re.compile(r"^[a-fA-F0-9]{40}$")
    _SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")

    def __init__(self, repository):
        self.repository = repository

    def _detect_type(self, value: str) -> EntryType:
        """
        Detect the type of the value: ip, domain, hash, or unknown.
        """
        if self._IP_REGEX.match(value):
            return EntryType.IP
        if self._DOMAIN_REGEX.match(value):
            return EntryType.DOMAIN
        if any(regex.match(value) for regex in [self._MD5_REGEX, self._SHA1_REGEX, self._SHA256_REGEX]):
            return EntryType.HASH
        return EntryType.UNKNOWN

    def _validate_tags(self, tags: Optional[List[str]]) -> List[str]:
        """
        Validate and clean tags.
        """
        if tags is None:
            return []
        if not isinstance(tags, list):
            raise ValueError("Tags must be a list of non-empty strings.")
        cleaned = [t.strip() for t in tags if isinstance(t, str) and t.strip()]
        if len(cleaned) != len(tags):
            raise ValueError("All tags must be non-empty strings.")
        return cleaned

    def submit(self, req: SubmitRequest) -> str:
        """
        Submit a new data entry after validation and type detection.
        Returns the unique ID of the entry.
        Raises ValueError for invalid or duplicate entries.
        """
        value = (req.value or "").strip()
        if not value:
            raise ValueError("Value must not be empty.")

        tags = self._validate_tags(req.tags)
        entry_type = self._detect_type(value)
        if entry_type == EntryType.UNKNOWN:
            raise ValueError("Value must be a valid IP, domain, or hash.")

        entry_id = str(uuid.uuid4())
        entry = DataEntry(
            id=entry_id,
            value=value,
            tags=tags,
            type=entry_type.value
        )
        if not self.repository.add(entry):
            raise ValueError("Duplicate entry: value with same tags and type already exists.")
        return entry_id

    def search(self, value: str, tags: List[str], limit: int) -> List[DataEntry]:
        """
        Search for entries matching the value and tags, limited by 'limit'.
        """
        return self.repository.search(value, tags, limit)