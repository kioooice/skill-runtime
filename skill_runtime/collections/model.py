from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CapabilityCollectionDefinition:
    collection_id: str
    label: str
    description: str
    skill_names: list[str] = field(default_factory=list)
