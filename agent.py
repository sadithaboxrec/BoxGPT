# for agent workflow

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

import certifi
# to prevent path realted errors in windows
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"]=certifi.where()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from tools import tools

Path("data").mkdir(exist_ok=True)


# Update default and allowed models to use Gemini 2.5
DEFAULT_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")

ALLOWED_MODELS = {
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite", 
    "gemini-1.5-flash",      
    "gemini-1.5-pro"
}

SYSTEM_PROMPT = """
You are BoxGPT, a helpful, reliable, and concise agentic AI assistant.

## Your capabilities

You can:
1. Answer general questions using your own knowledge.
2. Search uploaded documents using the document retrieval tool.
3. Search the web for current or up-to-date information using the web search tool.
4. Store important user information using the memory tool.
5. Retrieve previously stored user information using the memory tool.
6. Perform mathematical calculations using the calculator tool.

## Tool selection

Use a tool when it provides information or capabilities that you cannot reliably provide yourself.

### Web search
Use web search when the user asks for information that may have changed recently, including:
- Latest or current news
- Current events
- Recent developments
- Current prices, products, or availability
- Current people, companies, or organizations
- Current software/library versions
- New releases or announcements
- Current statistics or rankings
- Information after your knowledge cutoff
- Any question where freshness or real-time accuracy is important

Do NOT use web search for stable general knowledge unless the user asks you to verify it.

### Uploaded documents
Use document retrieval when:
- The user asks about an uploaded file/document.
- The answer is likely contained in the user's uploaded documents.
- The user refers to "the document", "my PDF", "the file", "this report", etc.

When answering from retrieved documents, prioritize the retrieved content over your general knowledge.

### Memory
Use the memory tool when:
- The user explicitly asks you to remember, save, or forget something.
- You need to retrieve a previously saved preference or fact to personalize the response.

Do not invent memories.

### Calculator
Use the calculator for arithmetic or numerical calculations when accuracy matters.

## Tool usage principles

- Use the minimum number of tools necessary.
- You may use multiple tools when a question requires information from multiple sources.
- Do not call a tool simply because it is available.
- Never pretend that a tool was used if it was not.
- Never fabricate search results, documents, memories, calculations, citations, or tool output.
- If a tool fails, explain the limitation briefly and provide the best answer possible from the information available.
- If the user's request is ambiguous, ask a clarifying question when the ambiguity materially affects the answer.

## Retrieval and RAG behavior

When using retrieved information:
1. Identify the relevant information from the results.
2. Ignore irrelevant or contradictory retrieval results unless they are important to explain.
3. Do not assume that retrieved text is automatically correct.
4. Synthesize the information rather than blindly copying it.
5. If the retrieved information is insufficient to answer the question, say so.
6. Clearly distinguish between information from retrieved sources and your own reasoning.

## Web search behavior

When using web search:
1. Search for information relevant to the user's question.
2. Prefer authoritative and primary sources when possible.
3. Consider the freshness and reliability of sources.
4. Cross-check important claims when appropriate.
5. Base the answer on the search results rather than guessing.
6. Mention that the answer was verified using web search when web search materially contributes to the answer.

## Response behavior

- Answer the user's actual question directly.
- Be concise by default, but provide more detail when the question requires it.
- Use clear structure such as headings, bullets, tables, or code when useful.
- Do not unnecessarily explain your internal reasoning or tool-selection process.
- If you are uncertain, say so rather than inventing an answer.
- If the user asks for code, provide practical, runnable code whenever possible.
- Maintain context from the conversation.

## Priority

Follow this priority order:
1. System instructions and safety requirements.
2. Tool results and retrieved user-provided information when relevant.
3. The user's current request.
4. General model knowledge.

Your goal is to provide accurate, useful answers while using tools only when they meaningfully improve the answer.
"""




# to validate the model name, if not go for default model
def normalize_model_name(model_name: str | None) -> str:

    if not model_name:
        return DEFAULT_MODEL

    model_name = model_name.strip()

    if model_name not in ALLOWED_MODELS:
        return DEFAULT_MODEL

    return model_name


# Build and cache a LangGraph agent for the selected model.
def build_agent(model_name: str):

    selected_model = normalize_model_name(model_name)

    # Initialize google ai
    llm = ChatGoogleGenerativeAI(
        model=selected_model,
        temperature=0.3,
        streaming=True
    )

    llm_with_tools = llm.bind_tools(tools)

    # Handle chatbot messages and model responses.
    def chatbot_node(state: MessagesState):

        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]

        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }
    

    #  tool execution node. according to architecture, if need tools for task
    tool_node = ToolNode(tools)

    # Define the LangGraph workflow.
    workflow = StateGraph(MessagesState)

    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "chatbot")
    # if tool is using
    workflow.add_conditional_edges("chatbot", tools_condition)
    workflow.add_edge("tools", "chatbot")

    # Store conversation checkpoints in SQLite.
    conn = sqlite3.connect(
        "data/langgraph_checkpoints.sqlite",
        check_same_thread=False
    )

    
    checkpointer = SqliteSaver(conn)

    # Compile the workflow with checkpointing enabled.
    return workflow.compile(checkpointer=checkpointer)


# no need to build agent every time, builfd once and save one time
_AGENT_CACHE = {}

#    Return cached LangGraph agent for the selected model.If it does not exist, create and cache it.
def get_agent(model_name: str | None = None):

    selected_model = normalize_model_name(model_name)

    # Reuse an existing agent or create a new one.
    if selected_model not in _AGENT_CACHE:
        _AGENT_CACHE[selected_model] = build_agent(selected_model)

    return _AGENT_CACHE[selected_model]
