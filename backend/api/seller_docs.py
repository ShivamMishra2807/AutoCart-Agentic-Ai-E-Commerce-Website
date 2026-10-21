"""
Seller document processing: read an uploaded image/PDF, pull out the details we need,
and compare them with what the seller typed into the application form.

Privacy rules (Aadhaar Act / UIDAI):
- Only a MASKED Aadhaar is accepted. A file that shows all 12 digits is rejected.
- Only the last 4 digits are ever stored. Saved text is redacted first.
- Bank account numbers are kept as last 4 digits only.

OCR is free and local (rapidocr-onnxruntime, pip only). If it is missing or fails,
the document is flagged for manual review. Nothing here ever crashes an upload.
"""

import os
import re
import logging
from typing import Any, Dict, List, Optional, Tuple

from .ocr_service import DocumentOCRService, GSTIN_REGEX, PAN_REGEX

logger = logging.getLogger(__name__)

ALL_DOC_TYPES = ['AADHAAR', 'PAN', 'GST_CERTIFICATE', 'ADDRESS_PROOF', 'BANK_PROOF', 'STORE_PHOTO']
REQUIRED_DOC_TYPES = ['AADHAAR', 'PAN']
MANDATORY_DOC_TYPES = ['AADHAAR', 'PAN']
OCR_DOC_TYPES = {'AADHAAR', 'PAN', 'GST_CERTIFICATE', 'ADDRESS_PROOF', 'BANK_PROOF'}

AADHAAR_PLAIN = re.compile(r'(?<![\dXx*])(\d{4})[\s-]?(\d{4})[\s-]?(\d{4})(?!\d)')
AADHAAR_MASKED = re.compile(r'[Xx*]{4}[\s-]*[Xx*]{4}[\s-]*(\d{4})')
DOB_RE = re.compile(r'(\d{2}[/-]\d{2}[/-]\d{4})')
PIN_RE = re.compile(r'(?<!\d)([1-9]\d{5})(?!\d)')
IFSC_RE = re.compile(r'\b([A-Z]{4}0[A-Z0-9]{6})\b')
ACCOUNT_RE = re.compile(r'(?<!\d)(\d{9,18})(?!\d)')

_NOT_NAMES = {
    'government', 'govt', 'india', 'aadhaar', 'unique', 'identification', 'authority', 'male', 'female', 'transgender',
    'dob', 'year', 'birth', 'address', 'vid', 'download', 'date', 'issued', 'income', 'tax', 'department', 'permanent',
    'account', 'number', 'card', 'father', 'name', 'signature', 'of', 'the', 'to', 'mera', 'aadhaar', 'enrolment', 'help',
    'bharat', 'sarkar', 'shri', 'smt', 'dr', 'mr', 'mrs', 'identity', 'national', 'republic', 'valid', 'parent', 'guardian',
    'verified', 'unverified', 'digitally', 'signed', 'hrr', 'dept', 'incometaxdept', 'holder', 'nsdl', 'uti', 'utitsl',
    'egov', 'protean', 'qr', 'code', 'scanning', 'facilitate', 'authenticity', 'certified', 'epan', 'not', 'photo',
    'seal', 'officer', 'incometax', 'time', 'gmt', 'ist', 'rule', 'rules', 'penalty', 'law', 'tinpanst', 'karvy', 'alankit',
}

_HEADER_SUBSTRINGS = (
    'govt', 'india', 'income', 'tax', 'dept', 'depart', 'permanent', 'account', 'card',
    'bharat', 'sarkar', 'father', 'signature', 'holder', 'republic', 'authority',
    'unique', 'identification', 'aadhaar', 'enroll', 'enrol', 'download', 'valid',
    'date', 'birth', 'gender', 'female', 'male', 'transgender', 'photo', 'address', 'pata',
    'www.', 'help@', '1947', 'republicofindia', 'verified', 'unverified', 'digitally', 'signed',
    'hrr', 'qr', 'scanning', 'facilitate', 'incometaxdept', 'authenticity', 'certified', 'epan'
)

_engine = None


# ---------------------------------------------------------------- OCR ------

def _get_engine():
    global _engine
    if _engine is None:
        from rapidocr_onnxruntime import RapidOCR  # imported lazily: it is heavy
        _engine = RapidOCR()
    return _engine


def _images_from_file(path: str, mime: str):
    """Yield numpy RGB arrays: one per image, or the first pages of a PDF."""
    import numpy as np
    from PIL import Image, ImageOps

    is_pdf = path.lower().endswith('.pdf') or 'pdf' in (mime or '').lower()
    if is_pdf:
        rendered = False
        try:
            import pymupdf as fitz
            doc = fitz.open(path)
            for i in range(min(len(doc), 2)):
                page = doc[i]
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                yield np.array(img)
            doc.close()
            rendered = True
        except Exception as e:
            logger.warning("PyMuPDF PDF rendering failed: %s", e)

        if not rendered:
            try:
                import pypdfium2 as pdfium
                pdf = pdfium.PdfDocument(path)
                for i in range(min(len(pdf), 2)):
                    yield np.array(pdf[i].render(scale=2).to_pil().convert('RGB'))
            except Exception as e:
                logger.warning("pypdfium2 rendering failed: %s", e)
    else:
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img)
            img = img.convert('RGB')
            longest = max(img.size)
            if longest > 1800:
                ratio = 1800 / longest
                img = img.resize((int(img.width * ratio), int(img.height * ratio)))
            yield np.array(img)
        except Exception as e:
            logger.warning("Image loading error for %s: %s", path, e)


def _orient_image(img_arr, engine):
    """Detects if an image is sideways (vertical text lines) and auto-rotates to upright orientation."""
    try:
        import numpy as np
        from PIL import Image

        det_func = None
        if hasattr(engine, 'text_detector'):
            det_func = engine.text_detector
        elif hasattr(engine, 'text_det'):
            det_func = engine.text_det

        if det_func is None:
            return img_arr

        boxes, _ = det_func(img_arr)
        if boxes is None or len(boxes) == 0:
            return img_arr

        vert = 0
        horiz = 0
        for b in boxes:
            w = np.linalg.norm(b[1] - b[0])
            h = np.linalg.norm(b[3] - b[0])
            if h > 1.2 * w:
                vert += 1
            elif w > 1.2 * h:
                horiz += 1

        if vert <= horiz:
            return img_arr

        pil_img = Image.fromarray(img_arr)
        cand_90 = pil_img.rotate(90, expand=True)
        cand_270 = pil_img.rotate(270, expand=True)

        header_kws = ('income', 'tax', 'department', 'govt', 'india', 'permanent', 'account', 'aadhaar', 'unique', 'government', 'gstin')
        footer_kws = ('signature', 'birth', 'dob', 'helpdesk', '1947', 'pata', 'address')

        best_cand = cand_90
        best_score = -9999

        for cand in (cand_90, cand_270):
            cand_arr = np.array(cand)
            res, _ = engine(cand_arr)
            if not res:
                continue
            n = len(res)
            score = 0
            for idx, item in enumerate(res):
                t_low = item[1].lower()
                conf = float(item[2])
                score += conf * 2
                if any(k in t_low for k in header_kws):
                    score += 15 if idx < n / 2 else -15
                if any(k in t_low for k in footer_kws):
                    score += 10 if idx >= n / 2 else -10
            if score > best_score:
                best_score = score
                best_cand = cand

        return np.array(best_cand)
    except Exception as e:
        logger.warning('Auto-orient error: %s', e)
        return img_arr


