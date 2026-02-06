import os
import uuid
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.document import Document, ProcessingStatus, DocumentType
from app.models.extraction import Extraction

settings = get_settings()


async def save_upload(
    db: AsyncSession,
    filename: str,
    content: bytes,
    company_id: str | None = None,
    document_type: DocumentType | None = None,
) -> Document:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_ext = Path(filename).suffix.lower()
    stored_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / stored_name

    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        company_id=company_id,
        filename=filename,
        file_type=file_ext.lstrip("."),
        file_path=str(file_path),
        file_size=len(content),
        document_type=document_type,
        processing_status=ProcessingStatus.pending,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


async def get_document(db: AsyncSession, doc_id: str) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    return result.scalar_one_or_none()


async def list_documents(
    db: AsyncSession,
    company_id: str | None = None,
    status: ProcessingStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Document], int]:
    query = select(Document)
    count_query = select(func.count(Document.id))

    if company_id:
        query = query.where(Document.company_id == company_id)
        count_query = count_query.where(Document.company_id == company_id)
    if status:
        query = query.where(Document.processing_status == status)
        count_query = count_query.where(Document.processing_status == status)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(query.order_by(Document.upload_date.desc()).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def update_document_status(
    db: AsyncSession,
    doc_id: str,
    status: ProcessingStatus,
    extracted_data: dict | None = None,
    raw_text: str | None = None,
    page_count: int | None = None,
    error_message: str | None = None,
) -> Document | None:
    doc = await get_document(db, doc_id)
    if not doc:
        return None
    doc.processing_status = status
    if extracted_data is not None:
        doc.extracted_data = extracted_data
    if raw_text is not None:
        doc.raw_text = raw_text
    if page_count is not None:
        doc.page_count = page_count
    if error_message is not None:
        doc.error_message = error_message
    await db.flush()
    await db.refresh(doc)
    return doc


async def save_extractions(
    db: AsyncSession,
    document_id: str,
    extractions: list[dict],
) -> list[Extraction]:
    records = []
    for ext in extractions:
        record = Extraction(
            document_id=document_id,
            field_name=ext["field_name"],
            field_value=str(ext["field_value"]),
            field_type=ext.get("field_type", "string"),
            confidence_score=ext.get("confidence_score", 0.0),
            extraction_method=ext.get("extraction_method", "llm"),
            page_number=ext.get("page_number"),
            context_snippet=ext.get("context_snippet"),
        )
        db.add(record)
        records.append(record)
    await db.flush()
    for r in records:
        await db.refresh(r)
    return records


async def get_extractions(
    db: AsyncSession,
    document_id: str,
) -> list[Extraction]:
    result = await db.execute(
        select(Extraction)
        .where(Extraction.document_id == document_id)
        .order_by(Extraction.field_name)
    )
    return list(result.scalars().all())


async def validate_extraction(
    db: AsyncSession,
    extraction_id: str,
    validated: bool,
    validated_by: str,
    corrected_value: str | None = None,
) -> Extraction | None:
    result = await db.execute(select(Extraction).where(Extraction.id == extraction_id))
    extraction = result.scalar_one_or_none()
    if not extraction:
        return None
    extraction.validated = validated
    extraction.validated_by = validated_by
    if corrected_value is not None:
        extraction.field_value = corrected_value
    await db.flush()
    await db.refresh(extraction)
    return extraction
