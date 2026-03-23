from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from python.phase_2.models.asset_class import Asset


@dataclass
class DatasetAsset(Asset):
    filename: str = ""
    format: str = ""
    path: str = ""
    row_count: int = 0
    schema: List[Dict[str, Any]] = field(default_factory=list)
    profile: Optional[Dict[str, Any]] = None