def _group_ocr_items_into_lines(items: List[Any]) -> List[Dict[str, Any]]:
    """
    Groups OCR bounding-box items that lie on the same horizontal line.
    Within each horizontal line, sorts items from left to right and joins texts with a single space.
    Returns reconstructed line dicts with {'text': str, 'score': float, 'items': list}.
    """
    if not items:
        return []

    enriched = []
    for it in items:
        if isinstance(it, (list, tuple)):
            box = it[0] if len(it) > 0 else None
            text = str(it[1]).strip() if len(it) > 1 else ''
            try:
                score = float(it[2]) if len(it) > 2 else 0.8
            except (ValueError, TypeError):
                score = 0.8
        elif isinstance(it, dict):
            box = it.get('box')
            text = str(it.get('text', '')).strip()
            score = float(it.get('score', 0.8))
        else:
            continue

        if not text:
            continue

        if box and len(box) >= 4:
            try:
                xs = [float(p[0]) for p in box]
                ys = [float(p[1]) for p in box]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                h = max(1.0, max_y - min_y)
                cy = (min_y + max_y) / 2.0
            except Exception:
                min_x, max_x, min_y, max_y, cy, h = 0.0, 0.0, 0.0, 0.0, 0.0, 1.0
        else:
            min_x, max_x, min_y, max_y, cy, h = 0.0, 0.0, 0.0, 0.0, 0.0, 1.0

        enriched.append({
            'text': text,
            'score': score,
            'box': box,
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'cy': cy,
            'h': h
        })

    # Sort items primarily from top to bottom
    enriched.sort(key=lambda x: (x['min_y'], x['min_x']))

    lines: List[Dict[str, Any]] = []
    for it in enriched:
        placed = False
        for line in lines:
            line_min_y = min(m['min_y'] for m in line['items'])
            line_max_y = max(m['max_y'] for m in line['items'])
            line_h = max(1.0, line_max_y - line_min_y)
            avg_cy = sum(m['cy'] for m in line['items']) / len(line['items'])

            # Vertical overlap:
            overlap_y = max(0.0, min(line_max_y, it['max_y']) - max(line_min_y, it['min_y']))
            min_box_h = min(line_h, it['h'])
            overlap_ratio = overlap_y / min_box_h if min_box_h > 0 else 0

            if overlap_ratio >= 0.45 or abs(it['cy'] - avg_cy) <= 0.45 * min_box_h:
                line['items'].append(it)
                placed = True
                break
        if not placed:
            lines.append({'items': [it]})

    # Sort lines by average Y
    lines.sort(key=lambda l: sum(m['min_y'] for m in l['items']) / len(l['items']))

    # Within each line, sort horizontally by min_x and join text with single space
    reconstructed = []
    for line in lines:
        line['items'].sort(key=lambda m: m['min_x'])
        line_text = ' '.join(m['text'] for m in line['items'] if m['text'])
        avg_score = sum(m['score'] for m in line['items']) / len(line['items'])
        reconstructed.append({
            'text': line_text,
            'score': avg_score,
            'items': line['items']
        })
    return reconstructed


def read_text(path: str, mime: str = '') -> Dict[str, Any]:
    """Returns {'status': DONE | UNREADABLE | OCR_UNAVAILABLE, 'text': str, 'items': list}."""
    try:
        engine = _get_engine()
    except Exception as exc:  # missing package or model files
        logger.warning('OCR engine unavailable: %s', exc)
        return {'status': 'OCR_UNAVAILABLE', 'text': '', 'items': []}
    try:
        lines: List[str] = []
        all_items: List[Dict[str, Any]] = []
        for img in _images_from_file(path, mime):
            img = _orient_image(img, engine)
            result, _ = engine(img)
            # Layout-aware line grouping to preserve horizontal word boundaries
            grouped = _group_ocr_items_into_lines(result or [])
            if grouped:
                for grp in grouped:
                    lines.append(grp['text'])
                    for item in grp['items']:
                        all_items.append({
                            'text': item['text'],
                            'score': item['score'],
                            'box': item['box']
                        })
            else:
                for item in (result or []):
                    line_text = str(item[1]).strip()
                    try:
                        score = float(item[2])
                    except (ValueError, TypeError):
                        score = 0.80
                    lines.append(line_text)
                    all_items.append({
                        'text': line_text,
                        'score': score,
                        'box': item[0]
                    })
        text = '\n'.join(lines).strip()
        return {'status': 'DONE' if text else 'UNREADABLE', 'text': text, 'items': all_items}
    except Exception as exc:
        logger.warning('OCR failed for %s: %s', os.path.basename(path), exc)
        return {'status': 'UNREADABLE', 'text': '', 'items': []}


# ------------------------------------------------------------- parsers -----

def _pretty_name(line: str) -> str:
    cleaned = re.sub(r'^(?:name\s*[:\-]|to\s*[:\-])\s*', '', line.strip(), flags=re.I)
    cleaned = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', cleaned.strip())
    return ' '.join(w.capitalize() for w in cleaned.split() if w)


def _looks_like_name(line: str) -> bool:
    if not line:
        return False
    clean = re.sub(r'^[/:#\-\s]+|[/:#\-\s]+$', '', line).strip()
    if len(clean) < 3:
        return False
    # Names in Latin transliteration contain at least one vowel; consonant acronyms (e.g. HRR, NSDL) are rejected
    if not re.search(r'[aeiouy]', clean, re.I):
        return False
    # Names cannot contain digits
    if re.search(r'\d', clean):
        return False
    clean_low = clean.lower()
    no_space = re.sub(r'[^a-z0-9]', '', clean_low)
    if any(h in no_space for h in _HEADER_SUBSTRINGS):
        return False
    # Reject lines containing explicit non-name phrases
    if any(p in clean_low for p in ['signature', 'verified', 'not verified', 'income tax', 'date of birth', 'permanent account', 'tax dept']):
        return False
    words = re.findall(r"[A-Za-z][A-Za-z.'-]*", clean)
    if not 1 <= len(words) <= 5:
        return False
    if re.sub(r"[A-Za-z .'-]", '', clean):
        return False
    return not any(w.lower().strip('.') in _NOT_NAMES for w in words)


_DISCLAIMER_PATTERNS = [
    r'proof of identity',
    r'not (?:of )?citizenship',
    r'not a proof of',
    r'verify (?:identity|authenticity)',
    r'qr code',
    r'keep your (?:mobile|email)',
    r'to update',
    r'visit (?:uidai|nearest)',
    r'toll[- ]?free',
    r'mera aadhaar',
    r'electronically generated',
    r'unique identification authority',
    r'government of india',
    r'enrolment (?:no|number)',
    r'download date',
    r'generation date',
    r'helpdesk',
    r'1947',
    r'www\.',
    r'uidai\.gov\.in',
    r'help@',
    r'valid throughout',
]


