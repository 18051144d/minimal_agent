chunk_summary_prompt = """/no_think
You are an expert summarizer.
Summarize the document text below in excatly ONE sentence with these rules:
- No bullets
- No preamble
- Keep it self-contained

Chunk: {chunk}
"""

doc_summary_prompt = """/no_think
You are an expert summarizer.
You are given a list of one-sentence chunk summaries from a document.
Write ONE single-paragraph description, summarizing the overall content with these rules:
- No bullets
- No preamble
- Keep it coherent and non-repetitive

Chunk Summaries: {chunk_summaries}
"""

router_prompt = """
You are an expert at routing a user question to a vectorstore or web search.
Here is a content summary of the vectorstore: {summary}.
Use web_search if the question is not related to the vectorstore content."""

rag_prompt = """
You are an assistant for Q&A tasks. Use the following pieces of retrieved context to answer the question.
IMPORTANT: You must cite the [Source: Page X] for every claim you make. If you don't know the answer, say that.
"""

websearch_prompt = """
You are a helpful assistant. Answer the question based on the web search results provided.
IMPORTANT: Include the Source URL at the end of your answer."
"""
