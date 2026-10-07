"""
Pydantic Data Models for Oracle EBS Leave Management APIs.
Provides rigorous request validation, typing, and schema generation for Power Automate / Swagger.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

class LeaveTypeEnum(str, Enum):
    ANNUAL_LEAVE = "ANNUAL_LEAVE"
    SICK_LEAVE = "SICK_LEAVE"
    MATERNITY_LEAVE = "MATERNITY_LEAVE"
    BEREAVEMENT_LEAVE = "BEREAVEMENT_LEAVE"
    UNPAID_LEAVE = "UNPAID_LEAVE"

class OverlapCheckRequest(BaseModel):
    employee_id: str = Field(..., examples=["EMP101"], description="Employee requesting leave")
    start_date: str = Field(..., examples=["2026-10-15"], description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., examples=["2026-10-18"], description="End date (YYYY-MM-DD)")
    department: Optional[str] = Field(default=None, examples=["Engineering"], description="Department to check overlap against")

class OverlapCheckResponse(BaseModel):
    has_overlap: bool
    overlapping_team_members: List[Dict[str, Any]]
    warning_message: Optional[str] = None
    can_proceed: bool = True

class DocumentAnalysisRequest(BaseModel):
    employee_id: str = Field(..., examples=["EMP101"])
    leave_type: LeaveTypeEnum = Field(..., examples=[LeaveTypeEnum.SICK_LEAVE])
    start_date: str = Field(..., examples=["2026-10-14"])
    end_date: str = Field(..., examples=["2026-10-16"])
    duration_days: float = Field(..., examples=[3.0])
    attachment_name: str = Field(..., examples=["medical_certificate.txt"])
    attachment_base64: str = Field(..., description="Base64 encoded string of supporting document")

class DocumentAnalysisResponse(BaseModel):
    document_type: str
    is_advisory_only: bool
    disclaimer: str
    recommendation: str = Field(..., examples=["RECOMMEND_APPROVAL"])
    confidence_score: float = Field(..., examples=[0.98])
    rationale: str
    extracted_entities: Dict[str, Any]
    validations: List[Dict[str, Any]]
    missing_or_inconsistent_info: List[str]
    analyzed_at: str

class LeaveSubmissionRequest(BaseModel):
    employee_id: str = Field(..., examples=["EMP101"])
    leave_type: LeaveTypeEnum = Field(..., examples=[LeaveTypeEnum.SICK_LEAVE])
    start_date: str = Field(..., examples=["2026-10-14"])
    end_date: str = Field(..., examples=["2026-10-16"])
    duration_days: float = Field(..., examples=[3.0])
    reason: str = Field(..., examples=["Acute viral infection and bed rest prescribed by doctor"])
    attachment_name: Optional[str] = Field(default=None, examples=["medical_cert.txt"])
    attachment_base64: Optional[str] = Field(default=None, description="Base64 encoded file attachment")

class LeaveSubmissionResponse(BaseModel):
    success: bool
    request_id: str
    transaction_status: str
    employee_id: str
    employee_name: str
    leave_type: str
    start_date: str
    end_date: str
    duration_days: float
    routing_to_approver: Dict[str, Any]
    ai_advisory: Optional[Dict[str, Any]] = None
    message: str

class ApprovalActionRequest(BaseModel):
    approver_id: str = Field(..., examples=["MGR201"])
    action: str = Field(..., examples=["APPROVE"], description="'APPROVE' or 'REJECT'")
    comments: Optional[str] = Field(default=None, examples=["Approved based on valid medical certificate and coverage arranged."])
