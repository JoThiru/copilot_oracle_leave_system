"""
Mock Database for Oracle E-Business Suite (EBS) Leave Management
Simulates Oracle HRMS / OTL (Oracle Time and Labor) database tables.
"""

from typing import Dict, List, Optional
from datetime import datetime, date

# -------------------------------------------------------------
# 1. EMPLOYEES REPOSITORY
# -------------------------------------------------------------
EMPLOYEES = {
    "EMP101": {
        "employee_id": "EMP101",
        "full_name": "Thirupathi Kumar",
        "email": "thirupathi.kumar@company.com",
        "job_title": "Senior Cloud Software Engineer",
        "department": "Engineering",
        "manager_id": "MGR201",
        "manager_name": "Sarah Connor",
        "manager_email": "sarah.connor@company.com",
        "hire_date": "2022-03-15",
        "status": "ACTIVE"
    },
    "EMP102": {
        "employee_id": "EMP102",
        "full_name": "Alex Rivera",
        "email": "alex.rivera@company.com",
        "job_title": "Software Engineer",
        "department": "Engineering",
        "manager_id": "MGR201",
        "manager_name": "Sarah Connor",
        "manager_email": "sarah.connor@company.com",
        "hire_date": "2023-06-01",
        "status": "ACTIVE"
    },
    "EMP103": {
        "employee_id": "EMP103",
        "full_name": "Priya Sharma",
        "email": "priya.sharma@company.com",
        "job_title": "HR Operations Specialist",
        "department": "Human Resources",
        "manager_id": "MGR202",
        "manager_name": "David Miller",
        "manager_email": "david.miller@company.com",
        "hire_date": "2021-11-10",
        "status": "ACTIVE"
    },
    "MGR201": {
        "employee_id": "MGR201",
        "full_name": "Sarah Connor",
        "email": "sarah.connor@company.com",
        "job_title": "Engineering Director",
        "department": "Engineering",
        "manager_id": "DIR301",
        "manager_name": "Chief Technology Officer",
        "manager_email": "cto@company.com",
        "hire_date": "2019-01-10",
        "status": "ACTIVE"
    }
}

# -------------------------------------------------------------
# 2. LEAVE BALANCES REPOSITORY (Accrual Balances in Oracle EBS)
# -------------------------------------------------------------
LEAVE_BALANCES = {
    "EMP101": {
        "employee_id": "EMP101",
        "employee_name": "Thirupathi Kumar",
        "balances": {
            "ANNUAL_LEAVE": {
                "name": "Annual Leave",
                "total_entitlement": 25.0,
                "used": 7.0,
                "pending": 0.0,
                "available": 18.0,
                "unit": "Days"
            },
            "SICK_LEAVE": {
                "name": "Sick Leave",
                "total_entitlement": 15.0,
                "used": 3.0,
                "pending": 0.0,
                "available": 12.0,
                "unit": "Days"
            },
            "MATERNITY_LEAVE": {
                "name": "Maternity / Parental Leave",
                "total_entitlement": 60.0,
                "used": 0.0,
                "pending": 0.0,
                "available": 60.0,
                "unit": "Days"
            },
            "BEREAVEMENT_LEAVE": {
                "name": "Bereavement / Compassionate Leave",
                "total_entitlement": 5.0,
                "used": 0.0,
                "pending": 0.0,
                "available": 5.0,
                "unit": "Days"
            },
            "UNPAID_LEAVE": {
                "name": "Unpaid Leave",
                "total_entitlement": 30.0,
                "used": 0.0,
                "pending": 0.0,
                "available": 30.0,
                "unit": "Days"
            }
        },
        "last_accrual_date": "2026-10-01"
    },
    "EMP102": {
        "employee_id": "EMP102",
        "employee_name": "Alex Rivera",
        "balances": {
            "ANNUAL_LEAVE": {"name": "Annual Leave", "total_entitlement": 22.0, "used": 10.0, "pending": 4.0, "available": 8.0, "unit": "Days"},
            "SICK_LEAVE": {"name": "Sick Leave", "total_entitlement": 15.0, "used": 2.0, "pending": 0.0, "available": 13.0, "unit": "Days"},
            "BEREAVEMENT_LEAVE": {"name": "Bereavement Leave", "total_entitlement": 5.0, "used": 0.0, "pending": 0.0, "available": 5.0, "unit": "Days"},
            "UNPAID_LEAVE": {"name": "Unpaid Leave", "total_entitlement": 30.0, "used": 0.0, "pending": 0.0, "available": 30.0, "unit": "Days"}
        },
        "last_accrual_date": "2026-10-01"
    }
}

