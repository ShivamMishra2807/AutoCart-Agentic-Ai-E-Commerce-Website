"""
AutoCart Deterministic Seller Risk Scoring Service.
Provides transparent, rule-based, explainable compliance evaluation for seller onboarding.
Never uses protected personal characteristics as risk factors.
Does not claim to predict fraud; calculates compliance uncertainty and verification gaps to guide human administrators.
"""

import re
from typing import Dict, List, Any, Optional
from .ocr_service import is_valid_pan, is_valid_gstin, is_valid_pincode, is_valid_ifsc
from . import seller_docs


class SellerRiskScoringService:
    """
    Deterministic compliance and risk evaluation service.
    Formula:
      Risk Score = Base (10)
                   + sum(missing_document_penalties)
                   + sum(format_error_penalties)
                   + sum(cross_check_discrepancy_penalties)
                   + sum(ocr_uncertainty_penalties)
                   + sum(duplicate_flag_penalties)
      Bounded to [0, 100].
    """

    VERSION = "2.1-deterministic"

    # Configurable weights
    PENALTY_MISSING_PAN = 20
    PENALTY_MISSING_AADHAAR = 20
    PENALTY_MISSING_GST = 15
    PENALTY_MISSING_ADDRESS_PROOF = 10
    PENALTY_MISSING_BANK_PROOF = 10
    PENALTY_MISSING_STORE_PHOTO = 10
    PENALTY_MISSING_STORE_COORDS = 15

    PENALTY_INVALID_PAN_FORMAT = 25
    PENALTY_INVALID_GSTIN_FORMAT = 25
    PENALTY_INVALID_PINCODE_FORMAT = 15

    PENALTY_PAN_DOC_MISMATCH = 25
    PENALTY_PAN_GSTIN_MISMATCH = 20
    PENALTY_GSTIN_DOC_MISMATCH = 25
    PENALTY_NAME_DOC_MISMATCH = 15
    PENALTY_PINCODE_DOC_MISMATCH = 10

    PENALTY_OCR_UNREADABLE = 15
    PENALTY_DUPLICATE_APPLICATION = 30

    REQUIRED_DOCS = ['AADHAAR', 'PAN']
    OPTIONAL_DOCS = ['GST_CERTIFICATE', 'ADDRESS_PROOF', 'BANK_PROOF', 'STORE_PHOTO']

    @classmethod
    def evaluate(cls, application, documents: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Evaluates a seller application and its associated documents deterministically.
        """
        from .models import SellerApplication

        docs = list(documents if documents is not None else application.documents.all())
        by_type = {d.docType: d for d in docs}
        extracted_by_type = {
            d.docType: (d.extractedFields or {}) for d in docs if d.ocrStatus == 'DONE'
        }

        factors: List[Dict[str, Any]] = []
        missing_info: List[str] = []
        discrepancies: List[Dict[str, str]] = []
        verified_facts: List[str] = []

        raw_score = 10  # Baseline compliance review point

        # 1. Mandatory Document Completeness Checks
        for req_doc in cls.REQUIRED_DOCS:
            if req_doc not in by_type:
                missing_info.append(req_doc)
                pts = {
                    'PAN': cls.PENALTY_MISSING_PAN,
                    'AADHAAR': cls.PENALTY_MISSING_AADHAAR,
                }.get(req_doc, 20)
                raw_score += pts
                factors.append({
                    'factor': f"MISSING_{req_doc}",
                    'points': pts,
                    'category': 'Document Completeness',
                    'description': f"Required document '{req_doc.replace('_', ' ').title()}' has not been uploaded."
                })
            else:
                doc_obj = by_type[req_doc]
                if doc_obj.ocrStatus == 'UNREADABLE':
                    raw_score += cls.PENALTY_OCR_UNREADABLE
                    factors.append({
                        'factor': f"UNREADABLE_{req_doc}",
                        'points': cls.PENALTY_OCR_UNREADABLE,
                        'category': 'OCR Legibility',
                        'description': f"Document '{req_doc}' was uploaded but OCR could not read the text legibly."
                    })
                elif doc_obj.ocrStatus == 'DONE':
                    verified_facts.append(f"Document '{req_doc}' uploaded and successfully read by OCR.")

        # Supporting optional documents (reward presence without penalizing absence)
        for opt_doc in cls.OPTIONAL_DOCS:
            if opt_doc in by_type:
                doc_obj = by_type[opt_doc]
                if doc_obj.ocrStatus == 'DONE':
                    verified_facts.append(f"Optional supporting document '{opt_doc}' uploaded and verified by OCR.")
                elif doc_obj.ocrStatus == 'UNREADABLE':
                    factors.append({
                        'factor': f"UNREADABLE_{opt_doc}",
                        'points': 5,
                        'category': 'OCR Legibility',
                        'description': f"Optional document '{opt_doc}' was uploaded but OCR could not read the text legibly."
                    })

        # 2. Store Coordinates & Location Check
        if application.storeLatitude is None or application.storeLongitude is None:
            missing_info.append('STORE_LOCATION')
            raw_score += cls.PENALTY_MISSING_STORE_COORDS
            factors.append({
                'factor': 'MISSING_STORE_COORDINATES',
                'points': cls.PENALTY_MISSING_STORE_COORDS,
                'category': 'Physical Presence',
                'description': 'Store physical location has not been pinned on the delivery map.'
            })
        else:
            verified_facts.append(f"Store location confirmed at coordinates ({application.storeLatitude:.4f}, {application.storeLongitude:.4f}).")

        # 3. Form Identifier Format Checks
        pan_val = (application.pan or '').strip().upper()
        if pan_val:
            if is_valid_pan(pan_val):
                verified_facts.append(f"PAN identifier format verified: {pan_val}")
            else:
                raw_score += cls.PENALTY_INVALID_PAN_FORMAT
                factors.append({
                    'factor': 'INVALID_PAN_FORMAT',
                    'points': cls.PENALTY_INVALID_PAN_FORMAT,
                    'category': 'Identifier Format',
                    'description': f"PAN '{pan_val}' does not conform to the standard 10-character format (5 letters, 4 digits, 1 letter)."
                })
        else:
            missing_info.append('PAN_FIELD')

        gstin_val = (application.gstin or '').strip().upper()
        if gstin_val:
            if is_valid_gstin(gstin_val):
                verified_facts.append(f"GSTIN identifier format verified: {gstin_val}")
            else:
                raw_score += cls.PENALTY_INVALID_GSTIN_FORMAT
                factors.append({
                    'factor': 'INVALID_GSTIN_FORMAT',
                    'points': cls.PENALTY_INVALID_GSTIN_FORMAT,
                    'category': 'Identifier Format',
                    'description': f"GSTIN '{gstin_val}' does not match standard 15-character Indian regulatory structure."
                })
        else:
            # GSTIN is optional for unregistered/exempt sellers
            pass

        pin_val = (application.pincode or '').strip()
        if pin_val:
            if is_valid_pincode(pin_val):
                verified_facts.append(f"PIN code format verified: {pin_val}")
            else:
                raw_score += cls.PENALTY_INVALID_PINCODE_FORMAT
                factors.append({
                    'factor': 'INVALID_PINCODE_FORMAT',
                    'points': cls.PENALTY_INVALID_PINCODE_FORMAT,
                    'category': 'Identifier Format',
                    'description': f"PIN code '{pin_val}' is not a valid 6-digit Indian postal code."
                })

        # 4. Cross-Document Consistency Checks
        pan_doc_data = extracted_by_type.get('PAN', {})
        gst_doc_data = extracted_by_type.get('GST_CERTIFICATE', {})
        aad_doc_data = extracted_by_type.get('AADHAAR', {})
        addr_doc_data = extracted_by_type.get('ADDRESS_PROOF', {})

        # PAN in GSTIN check (Chars 3 to 12 of 15-char GSTIN must match PAN)
        if pan_val and gstin_val and len(gstin_val) >= 12:
            gstin_pan = gstin_val[2:12]
            if pan_val == gstin_pan:
                verified_facts.append(f"PAN '{pan_val}' correctly matches embedded GSTIN entity portion '{gstin_pan}'.")
            else:
                raw_score += cls.PENALTY_PAN_GSTIN_MISMATCH
                discrepancies.append({
                    'field': 'pan_in_gstin',
                    'expected': pan_val,
                    'found': gstin_pan,
                    'detail': f"PAN mismatch: Form PAN is '{pan_val}', but GSTIN specifies '{gstin_pan}'."
                })
                factors.append({
                    'factor': 'PAN_GSTIN_MISMATCH',
                    'points': cls.PENALTY_PAN_GSTIN_MISMATCH,
                    'category': 'Cross-Document Consistency',
                    'description': f"Submitted PAN '{pan_val}' contradicts embedded GSTIN tax PAN '{gstin_pan}'."
                })

        # PAN card document vs form check
        ocr_pan = pan_doc_data.get('pan')
        if pan_val and ocr_pan:
            if pan_val == ocr_pan.strip().upper():
                verified_facts.append(f"PAN on uploaded card matches form: {pan_val}")
            else:
                raw_score += cls.PENALTY_PAN_DOC_MISMATCH
                discrepancies.append({
                    'field': 'pan',
                    'expected': pan_val,
                    'found': ocr_pan,
                    'detail': f"Form PAN is '{pan_val}', but OCR read '{ocr_pan}' from PAN card."
                })
                factors.append({
                    'factor': 'PAN_DOCUMENT_MISMATCH',
                    'points': cls.PENALTY_PAN_DOC_MISMATCH,
                    'category': 'Cross-Document Consistency',
                    'description': f"PAN card OCR read '{ocr_pan}', differing from form '{pan_val}'."
                })

        # GST certificate document vs form check
        ocr_gst = gst_doc_data.get('gstin')
        if gstin_val and ocr_gst:
            if gstin_val == ocr_gst.strip().upper():
                verified_facts.append(f"GSTIN on certificate matches form: {gstin_val}")
            else:
                raw_score += cls.PENALTY_GSTIN_DOC_MISMATCH
                discrepancies.append({
                    'field': 'gstin',
                    'expected': gstin_val,
                    'found': ocr_gst,
                    'detail': f"Form GSTIN is '{gstin_val}', but OCR certificate read '{ocr_gst}'."
                })
                factors.append({
                    'factor': 'GSTIN_DOCUMENT_MISMATCH',
                    'points': cls.PENALTY_GSTIN_DOC_MISMATCH,
                    'category': 'Cross-Document Consistency',
                    'description': f"GST certificate OCR read '{ocr_gst}', differing from form '{gstin_val}'."
                })

        # Name match checks (Applicant vs Aadhaar and PAN)
        app_name = (application.applicantName or '').strip()
        for doc_key, doc_name_field, doc_label in [('AADHAAR', 'name', 'Aadhaar'), ('PAN', 'name', 'PAN Card')]:
            doc_info = extracted_by_type.get(doc_key, {})
            name_in_doc = doc_info.get(doc_name_field)
            if app_name and name_in_doc:
                if seller_docs._names_match(app_name, name_in_doc):
                    verified_facts.append(f"Applicant name matches {doc_label} identity: {app_name}")
                else:
                    raw_score += cls.PENALTY_NAME_DOC_MISMATCH
                    discrepancies.append({
                        'field': f"name_{doc_key.lower()}",
                        'expected': app_name,
                        'found': name_in_doc,
                        'detail': f"Name mismatch: Form has '{app_name}', but {doc_label} reads '{name_in_doc}'."
                    })
                    factors.append({
                        'factor': f"NAME_{doc_key}_MISMATCH",
                        'points': cls.PENALTY_NAME_DOC_MISMATCH,
                        'category': 'Cross-Document Consistency',
                        'description': f"Applicant name '{app_name}' does not correlate with {doc_label} name '{name_in_doc}'."
                    })

        # Pincode match check
        doc_pin = addr_doc_data.get('pincode') or aad_doc_data.get('pincode')
        if pin_val and doc_pin:
            if pin_val == doc_pin.strip():
                verified_facts.append(f"Store PIN code '{pin_val}' matches address documentation.")
            else:
                raw_score += cls.PENALTY_PINCODE_DOC_MISMATCH
                discrepancies.append({
                    'field': 'pincode',
                    'expected': pin_val,
                    'found': doc_pin,
                    'detail': f"Store PIN code is '{pin_val}', but address proof reads '{doc_pin}'."
                })
                factors.append({
                    'factor': 'PINCODE_DOCUMENT_MISMATCH',
                    'points': cls.PENALTY_PINCODE_DOC_MISMATCH,
                    'category': 'Cross-Document Consistency',
                    'description': f"Store PIN '{pin_val}' differs from address proof PIN '{doc_pin}'."
                })

        # 5. Duplicate Application Check
        if pan_val and application.id:
            dup_pan = SellerApplication.objects.filter(
                pan__iexact=pan_val
            ).exclude(id=application.id).exclude(status='REJECTED').first()
            if dup_pan:
                raw_score += cls.PENALTY_DUPLICATE_APPLICATION
                factors.append({
                    'factor': 'DUPLICATE_PAN_RECORD',
                    'points': cls.PENALTY_DUPLICATE_APPLICATION,
                    'category': 'Marketplace Integrity',
                    'description': f"PAN '{pan_val}' is already associated with existing application {dup_pan.id} ({dup_pan.companyName})."
                })

        if gstin_val and application.id:
            dup_gst = SellerApplication.objects.filter(
                gstin__iexact=gstin_val
            ).exclude(id=application.id).exclude(status='REJECTED').first()
            if dup_gst:
                raw_score += cls.PENALTY_DUPLICATE_APPLICATION
                factors.append({
                    'factor': 'DUPLICATE_GSTIN_RECORD',
                    'points': cls.PENALTY_DUPLICATE_APPLICATION,
                    'category': 'Marketplace Integrity',
                    'description': f"GSTIN '{gstin_val}' is already registered with application {dup_gst.id} ({dup_gst.companyName})."
                })

        final_score = max(0, min(100, raw_score))

        # Risk Category
        if final_score <= 25:
            risk_category = 'Low'
            rec_action = 'APPROVE_APPLICATION' if not missing_info and not discrepancies else 'REQUEST_ADDITIONAL_INFO'
        elif final_score <= 55:
            risk_category = 'Medium'
            rec_action = 'FLAG_FOR_MANUAL_REVIEW'
        else:
            risk_category = 'High'
            rec_action = 'FLAG_FOR_MANUAL_REVIEW'

        explanation = (
            f"Deterministic Risk Score: {final_score}/100 ({risk_category} Risk). "
            f"Evaluated across {len(factors)} risk factor(s), {len(missing_info)} missing field(s), "
            f"and {len(discrepancies)} cross-document discrepancy/discrepancies."
        )

        return {
            'riskScore': final_score,
            'score': final_score,
            'riskCategory': risk_category,
            'category': risk_category,
            'scoringVersion': cls.VERSION,
            'contributingFactors': factors,
            'missingInformation': missing_info,
            'validationDiscrepancies': discrepancies,
            'verifiedFacts': verified_facts,
            'recommendedAction': rec_action,
            'explanation': explanation,
        }

    calculate_risk_score = evaluate
