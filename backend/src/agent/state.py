# src/agent/state.py

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class OSINTState(BaseModel):
    query: str

    parsed: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tasks: Optional[List[str]] = Field(default_factory=list)
    retrievals: Optional[Dict[str, Any]] = Field(default_factory=dict)
    report: Optional[str] = ""
    judgement: Optional[Dict[str, Any]] = Field(default_factory=dict)
    retry_count: Optional[int] = Field(default=0)
    provenance: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    graph: Optional[Dict[str, Any]] = Field(default_factory=dict)
    deduplicated: Optional[Dict[str, Any]] = Field(default_factory=dict)
    retrieval_model: Optional[str] = "claude-opus-4-20250514"
    synthesis_model: Optional[str] = "gemini-1.5-pro"
