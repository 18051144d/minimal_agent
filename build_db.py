import os
import re
import copy
import asyncio
import requests

from qdrant_client import QdrantClient
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_core.messages import SystemMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from prompts import chunk_summary_prompt, doc_summary_prompt

DOC_URL = os.getenv(
    'DOC_URL', 'https://requests.readthedocs.io/_/downloads/en/v2.0.0/pdf/')
DOC_PAGE_START = int(os.getenv('DOC_PAGE_START', '11'))
DOC_PAGE_END = int(os.getenv('DOC_PAGE_END', '19'))

EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL',
                            'jinaai/jina-code-embeddings-1.5b')
EMBEDDING_URL = os.getenv('EMBEDDING_URL', 'http://localhost:8000/v1')

SLM_MODEL = os.getenv('SLM_MODEL', 'Qwen/Qwen3-0.6B')
SLM_URL = os.getenv('SLM_URL', 'http://localhost:8001/v1')

DB_COLLECTION_NAME = os.getenv('DB_COLLECTION_NAME', 'minimal_example')
DB_URL = os.getenv('DB_URL', 'http://localhost:6333')


def remove_think_tags(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>",
                     "",
                     text,
                     flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()


async def _generate_document_summary(
    *,
    chunks: list[Document],
    summary_model: ChatOpenAI,
    max_concurrency: int = 10,
) -> str:

    semaphore = asyncio.Semaphore(max_concurrency)

    async def worker(i: int, doc: Document) -> tuple[int, str]:
        async with semaphore:
            s = await summary_model.ainvoke([
                SystemMessage(
                    content=copy.deepcopy(chunk_summary_prompt).format(
                        chunk=doc.page_content))
            ])
            return i, remove_think_tags(s.text).strip()

    tasks = [asyncio.create_task(worker(i, c)) for i, c in enumerate(chunks)]
    results = await asyncio.gather(*tasks)

    results.sort(key=lambda x: x[0])
    chunk_summaries = [s for _, s in results]

    joined = "\n".join(f"- {s}" for s in chunk_summaries)
    document_summary = await summary_model.ainvoke([
        SystemMessage(content=copy.deepcopy(doc_summary_prompt).format(
            chunk_summaries=joined))
    ])

    return remove_think_tags(document_summary.content).strip(), joined


async def ingest_data():
    # download the document
    r = requests.get(DOC_URL, timeout=60)
    r.raise_for_status()
    with open("download.pdf", "wb") as f:
        f.write(r.content)

    # load and split
    docs = PyPDFLoader("download.pdf").load()
    try:
        docs = docs[DOC_PAGE_START:
                    DOC_PAGE_END]  # default: only the quick start
    except Exception as e:
        print(f'Error slicing documents: {e}')

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1500, chunk_overlap=100,
        add_start_index=True).split_documents(docs)

    # generate summary
    summary_model = ChatOpenAI(
        model=SLM_MODEL,
        temperature=0,
        base_url=SLM_URL,
        api_key='',
    )

    document_summary, joined = await _generate_document_summary(
        chunks=chunks, summary_model=summary_model)

    # generate embeddings and build vector store
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_base=EMBEDDING_URL,
        openai_api_key="",
    )

    client = QdrantClient(url=DB_URL)
    try:
        exists = client.collection_exists(collection_name=DB_COLLECTION_NAME)
    except Exception as e:
        print('Error checking collection existence:', e)
        exists = False

    if exists:
        try:
            vector_store = QdrantVectorStore.from_existing_collection(
                embedding=embeddings,
                url=DB_URL,
                collection_name=DB_COLLECTION_NAME,
            )
        except Exception as e:
            print(f"Failed to load existing collection: {e}")
            try:
                client.delete_collection(collection_name=DB_COLLECTION_NAME)
            except:
                pass
            import time
            time.sleep(1)
            vector_store = QdrantVectorStore.from_documents(
                documents=chunks,
                embedding=embeddings,
                url=DB_URL,
                collection_name=DB_COLLECTION_NAME,
            )
    else:
        vector_store = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=DB_URL,
            collection_name=DB_COLLECTION_NAME,
        )

    # DEBUG: In memory vector store
    # vector_store = InMemoryVectorStore.from_documents(
    #     documents=chunks,
    #     embedding=embeddings,
    # )

    return vector_store, document_summary
