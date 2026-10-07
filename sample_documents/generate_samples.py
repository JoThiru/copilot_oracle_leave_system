"""
Generates realistic supporting documents for leave request testing.
Provides plain text, Base64 strings, and JSON test payloads.
"""

import base64
import json
import os

SAMPLE_DIR = "D:/copilot_oracle_leave_system/sample_documents"

# Sample 1: Valid Medical Certificate (All checks pass -> RECOMMEND_APPROVAL)
VALID_CERT_TEXT = """================================================================================
                    EMIRATES ADVANCED HEALTHCARE CLINIC
                    Official Medical Certificate & Rest Note
                    License: DHA-MED-2024-99812
================================================================================

Date of Issue: 2026-10-14
Patient Name: Thirupathi Kumar
Employee ID: EMP101
Date of Birth: 1994-08-20

CLINICAL ASSESSMENT & DIAGNOSIS:
The above patient was examined in outpatient consultation on 2026-10-14.
Diagnosis: Acute Viral Gastroenteritis and Upper Respiratory Tract Infection.
Patient presented with acute dehydration, fever (38.8 C), and bodily fatigue.

RECOMMENDED MEDICAL REST:
The patient is medically unfit for work duties and is advised complete bed rest.
Recommended Rest Period:
Start Date: 2026-10-14
End Date:   2026-10-16
Total Duration: 3 consecutive days of medical rest.

ATTENDING MEDICAL PRACTITIONER:
Doctor Name: Dr. Robert Langdon, MD (Internal Medicine)
Medical Council Reg #: GMC-49821
Clinic Name: Emirates Advanced Healthcare Clinic, Downtown Medical Tower, Dubai, UAE

Status: VERIFIED & OFFICIALLY SIGNED
[Doctor's Stamp & Electronic Signature Applied]
================================================================================
"""

# Sample 2: Date Mismatch Certificate (Date covers August -> RECOMMEND_REJECTION)
INVALID_DATE_CERT_TEXT = """================================================================================
                    ST. JUDE COMMUNITY HEALTH CLINIC
                    Official Medical Certificate
                    License: DHA-MED-2023-1104
================================================================================

Date of Issue: 2026-08-01
Patient Name: Thirupathi Kumar
Employee ID: EMP101

DIAGNOSIS:
Patient presented with mild seasonal allergies and fatigue.

RECOMMENDED REST:
Recommended Rest Period:
Start Date: 2026-08-01
End Date:   2026-08-03
Total Duration: 3 days of medical rest.

ATTENDING PRACTITIONER:
Doctor Name: Dr. Arthur Pendelton, MBBS
Clinic Name: St. Jude Community Health Clinic
[Doctor's Stamp & Electronic Signature Applied]
================================================================================
"""

# Sample 3: Missing Signature / Incomplete Certificate (-> RECOMMEND_REVIEW)
UNVERIFIED_CERT_TEXT = """================================================================================
                    CITY CLINIC & WELLNESS CONSULT
                    Consultation Summary Note
================================================================================

Date of Issue: 2026-10-14
Patient Name: Thirupathi Kumar

Diagnosis: Headache and back pain.
Rest advised from 2026-10-14 to 2026-10-16 (3 days).

Note: Draft consultation note pending senior doctor review.
Physician: Unassigned Resident
Signature: [UNAVAILABLE - PENDING DOCTOR SIGN-OFF]
================================================================================
"""

def generate_sample_files():
    samples = [
        ("valid_medical_certificate", VALID_CERT_TEXT, "RECOMMEND_APPROVAL"),
        ("invalid_date_medical_certificate", INVALID_DATE_CERT_TEXT, "RECOMMEND_REJECTION"),
        ("unverified_medical_certificate", UNVERIFIED_CERT_TEXT, "RECOMMEND_REVIEW")
    ]

    for name, content, expected in samples:
        # Save raw txt
        txt_path = os.path.join(SAMPLE_DIR, f"{name}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Encode to Base64
        b64_str = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        # Save b64 text
        b64_path = os.path.join(SAMPLE_DIR, f"{name}_base64.txt")
        with open(b64_path, "w", encoding="utf-8") as f:
            f.write(b64_str)

        # Save ready-to-test JSON payload
        payload = {
            "employee_id": "EMP101",
            "leave_type": "SICK_LEAVE",
            "start_date": "2026-10-14",
            "end_date": "2026-10-16",
            "duration_days": 3.0,
            "attachment_name": f"{name}.txt",
            "attachment_base64": b64_str,
            "_expected_ai_outcome": expected
        }
        json_path = os.path.join(SAMPLE_DIR, f"{name}_payload.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        print(f"Generated: {name}.txt, {name}_base64.txt, {name}_payload.json (Expected: {expected})")

if __name__ == "__main__":
    generate_sample_files()