# -------------------------------------------------------------
# 3. LEAVE POLICIES AND BUSINESS RULES
# -------------------------------------------------------------
LEAVE_POLICIES = {
    "ANNUAL_LEAVE": {
        "leave_type": "ANNUAL_LEAVE",
        "display_name": "Annual Vacation Leave",
        "min_notice_days": 3,
        "max_consecutive_days": 14,
        "requires_document": False,
        "document_type_required": None,
        "min_days_for_document": None,
        "allow_half_day": True,
        "description": "Standard paid vacation leave. Requires at least 3 days advance notice for requests over 2 days. Manager approval required.",
        "rules": [
            "Minimum 3 days advance notice required.",
            "Maximum 14 consecutive working days per request without VP approval.",
            "Must have sufficient available balance."
        ]
    },
    "SICK_LEAVE": {
        "leave_type": "SICK_LEAVE",
        "display_name": "Medical / Sick Leave",
        "min_notice_days": 0,
        "max_consecutive_days": 15,
        "requires_document": True,
        "document_type_required": "MEDICAL_CERTIFICATE",
        "min_days_for_document": 2,  # Document required if > 2 days
        "allow_half_day": True,
        "description": "Paid leave due to personal illness or medical appointment. A certified medical certificate is mandatory if leave exceeds 2 consecutive days.",
        "rules": [
            "For leave exceeding 2 consecutive days, a certified medical certificate from a licensed practitioner/clinic is mandatory.",
            "The certificate date range must match the requested leave duration.",
            "The document must contain: Patient Name, Doctor/Clinic Name, Official Medical Registration Number, Recommended Rest Period, and Doctor Signature/Stamp.",
            "Emergency sick leave can be reported on day 1 with retrospective documentation within 48 hours."
        ]
    },
    "MATERNITY_LEAVE": {
        "leave_type": "MATERNITY_LEAVE",
        "display_name": "Maternity Leave",
        "min_notice_days": 30,
        "max_consecutive_days": 60,
        "requires_document": True,
        "document_type_required": "BIRTH_OR_MEDICAL_CERTIFICATE",
        "min_days_for_document": 1,
        "allow_half_day": False,
        "description": "60 calendar days maternity leave. Requires official birth certificate or expected delivery medical certificate at least 30 days prior.",
        "rules": [
            "Official medical document indicating expected delivery date or birth certificate required.",
            "Notice must be submitted 30 days prior where possible."
        ]
    },
    "BEREAVEMENT_LEAVE": {
        "leave_type": "BEREAVEMENT_LEAVE",
        "display_name": "Bereavement / Compassionate Leave",
        "min_notice_days": 0,
        "max_consecutive_days": 5,
        "requires_document": True,
        "document_type_required": "DEATH_CERTIFICATE_OR_RELATION_PROOF",
        "min_days_for_document": 3,
        "allow_half_day": False,
        "description": "Paid leave granted in the event of immediate family bereavement. Up to 5 consecutive working days.",
        "rules": [
            "Immediate family only (spouse, parents, siblings, children).",
            "Proof/Certificate to be submitted to HR within 7 days of return."
        ]
    },
    "UNPAID_LEAVE": {
        "leave_type": "UNPAID_LEAVE",
        "display_name": "Unpaid Leave (Loss of Pay)",
        "min_notice_days": 7,
        "max_consecutive_days": 30,
        "requires_document": False,
        "document_type_required": None,
        "min_days_for_document": None,
        "allow_half_day": False,
        "description": "Leave without pay granted when annual balance is exhausted or for special personal reasons. Requires HR & Manager approval.",
        "rules": [
            "Requires prior exhaustion of Annual Leave.",
            "Must be approved by Line Manager and HR Operations Director."
        ]
    }
}

# -------------------------------------------------------------
# 4. EXISTING SCHEDULES / APPROVED LEAVES (FOR OVERLAP CHECKING)
# -------------------------------------------------------------
SCHEDULED_LEAVES = [
    {
        "leave_id": "LV-1001",
        "employee_id": "EMP102",
        "employee_name": "Alex Rivera",
        "department": "Engineering",
        "leave_type": "ANNUAL_LEAVE",
        "start_date": "2026-10-15",
        "end_date": "2026-10-18",
        "status": "APPROVED",
        "coverage_person": "EMP101"
    },
    {
        "leave_id": "LV-1002",
        "employee_id": "EMP103",
        "employee_name": "Priya Sharma",
        "department": "Human Resources",
        "leave_type": "ANNUAL_LEAVE",
        "start_date": "2026-10-20",
        "end_date": "2026-10-22",
        "status": "APPROVED",
        "coverage_person": None
    }
]

# -------------------------------------------------------------
# 5. SUBMITTED LEAVE REQUESTS TABLE (Simulating Oracle EBS Transaction Store)
# -------------------------------------------------------------
LEAVE_REQUESTS: Dict[str, dict] = {
    "LV-2026-001": {
        "request_id": "LV-2026-001",
        "employee_id": "EMP101",
        "employee_name": "Thirupathi Kumar",
        "department": "Engineering",
        "leave_type": "ANNUAL_LEAVE",
        "start_date": "2026-09-10",
        "end_date": "2026-09-12",
        "duration_days": 3,
        "reason": "Family vacation",
        "has_attachment": False,
        "attachment_name": None,
        "attachment_base64": None,
        "ai_analysis": None,
        "status": "APPROVED",
        "approver_id": "MGR201",
        "approver_name": "Sarah Connor",
        "approver_comments": "Approved as per team schedule.",
        "created_at": "2026-09-01T09:00:00Z",
        "updated_at": "2026-09-02T10:30:00Z"
    }
}
