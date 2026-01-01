import os

from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults

from states import GraphState
from prompts import router_prompt, rag_prompt, websearch_prompt

OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini")

llm = ChatOpenAI(model=OPENAI_MODEL_NAME, temperature=0)


class RouteQuery(BaseModel):
    reasoning: str = Field(...,
                           description="Reasoning for the routing decision")
    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description=
        "Given a user question choose to route it to web_search or a vectorstore."
    )


class GeneratedOutput(BaseModel):
    generation: str = Field(..., description="The generated answer")
    source: str = Field(...,
                        description="The source of the answer: page id or URL")


def router_node(state: GraphState):
    question = state["question"]

    structured_llm_router = llm.with_structured_output(RouteQuery)
    result = structured_llm_router.invoke([
        SystemMessage(content=router_prompt.format(summary=state["summary"])),
        HumanMessage(content=f'Question: {question}')
    ])

    return {"decision": result.datasource}


def retrieve_node(state: GraphState):
    question = state["question"]
    vector_store = state['vector_store']

    documents = vector_store.similarity_search(question, k=3)
    context_list = []
    for doc in documents:
        page = doc.metadata.get('page', 'Unknown')
        context_list.append(f"[Source: Page {page}] {doc.page_content}")
    print(context_list)

    return {"documents": context_list, "question": question}


def generate_rag_node(state: GraphState):
    question = state["question"]
    documents = state["documents"]

    generator = llm.with_structured_output(GeneratedOutput)

    prompt = [
        SystemMessage(content=rag_prompt),
        HumanMessage(content=f"Question: {question} \n\n Context: {documents}")
    ]
    generation = generator.invoke(prompt)

    return {
        "generation": f'{generation.generation} (sources: {generation.source})'
    }


def web_search_node(state: GraphState):
    question = state["question"]

    tool = TavilySearchResults(max_results=3)
    results = tool.invoke({"query": question})

    context_str = "\n".join([
        f"Content: {res['content']} \n Source: {res['url']}" for res in results
    ])
    return {"web_results": context_str}


def generate_web_node(state: GraphState):
    question = state["question"]
    web_results = state["web_results"]

    generator = llm.with_structured_output(GeneratedOutput)

    prompt = [
        SystemMessage(content=websearch_prompt),
        HumanMessage(
            content=f"Question: {question} \n\n Search Results: {web_results}")
    ]
    generation = generator.invoke(prompt)

    return {
        "generation": f'{generation.generation} (sources: {generation.source})'
    }
