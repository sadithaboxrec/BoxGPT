### test version

from agent import get_agent
from langchain_core.messages import HumanMessage


agent = get_agent("gemini-2.5-flash")


# Configuration used by LangGraph for conversation checkpointing.
config = {
    "configurable": {
        "thread_id": "test_thread_id",
    }
}

# Send a message to  agent and stream the response.
for message_chunk, metadata in agent.stream(
    {
        "messages": [
            HumanMessage(
                content="Generate a sentence about Mike Tyson"
            )
        ]
    },
    config=config,
    stream_mode="messages"
):

    # Print only chunks that contain text.
    if message_chunk.content:
        print(message_chunk.content,end="",flush=True)
