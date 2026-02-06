
from datetime import datetime
from pydantic import BaseModel

from app.models.document import DocumentType, ProcessingStatus
from app.models.extraction import ExtractionMethod


class DocumentResponse(BaseModel):
    id: str
    company_id: str | None
    filename: str
    file_type: str
    file_size: int
    document_type: DocumentType | None
    processing_status: ProcessingStatus
    extracted_data: dict | None
    page_count: int | None
    error_message: str | None
    upload_date: datetime
    extraction_count: int = 0

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class ExtractionResponse(BaseModel):
    id: str
    document_id: str
    field_name: str
    field_value: str
    field_type: str
    confidence_score: float
    extraction_method: ExtractionMethod
    page_number: int | None
    context_snippet: str | None
    validated: bool
    validated_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExtractionValidation(BaseModel):
    validated: bool
    validated_by: str
    corrected_value: str | None = None


class ExtractionListResponse(BaseModel):
    extractions: list[ExtractionResponse]
    total: int
