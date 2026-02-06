import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.document import ProcessingStatus, DocumentType
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    ExtractionResponse,
    ExtractionValidation,
    ExtractionListResponse,
)
from app.services import ingestion as svc

settings = get_settings()

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    company_id: str | None = Form(None),
    document_type: DocumentType | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(413, f"File exceeds {settings.max_upload_size_mb}MB limit")

    doc = await svc.save_upload(db, file.filename, content, company_id, document_type)
    return _doc_response(doc)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    company_id: str | None = None,
    status: ProcessingStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    docs, total = await svc.list_documents(db, company_id, status, skip, limit)
    return DocumentListResponse(
        documents=[_doc_response(d) for d in docs],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    doc = await svc.get_document(db, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return _doc_response(doc)


@router.post("/{document_id}/extract", response_model=ExtractionListResponse)
async def extract_document(document_id: str, db: AsyncSession = Depends(get_db)):
    doc = await svc.get_document(db, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    await svc.update_document_status(db, document_id, ProcessingStatus.parsing)

    try:
        from app.ai.document_parser import parse_document
        from app.ai.llm_extractor import extract_fields

        raw_text, page_count = await parse_document(doc.file_path, doc.file_type)
        await svc.update_document_status(
            db, document_id, ProcessingStatus.extracting,
            raw_text=raw_text, page_count=page_count,
        )

        extracted = await extract_fields(raw_text, doc.document_type)
        extractions = await svc.save_extractions(db, document_id, extracted)

        await svc.update_document_status(
            db, document_id, ProcessingStatus.completed,
            extracted_data={e["field_name"]: e["field_value"] for e in extracted},
        )

        return ExtractionListResponse(
            extractions=[ExtractionResponse.model_validate(e) for e in extractions],
            total=len(extractions),
        )
    except Exception as e:
        await svc.update_document_status(
            db, document_id, ProcessingStatus.failed,
            error_message=str(e),
        )
        raise HTTPException(500, f"Extraction failed: {str(e)}")


@router.get("/{document_id}/extractions", response_model=ExtractionListResponse)
async def get_extractions(document_id: str, db: AsyncSession = Depends(get_db)):
    extractions = await svc.get_extractions(db, document_id)
    return ExtractionListResponse(
        extractions=[ExtractionResponse.model_validate(e) for e in extractions],
        total=len(extractions),
    )


@router.patch("/extractions/{extraction_id}", response_model=ExtractionResponse)
async def validate_extraction(
    extraction_id: str,
    data: ExtractionValidation,
    db: AsyncSession = Depends(get_db),
):
    extraction = await svc.validate_extraction(
        db, extraction_id, data.validated, data.validated_by, data.corrected_value,
    )
    if not extraction:
        raise HTTPException(404, "Extraction not found")
    return ExtractionResponse.model_validate(extraction)


def _doc_response(doc) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        company_id=doc.company_id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        document_type=doc.document_type,
        processing_status=doc.processing_status,
        extracted_data=doc.extracted_data,
        page_count=doc.page_count,
        error_message=doc.error_message,
        upload_date=doc.upload_date,
        extraction_count=len(doc.extractions) if doc.extractions else 0,
    )
