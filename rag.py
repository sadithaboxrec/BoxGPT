from pathlib import Path
from typing import List

from dotenv import load_dotenv
import os
import certifi

load_dotenv()


os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


# Import Chroma for storing and searching vector embeddings.
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

# Used to split large documents into smaller chunks.
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import docx2txt

Path("uploads").mkdir(exist_ok=True)
Path("chroma_db").mkdir(exist_ok=True)




# Convert text into numerical vectors (embeddings).
# Similar pieces of text will have similar vector representations.
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)



# Create/load a persistent Chroma vector database. stores document chunks and their embeddings.
vectorstore = Chroma(
    collection_name="agentic_chatbot_docs",
    embedding_function=embeddings,
    persist_directory="chroma_db"
)



def read_file_text(file_path: str) -> str:

    # Convert the file path to a Path object.
    path = Path(file_path)

    #  file extension and convert in to lowercase.
    suffix = path.suffix.lower()


    if suffix == ".pdf":

        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""
            text += "\n"

        return text

    if suffix == ".docx":

        return docx2txt.process(file_path)


    if suffix in [".txt", ".md", ".py", ".csv"]:

        # Read the file as UTF-8 text.
        # Invalid characters are ignored instead  causing an error.
        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    raise ValueError(
        "Unsupported file type. Upload PDF, DOCX, TXT, MD, PY, or CSV."
    )



#read,split it into chunks, create embeddings,and store in db
def add_document_to_rag(file_path: str, thread_id: str):

    text = read_file_text(file_path)

    if not text.strip():
        raise ValueError(
            "No text could be extracted from this file."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150
    )

    chunks = splitter.split_text(text)


    # Convert every chunk into a LangChain Document.
    docs: List[Document] = [
        Document(
            page_content=chunk,

            # metadata  with each chunk.
            metadata={

                "thread_id": thread_id,
                # Store the original filename.
                "source": Path(file_path).name
            }
        )

        for chunk in chunks
    ]


    # Store the document chunks and  embeddings in Chroma.
    vectorstore.add_documents(docs)


    return {
        "filename": Path(file_path).name,
        "chunks": len(docs)
    }


    # Perform similarity search in Chroma.
    # query:The user's question.
    # k:Number of relevant chunks to retrieve.
    # filter:Only search documents belonging to this convo.

def retrieve_from_rag(query: str,thread_id: str,k: int = 4) -> str:

    docs = vectorstore.similarity_search(
        query,
        k=k,
        filter={
            "thread_id": thread_id
        }
    )

    if not docs:
        return "No relevant uploaded document content found."

    results = []


    # Format each retrieved document chunk.
    for i, doc in enumerate(docs, start=1):

        # Get the original filename from metadata.
        source = doc.metadata.get(
            "source",
            "uploaded document"
        )

        results.append(
            f"[Source {i}: {source}]\n{doc.page_content}"
        )


    # Combine all retrieved chunks into one string.
    return "\n\n".join(results)
