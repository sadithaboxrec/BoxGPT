import math
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

# for long-term memory storage and search.
from database import save_memory, search_memory
#  for searching uploaded documents.
from rag import retrieve_from_rag


load_dotenv()


# Stores the ID of the conversation currently being used.
CURRENT_THREAD_ID = "default"


def set_current_thread_id(thread_id: str):
    # Update the current thread ID.
    global CURRENT_THREAD_ID
    CURRENT_THREAD_ID = thread_id


# Create a Tavily web-search tool.
#  to search the internet when needed.
web_search = TavilySearch(
    max_results=5,       # Return up to 5 search results.
    topic="general",     
    search_depth="advanced"  #  deeper search for better results.
)


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic mathematical expression."""

    try:

        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum
        }

        # Evaluate the expression without allowing normal Python built-ins.
        result = eval(expression, {"__builtins__": {}}, allowed)

        return str(result)

    except Exception as e:

        return f"Calculation error: {str(e)}"


@tool
def search_uploaded_documents(query: str) -> str:
    """Search uploaded documents for relevant information."""

    # Search the user's uploaded documents using the current thread.
    return retrieve_from_rag(
        query=query,
        thread_id=CURRENT_THREAD_ID
    )


# long term memory
@tool
def remember_this(memory: str) -> str:
    """Save a useful fact to conversation memory."""

    return save_memory(
        thread_id=CURRENT_THREAD_ID,
        memory=memory
    )


@tool
def recall_memory(query: str) -> str:
    """Search conversation memory for relevant facts."""

    return search_memory(
        thread_id=CURRENT_THREAD_ID,
        query=query
    )


# List of all tools  to the LangGraph agent.
# The agent can decide which tool to call 
tools = [
    calculator,                  
    search_uploaded_documents,  
    remember_this,               
    recall_memory,               
    web_search                   
]
