"""
FastAPI Mock Oracle E-Business Suite (EBS) REST Service
Provides end-to-end leave management APIs, Base64 document analysis, and approval routing.
"""

from fastapi import FastAPI, HTTPException, Header, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from .models import (
    LeaveTypeEnum,
    OverlapCheckRequest,
    OverlapCheckResponse,
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    LeaveSubmissionRequest,
    LeaveSubmissionResponse,
    ApprovalActionRequest
)
from .database import (
    EMPLOYEES,
    LEAVE_BALANCES,
    LEAVE_POLICIES,
    SCHEDULED_LEAVES,
    LEAVE_REQUESTS
)
from .document_analyzer import DocumentAnalyzer

app = FastAPI(
    title="Oracle E-Business Suite (EBS) Leave Management Mock API",
    description="Mock Oracle EBS REST API for Copilot Studio and Power Automate integration with Agentic AI Document Intelligence.",
    version="1.0.0"
)

# Enable CORS for Power Platform / Copilot Studio integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_API_KEY = "EBS-SECRET-KEY-2026"

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Security check: Demonstrates API Key authorization.
    Allows empty key in local development to avoid blocking testers,
    but validates against expected key if provided.
    """
    if x_api_key is not None and x_api_key != MOCK_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired X-API-KEY provided for Oracle EBS service."
        )
    return True

# -------------------------------------------------------------
# 1. HEALTH & SYSTEM METRICS
# -------------------------------------------------------------
@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {
        "status": "ONLINE",
        "service": "Oracle EBS Leave Management Gateway",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database_connected": True
    }

# -------------------------------------------------------------
# 2. EMPLOYEE INFORMATION
# -------------------------------------------------------------
@app.get("/api/v1/employees/{employee_id}", tags=["Employees"])
def get_employee_profile(employee_id: str, authenticated: bool = Depends(verify_api_key)):
    emp_id = employee_id.upper()
    if emp_id not in EMPLOYEES:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found in Oracle EBS HRMS.")
    return EMPLOYEES[emp_id]

# -------------------------------------------------------------
# 3. LEAVE BALANCES
# -------------------------------------------------------------
@app.get("/api/v1/employees/{employee_id}/balances", tags=["Leave Balances"])
def get_leave_balances(employee_id: str, authenticated: bool = Depends(verify_api_key)):
    emp_id = employee_id.upper()
    if emp_id not in LEAVE_BALANCES:
        # Default mock balance structure if new employee
        if emp_id in EMPLOYEES:
            return {
                "employee_id": emp_id,
                "employee_name": EMPLOYEES[emp_id]["full_name"],
                "balances": {
                    "ANNUAL_LEAVE": {"name": "Annual Leave", "available": 20.0, "used": 0.0, "unit": "Days"},
                    "SICK_LEAVE": {"name": "Sick Leave", "available": 15.0, "used": 0.0, "unit": "Days"}
                }
            }
        raise HTTPException(status_code=404, detail=f"No leave accruals found for Employee '{employee_id}'.")
    return LEAVE_BALANCES[emp_id]

# -------------------------------------------------------------
# 4. LEAVE POLICIES & BUSINESS RULES
# -------------------------------------------------------------
@app.get("/api/v1/policies", tags=["Policies"])
def list_all_policies(authenticated: bool = Depends(verify_api_key)):
    return list(LEAVE_POLICIES.values())

@app.get("/api/v1/policies/{leave_type}", tags=["Policies"])
def get_policy_by_type(leave_type: str, authenticated: bool = Depends(verify_api_key)):
    lt = leave_type.upper()
    if lt not in LEAVE_POLICIES:
        raise HTTPException(status_code=404, detail=f"Policy for leave type '{leave_type}' not found.")
    return LEAVE_POLICIES[lt]

# -------------------------------------------------------------
# 5. TEAM SCHEDULE OVERLAP CHECK
# -------------------------------------------------------------
@app.post("/api/v1/leaves/check-overlap", response_model=OverlapCheckResponse, tags=["Schedules & Approvals"])
def check_team_overlap(req: OverlapCheckRequest, authenticated: bool = Depends(verify_api_key)):
    emp_id = req.employee_id.upper()
    emp_dept = req.department or (EMPLOYEES.get(emp_id, {}).get("department", "Engineering"))

    overlapping_members = []
    
    # Check scheduled leaves in the same department
    for item in SCHEDULED_LEAVES:
        if item["department"].lower() == emp_dept.lower() and item["employee_id"] != emp_id:
            # Check date overlap: (StartA <= EndB) and (EndA >= StartB)
            if (req.start_date <= item["end_date"]) and (req.end_date >= item["start_date"]):
                overlapping_members.append({
                    "employee_id": item["employee_id"],
                    "employee_name": item["employee_name"],
                    "department": item["department"],
                    "leave_type": item["leave_type"],
                    "overlapping_start": max(req.start_date, item["start_date"]),
                    "overlapping_end": min(req.end_date, item["end_date"])
                })

    has_overlap = len(overlapping_members) > 0
    warning = None
    if has_overlap:
        names = ", ".join([m["employee_name"] for m in overlapping_members])
        warning = f"Warning: {len(overlapping_members)} colleague(s) in {emp_dept} ({names}) are already scheduled on leave during this period. Ensure adequate project coverage."

    return OverlapCheckResponse(
        has_overlap=has_overlap,
        overlapping_team_members=overlapping_members,
        warning_message=warning,
        can_proceed=True  # Advisory warning; does not hard-block submission
    )

# -------------------------------------------------------------
# 6. SUPPORTING DOCUMENT ANALYSIS (AI AGENT REASONING ENGINE)
# -------------------------------------------------------------
@app.post("/api/v1/leaves/analyze-document", response_model=DocumentAnalysisResponse, tags=["Document Intelligence"])
def analyze_supporting_document(req: DocumentAnalysisRequest, authenticated: bool = Depends(verify_api_key)):
    emp_id = req.employee_id.upper()
    emp_info = EMPLOYEES.get(emp_id, {"full_name": "Employee"})
    emp_name = emp_info.get("full_name", "Employee")

    if not req.attachment_base64:
        raise HTTPException(status_code=400, detail="Missing required 'attachment_base64' payload.")

    analysis_result = DocumentAnalyzer.analyze_medical_certificate(
        base64_content=req.attachment_base64,
        employee_id=emp_id,
        employee_name=emp_name,
        requested_leave_type=req.leave_type.value,
        requested_start_date=req.start_date,
        requested_end_date=req.end_date,
        requested_days=req.duration_days
    )

    return DocumentAnalysisResponse(**analysis_result)

# -------------------------------------------------------------
# 7. SUBMIT LEAVE REQUEST
# -------------------------------------------------------------
@app.post("/api/v1/leaves/submit", response_model=LeaveSubmissionResponse, tags=["Leave Requests"])
def submit_leave_request(req: LeaveSubmissionRequest, authenticated: bool = Depends(verify_api_key)):
    emp_id = req.employee_id.upper()
    if emp_id not in EMPLOYEES:
        raise HTTPException(status_code=404, detail=f"Employee '{emp_id}' not found.")

    emp = EMPLOYEES[emp_id]
    leave_type_str = req.leave_type.value

    # Validate Leave Policy Requirements
    policy = LEAVE_POLICIES.get(leave_type_str, {})
    if policy.get("requires_document") and req.duration_days > policy.get("min_days_for_document", 0):
        if not req.attachment_base64:
            raise HTTPException(
                status_code=400,
                detail=f"Policy Violation: {policy.get('display_name')} exceeding {policy.get('min_days_for_document')} days requires a supporting medical certificate."
            )

    # Validate Leave Balance
    emp_balances = LEAVE_BALANCES.get(emp_id, {}).get("balances", {})
    balance_entry = emp_balances.get(leave_type_str)
    if balance_entry:
        available_days = balance_entry.get("available", 0.0)
        if req.duration_days > available_days:
            raise HTTPException(
                status_code=409,
                detail=f"Insufficient Balance: Requested {req.duration_days} days of {policy.get('display_name')}, but only {available_days} days are available in Oracle EBS."
            )

    # Execute AI Document Analysis if attachment is provided
    ai_advisory = None
    if req.attachment_base64:
        ai_advisory = DocumentAnalyzer.analyze_medical_certificate(
            base64_content=req.attachment_base64,
            employee_id=emp_id,
            employee_name=emp["full_name"],
            requested_leave_type=leave_type_str,
            requested_start_date=req.start_date,
            requested_end_date=req.end_date,
            requested_days=req.duration_days
        )

    # Generate Oracle EBS Request ID
    req_num = len(LEAVE_REQUESTS) + 1
    request_id = f"LV-2026-{req_num:03d}"

    # Fetch Line Manager for Approval Routing
    mgr_id = emp.get("manager_id", "MGR201")
    mgr_info = EMPLOYEES.get(mgr_id, {
        "full_name": "Line Manager",
        "email": "manager@company.com"
    })

    # Save to Mock Database
    LEAVE_REQUESTS[request_id] = {
        "request_id": request_id,
        "employee_id": emp_id,
        "employee_name": emp["full_name"],
        "department": emp["department"],
        "leave_type": leave_type_str,
        "start_date": req.start_date,
        "end_date": req.end_date,
        "duration_days": req.duration_days,
        "reason": req.reason,
        "has_attachment": bool(req.attachment_base64),
        "attachment_name": req.attachment_name,
        "attachment_base64": req.attachment_base64,
        "ai_analysis": ai_advisory,
        "status": "PENDING_APPROVAL",
        "approver_id": mgr_id,
        "approver_name": mgr_info["full_name"],
        "approver_email": mgr_info["email"],
        "approver_comments": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }

    # Deduct / hold pending balance in Oracle EBS
    if balance_entry:
        balance_entry["pending"] += req.duration_days
        balance_entry["available"] -= req.duration_days

    return LeaveSubmissionResponse(
        success=True,
        request_id=request_id,
        transaction_status="PENDING_APPROVAL",
        employee_id=emp_id,
        employee_name=emp["full_name"],
        leave_type=leave_type_str,
        start_date=req.start_date,
        end_date=req.end_date,
        duration_days=req.duration_days,
        routing_to_approver={
            "manager_id": mgr_id,
            "manager_name": mgr_info["full_name"],
            "manager_email": mgr_info["email"]
        },
        ai_advisory=ai_advisory,
        message=f"Leave request {request_id} successfully created in Oracle EBS and routed to {mgr_info['full_name']} for approval."
    )

# -------------------------------------------------------------
# 8. TRACK LEAVE REQUEST STATUS
# -------------------------------------------------------------
@app.get("/api/v1/leaves/{request_id}/status", tags=["Leave Requests"])
def get_leave_status(request_id: str, authenticated: bool = Depends(verify_api_key)):
    req_id = request_id.upper()
    if req_id not in LEAVE_REQUESTS:
        raise HTTPException(status_code=404, detail=f"Leave request '{request_id}' not found in Oracle EBS.")
    
    rec = LEAVE_REQUESTS[req_id]
    return {
        "request_id": rec["request_id"],
        "employee_id": rec["employee_id"],
        "employee_name": rec["employee_name"],
        "leave_type": rec["leave_type"],
        "start_date": rec["start_date"],
        "end_date": rec["end_date"],
        "duration_days": rec["duration_days"],
        "status": rec["status"],
        "approver_name": rec["approver_name"],
        "approver_comments": rec["approver_comments"],
        "ai_advisory_recommendation": rec["ai_analysis"].get("recommendation") if rec.get("ai_analysis") else "N/A",
        "ai_rationale": rec["ai_analysis"].get("rationale") if rec.get("ai_analysis") else "No document attached",
        "created_at": rec["created_at"],
        "updated_at": rec["updated_at"]
    }

# -------------------------------------------------------------
# 9. APPROVAL ACTION (APPROVE / REJECT)
# -------------------------------------------------------------
@app.post("/api/v1/leaves/{request_id}/action", tags=["Schedules & Approvals"])
def take_approval_action(request_id: str, act: ApprovalActionRequest, authenticated: bool = Depends(verify_api_key)):
    req_id = request_id.upper()
    if req_id not in LEAVE_REQUESTS:
        raise HTTPException(status_code=404, detail=f"Leave request '{request_id}' not found.")
    
    rec = LEAVE_REQUESTS[req_id]
    action_upper = act.action.upper()
    if action_upper not in ["APPROVE", "REJECT", "REVIEW"]:
        raise HTTPException(status_code=400, detail="Action must be 'APPROVE', 'REJECT', or 'REVIEW'.")

    rec["status"] = "APPROVED" if action_upper == "APPROVE" else ("REJECTED" if action_upper == "REJECT" else "UNDER_REVIEW")
    rec["approver_comments"] = act.comments
    rec["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Update balance counters
    emp_balances = LEAVE_BALANCES.get(rec["employee_id"], {}).get("balances", {})
    bal = emp_balances.get(rec["leave_type"])
    if bal:
        if action_upper == "APPROVE":
            bal["pending"] -= rec["duration_days"]
            bal["used"] += rec["duration_days"]
        elif action_upper == "REJECT":
            bal["pending"] -= rec["duration_days"]
            bal["available"] += rec["duration_days"]

    return {
        "success": True,
        "request_id": req_id,
        "new_status": rec["status"],
        "approver_id": act.approver_id,
        "comments": act.comments,
        "updated_at": rec["updated_at"]
    }
