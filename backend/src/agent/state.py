# from __future__ import annotations

# from dataclasses import dataclass, field
# from typing import TypedDict

# from langgraph.graph import add_messages
# from typing_extensions import Annotated


# import operator
# from dataclasses import dataclass, field
# from typing_extensions import Annotated

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



# class OverallState(TypedDict):
#     messages: Annotated[list, add_messages]
#     search_query: Annotated[list, operator.add]
#     web_research_result: Annotated[list, operator.add]
#     sources_gathered: Annotated[list, operator.add]
#     initial_search_query_count: int
#     max_research_loops: int
#     research_loop_count: int
#     reasoning_model: str


# class ReflectionState(TypedDict):
#     is_sufficient: bool
#     knowledge_gap: str
#     follow_up_queries: Annotated[list, operator.add]
#     research_loop_count: int
#     number_of_ran_queries: int


# class Query(TypedDict):
#     query: str
#     rationale: str


# class QueryGenerationState(TypedDict):
#     query_list: list[Query]


# class WebSearchState(TypedDict):
#     search_query: str
#     id: str


# @dataclass(kw_only=True)
# class SearchStateOutput:
#     running_summary: str = field(default=None)  # Final report
