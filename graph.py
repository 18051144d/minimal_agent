from langgraph.graph import StateGraph, END, START


from states import GraphState
from nodes import router_node, retrieve_node, web_search_node, generate_rag_node, generate_web_node

def build_graph():
    workflow = StateGraph(GraphState)

    # nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("rag_gen", generate_rag_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("web_gen", generate_web_node)

    # edges
    workflow.add_edge(START, "router")

    def decide_path(state):
        if state["decision"] == "vectorstore":
            return "retrieve"
        else:
            return "web_search"

    workflow.add_conditional_edges(
        "router",
        decide_path,
        {
            "retrieve": "retrieve",
            "web_search": "web_search"
        }
    )

    workflow.add_edge("retrieve", "rag_gen")
    workflow.add_edge("rag_gen", END)

    workflow.add_edge("web_search", "web_gen")
    workflow.add_edge("web_gen", END)

    complied_graph = workflow.compile()

    return complied_graph