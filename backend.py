from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request

from langgraph.graph.state import CompiledStateGraph

from graph import build_graph
from build_db import ingest_data


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        vector_store, summary = await ingest_data()

        workflow = build_graph()

        app.state.vector_store = vector_store
        app.state.workflow = workflow
        app.state.summary = summary

    except Exception as e:
        print(f"Startup failed: {e}")

    yield

    # clear rss
    for name in ("vector_store", "workflow"):
        if hasattr(app.state, name):
            delattr(app.state, name)


app = FastAPI(title="Minimal Agent API", lifespan=lifespan)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, raw_request: Request):

    workflow: CompiledStateGraph | None = getattr(raw_request.app.state,
                                                  "workflow", None)
    if workflow is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    try:
        result = workflow.invoke({"question": request.question,
                                  "vector_store": raw_request.app.state.vector_store,
                                  "summary": raw_request.app.state.summary})
        return ChatResponse(answer=result["generation"])
    except KeyError:
        raise HTTPException(status_code=500,
                            detail="Workflow did not return 'generation'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