def parse_aadhaar(text: str, items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Layout- and score-aware extraction of details from a masked Aadhaar document.
    Prevents UIDAI disclaimer pollution in address, extracts real English name adjacent to DOB,
    and returns field-level confidence scores.
    """
    masked = AADHAAR_MASKED.search(text)
    if AADHAAR_PLAIN.search(text) and not masked:
        return {'unmasked': True}

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    items_list = list(items or [])

    # Map text line to score if items available
    line_scores = {}
    for it in items_list:
        t_clean = it['text'].strip()
        if t_clean and t_clean not in line_scores:
            line_scores[t_clean] = it.get('score', 0.80)

    # 1. Identify True DOB line
    # A true DOB line contains an explicit date DD/MM/YYYY or DD-MM-YYYY, not generic disclaimer text
    dob = None
    dob_score = 0.85
    dob_line_idx = None

    for idx, line in enumerate(lines):
        # Exclude disclaimer sentences
        if any(w in line.lower() for w in ['not of citizenship', 'proof of identity', 'should be used with verification']):
            continue
        d_match = DOB_RE.search(line)
        if d_match:
            # Check calendar validity: DD <= 31, MM <= 12, YYYY between 1940 and 2026
            parts = re.split(r'[/-]', d_match.group(1))
            if len(parts) == 3:
                try:
                    d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                    if 1 <= d <= 31 and 1 <= m <= 12 and 1920 <= y <= 2026:
                        dob = f"{d:02d}/{m:02d}/{y:04d}"
                        dob_line_idx = idx
                        dob_score = line_scores.get(line, 0.88)
                        break
                except (ValueError, TypeError):
                    pass

    # 2. Extract Applicant Name
    # In Aadhaar front panel, the true English name is directly above the DOB line.
    name = None
    name_score = 0.85

    # Check candidates immediately preceding the confirmed DOB line
    if dob_line_idx is not None and dob_line_idx > 0:
        # Check 1 to 3 lines directly above DOB
        start_search = max(0, dob_line_idx - 3)
        candidates = list(range(start_search, dob_line_idx))
        candidates.reverse()  # Check line directly above (dob_line_idx - 1) first!

        for c_idx in candidates:
            cand_text = lines[c_idx]
            cand_clean = _pretty_name(cand_text)
            c_score = line_scores.get(cand_text, 0.80)

            # Skip lines matching header keywords or disclaimers
            cand_lower = cand_text.lower()
            if any(h in cand_lower for h in ['government', 'authority', 'india', 'unique', 'enrolment', 'vid', 'aadhaar', 'dob', 'male', 'female']):
                continue

            # Must look like a valid name and have high confidence
            if _looks_like_name(cand_text) and c_score >= 0.70:
                words = cand_clean.split()
                # Favor names with 2-4 words and reasonable letter structure
                if len(words) >= 2:
                    name = cand_clean
                    name_score = c_score
                    break
                elif len(words) == 1 and not name:
                    name = cand_clean
                    name_score = c_score

    # Check for explicit name label: "Name: ..." or "To: ..."
    if not name:
        for line in lines:
            labeled = re.search(r'(?:^|\b)(?:name|to)\s*[:\-]\s*([A-Za-z\s.\'-]{3,40})', line, re.I)
            if labeled:
                cand = labeled.group(1).strip()
                if _looks_like_name(cand) and line_scores.get(line, 0.80) >= 0.70:
                    cand_words = _pretty_name(cand).split()
                    if len(cand_words) >= 2:
                        name = _pretty_name(cand)
                        name_score = line_scores.get(line, 0.85)
                        break

    # Fallback to high-confidence candidate passing name check with 2+ words
    if not name:
        for it in items_list:
            t = it['text'].strip()
            if _looks_like_name(t) and it.get('score', 0) >= 0.75:
                words = _pretty_name(t).split()
                if 2 <= len(words) <= 4:
                    name = _pretty_name(t)
                    name_score = it.get('score', 0.80)
                    break

    # 3. Extract Gender
    gender = None
    gender_score = 0.85
    g_match = re.search(r'\b(male|female|transgender)\b', text, re.I)
    if g_match:
        gender = g_match.group(1).title()
        for it in items_list:
            if re.search(rf'\b{re.escape(g_match.group(1))}\b', it['text'], re.I):
                gender_score = it.get('score', 0.85)
                break

    # 4. Extract Residential Address and PIN (with strict UIDAI disclaimer cutoff)
    residential_address = None
    residential_pin = None
    address_score = 0.85
    pin_score = 0.85

    addr_header_idx = None
    for idx, l in enumerate(lines):
        if re.search(r'^(?:address|pata|addr)\s*[:\-]|\b(?:address|pata)\s*:', l, re.I):
            addr_header_idx = idx
            break

    if addr_header_idx is not None:
        addr_lines = []
        scores_collector = []
        # Strip header keyword and preceding text (such as "SW/ MALE Address:")
        first_line = re.sub(r'^.*?\b(?:address|pata|addr)\s*[:\-,\s]*', '', lines[addr_header_idx], flags=re.I).strip()
        first_line = re.sub(r'^(?:[sS][wW][/\\-]?\s*|(?:male|female|transgender)\s*|[,\-:\s]+)+', '', first_line, flags=re.I).strip()
        if first_line and len(first_line) > 3 and not any(re.search(pat, first_line, re.I) for pat in _DISCLAIMER_PATTERNS):
            addr_lines.append(first_line)
            scores_collector.append(line_scores.get(lines[addr_header_idx], 0.80))
            first_pin = PIN_RE.search(first_line)
            if first_pin:
                residential_pin = first_pin.group(1)
                pin_score = line_scores.get(lines[addr_header_idx], 0.85)

        # Collect subsequent lines until disclaimer or PIN line
        for l in lines[addr_header_idx + 1:]:
            # STRICT STOP: Check if disclaimer pattern or UIDAI footer keywords appear
            if any(re.search(pat, l, re.I) for pat in _DISCLAIMER_PATTERNS):
                break
            if any(w in l.lower() for w in ['not of citizenship', 'proof of identity', 'uidai.gov.in', '1947', 'help@', 'xxxx xxxx', 'vid:']):
                break
            # Skip OCR artifacts/gibberish lines
            if len(l) <= 2 or re.search(r'^[/a-zA-Z0-9]{1,4}$', l.strip()) or re.search(r'xml|aheafer', l, re.I):
                continue
            # Skip lines that are mostly garbled characters or Hindi font artifacts in Latin OCR
            words_in_l = re.findall(r'[A-Za-z]+', l)
            if words_in_l and all(len(w) <= 2 for w in words_in_l):
                continue

            l_clean = re.sub(r'^[:\-\s]+', '', l).strip()
            l_clean = re.sub(r'^(?:[sS][wW][/\\-]?\s*|(?:male|female|transgender)\s*|[,\-:\s]+)+', '', l_clean, flags=re.I).strip()
            l_score = line_scores.get(l, 0.80)

            # Check if this line contains the 6-digit Indian PIN code
            pin_match = PIN_RE.search(l_clean)
            if pin_match:
                residential_pin = pin_match.group(1)
                pin_score = l_score
                addr_lines.append(l_clean)
                scores_collector.append(l_score)
                # Once we encounter the PIN code line in the address block, the address is complete!
                break

            addr_lines.append(l_clean)
            scores_collector.append(l_score)

        if addr_lines:
            candidate_address = ', '.join(addr_lines).strip()
            candidate_address = re.sub(r'\s+', ' ', candidate_address)
            candidate_address = re.sub(r',\s*,', ',', candidate_address)
            # Remove leading "SW/ MALE Address:," or stray gender tokens if somehow still present
            candidate_address = re.sub(r'^(?:[sS][wW][/\\-]?\s*|(?:male|female|transgender)\s*|address\s*[:\-,]?\s*|[,\-:\s]+)+', '', candidate_address, flags=re.I).strip()
            # Clean OCR artifacts on state and district names (e.g. EMaharashtra -> Maharashtra, EAkola -> Akola)
            candidate_address = re.sub(r'\b[E|e](Maharashtra|Gujarat|Karnataka|Rajasthan|Delhi|Punjab|Haryana|Telangana|Tamil Nadu|Kerala|Madhya Pradesh|Uttar Pradesh|Bihar|West Bengal|Akola|Thane|Kalyan|Pune|Mumbai)\b', r'\1', candidate_address, flags=re.I)
            if len(candidate_address) >= 10:
                residential_address = candidate_address[:250]
                if scores_collector:
                    address_score = sum(scores_collector) / len(scores_collector)

    # Fallback PIN code search if not caught in address block
    if not residential_pin:
        # Check bottom lines of document
        for it in reversed(items_list):
            p_match = PIN_RE.search(it['text'])
            if p_match:
                # Exclude enrolment numbers or dates
                if not re.search(r'enrolment|date|mobile|phone', it['text'], re.I):
                    residential_pin = p_match.group(1)
                    pin_score = it.get('score', 0.85)
                    break

    # Masked Aadhaar last 4 digits
    last4 = masked.group(1) if masked else None
    masked_str = f"XXXX-XXXX-{last4}" if last4 else None
    aadhaar_score = 0.85
    if masked_str:
        for it in items_list:
            if last4 and last4 in it['text'] and ('X' in it['text'].upper() or '*' in it['text']):
                aadhaar_score = it.get('score', 0.88)
                break

    # Build field-level confidence map (0 to 100%)
    field_confidences = {}
    if name:
        field_confidences['name'] = round(float(name_score) * 100, 1)
    if dob:
        field_confidences['dob'] = round(float(dob_score) * 100, 1)
    if gender:
        field_confidences['gender'] = round(float(gender_score) * 100, 1)
    if residential_address:
        field_confidences['residentialAddress'] = round(float(address_score) * 100, 1)
    if residential_pin:
        field_confidences['residentialPincode'] = round(float(pin_score) * 100, 1)
    if masked_str:
        field_confidences['aadhaarMasked'] = round(float(aadhaar_score) * 100, 1)
        field_confidences['aadhaarLast4'] = round(float(aadhaar_score) * 100, 1)

    # Automatically resolve residential city, district, and state from PIN code & address
    residential_city = None
    residential_district = None
    residential_state = None
    localities = []
    is_ambiguous = False

    if residential_pin:
        try:
            from .location_service import lookup_pincode_details
            loc_data = lookup_pincode_details(residential_pin, address_context=residential_address)
            if loc_data and loc_data.get('valid'):
                residential_city = loc_data.get('city')
                residential_district = loc_data.get('district')
                residential_state = loc_data.get('state')
                localities = loc_data.get('localities') or []
                is_ambiguous = loc_data.get('isAmbiguous', False)
                if residential_city:
                    field_confidences['residentialCity'] = round(float(pin_score) * 100, 1)
                if residential_state:
                    field_confidences['residentialState'] = round(float(pin_score) * 100, 1)
        except Exception as e:
            logger.debug("Automatic PIN lookup failed during Aadhaar parsing: %s", e)

    return {
        'name': name,
        'dob': dob,
        'gender': gender,
        'residentialAddress': residential_address,
        'residentialPincode': residential_pin,
        'residentialCity': residential_city,
        'residentialDistrict': residential_district,
        'residentialState': residential_state,
        'city': residential_city,
        'state': residential_state,
        'localities': localities,
        'isAmbiguous': is_ambiguous,
        # Keep commercial store address separate from residential address
        'address': None,
        'pincode': None,
        'aadhaarLast4': last4,
        'aadhaarMasked': masked_str,
        'fieldConfidences': field_confidences,
    }


_INDIAN_SURNAMES = {
    'mishra', 'sharma', 'verma', 'gupta', 'singh', 'kumar', 'patel', 'shah', 'jain', 'yadav',
    'tiwari', 'pandey', 'pathak', 'tripathi', 'shukla', 'dubey', 'chaubey', 'joshi', 'bhat',
    'bhatt', 'reddy', 'nair', 'menon', 'pillai', 'rao', 'iyer', 'iyengar', 'das', 'chatterjee',
    'banerjee', 'mukherjee', 'bose', 'ghosh', 'sen', 'roy', 'dey', 'dutta', 'agrawal', 'agarwal',
    'aggrawal', 'kulkarni', 'deshmukh', 'patil', 'pawar', 'shinde', 'gaikwad', 'choudhary',
    'chaudhary', 'meena', 'khan', 'ahmed', 'ansari', 'ali', 'malhotra', 'kapoor', 'khanna',
    'chopra', 'bhatia', 'arora', 'grover', 'saxena', 'mathur', 'srivastava', 'rastogi', 'seth',
    'bansal', 'mittal', 'garg', 'goel', 'goyal', 'jindal', 'singhal', 'chawla', 'sood', 'mahajan',
    'thakur', 'chauhan', 'rathore', 'rajput', 'shekhawat', 'nayak', 'swain', 'mohanty', 'dasgupta',
    'bhattacharya', 'chattopadhyay', 'mukhopadhyay', 'bandyopadhyay', 'chavan', 'kale', 'more',
    'jadav', 'soni', 'khatri', 'maheshwari', 'modi', 'somani', 'lodha', 'oswal', 'porwal',
    'bhansali', 'kothari', 'choraria', 'munot', 'surana', 'bardia', 'lunawat', 'gang', 'jhabak'
}

_INDIAN_NAME_COMPONENTS = {
    'chandra', 'prakash', 'kumar', 'kumari', 'narayan', 'prasad', 'nand', 'kishor', 'kishore',
    'anand', 'lal', 'kant', 'bhai', 'ben', 'ram', 'deo', 'dutt', 'nath', 'mani', 'mohan',
    'veer', 'deep', 'jeet', 'raj', 'swarup', 'shankar', 'charan', 'sundar', 'dayal', 'dhar',
    'ratan', 'ballabh', 'vallabh', 'datt', 'babu', 'rani', 'devi', 'shekhar', 'bhushan',
    'ratna', 'sen', 'vardhan', 'vardhana', 'pal', 'preet', 'inder', 'vinder'
}


def _split_single_token(tok: str, candidate_words: List[str]) -> Tuple[List[str], bool]:
    """Splits a single token if it contains glued words, preserving proper names and boundaries."""
    # 1. CamelCase splitting (e.g. 'ShivamChandraprakashMishra')
    c_parts = re.findall(r'[A-Z][a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)|[a-z]+', tok)
    if len(c_parts) > 1 and len(tok) >= 6:
        final_parts = []
        is_amb = False
        for p in c_parts:
            sub, amb = _split_single_token(p, candidate_words)
            if amb:
                is_amb = True
            final_parts.extend(sub)
        return final_parts, is_amb

    t_low = tok.lower()
    if len(t_low) < 7:
        return [tok], False

    # 2. Corroborating candidate words from context/documents
    if candidate_words:
        known = [w for w in candidate_words if len(w) >= 3 and w.lower() in t_low]
        if known:
            sorted_cands = sorted(known, key=len, reverse=True)

            def backtrack(pos: int) -> Optional[List[str]]:
                if pos == len(t_low):
                    return []
                for cand in sorted_cands:
                    c_low = cand.lower()
                    if t_low.startswith(c_low, pos):
                        sub = backtrack(pos + len(c_low))
                        if sub is not None:
                            return [c_low] + sub
                return None

            res = backtrack(0)
            if res and len(res) > 1 and ''.join(res) == t_low:
                return res, False

    # 3. Surname match at end (e.g. 'chandraprakashmishra' -> 'chandraprakash' + 'mishra')
    for sur in sorted(_INDIAN_SURNAMES, key=len, reverse=True):
        if t_low.endswith(sur) and len(t_low) >= len(sur) + 3:
            prefix = t_low[:-len(sur)]
            return [prefix, sur], False

    is_ambig = len(t_low) > 14
    return [tok], is_ambig


def _split_glued_pan_names(name: Optional[str], father: Optional[str],
                           context_names: Optional[List[str]] = None,
                           doc_text: str = '') -> Tuple[Optional[str], Optional[str], bool]:
    """
    Splits OCR-glued names into separate words with proper boundaries.
    Preserves existing spaced names, patronymics, and family surnames across all PAN cards.
    """
    if not name and not father:
        return name, father, False

    cands = set(_INDIAN_SURNAMES)
    if context_names:
        for cn in context_names:
            if cn:
                for w in re.findall(r'[A-Za-z]{3,}', cn):
                    cands.add(w.lower())
    if doc_text:
        for w in re.findall(r'[A-Za-z]{4,}', doc_text):
            w_l = w.lower()
            if w_l not in ('income', 'department', 'permanent', 'account', 'number', 'signature', 'father', 'card'):
                cands.add(w_l)

    n_raw = (name or '').strip()
    f_raw = (father or '').strip()

    n_lower = re.sub(r'[^a-z]', '', n_raw.lower())
    f_lower = re.sub(r'[^a-z]', '', f_raw.lower())

    # Check cross-name patronymic relationship
    if n_lower and f_lower:
        # Son name ends with father name (e.g. SHIVAMCHANDRAPRAKASHMISHRA & CHANDRAPRAKASHMISHRA)
        if n_lower.endswith(f_lower) and len(n_lower) > len(f_lower) + 2:
            son_given = n_lower[:-len(f_lower)]
            f_parts, _ = _split_single_token(f_lower, list(cands))
            n_clean = ' '.join([son_given.capitalize()] + [p.capitalize() for p in f_parts])
            f_clean = ' '.join([p.capitalize() for p in f_parts])
            return n_clean, f_clean, False

        # Common family surname at end (e.g. ASHWINANANDAGRAWAL & ANANDNANDKISHORAGRAWAL)
        common_sur = os.path.commonprefix([n_lower[::-1], f_lower[::-1]])[::-1]
        if len(common_sur) >= 3:
            rem_n = n_lower[:-len(common_sur)]
            rem_f = f_lower[:-len(common_sur)]
            for ov_len in range(min(len(rem_n), len(rem_f)), 2, -1):
                sub = rem_f[:ov_len]
                if rem_n.endswith(sub) and len(rem_n) >= ov_len + 3:
                    son_first = rem_n[:-ov_len]
                    f_first = sub
                    f_mid = rem_f[ov_len:]
                    f_mid_parts, _ = _split_single_token(f_mid, list(cands)) if f_mid else ([], False)
                    n_clean = f'{son_first.capitalize()} {f_first.capitalize()} {common_sur.capitalize()}'
                    f_clean = ' '.join([f_first.capitalize()] + [p.capitalize() for p in f_mid_parts] + [common_sur.capitalize()])
                    return n_clean, f_clean, False

    ambiguous = False

    def process_field(val: Optional[str]) -> Optional[str]:
        nonlocal ambiguous
        if not val:
            return val
        words = [w.strip() for w in re.sub(r'[ \t]+', ' ', val).split() if w.strip()]
        out_tokens = []
        for w in words:
            parts, amb = _split_single_token(w, list(cands))
            if amb:
                ambiguous = True
            for p in parts:
                out_tokens.append(p.capitalize())
        return ' '.join(out_tokens)

    n_clean = process_field(n_raw)
    f_clean = process_field(f_raw)
    return n_clean, f_clean, ambiguous


def parse_pan(text: str, items: Optional[List[Dict[str, Any]]] = None,
              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    clean_upper = text.upper()
    pan_match = re.search(PAN_REGEX, clean_upper)
    if not pan_match:
        spaced = re.search(r'\b([A-Z]{5})\s*([0-9]{4})\s*([A-Z])\b', clean_upper)
        pan = f"{spaced.group(1)}{spaced.group(2)}{spaced.group(3)}" if spaced else None
    else:
        pan = pan_match.group(0)

    # Normalize repeated spaces, tabs, and line breaks into clean single-spaced lines
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in text.splitlines() if l.strip()]

    # 1. Detect if OCR output lines are read bottom-to-top / inverted
    headers = ('INCOME', 'TAX', 'GOVT', 'PERMANENT', 'ACCOUNT')
    footers = ('DATE OF BIRTH', 'BIRTH', 'SIGNATURE')
    hdr_idx = [i for i, l in enumerate(lines) if any(w in l.upper() for w in headers)]
    ftr_idx = [i for i, l in enumerate(lines) if any(w in l.upper() for w in footers)]
    if hdr_idx and ftr_idx and max(hdr_idx) > max(ftr_idx) and min(hdr_idx) > min(ftr_idx):
        lines = list(reversed(lines))

    # 2. Strict section bounding: find PAN index and DOB index
    # In PAN cards, cardholder and father names must exist strictly within the identity band
    # (between PAN/Header and Date of Birth). They can never be taken from below Date of Birth or above Header.
    pan_idx = -1
    for i, line in enumerate(lines):
        if pan and pan in line.upper():
            pan_idx = i
            break
        elif re.search(PAN_REGEX, line.upper()):
            pan_idx = i
            break

    dob = None
    dob_idx = -1
    for i, line in enumerate(lines):
        d_match = DOB_RE.search(line)
        if d_match:
            parts = re.split(r'[/-]', d_match.group(1))
            if len(parts) == 3:
                try:
                    d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                    if 1 <= d <= 31 and 1 <= m <= 12 and 1920 <= y <= 2026:
                        dob = f"{d:02d}/{m:02d}/{y:04d}"
                        dob_idx = i
                        break
                except (ValueError, TypeError):
                    pass
        elif re.search(r'\b(?:date\s*of\s*birth|dob|janam)\b', line, re.I):
            if dob_idx == -1:
                dob_idx = i

    # Upper boundary: lines before DOB, excluding header keywords
    end_search = dob_idx if dob_idx != -1 else len(lines)
    candidate_lines = []
    for l in lines[:end_search]:
        clean_l = re.sub(r'[^a-z0-9]', '', l.lower())
        if any(h in clean_l for h in ('incometax', 'permanentaccount', 'govtofindia', 'republicofindia', 'department')):
            continue
        if pan and pan in l.upper():
            continue
        elif re.search(PAN_REGEX, l.upper()):
            continue
        candidate_lines.append(l)

    name = father = None

    # 3. Check for same-line bilingual or labeled names within candidate lines
    for line in candidate_lines:
        if not father:
            m_f = re.search(r'(?:^|[\s/])(?:fa[a-z]?[/:]?\s*)?(?:father(?:\'s)?|parent(?:\'s)?|pita)\s*(?:ka\s*)?(?:name|nam)?\s*[:\-\s/]+([A-Za-z\s.\'-]{3,50})$', line, re.I)
            if m_f:
                val = m_f.group(1).strip()
                val = re.sub(r'[\d\s]+$', '', val).strip()
                if _looks_like_name(val):
                    father = val
                    continue

        if not name:
            m_n = re.search(r'(?:^|[\s/])(?:name|applicant(?:\'s)?\s*name|naam)\s*[:\-\s/]+([A-Za-z\s.\'-]{3,50})$', line, re.I)
            if m_n:
                low = line.lower()
                if not any(w in low for w in ['father', 'pita', 'parent', 'department', 'permanent', 'account', 'income', 'govt', 'india']):
                    val = m_n.group(1).strip()
                    val = re.sub(r'[\d\s]+$', '', val).strip()
                    if _looks_like_name(val):
                        name = val
                        continue

    # 4. Multi-line section scanning between labels within candidate lines
    name_label_idx = -1
    father_label_idx = -1
    for i, line in enumerate(candidate_lines):
        clean_line = re.sub(r'[^a-zA-Z]', '', line).lower()
        if any(w in clean_line for w in ('father', 'parent', 'guardian', 'pita')):
            if father_label_idx == -1:
                father_label_idx = i
        elif 'name' in clean_line and not any(w in clean_line for w in ('father', 'pita', 'parent', 'department', 'permanent', 'account', 'govt', 'india')):
            if name_label_idx == -1:
                name_label_idx = i

    if not name and name_label_idx != -1:
        end_idx = father_label_idx if father_label_idx > name_label_idx else len(candidate_lines)
        name_parts = [re.sub(r'[\d\s]+$', '', re.sub(r'^[/:#\-\s]+', '', candidate_lines[idx])).strip()
                      for idx in range(name_label_idx + 1, end_idx) if _looks_like_name(candidate_lines[idx])]
        if name_parts:
            name = ' '.join(name_parts)

    if not father and father_label_idx != -1:
        father_parts = [re.sub(r'[\d\s]+$', '', re.sub(r'^[/:#\-\s]+', '', candidate_lines[idx])).strip()
                        for idx in range(father_label_idx + 1, len(candidate_lines)) if _looks_like_name(candidate_lines[idx])]
        if father_parts:
            father = ' '.join(father_parts)

    # 5. Adjacent-line check fallback within candidate lines
    if not name or not father:
        for idx in range(len(candidate_lines)):
            l = candidate_lines[idx]
            low = l.lower()
            nxt = candidate_lines[idx + 1] if idx + 1 < len(candidate_lines) else None
            if not nxt:
                continue

            nxt_clean = re.sub(r'[\d\s]+$', '', nxt).strip()
            nxt_clean = re.sub(r'^[/:#\-\s]+', '', nxt_clean).strip()

            if any(w in low for w in ['father', 'parent', 'pita']) and not father:
                if _looks_like_name(nxt_clean):
                    father = nxt_clean
            elif any(w in low for w in ['name', 'naam']) and not any(w in low for w in ['father', 'pita', 'parent', 'department', 'account', 'permanent', 'income', 'card']) and not name:
                if _looks_like_name(nxt_clean):
                    name = nxt_clean

    # 6. Positional fallback strictly within candidate lines
    if not name or not father:
        caps = [re.sub(r'^[/:#\-\s]+|[\d\s]+$', '', l).strip() for l in candidate_lines]
        caps = [c for c in caps if _looks_like_name(c)]
        if not name and caps:
            name = caps[0]
        if not father:
            for c in caps:
                if c != name:
                    father = c
                    break

    # Context names from form or previous documents (e.g. Aadhaar)
    context_names = []
    if context:
        for k in ('applicantName', 'aadhaarName', 'userName', 'name'):
            v = context.get(k)
            if v and isinstance(v, str):
                context_names.append(v)

    # 6. Split glued tokens and preserve word boundaries
    name, father, is_ambiguous = _split_glued_pan_names(name, father, context_names=context_names, doc_text=text)

    # 7. Verify and correct patronymic inversion:
    # In Indian naming, the son's middle name is the father's first name.
    # If father's middle name equals applicant's first name, they are inverted!
    if name and father:
        n_words = name.split()
        f_words = father.split()
        if len(n_words) >= 2 and len(f_words) >= 2:
            if n_words[0].lower() in [w.lower() for w in f_words[1:-1]]:
                name, father = father, name

    # 8. Calculate genuine field-level OCR confidences from items
    items_list = list(items or [])
    field_confidences = {}

    # PAN score
    pan_score = 90.0
    if pan:
        for it in items_list:
            if pan in str(it.get('text', '')).upper():
                pan_score = round(float(it.get('score', 0.90)) * 100, 1)
                break
        field_confidences['pan'] = pan_score

    # Name score
    if name:
        n_words = [w.lower() for w in name.split()]
        matched_scores = []
        for it in items_list:
            t_low = str(it.get('text', '')).lower()
            for w in n_words:
                if w in t_low:
                    matched_scores.append(float(it.get('score', 0.85)) * 100)
        field_confidences['name'] = round(sum(matched_scores) / len(matched_scores), 1) if matched_scores else 86.0

    # Father name score
    if father:
        f_words = [w.lower() for w in father.split()]
        matched_scores = []
        for it in items_list:
            t_low = str(it.get('text', '')).lower()
            for w in f_words:
                if w in t_low:
                    matched_scores.append(float(it.get('score', 0.85)) * 100)
        field_confidences['fatherName'] = round(sum(matched_scores) / len(matched_scores), 1) if matched_scores else 86.0

    # DOB score
    if dob:
        d_score = 88.0
        for it in items_list:
            if dob in str(it.get('text', '')):
                d_score = round(float(it.get('score', 0.88)) * 100, 1)
                break
        field_confidences['dob'] = d_score

    return {
        'pan': pan,
        'name': name,
        'fatherName': father,
        'dob': dob,
        'isAmbiguous': is_ambiguous,
        'fieldConfidences': field_confidences,
    }


def parse_gst(text: str) -> Dict[str, Any]:
    ent = DocumentOCRService.extract_document_entities(text, 'GST_CERTIFICATE')
    biz_name = ent.get('extractedName')
    return {
        'gstin': ent.get('extractedGstin'),
        'pan': ent.get('extractedPan'),
        'businessName': biz_name,
        'companyName': biz_name,
    }


def parse_address_proof(text: str) -> Dict[str, Any]:
    pin = PIN_RE.search(text)
    return {'pincode': pin.group(1) if pin else None, 'addressSnippet': re.sub(r'\s+', ' ', text)[:200] or None}


def parse_bank(text: str) -> Dict[str, Any]:
    ifsc = IFSC_RE.search(text.upper())
    acct = ACCOUNT_RE.search(text)
    return {'ifsc': ifsc.group(1) if ifsc else None, 'accountLast4': acct.group(1)[-4:] if acct else None}


# ------------------------------------------------------- orchestration -----

def process_document(doc_type: str, path: str, mime: str = '',
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Reads one uploaded file. Returns fields ready to save on a SellerDocument."""
    out: Dict[str, Any] = {'ocrStatus': 'NOT_REQUIRED', 'extractedFields': {}, 'redactedText': '', 'confidence': 0.0, 'warnings': []}
    if doc_type not in OCR_DOC_TYPES:
        return out

    res = read_text(path, mime)
    out['ocrStatus'] = res['status']
    text = res['text']
    if res['status'] == 'OCR_UNAVAILABLE':
        out['warnings'].append('Automatic reading is not available. An administrator will read this document by hand.')
        return out
    if res['status'] == 'UNREADABLE':
        out['warnings'].append('We could not read this file. Upload a clearer, well-lit image or PDF.')
        return out

    clean_text_low = text.lower()
    has_aadhaar_markers = bool(re.search(r'\b(aadhaar|uidai|unique identification|mera aadhaar)\b', clean_text_low) or AADHAAR_MASKED.search(text) or AADHAAR_PLAIN.search(text))
    has_pan_markers = bool(re.search(r'\b(income tax|permanent account|pan card)\b', clean_text_low) or re.search(PAN_REGEX, text.upper()))

    if doc_type == 'AADHAAR':
        # Reject if document appears to be a PAN card uploaded as Aadhaar
        if has_pan_markers and not has_aadhaar_markers:
            out.update(ocrStatus='REJECTED', extractedFields={}, redactedText='')
            out['warnings'].append('The uploaded document appears to be a PAN card, not an Aadhaar card. Please upload a masked Aadhaar.')
            return out

        fields = parse_aadhaar(text, items=res.get('items'))
        if fields.get('unmasked'):
            out.update(ocrStatus='REJECTED', extractedFields={}, redactedText='')
            out['warnings'].append('This Aadhaar shows all 12 digits. Upload the masked Aadhaar from myAadhaar (first 8 digits hidden).')
            return out

        if not fields.get('aadhaarLast4'):
            out.update(ocrStatus='REJECTED', extractedFields={}, redactedText='')
            out['warnings'].append('We could not find the masked Aadhaar number (XXXX XXXX 1234). Please upload a valid masked Aadhaar.')
            return out

        wanted = ('name', 'dob', 'gender', 'residentialAddress', 'residentialPincode', 'residentialCity', 'residentialState', 'aadhaarMasked', 'aadhaarLast4')

    elif doc_type == 'PAN':
        # Reject wrong document types uploaded as PAN (e.g. Aadhaar card or unrelated invoice)
        if has_aadhaar_markers and not re.search(PAN_REGEX, text.upper()):
            out.update(ocrStatus='REJECTED', extractedFields={}, redactedText='')
            out['warnings'].append('The uploaded document appears to be an Aadhaar card, not a PAN card. Please upload a valid PAN card.')
            return out

        fields, wanted = parse_pan(text, items=res.get('items'), context=context), ('pan', 'name', 'fatherName', 'dob')
        if not fields.get('pan'):
            out.update(ocrStatus='REJECTED', extractedFields={}, redactedText='')
            out['warnings'].append('We could not find a valid PAN number on this file. Please upload a valid PAN card.')
            return out

    elif doc_type == 'GST_CERTIFICATE':
        fields, wanted = parse_gst(text), ('gstin', 'pan', 'businessName', 'companyName')
        if not fields.get('gstin'):
            out['warnings'].append('We could not find a valid GSTIN on this file.')
    elif doc_type == 'ADDRESS_PROOF':
        fields, wanted = parse_address_proof(text), ('pincode', 'addressSnippet')
    else:
        fields, wanted = parse_bank(text), ('ifsc', 'accountLast4')

    out['extractedFields'] = {k: fields.get(k) for k in wanted if fields.get(k)}
    out['redactedText'] = DocumentOCRService.redact_sensitive_pii(text)[:1500]

    if fields.get('fieldConfidences'):
        out['fieldConfidences'] = fields['fieldConfidences']
        fc_vals = list(fields['fieldConfidences'].values())
        out['confidence'] = round(sum(fc_vals) / max(1, len(fc_vals)), 1)
    else:
        found = sum(1 for k in wanted if fields.get(k))
        out['confidence'] = round(100.0 * found / max(1, len(wanted)), 1)

    # Set appropriate status based on confidence
    if doc_type == 'AADHAAR':
        if not fields.get('name') or out['confidence'] < 60.0:
            out['ocrStatus'] = 'NEEDS_REVIEW'
            out['warnings'].append('Name could not be extracted with high confidence. Please verify your name.')
        else:
            out['ocrStatus'] = 'DONE'
    elif doc_type == 'PAN':
        if not fields.get('name') or fields.get('isAmbiguous') or out['confidence'] < 50.0:
            out['ocrStatus'] = 'NEEDS_REVIEW'
            if fields.get('isAmbiguous'):
                out['warnings'].append('Extracted PAN name contains unsegmented or ambiguous words. Please review your details.')
            else:
                out['warnings'].append('PAN details could not be extracted with high confidence. Please verify.')
        else:
            out['ocrStatus'] = 'DONE'

    return out


def remediate_pan_documents_and_applications() -> Dict[str, int]:
    """
    Safely remediates previously stored PAN documents and seller applications where names
    were extracted without proper word boundaries or with erroneous OCR tokens.
    """
    from .models import SellerDocument, SellerApplication
    from .risk_service import SellerRiskScoringService

    remediated_docs = 0
    remediated_apps = 0

    for doc in SellerDocument.objects.filter(docType='PAN'):
        fields = doc.extractedFields or {}
        old_name = fields.get('name')
        old_father = fields.get('fatherName')

        app = doc.application
        ctx = {}
        if app:
            ctx['applicantName'] = app.applicantName
            aadhaar_doc = app.documents.filter(docType='AADHAAR').first()
            if aadhaar_doc and (aadhaar_doc.extractedFields or {}).get('name'):
                ctx['aadhaarName'] = aadhaar_doc.extractedFields['name']

        # If previous name was a non-name token like 'Hrr' or fatherName was 'Verified', or doc has file, reprocess
        is_garbage = (old_name and (old_name.lower() in _NOT_NAMES or not _looks_like_name(old_name))) or \
                     (old_father and (old_father.lower() in _NOT_NAMES or not _looks_like_name(old_father)))

        if is_garbage and doc.file and os.path.exists(doc.file.path):
            result = process_document('PAN', doc.file.path, doc.mimeType, context=ctx)
            doc.ocrStatus = result['ocrStatus']
            doc.extractedFields = dict(result['extractedFields'])
            if result.get('fieldConfidences'):
                doc.extractedFields['fieldConfidences'] = result['fieldConfidences']
            doc.confidence = result['confidence']
            doc.warnings = result['warnings']
            doc.save()
            new_name = doc.extractedFields.get('name')
            new_father = doc.extractedFields.get('fatherName')
            remediated_docs += 1
        elif old_name or old_father:
            new_name, new_father, _ = _split_glued_pan_names(
                old_name, old_father, context_names=list(ctx.values()), doc_text=doc.redactedText or ''
            )
            changed = False
            if new_name and new_name != old_name:
                fields['name'] = new_name
                changed = True
            if new_father and new_father != old_father:
                fields['fatherName'] = new_father
                changed = True
            if changed:
                doc.extractedFields = fields
                doc.save(update_fields=['extractedFields'])
                remediated_docs += 1
        else:
            continue

        if app:
            app_updates = []
            if app.identityDetails:
                ident = dict(app.identityDetails)
                if new_name and ident.get('panName') != new_name:
                    ident['panName'] = new_name
                if new_father and ident.get('fatherName') != new_father:
                    ident['fatherName'] = new_father
                app.identityDetails = ident
                app_updates.append('identityDetails')

            if app.ocrExtractedData and 'PAN' in app.ocrExtractedData:
                ocr_d = dict(app.ocrExtractedData)
                ocr_pan = dict(ocr_d['PAN'])
                if new_name:
                    ocr_pan['name'] = new_name
                if new_father:
                    ocr_pan['fatherName'] = new_father
                ocr_d['PAN'] = ocr_pan
                app.ocrExtractedData = ocr_d
                app_updates.append('ocrExtractedData')

            if new_name and (app.applicantName in (old_name, 'Hrr') or not app.applicantName or re.sub(r'[^a-zA-Z]', '', app.applicantName).lower() == re.sub(r'[^a-zA-Z]', '', new_name).lower()):
                app.applicantName = new_name
                app_updates.append('applicantName')

            if app_updates:
                all_docs = list(app.documents.all())
                eval_res = SellerRiskScoringService.evaluate(app, all_docs)
                app.riskScore = eval_res['riskScore']
                app.riskCategory = eval_res['riskCategory']
                app.aiAssessment = eval_res
                app_updates.extend(['riskScore', 'riskCategory', 'aiAssessment'])
                app.save(update_fields=list(set(app_updates)))
                remediated_apps += 1

    return {'remediated_docs': remediated_docs, 'remediated_apps': remediated_apps}


def remediate_aadhaar_documents_and_applications() -> Dict[str, int]:
    """
    Remediates stored Aadhaar documents by cleaning SW/ MALE pollution and OCR state prefixes,
    and syncing clean address data to SellerApplication.
    """
    from .models import SellerDocument, SellerApplication

    remediated_docs = 0
    remediated_apps = 0

    for doc in SellerDocument.objects.filter(docType='AADHAAR'):
        fields = doc.extractedFields or {}
        addr = fields.get('residentialAddress') or fields.get('address')
        if not addr:
            continue

        clean_addr = re.sub(r'^(?:[sS][wW][/\\-]?\s*|(?:male|female|transgender)\s*|address\s*[:\-,]?\s*|[,\-:\s]+)+', '', addr, flags=re.I).strip()
        clean_addr = re.sub(r'\b[E|e](Maharashtra|Gujarat|Karnataka|Rajasthan|Delhi|Punjab|Haryana|Telangana|Tamil Nadu|Kerala|Madhya Pradesh|Uttar Pradesh|Bihar|West Bengal|Akola|Thane|Kalyan|Pune|Mumbai)\b', r'\1', clean_addr, flags=re.I)

        changed = False
        if clean_addr != addr:
            fields['residentialAddress'] = clean_addr
            if 'address' in fields:
                fields['address'] = clean_addr
            changed = True

        if changed:
            doc.extractedFields = fields
            doc.save(update_fields=['extractedFields'])
            remediated_docs += 1

        app = doc.application
        if app and app.residentialAddress and ('SW/ MALE' in app.residentialAddress or 'EMaharashtra' in app.residentialAddress):
            app.residentialAddress = clean_addr
            app.save(update_fields=['residentialAddress'])
            remediated_apps += 1

    return {'remediated_docs': remediated_docs, 'remediated_apps': remediated_apps}


def remediate_all_documents_and_applications() -> Dict[str, Any]:
    pan_res = remediate_pan_documents_and_applications()
    aadhaar_res = remediate_aadhaar_documents_and_applications()
    return {'pan': pan_res, 'aadhaar': aadhaar_res}

    return out


def normalize_name(name: Optional[str]) -> str:
    """
    Normalizes a person's name for robust identity matching:
    - Strips leading name labels like 'Name:', 'To:'
    - Converts to lower case and strips whitespace
    - Replaces non-alphanumeric punctuation with spaces (e.g. 'R.K.' -> 'r k')
    - Strips common prefixes/honorifics ('shri', 'shree', 'dr', 'mr', 'mrs', 'ms', 'smt')
    - Collapses multiple spaces
    """
    if not name:
        return ""
    cleaned = re.sub(r'^(?:name\s*[:\-]|to\s*[:\-])\s*', '', str(name).strip(), flags=re.I)
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned).lower()
    tokens = [t for t in cleaned.split() if t]
    prefixes = {'shri', 'shree', 'dr', 'mr', 'mrs', 'ms', 'smt', 'kumar', 'kumari'}
    while tokens and tokens[0] in prefixes:
        tokens.pop(0)
    return ' '.join(tokens)


