from typing import TypedDict
from langchain_core.vectorstores import InMemoryVectorStore

class GraphState(TypedDict):
    question: str
    generation: str
    documents: list[str]
    web_results: str
    decision: str
    vector_store: InMemoryVectorStore
    summary: str