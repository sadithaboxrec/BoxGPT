from pathlib import Path
import uuid

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from database import create_or_update_convo
from rag import add_document_to_rag


router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    thread_id: str = Form(...)
):
    try:
        allowed_extensions = [
            ".pdf",
            ".docx",
            ".txt",
            ".md",
            ".py",
            ".csv"
        ]

        filename = file.filename or "uploaded_file"
        suffix = Path(filename).suffix.lower()

        if suffix not in allowed_extensions:
            return JSONResponse(
                {
                    "success": False,
                    "message": (
                        "Unsupported file type. "
                        "Upload PDF, DOCX, TXT, MD, PY, or CSV."
                    )
                },
                status_code=400
            )

        file_id = str(uuid.uuid4())
        safe_filename = filename.replace(" ", "_")

        file_path = f"uploads/{file_id}_{safe_filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        create_or_update_convo( thread_id,"Uploaded document")

        result = add_document_to_rag(
            file_path=file_path,
            thread_id=thread_id
        )

        return JSONResponse({
            "success": True,
            "message": (
                f"Uploaded {result['filename']} "
                f"and created {result['chunks']} chunks."
            )
        })

    except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "message": str(e)
            },
            status_code=500
        )
