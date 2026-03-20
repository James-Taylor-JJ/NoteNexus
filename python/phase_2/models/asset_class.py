from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Asset:
    asset_id: str
    asset_type: str
    title: str
    author: str
    created: str
    modified: str
    tags: List[str] = field(default_factory=list)
    status: Optional[str] = None
    priority: Optional[int] = None