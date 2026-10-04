from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


Path("data").mkdir(exist_ok=True)


#  used to store conversations, messages, and memories.
DATABASE_URL = "sqlite:///data/chatbot_memory.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Create a database session factory.to read and write data to the database.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()



class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    # Unique identifier for the conversation
    thread_id = Column(String, unique=True, index=True)

    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)




class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    # ID of the conversation this message belongs to.
    thread_id = Column(String, index=True)

    # Message sender type, such as "user" or "assistant".
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)




class LongTermMemory(Base):

    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    # Conversation associated with the memory.
    thread_id = Column(String, index=True)
    memory = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)




def init_db():
    Base.metadata.create_all(bind=engine)


def create_or_update_convo(thread_id: str,first_message: str | None = None):
    # Open a database session.
    db = SessionLocal()

    try:
        # Look for an existing conversation with  thread ID.
        conversation = ( db.query(Conversation).filter(Conversation.thread_id == thread_id).first())

        if not conversation:
            title = "New Chat Session"

            if first_message:
                title = first_message.strip()[:30]

                # Add "..." if the message is longer than 30 .
                if len(first_message.strip()) > 30:
                    title += "..."

            # Create a new conversation record.
            conversation = Conversation(
                thread_id=thread_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(conversation)

        else:
            # Update the timestamp with existing conversation 
            conversation.updated_at = datetime.utcnow()

        # Save the changes to the database.
        db.commit()

    finally:
        # close the database session.
        db.close()



# get all conversations sidebar
def list_conversations():

    db = SessionLocal()

    try:

        return (
            db.query(Conversation)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    finally:
        db.close()



def save_chat_message(thread_id: str, role: str, content: str):

    db = SessionLocal()

    try:
        msg = ChatMessage(
            thread_id=thread_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )

        db.add(msg)

        # Find the conversation that owns this message.
        conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id == thread_id)
            .first()
        )

        if conversation:
            conversation.updated_at = datetime.utcnow()

        db.commit()

    finally:

        db.close()



def get_chat_history(thread_id: str):

    db = SessionLocal()

    try:
        # Get all messages belonging to this thread.Oldest messages are returned first.
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    finally:
        db.close()




def save_memory(thread_id: str, memory: str):

    db = SessionLocal()

    try:
        # Create a new memory record.
        item = LongTermMemory(
            thread_id=thread_id,
            memory=memory,
            created_at=datetime.utcnow()
        )

        db.add(item)

        db.commit()

        return "Memory saved successfully in BoxGPT."

    finally:
        db.close()




def search_memory(thread_id: str, query: str):

    db = SessionLocal()

    try:

        memories = (
            db.query(LongTermMemory)
            .filter(LongTermMemory.thread_id == thread_id)
            .order_by(LongTermMemory.created_at.desc())
            .limit(20)
            .all()
        )

        if not memories:
            return "No saved memory found."

        # Convert the memories into a simple text list.
        return "\n".join(
            [f"- {m.memory}" for m in memories]
        )

    finally:
        db.close()


# Initialize database tables when this module is imported
init_db()