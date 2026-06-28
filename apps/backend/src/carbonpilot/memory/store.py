from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryNamespace:
    organization_id: str
    memory_type: str


def build_memory_namespace(organization_id: str, memory_type: str) -> str:
    return f"{organization_id}:{memory_type}"
