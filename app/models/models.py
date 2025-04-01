from pydantic import BaseModel
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph.message import add_messages


class UserRequest(BaseModel):
    user_id: str
    query: str


class State(TypedDict):
    original_question: str
    expanded_question: str
    search_queries: List[str]
    search_results: List[Dict]
    messages: Annotated[List, add_messages]