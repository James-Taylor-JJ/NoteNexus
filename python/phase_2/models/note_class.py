from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Note:
    filename: str
    title: str
    content: str
    created: str
    modified: str
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    status: Optional[str] = None
    priority: Optional[int] = None
    archived_at: Optional[str] = None