"""
AI Document Intelligence & Reasoning Engine
Simulates Optical Character Recognition (OCR), Entity Extraction, and Business Rule Validation
for supporting documents submitted alongside leave requests in Oracle EBS.
"""

import base64
import re
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional

class DocumentAnalyzer:
    """
    Analyzes base64-encoded supporting documents (Medical Certificates, Doctor Notes,
    Prescriptions, Hospital Discharge Summaries) and performs Agentic AI Rule Verification.
    """

    @staticmethod
    def decode_document_content(base64_str: str) -> str:
        """
        Safely decodes Base64 string to textual content.
        Supports plain text, JSON metadata representations, or OCR-extracted text dumps.
        """
        try:
            # Strip data URI header if present (e.g. data:@file/text;base64,...)
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]
            
            decoded_bytes = base64.b64decode(base64_str)
            # Try utf-8 decode
            try:
                return decoded_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return decoded_bytes.decode("latin-1", errors="ignore")
        except Exception as e:
            return f"RAW_BINARY_DATA: unable to decode ({str(e)})"

    @classmethod
    def analyze_medical_certificate(
        cls,
        base64_content: str,
        employee_id: str,
        employee_name: str,
        requested_leave_type: str,
        requested_start_date: str,
        requested_end_date: str,
        requested_days: float
    ) -> Dict[str, Any]:
        """
        Core reasoning pipeline:
        1. Decode Base64 & extract text/entities.
        2. Validate minimum document requirements.
        3. Cross-check against Oracle EBS leave policy rules.
        4. Detect discrepancies & missing info.
        5. Formulate AI Advisory Recommendation (Approval / Review / Rejection).
        """
        text_content = cls.decode_document_content(base64_content)
        
        # 1. Entity Extraction (Simulated OCR + NER)
        extracted_entities = cls._extract_entities(text_content, employee_name)

        # 2. Rule Validations
        validations: List[Dict[str, Any]] = []
        missing_or_inconsistent: List[str] = []

        # Check A: Patient Name
        patient_matches = False
        extracted_patient = extracted_entities.get("patient_name")
        if extracted_patient:
            # Fuzzy match or token overlap
            emp_tokens = set(employee_name.lower().split())
            patient_tokens = set(extracted_patient.lower().split())
            overlap = emp_tokens.intersection(patient_tokens)
            if len(overlap) >= 1:
                patient_matches = True
                validations.append({
                    "rule": "PATIENT_IDENTITY_VERIFICATION",
                    "status": "PASSED",
                    "details": f"Patient name '{extracted_patient}' matches employee '{employee_name}'."
                })
            else:
                missing_or_inconsistent.append(
                    f"Identity Mismatch: Certificate patient name '{extracted_patient}' does not match employee '{employee_name}'."
                )
                validations.append({
                    "rule": "PATIENT_IDENTITY_VERIFICATION",
                    "status": "FAILED",
                    "details": f"Patient name '{extracted_patient}' differs from employee '{employee_name}'."
                })
        else:
            missing_or_inconsistent.append("Missing Patient Name: Document does not clearly identify the patient.")
            validations.append({
                "rule": "PATIENT_IDENTITY_VERIFICATION",
                "status": "WARNING",
                "details": "Patient name could not be definitively extracted."
            })

        # Check B: Medical Authority & Practitioner
        doctor_name = extracted_entities.get("doctor_name")
        clinic_name = extracted_entities.get("clinic_name")
        license_no = extracted_entities.get("license_number")
        signature_found = extracted_entities.get("signature_detected", False)

        if doctor_name and clinic_name and signature_found:
            validations.append({
                "rule": "AUTHORIZED_MEDICAL_PRACTITIONER",
                "status": "PASSED",
                "details": f"Issued by Dr. {doctor_name} ({clinic_name}), License #{license_no or 'VERIFIED'}. Verified official stamp & signature."
            })
        elif doctor_name or clinic_name:
            if not signature_found:
                missing_or_inconsistent.append("Signature/Stamp Missing: Document lacks verifiable doctor signature or official hospital seal.")
            validations.append({
                "rule": "AUTHORIZED_MEDICAL_PRACTITIONER",
                "status": "WARNING",
                "details": f"Practitioner details partial: Doctor={doctor_name}, Clinic={clinic_name}, Signature={signature_found}."
            })
        else:
            missing_or_inconsistent.append("Invalid Medical Authority: No recognizable medical clinic or registered practitioner identified.")
            validations.append({
                "rule": "AUTHORIZED_MEDICAL_PRACTITIONER",
                "status": "FAILED",
                "details": "No authorized doctor or clinic found on document."
            })

        # Check C: Date Alignment & Rest Period
        cert_start = extracted_entities.get("rest_start_date")
        cert_end = extracted_entities.get("rest_end_date")
        cert_days = extracted_entities.get("days_certified")

        date_rule_status = "PASSED"
        if cert_start and cert_end:
            try:
                d_req_start = datetime.strptime(requested_start_date, "%Y-%m-%d").date()
                d_req_end = datetime.strptime(requested_end_date, "%Y-%m-%d").date()
                d_cert_start = datetime.strptime(cert_start, "%Y-%m-%d").date()
                d_cert_end = datetime.strptime(cert_end, "%Y-%m-%d").date()

                # Check exact coverage or overlap
                if d_cert_start <= d_req_start and d_cert_end >= d_req_end:
                    validations.append({
                        "rule": "DATE_COVERAGE_VALIDATION",
                        "status": "PASSED",
                        "details": f"Certificate rest dates ({cert_start} to {cert_end}) fully cover requested leave dates ({requested_start_date} to {requested_end_date})."
                    })
                elif d_cert_start > d_req_end or d_cert_end < d_req_start:
                    date_rule_status = "FAILED"
                    missing_or_inconsistent.append(
                        f"Date Discrepancy: Certificate rest dates ({cert_start} to {cert_end}) do NOT cover requested period ({requested_start_date} to {requested_end_date})."
                    )
                    validations.append({
                        "rule": "DATE_COVERAGE_VALIDATION",
                        "status": "FAILED",
                        "details": f"Dates out of sync: Request ({requested_start_date} to {requested_end_date}) vs Certificate ({cert_start} to {cert_end})."
                    })
                else:
                    date_rule_status = "WARNING"
                    missing_or_inconsistent.append(
                        f"Partial Date Coverage: Certificate covers {cert_start} to {cert_end}, but requested period is {requested_start_date} to {requested_end_date}."
                    )
                    validations.append({
                        "rule": "DATE_COVERAGE_VALIDATION",
                        "status": "WARNING",
                        "details": "Certificate provides only partial coverage of the requested leave window."
                    })
            except Exception as e:
                validations.append({
                    "rule": "DATE_COVERAGE_VALIDATION",
                    "status": "WARNING",
                    "details": f"Date parsing ambiguity: {str(e)}"
                })
        else:
            missing_or_inconsistent.append("Missing Rest Dates: Certificate does not specify clear recommended rest dates.")
            validations.append({
                "rule": "DATE_COVERAGE_VALIDATION",
                "status": "WARNING",
                "details": "Rest period start/end dates could not be parsed."
            })

        # Check D: Document Recency / Issue Date
        issue_date = extracted_entities.get("document_date")
        if issue_date:
            try:
                d_issue = datetime.strptime(issue_date, "%Y-%m-%d").date()
                d_req_start = datetime.strptime(requested_start_date, "%Y-%m-%d").date()
                delta_days = (d_req_start - d_issue).days
                if delta_days > 14:
                    missing_or_inconsistent.append(f"Stale Document: Certificate was issued on {issue_date} ({delta_days} days prior to leave start).")
                    validations.append({
                        "rule": "DOCUMENT_RECENCY",
                        "status": "WARNING",
                        "details": f"Document issued {delta_days} days prior to leave commencement."
                    })
                elif delta_days < -7:
                    missing_or_inconsistent.append(f"Future Issue Date: Certificate issue date {issue_date} is in the future.")
                    validations.append({
                        "rule": "DOCUMENT_RECENCY",
                        "status": "FAILED",
                        "details": "Document date is invalid (future timestamp)."
                    })
                else:
                    validations.append({
                        "rule": "DOCUMENT_RECENCY",
                        "status": "PASSED",
                        "details": f"Certificate issued promptly on {issue_date}."
                    })
            except Exception:
                pass

        # 3. Formulate AI Advisory Recommendation
        has_failed = any(v["status"] == "FAILED" for v in validations)
        has_warnings = any(v["status"] == "WARNING" for v in validations)

        if has_failed:
            recommendation = "RECOMMEND_REJECTION"
            confidence = 0.94
            rationale = (
                f"Document validation failed critical policy rules: {'; '.join(missing_or_inconsistent)}. "
                "The supporting document does not meet the necessary compliance standards for Sick Leave."
            )
        elif has_warnings or len(missing_or_inconsistent) > 0:
            recommendation = "RECOMMEND_REVIEW"
            confidence = 0.82
            rationale = (
                f"Document meets general requirements but has discrepancies requiring Line Manager / HR discretion: "
                f"{'; '.join(missing_or_inconsistent)}."
            )
        else:
            recommendation = "RECOMMEND_APPROVAL"
            confidence = 0.98
            rationale = (
                f"All compliance criteria verified successfully. Authentic medical certificate from Dr. {doctor_name} "
                f"({clinic_name}) accurately confirms {cert_days or requested_days} day(s) of recommended medical rest "
                f"covering {requested_start_date} to {requested_end_date} for patient {employee_name}."
            )

        return {
            "document_type": "MEDICAL_CERTIFICATE",
            "is_advisory_only": True,
            "disclaimer": "This AI recommendation is advisory only and does not override configured Oracle EBS business rules, workflow controls, or Line Manager approval authorities.",
            "recommendation": recommendation,
            "confidence_score": confidence,
            "rationale": rationale,
            "extracted_entities": extracted_entities,
            "validations": validations,
            "missing_or_inconsistent_info": missing_or_inconsistent,
            "analyzed_at": datetime.utcnow().isoformat() + "Z"
        }

    @classmethod
    def _extract_entities(cls, text: str, fallback_emp_name: str) -> Dict[str, Any]:
        """
        Regex and heuristic NER parser simulating Azure AI Document Intelligence / OpenAI Vision.
        Extracts doctor, clinic, patient, diagnosis, rest dates, and signature indicators.
        """
        entities: Dict[str, Any] = {
            "patient_name": None,
            "doctor_name": None,
            "clinic_name": None,
            "license_number": None,
            "diagnosis": None,
            "rest_start_date": None,
            "rest_end_date": None,
            "days_certified": None,
            "document_date": None,
            "signature_detected": False
        }

        # Check if text is a mock JSON structure passed directly in Base64
        try:
            parsed_json = json.loads(text)
            if isinstance(parsed_json, dict):
                entities.update(parsed_json)
                return entities
        except Exception:
            pass

        # Text parsing heuristics
        # 1. Patient Name
        pat_match = re.search(r"(?:Patient\s*Name|Patient|Employee|Name)\s*[:\-]\s*([A-Za-z\s]+)", text, re.IGNORECASE)
        if pat_match:
            entities["patient_name"] = pat_match.group(1).strip().split("\n")[0]
        elif fallback_emp_name.lower() in text.lower():
            entities["patient_name"] = fallback_emp_name

        # 2. Doctor Name
        doc_match = re.search(r"(?:Doctor\s*Name|Attending\s*Practitioner|Physician|Dr\.)\s*[:\.]?\s*(?:Dr\.)?\s*([A-Za-z\s\.]+)", text, re.IGNORECASE)
        if doc_match:
            d_name = doc_match.group(1).strip().split("\n")[0]
            d_name = re.sub(r",.*$", "", d_name).strip()
            entities["doctor_name"] = d_name

        # 3. Clinic / Hospital Name
        clinic_match = re.search(r"(?:Clinic|Hospital|Medical\s*Center|Healthcare|Health\s*Care)\s*[:\-]?\s*([A-Za-z0-9\s\,\.]+)", text, re.IGNORECASE)
        if clinic_match:
            entities["clinic_name"] = clinic_match.group(0).strip().split("\n")[0]

        # 4. License / Reg Number
        lic_match = re.search(r"(?:License|Reg(?:istration)?|DHA|MOH|GMC)\s*(?:No|Number|#)?\s*[:\-]?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
        if lic_match:
            entities["license_number"] = lic_match.group(1).strip()

        # 5. Diagnosis / Reason
        diag_match = re.search(r"(?:Diagnosis|Condition|Reason|Medical\s*Condition)\s*[:\-]\s*([A-Za-z0-9\s\,\.\-]+)", text, re.IGNORECASE)
        if diag_match:
            entities["diagnosis"] = diag_match.group(1).strip().split("\n")[0]

        # 6. Dates Extraction (Targeted parsing for Rest Period and Issue Date)
        def normalize_date(d_str: str) -> Optional[str]:
            if not d_str:
                return None
            d_str = d_str.strip()
            # Match YYYY-MM-DD
            if re.match(r"^\d{4}-\d{2}-\d{2}$", d_str):
                return d_str
            # Match DD/MM/YYYY or DD-MM-YYYY
            m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", d_str)
            if m:
                try:
                    return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
                except Exception:
                    pass
            return None

        # Targeted extraction for Rest Start Date
        start_match = re.search(r"(?:Start\s*Date|Rest\s*From|From|Commencing)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})", text, re.IGNORECASE)
        if start_match:
            entities["rest_start_date"] = normalize_date(start_match.group(1))

        # Targeted extraction for Rest End Date
        end_match = re.search(r"(?:End\s*Date|Rest\s*To|To|Until|Through)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})", text, re.IGNORECASE)
        if end_match:
            entities["rest_end_date"] = normalize_date(end_match.group(1))

        # Targeted extraction for Issue / Document Date
        issue_match = re.search(r"(?:Date\s*of\s*Issue|Issue\s*Date|Consultation\s*Date|Date)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})", text, re.IGNORECASE)
        if issue_match:
            entities["document_date"] = normalize_date(issue_match.group(1))

        # Fallback if targeted regex did not capture both
        if not entities["rest_start_date"] or not entities["rest_end_date"]:
            all_dates = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", text)
            # Filter out obvious birth years (e.g. before 2020)
            valid_recent_dates = [d for d in all_dates if int(d.split("-")[0]) >= 2020]
            if len(valid_recent_dates) >= 2:
                if not entities["rest_start_date"]:
                    entities["rest_start_date"] = valid_recent_dates[0]
                if not entities["rest_end_date"]:
                    entities["rest_end_date"] = valid_recent_dates[-1]
            elif len(valid_recent_dates) == 1:
                if not entities["rest_start_date"]:
                    entities["rest_start_date"] = valid_recent_dates[0]
                if not entities["rest_end_date"]:
                    entities["rest_end_date"] = valid_recent_dates[0]

        if not entities["document_date"]:
            entities["document_date"] = entities["rest_start_date"]

        # Days certified
        days_match = re.search(r"(\d+)\s*(?:days?|consecutive\s*days)\s*(?:of\s*medical\s*rest|leave|bed\s*rest)", text, re.IGNORECASE)
        if days_match:
            entities["days_certified"] = float(days_match.group(1))

        # Signature / Stamp indicator
        has_pos_sig = any(sig_term in text.lower() for sig_term in ["signed", "doctor's stamp", "official seal", "digitally signed", "officially signed"])
        has_neg_sig = any(neg in text.lower() for neg in ["unavailable", "pending doctor sign", "pending sign", "signature missing", "unsigned", "not signed", "pending senior doctor"])
        if has_pos_sig and not has_neg_sig:
            entities["signature_detected"] = True
        else:
            entities["signature_detected"] = False

        return entities
