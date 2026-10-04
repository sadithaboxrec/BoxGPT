import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from langchain_core.messages import (HumanMessage, AIMessage, AIMessageChunk, ToolMessage)

from agent import get_agent

from database import (save_chat_message,create_or_update_convo)
from tools import set_current_thread_id


router = APIRouter()


# SSE helper
def sse_data(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


# Stream filtering
def should_stream_chunk(chunk, metadata) -> bool:
    """
    Prevent raw tool/search/RAG output from appearing
    directly in the frontend.

    Only normal AI text chunks are streamed.
    """

    metadata = metadata or {}
    node_name = str(metadata.get("langgraph_node", "")).lower()

    # Don't stream tool-node output
    if "tool" in node_name:
        return False

    # Don't stream ToolMessage
    if isinstance(chunk, ToolMessage):
        return False

    # Only allow normal AI messages
    if not isinstance(chunk, (AIMessage, AIMessageChunk)):
        return False

    # Don't stream tool calls
    if getattr(chunk, "tool_calls", None):
        return False

    # Don't stream invalid tool calls
    if getattr(chunk, "invalid_tool_calls", None):
        return False

    # Don't stream tool calls hidden inside additional_kwargs
    additional_kwargs = getattr(chunk, "additional_kwargs", {}) or {}

    if additional_kwargs.get("tool_calls"):
        return False

    return True


# Extract text from AI chunk
def extract_text_from_chunk(chunk) -> str:
    content = getattr(chunk, "content", "")

    if not content:
        return ""

    # Normal string content
    if isinstance(content, str):
        return content

    # Content represented as a list
    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                if (
                    item.get("type") == "text"
                    and isinstance(item.get("text"), str)
                ):
                    text_parts.append(item["text"])

                elif isinstance(item.get("text"), str):
                    text_parts.append(item["text"])

                elif isinstance(item.get("content"), str):
                    text_parts.append(item["content"])

        return "".join(text_parts)

    return ""


# Chat streaming endpoint
@router.post("/chat/stream")
async def chat_stream(request: Request):

    # Read request JSON
    try:
        data = await request.json()

    except Exception:
        return JSONResponse(
            {"error": "Invalid JSON body."},
            status_code=400
        )

    # get values
    user_message = data.get("message", "")
    thread_id = data.get("thread_id", "default")
    selected_model = data.get("model", "gemini-2.5-flash")

    # validate
    if not user_message.strip():
        return JSONResponse(
            {"error": "Message is required."},
            status_code=400
        )

    # get agent
    agent = get_agent(selected_model)

    # save user message
    create_or_update_convo(thread_id, user_message)
    save_chat_message(thread_id, "user", user_message)

    set_current_thread_id(thread_id)

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # generate streaming response
    def event_generator():

        final_answer = ""

        try:
            inputs = {"messages": [HumanMessage(content=user_message)]}

            # Stream LangGraph messages
            for chunk, metadata in agent.stream(
                inputs,
                config=config,
                stream_mode="messages"
            ):

                # Ignore tool/RAG/internal messages
                if not should_stream_chunk(chunk, metadata):
                    continue

                # Extract only visible text
                token = extract_text_from_chunk(chunk)

                if token:
                    final_answer += token

                    yield sse_data({
                        "token": token
                    })

            # Save final assistant response

            if final_answer.strip():
                save_chat_message(
                    thread_id,
                    "assistant",
                    final_answer
                )
            # Tell frontend streaming is finished

            yield sse_data({
                "done": True
            })

        except Exception as e:
            yield sse_data({
                "error": str(e)
            })

            yield sse_data({
                "done": True
            })

    # Return SSE stream
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
