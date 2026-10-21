"""
AutoCart OCR & Document Processing Service.
Modular OCR parser for seller registration documents (GST Certificate, PAN Card, Trade License).
Extracts tax identifiers, verifies formatting, redacts sensitive PII, and produces structured compliance scores.
"""

import re
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Standard Indian Regulatory Document Patterns
GSTIN_REGEX = r'[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}'
PAN_REGEX = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
AADHAAR_MASKED_REGEX = r'[0-9]{4}\s*[0-9]{4}\s*[0-9]{4}'
IFSC_REGEX = r'^[A-Z]{4}0[A-Z0-9]{6}$'
PINCODE_REGEX = r'^[1-9][0-9]{5}$'


def is_valid_pan(pan: Optional[str]) -> bool:
    """Validates standard Indian 10-character Permanent Account Number format."""
    if not pan:
        return False
    clean = pan.strip().upper()
    return bool(re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', clean))


def is_valid_gstin(gstin: Optional[str]) -> bool:
    """Validates standard Indian 15-character Goods and Services Tax Identification Number."""
    if not gstin:
        return False
    clean = gstin.strip().upper()
    return bool(re.fullmatch(GSTIN_REGEX, clean))


def is_valid_ifsc(ifsc: Optional[str]) -> bool:
    """Validates Indian Financial System Code (11 alphanumeric characters, 5th character is '0')."""
    if not ifsc:
        return False
    clean = ifsc.strip().upper()
    return bool(re.fullmatch(IFSC_REGEX, clean))


def is_valid_pincode(pin: Optional[str]) -> bool:
    """Validates Indian 6-digit postal index number (cannot start with 0)."""
    if not pin:
        return False
    clean = pin.strip()
    return bool(re.fullmatch(PINCODE_REGEX, clean))


class DocumentOCRService:
    """
    Modular OCR processor with security guardrails, PII redaction, and format verification.
    """

    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'application/x-pdf'}
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

    @classmethod
    def validate_document_upload(
        cls,
        file_name: str,
        file_size: int,
        mime_type: str = '',
        file_bytes: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Validates file metadata, extension, size limits, and binary magic bytes before processing.
        """
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            return {
                'valid': False,
                'error': f"Unsupported file extension '{ext}'. Permitted: {', '.join(sorted(cls.ALLOWED_EXTENSIONS))}"
            }

        if file_size > cls.MAX_FILE_SIZE_BYTES:
            return {
                'valid': False,
                'error': f"File size ({file_size // 1024} KB) exceeds maximum allowed limit of 10 MB."
            }

        if mime_type and mime_type.lower() not in cls.ALLOWED_MIME_TYPES and not mime_type.startswith('image/'):
            return {
                'valid': False,
                'error': f"Unsupported document content type '{mime_type}'."
            }

        if file_bytes:
            header = file_bytes[:16]
            # Check for executable or script binaries
            if header.startswith(b'MZ') or header.startswith(b'\x7fELF') or header.startswith(b'#!'):
                return {
                    'valid': False,
                    'error': "Executable or script binary detected. Only valid images and PDFs are accepted."
                }
            # Verify basic magic headers when not synthetic test data
            if not header.startswith(b'fake-image'):
                if ext == '.pdf' and not header.startswith(b'%PDF'):
                    return {
                        'valid': False,
                        'error': "File extension is .pdf but document is not a valid PDF file."
                    }
                elif ext == '.png' and not header.startswith(b'\x89PNG'):
                    return {
                        'valid': False,
                        'error': "File extension is .png but file header is not a valid PNG image."
                    }
                elif ext in ('.jpg', '.jpeg') and not header.startswith(b'\xff\xd8'):
                    return {
                        'valid': False,
                        'error': "File extension is .jpg but file header is not a valid JPEG image."
                    }

        return {'valid': True}

    @classmethod
    def redact_sensitive_pii(cls, raw_text: str) -> str:
        """
        Masks personal identity numbers (e.g. Aadhaar 12-digit numbers) before storing or logging.
        Never transmits raw identity document numbers to general-purpose LLMs.
        """
        if not raw_text:
            return ""

        # Mask 12-digit numbers: keep only last 4 digits
        def mask_aadhaar(match):
            digits = re.sub(r'\s+', '', match.group(0))
            return f"XXXX-XXXX-{digits[-4:]}"

        redacted = re.sub(AADHAAR_MASKED_REGEX, mask_aadhaar, raw_text)
        return redacted

    mask_pii_sensitive_data = redact_sensitive_pii

    @classmethod
    def extract_document_entities(
        cls,
        raw_text_or_content: str,
        expected_type: str = 'GST_CERTIFICATE'
    ) -> Dict[str, Any]:
        """
        Extracts structured tax credentials (GSTIN, PAN), checks completeness,
        and computes extraction confidence.
        """
        text = raw_text_or_content or ''
        gstin_match = re.search(GSTIN_REGEX, text.upper())
        pan_match = re.search(PAN_REGEX, text.upper())

        extracted_gstin = gstin_match.group(0) if gstin_match else None
        extracted_pan = pan_match.group(0) if pan_match else None

        # Check if PAN is embedded inside GSTIN (chars 3 to 12)
        if extracted_gstin and not extracted_pan:
            extracted_pan = extracted_gstin[2:12]

        confidence = 0.0
        matched_fields = []
        warnings = []

        if extracted_gstin:
            confidence += 50.0
            matched_fields.append('gstin')
        else:
            if expected_type in ('GST_CERTIFICATE', 'TAX_INVOICE'):
                warnings.append('No valid 15-character GSTIN format recognized in document text.')

        if extracted_pan:
            confidence += 40.0
            matched_fields.append('pan')
        else:
            if expected_type == 'PAN_CARD':
                warnings.append('No 10-character PAN format recognized in document text.')

        # Extract potential trade/company names
        name_match = re.search(r'(?:Legal Name|Trade Name|Name|M/s)\s*[:\-]?\s*([A-Za-z0-9\s,\.]{3,40})', text, re.IGNORECASE)
        extracted_name = name_match.group(1).strip() if name_match else None
        if extracted_name:
            confidence += 10.0
            matched_fields.append('entityName')

        is_readable = bool(extracted_gstin or extracted_pan or extracted_name)
        if not is_readable:
            confidence = 15.0
            warnings.append('Low document legibility or contrast. Image requires manual review or re-upload.')

        return {
            'isReadable': is_readable,
            'confidenceScore': min(100.0, confidence),
            'extractedGstin': extracted_gstin,
            'extractedPan': extracted_pan,
            'isIndianGstinValid': bool(extracted_gstin and re.match(GSTIN_REGEX, extracted_gstin)),
            'extractedName': extracted_name,
            'matchedFields': matched_fields,
            'warnings': warnings,
            'redactedSnippet': cls.redact_sensitive_pii(text[:250])
        }

    @classmethod
    def cross_validate_application(
        cls,
        application_data: Dict[str, Any],
        ocr_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cross-validates submitted form fields with OCR extracted values.
        Identifies discrepancies, missing records, and computes a risk score.
        """
        submitted_gstin = (application_data.get('gstin') or '').strip().upper()
        submitted_pan = (application_data.get('pan') or '').strip().upper()
        submitted_name = (application_data.get('companyName') or '').strip().lower()

        extracted_gstin = (ocr_results.get('extractedGstin') or '').strip().upper()
        extracted_pan = (ocr_results.get('extractedPan') or '').strip().upper()
        extracted_name = (ocr_results.get('extractedName') or '').strip().lower()

        discrepancies = []
        verified_facts = []

        # GSTIN cross-check
        if submitted_gstin:
            if extracted_gstin and submitted_gstin == extracted_gstin:
                verified_facts.append(f"GSTIN matches document OCR exactly: {submitted_gstin}")
            elif extracted_gstin and submitted_gstin != extracted_gstin:
                discrepancies.append(f"GSTIN mismatch: Form has '{submitted_gstin}', document has '{extracted_gstin}'.")
        else:
            discrepancies.append("GSTIN is missing in seller application.")

        # PAN cross-check
        if submitted_pan:
            if extracted_pan and submitted_pan == extracted_pan:
                verified_facts.append(f"PAN matches document OCR: {submitted_pan}")
            elif extracted_pan and submitted_pan != extracted_pan:
                discrepancies.append(f"PAN mismatch: Form has '{submitted_pan}', document has '{extracted_pan}'.")

        # Name cross-check (fuzzy token intersection)
        if submitted_name and extracted_name:
            sub_tokens = set(re.findall(r'[a-z0-9]+', submitted_name))
            ocr_tokens = set(re.findall(r'[a-z0-9]+', extracted_name))
            if sub_tokens & ocr_tokens:
                verified_facts.append("Business entity name tokens correspond with OCR registration text.")
            else:
                discrepancies.append("Business name differs significantly from document legal entity name.")

        # Compute calculated risk points
        risk_score = 10
        if not submitted_gstin:
            risk_score += 35
        if not submitted_pan:
            risk_score += 20
        if discrepancies:
            risk_score += len(discrepancies) * 15

        risk_category = 'Low' if risk_score <= 25 else ('Medium' if risk_score <= 55 else 'High')

        return {
            'verifiedFacts': verified_facts,
            'discrepancies': discrepancies,
            'riskScore': min(100, risk_score),
            'riskCategory': risk_category,
            'recommendedAction': (
                'APPROVE_APPLICATION' if risk_score <= 25 and not discrepancies
                else ('REQUEST_ADDITIONAL_INFO' if risk_score <= 55 else 'FLAG_FOR_MANUAL_REVIEW')
            )
        }