def _name_tokens(value: Optional[str]) -> List[str]:
    return [w for w in normalize_name(value).split() if w]


def _names_match(a: Optional[str], b: Optional[str]) -> bool:
    """
    Deterministic name matching service:
    - Normalizes case, spacing, punctuation, and honorifics.
    - Handles token reordering (e.g. 'Sharma Rahul' vs 'Rahul Sharma').
    - Handles middle names (e.g. 'Rahul Mohan Sharma' vs 'Rahul Sharma').
    - Handles initials (e.g. 'R. Sharma' vs 'Rahul Sharma').
    - Handles fused OCR tokens (e.g. 'RahulSharma' vs 'Rahul Sharma').
    - Strictly avoids false positives on shared common surnames when first names conflict!
      (e.g. 'Rahul Sharma' vs 'Priya Sharma' returns False).
    """
    t_a = _name_tokens(a)
    t_b = _name_tokens(b)
    if not t_a or not t_b:
        return False

    # 1. Exact token match or reordered token match
    if t_a == t_b or sorted(t_a) == sorted(t_b):
        return True

    # 2. Fused characters check (e.g. 'rahulsharma' vs 'rahul sharma')
    joined_a = ''.join(t_a)
    joined_b = ''.join(t_b)
    if joined_a == joined_b:
        return True

    # Single-word name comparison
    if len(t_a) == 1 and len(t_b) == 1:
        w_a, w_b = t_a[0], t_b[0]
        if w_a == w_b:
            return True
        if len(w_a) >= 4 and len(w_a) == len(w_b):
            diffs = sum(1 for c1, c2 in zip(w_a, w_b) if c1 != c2)
            if diffs <= 1:
                return True
        return False

    # 3. Both have first and last names
    last_a, last_b = t_a[-1], t_b[-1]
    first_a, first_b = t_a[0], t_b[0]

    # Inverted first/last name
    if first_a == last_b and last_a == first_b:
        return True

    last_match = (last_a == last_b) or (len(last_a) >= 4 and len(last_b) >= 4 and sum(1 for c1, c2 in zip(last_a, last_b) if c1 != c2) <= 1)
    first_match = (first_a == first_b) or (len(first_a) >= 4 and len(first_b) >= 4 and sum(1 for c1, c2 in zip(first_a, first_b) if c1 != c2) <= 1)
    first_initial_match = (len(first_a) == 1 and first_b.startswith(first_a)) or (len(first_b) == 1 and first_a.startswith(first_b))

    if last_match:
        # If last names match, first names MUST either match or be a valid initial match
        if first_match or first_initial_match:
            return True
        # If first names clearly conflict (e.g. 'rahul' vs 'priya'), DO NOT MATCH!
        return False

    # Check if one is a subset of the other (e.g. 'Rahul Mohan Sharma' contains all tokens of 'Rahul Sharma')
    set_a, set_b = set(t_a), set(t_b)
    if set_a.issubset(set_b) and len(set_a) >= 2:
        return True
    if set_b.issubset(set_a) and len(set_b) >= 2:
        return True

    # Overall fused token substring check
    if len(joined_a) >= 6 and (joined_a in joined_b or joined_b in joined_a):
        return True

    return False


