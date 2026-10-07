"""
End-to-End Automated Test Suite for Intelligent Leave Request Agent
Validates all functional requirements of the enterprise leave management system:
1. Health Check & Employee Lookup
2. Leave Balances Retrieval
3. Policy & Business Rule Inquiries
4. Team Overlap Schedule Detection
5. Document Analysis & AI Reasoning (Approval, Review, Rejection)
6. Leave Submission with Base64 Attachments
7. Status Tracking & Approval Routing Lifecycle
"""

import sys
import json
from fastapi.testclient import TestClient
from mock_oracle_ebs_api.main import app

client = TestClient(app)

def run_tests():
    print("=" * 80)
    print("RUNNING END-TO-END VERIFICATION FOR INTELLIGENT LEAVE AGENT")
    print("=" * 80)

    # TEST 1: Health check
    print("\n[TEST 1] System Health & EBS Gateway Connectivity...")
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    print(f" -> Passed: {resp.json()}")

    # TEST 2: Employee Balances
    print("\n[TEST 2] Checking Leave Balances for EMP101 (Thirupathi Kumar)...")
    resp = client.get("/api/v1/employees/EMP101/balances")
    assert resp.status_code == 200
    data = resp.json()
    assert "ANNUAL_LEAVE" in data["balances"]
    assert "SICK_LEAVE" in data["balances"]
    print(f" -> Annual Leave Available: {data['balances']['ANNUAL_LEAVE']['available']} days")
    print(f" -> Sick Leave Available: {data['balances']['SICK_LEAVE']['available']} days")

    # TEST 3: Policy Inquiry
    print("\n[TEST 3] Inquiring Sick Leave Policy & Business Rules...")
    resp = client.get("/api/v1/policies/SICK_LEAVE")
    assert resp.status_code == 200
    policy = resp.json()
    print(f" -> Policy: {policy['display_name']}")
    print(f" -> Requires document over: {policy['min_days_for_document']} days")
    print(f" -> Rules: {json.dumps(policy['rules'], indent=2)}")

    # TEST 4: Team Schedule Overlap
    print("\n[TEST 4] Checking Overlapping Team Schedules for Oct 15-18...")
    overlap_payload = {
        "employee_id": "EMP101",
        "start_date": "2026-10-15",
        "end_date": "2026-10-18",
        "department": "Engineering"
    }
    resp = client.post("/api/v1/leaves/check-overlap", json=overlap_payload)
    assert resp.status_code == 200
    overlap_res = resp.json()
    print(f" -> Overlap Detected: {overlap_res['has_overlap']}")
    print(f" -> Overlapping Members: {overlap_res['overlapping_team_members']}")
    print(f" -> Warning Message: {overlap_res['warning_message']}")
    assert overlap_res["has_overlap"] is True
    assert overlap_res["overlapping_team_members"][0]["employee_name"] == "Alex Rivera"

    # TEST 5: Document AI Reasoning - VALID CERTIFICATE
    print("\n[TEST 5] AI Document Analysis: Valid 3-Day Sick Leave Medical Certificate...")
    with open("D:/copilot_oracle_leave_system/sample_documents/valid_medical_certificate_payload.json", "r") as f:
        valid_payload = json.load(f)
    resp = client.post("/api/v1/leaves/analyze-document", json=valid_payload)
    assert resp.status_code == 200
    doc_res = resp.json()
    print(f" -> Recommendation: {doc_res['recommendation']}")
    print(f" -> Confidence: {doc_res['confidence_score']}")
    print(f" -> Advisory Rationale: {doc_res['rationale']}")
    print(f" -> Is Advisory Only: {doc_res['is_advisory_only']}")
    assert doc_res["recommendation"] == "RECOMMEND_APPROVAL"

    # TEST 6: Document AI Reasoning - DATE MISMATCH
    print("\n[TEST 6] AI Document Analysis: Date Mismatch Certificate (August vs October)...")
    with open("D:/copilot_oracle_leave_system/sample_documents/invalid_date_medical_certificate_payload.json", "r") as f:
        invalid_payload = json.load(f)
    resp = client.post("/api/v1/leaves/analyze-document", json=invalid_payload)
    assert resp.status_code == 200
    doc_res_inv = resp.json()
    print(f" -> Recommendation: {doc_res_inv['recommendation']}")
    print(f" -> Rationale: {doc_res_inv['rationale']}")
    print(f" -> Discrepancies: {doc_res_inv['missing_or_inconsistent_info']}")
    assert doc_res_inv["recommendation"] == "RECOMMEND_REJECTION"

    # TEST 7: Document AI Reasoning - UNVERIFIED / MISSING SIGNATURE
    print("\n[TEST 7] AI Document Analysis: Unverified Certificate with Missing Signature...")
    with open("D:/copilot_oracle_leave_system/sample_documents/unverified_medical_certificate_payload.json", "r") as f:
        unver_payload = json.load(f)
    resp = client.post("/api/v1/leaves/analyze-document", json=unver_payload)
    assert resp.status_code == 200
    doc_res_unver = resp.json()
    print(f" -> Recommendation: {doc_res_unver['recommendation']}")
    print(f" -> Discrepancies: {doc_res_unver['missing_or_inconsistent_info']}")
    assert doc_res_unver["recommendation"] == "RECOMMEND_REVIEW"

    # TEST 8: Submit Leave Request with Attachment
    print("\n[TEST 8] Submitting Leave Request with Base64 Attachment to Oracle EBS...")
    submit_payload = {
        "employee_id": "EMP101",
        "leave_type": "SICK_LEAVE",
        "start_date": "2026-10-14",
        "end_date": "2026-10-16",
        "duration_days": 3.0,
        "reason": "Acute viral infection with high fever",
        "attachment_name": "valid_medical_certificate.txt",
        "attachment_base64": valid_payload["attachment_base64"]
    }
    resp = client.post("/api/v1/leaves/submit", json=submit_payload)
    assert resp.status_code == 200
    sub_res = resp.json()
    print(f" -> Leave Request ID Created: {sub_res['request_id']}")
    print(f" -> Status: {sub_res['transaction_status']}")
    print(f" -> Routed to Approver: {sub_res['routing_to_approver']['manager_name']} ({sub_res['routing_to_approver']['manager_email']})")
    print(f" -> AI Advisory Attached: {sub_res['ai_advisory']['recommendation']}")
    request_id = sub_res["request_id"]

    # TEST 9: Track Leave Status
    print(f"\n[TEST 9] Tracking Leave Request Status for {request_id}...")
    resp = client.get(f"/api/v1/leaves/{request_id}/status")
    assert resp.status_code == 200
    stat_res = resp.json()
    print(f" -> Status: {stat_res['status']}")
    print(f" -> Approver: {stat_res['approver_name']}")
    print(f" -> AI Recommendation on Record: {stat_res['ai_advisory_recommendation']}")

    # TEST 10: Approver Action (Manager Approval)
    print(f"\n[TEST 10] Manager Approving Request {request_id}...")
    act_payload = {
        "approver_id": "MGR201",
        "action": "APPROVE",
        "comments": "Approved based on valid clinic certificate and AI advisory verification."
    }
    resp = client.post(f"/api/v1/leaves/{request_id}/action", json=act_payload)
    assert resp.status_code == 200
    act_res = resp.json()
    print(f" -> New Status: {act_res['new_status']}")
    print(f" -> Comments: {act_res['comments']}")

    print("\n" + "=" * 80)
    print("ALL 10 END-TO-END TEST CASES PASSED SUCCESSFULLY (100% COMPLIANT)!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
