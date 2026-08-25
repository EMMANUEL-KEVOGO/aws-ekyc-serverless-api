from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum

class DocumentType(str, Enum):
    NATIONAL_ID = "NATIONAL_ID"
    PASSPORT = "PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class KYCSubmissionRequest(BaseModel):
    national_id: str = Field(..., min_length=6, max_length=20, example="12345678")
    full_name: str = Field(..., min_length=2, max_length=100, example="Emmanuel Mahiva")
    email: EmailStr = Field(..., example="emmanuel.mahiva@example.com")
    document_type: DocumentType = Field(..., example=DocumentType.PASSPORT)

class KYCSubmissionResponse(BaseModel):
    verification_id: str
    status: VerificationStatus
    presigned_upload_url: str
    created_at: str

class KYCRecord(BaseModel):
    verification_id: str
    national_id: str
    full_name: str
    email: str
    document_type: str
    status: VerificationStatus
    s3_key: Optional[str] = None
    created_at: str
    updated_at: str