def compare_application(app, docs) -> Dict[str, Any]:
    """Compares the form with what the documents say. Returns checks plus a risk score."""
    by_type = {d.docType: (d.extractedFields or {}) for d in docs if d.ocrStatus == 'DONE'}
    aad, pan, gst, addr = by_type.get('AADHAAR', {}), by_type.get('PAN', {}), by_type.get('GST_CERTIFICATE', {}), by_type.get('ADDRESS_PROOF', {})
    checks: List[Dict[str, str]] = []

    def add(label: str, status: str, detail: str):
        checks.append({'label': label, 'status': status, 'detail': detail})

    form_pan = (app.pan or '').strip().upper()
    form_gstin = (app.gstin or '').strip().upper()

    if form_pan and pan.get('pan'):
        ok = form_pan == pan['pan']
        add('PAN matches the PAN card', 'match' if ok else 'mismatch', f"Form {form_pan}, card {pan['pan']}")
    else:
        add('PAN matches the PAN card', 'missing', 'PAN could not be read from the card')

    if form_gstin and len(form_gstin) >= 12 and form_pan:
        ok = form_gstin[2:12] == form_pan
        add('PAN is inside the GSTIN', 'match' if ok else 'mismatch', f"GSTIN holds {form_gstin[2:12]}, form PAN {form_pan}")
    if form_gstin and gst.get('gstin'):
        ok = form_gstin == gst['gstin']
        add('GSTIN matches the certificate', 'match' if ok else 'mismatch', f"Form {form_gstin}, certificate {gst['gstin']}")

    # Auto-heal applicantName if it was previously set to father's name
    for doc in (pan, aad):
        if doc.get('fatherName') and doc.get('name'):
            if _names_match(app.applicantName, doc['fatherName']) and not _names_match(app.applicantName, doc['name']):
                app.applicantName = doc['name']
                try:
                    app.save(update_fields=['applicantName'])
                except Exception:
                    pass
                break

    for label, doc in (('Applicant name matches Aadhaar', aad), ('Applicant name matches PAN card', pan)):
        if doc.get('name'):
            ok = _names_match(app.applicantName, doc['name'])
            add(label, 'match' if ok else 'mismatch', f"Form '{app.applicantName}', document '{doc['name']}'")
        else:
            add(label, 'missing', 'Name could not be read')

    # 1. Residential PIN code verification against Aadhaar
    form_res_pin = (getattr(app, 'residentialPincode', None) or '').strip()
    aad_res_pin = (aad.get('residentialPincode') or aad.get('pincode') or '').strip()
    if form_res_pin and aad_res_pin:
        ok = form_res_pin == aad_res_pin
        add('Residential PIN code matches Aadhaar', 'match' if ok else 'mismatch', f"Form residential PIN {form_res_pin}, Aadhaar {aad_res_pin}")

    # 2. Store PIN code verification (independent from residential Aadhaar)
    form_store_pin = (app.pincode or '').strip()
    if addr.get('pincode'):
        # Verified against uploaded store address proof
        ok = form_store_pin == addr['pincode']
        add('Store PIN matches store address proof', 'match' if ok else 'mismatch', f"Store PIN {form_store_pin}, address proof {addr['pincode']}")
    elif form_store_pin and app.storeLatitude and app.storeLongitude:
        add('Store PIN and confirmed map location', 'match', f"Store PIN {form_store_pin} positioned at ({app.storeLatitude:.4f}, {app.storeLongitude:.4f})")
    elif form_store_pin:
        add('Store PIN code provided', 'match', f"Store PIN {form_store_pin}")

    mismatches = sum(1 for c in checks if c['status'] == 'mismatch')
    missing = sum(1 for c in checks if c['status'] == 'missing')

    from .risk_service import SellerRiskScoringService
    eval_res = SellerRiskScoringService.evaluate(app, docs)
    risk = min(100, 10 + 20 * mismatches + 8 * missing)
    risk_cat = 'Low' if risk <= 25 else ('Medium' if risk <= 55 else 'High')

    return {
        'checks': checks,
        'mismatches': mismatches,
        'missing': missing,
        'riskScore': risk,
        'riskCategory': risk_cat,
        'scoringVersion': eval_res['scoringVersion'],
        'contributingFactors': eval_res['contributingFactors'],
        'missingInformation': eval_res['missingInformation'],
        'validationDiscrepancies': eval_res['validationDiscrepancies'],
        'verifiedFacts': eval_res['verifiedFacts'],
        'recommendedAction': eval_res['recommendedAction'],
        'explanation': eval_res['explanation'],
    }


