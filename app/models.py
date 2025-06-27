from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EntryType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    HASH = "hash"
    UNKNOWN = "unknown"


class SubmitRequest(BaseModel):
    """
    Request model for submitting a new data entry.
    """

    value: str
    tags: Optional[List[str]] = Field(default_factory=list)


class SubmitResponse(BaseModel):
    """
    Response model for a successful submission.
    """

    id: str


class DataEntry(BaseModel):
    """
    Internal model representing a stored data entry.
    """

    id: str
    value: str
    tags: List[str]
    type: str


class DataResponse(BaseModel):
    """
    Response model for returning a list of data entries.
    """

    data: List[Dict[str, Any]]