def merge_identity(docs) -> Dict[str, Any]:
    """One masked identity card for the admin, built from the Aadhaar and PAN reads."""
    ident: Dict[str, Any] = {}
    for d in docs:
        f = d.extractedFields or {}
        if d.docType == 'AADHAAR' and d.ocrStatus == 'DONE':
            ident.update({k: f[k] for k in ('name', 'dob', 'gender', 'residentialAddress', 'residentialPincode', 'address', 'pincode', 'aadhaarMasked') if f.get(k)})
        if d.docType == 'PAN' and d.ocrStatus == 'DONE':
            ident.update({'pan': f.get('pan'), 'panName': f.get('name'), 'fatherName': f.get('fatherName')})
            ident.setdefault('dob', f.get('dob'))
    return {k: v for k, v in ident.items() if v}


def decide_status(app, docs, comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Which status a submitted application should land in, and why."""
    have = {d.docType for d in docs}
    missing = [t for t in MANDATORY_DOC_TYPES if t not in have]
    if missing:
        return {'status': 'NEEDS_MORE_INFORMATION', 'reason': f"Missing mandatory documents: {', '.join(missing)}", 'missing': missing}
    rejected = [d.docType for d in docs if d.ocrStatus == 'REJECTED']
    if rejected:
        return {'status': 'NEEDS_MORE_INFORMATION', 'reason': 'A document must be uploaded again: ' + ', '.join(rejected), 'missing': rejected}
    unread = [d.docType for d in docs if d.docType in MANDATORY_DOC_TYPES and d.ocrStatus != 'DONE']
    if comparison['mismatches'] or unread:
        why = 'Details do not match the documents' if comparison['mismatches'] else 'Identity documents could not be read automatically'
        return {'status': 'NEEDS_MANUAL_REVIEW', 'reason': why, 'missing': []}
    return {'status': 'PENDING_ADMIN_APPROVAL', 'reason': 'All mandatory documents uploaded and details verified.', 'missing': []}
