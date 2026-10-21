"""
Seller onboarding API.

Flow:  create application (DRAFT) -> upload documents (read automatically) -> submit
       -> admin reviews the full profile -> APPROVE / REJECT / REQUEST_INFO / SUSPEND.

Rules enforced here, on the server:
- Only a signed-in user can apply, and sees only their own application.
- Only ADMIN / STAFF can list everything or take a decision.
- Uploaded files are private: served only to the applicant and to admins.
- The AI/OCR never approves anyone. It only reads documents and suggests a risk score.
"""

import re
import uuid
import datetime
from typing import Optional, Tuple

from django.http import FileResponse
from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import seller_docs
from .models import (
    Product, Seller, SellerApplication, SellerApplicationAudit, SellerDocument, Store, User,
)
from .ocr_service import GSTIN_REGEX, PAN_REGEX, DocumentOCRService
from .location_service import resolve_coordinates
from .serializers import SellerApplicationAuditSerializer, SellerApplicationSerializer
from .views import get_user_from_token

ADMIN_ROLES = ('ADMIN', 'STAFF')
FINAL_STATES = ('APPROVED', 'REJECTED', 'SUSPENDED')
EDITABLE_STATES = ('DRAFT', 'NEEDS_MORE_INFORMATION')
IMAGE_ONLY = {'STORE_PHOTO'}


# ----------------------------------------------------------------- helpers --

def _require(request, roles: Optional[Tuple[str, ...]] = None):
    """Returns (user, error_response). error_response is None when the caller may continue."""
    user = get_user_from_token(request)
    if not user:
        return None, Response({'detail': 'Please sign in to continue.'}, status=http.HTTP_401_UNAUTHORIZED)
    if roles and user.role not in roles:
        return user, Response({'detail': 'You do not have permission to do this.'}, status=http.HTTP_403_FORBIDDEN)
    return user, None


def _is_admin(user) -> bool:
    return user.role in ADMIN_ROLES


def _owns(user, app) -> bool:
    return bool(app.ownerUserId) and app.ownerUserId == user.id


def _audit(app, from_status, to_status, action, by, reason=''):
    SellerApplicationAudit.objects.create(
        id=f"aud-{uuid.uuid4().hex[:8]}", application=app, fromStatus=from_status, toStatus=to_status,
        action=action, performedBy=by, reason=reason,
    )


def _load(pk):
    return SellerApplication.objects.filter(id=pk).first()


def _doc_json(doc, admin: bool):
    raw_fields = dict(doc.extractedFields or {})
    field_confidences = raw_fields.pop('fieldConfidences', None)
    data = {
        'id': doc.id, 'docType': doc.docType, 'fileName': doc.fileName, 'mimeType': doc.mimeType, 'sizeBytes': doc.sizeBytes,
        'ocrStatus': doc.ocrStatus, 'extractedFields': raw_fields, 'fieldConfidences': field_confidences, 'confidence': doc.confidence,
        'warnings': doc.warnings, 'uploadedAt': doc.uploadedAt,
        'fileUrl': f"/api/seller/applications/{doc.application_id}/documents/{doc.id}/file",
    }
    if admin:
        data['redactedText'] = doc.redactedText
    return data


def _profile(app, viewer):
    """Everything an admin (or the applicant) needs to see about one application, in one response."""
    admin = _is_admin(viewer)
    docs = list(app.documents.all().order_by('uploadedAt'))
    comparison = seller_docs.compare_application(app, docs)
    have = {d.docType for d in docs}
    data = SellerApplicationSerializer(app).data
    data.pop('audit_logs', None)
    data.update({
        'documents': [_doc_json(d, admin) for d in docs],
        'requiredDocuments': seller_docs.REQUIRED_DOC_TYPES,
        'missingDocuments': [t for t in seller_docs.REQUIRED_DOC_TYPES if t not in have],
        'identity': app.identityDetails or seller_docs.merge_identity(docs),
        'comparison': comparison,
        'store': {
            'name': app.storeName or app.companyName, 'address': app.address, 'city': app.city, 'state': app.addressState,
            'pincode': app.pincode, 'latitude': app.storeLatitude, 'longitude': app.storeLongitude,
        },
        'residential': {
            'address': app.residentialAddress or '',
            'pincode': app.residentialPincode or '',
            'city': app.residentialCity or '',
            'state': app.residentialState or '',
        },
        'auditTrail': SellerApplicationAuditSerializer(app.audit_logs.all().order_by('timestamp'), many=True).data,
        'liveProducts': [
            {'id': p.id, 'name': p.name, 'price': p.price, 'image': (p.images or [''])[0]}
            for p in Product.objects.filter(seller=app.companyName)[:24]
        ] if app.status == 'APPROVED' else [],
    })
    return data


def _validate_form(data, stage='ALL') -> dict:
    errors = {}
    stage = str(stage or 'ALL').upper()
    if stage in ('DRAFT', 'NONE'):
        return errors

    get = lambda k: str(data.get(k) or '').strip()  # noqa: E731

    validate_stage1 = stage in ('ALL', 'STAGE_1', '1', 'IDENTITY_BUSINESS')
    validate_stage2 = stage in ('ALL', 'STAGE_2', '2', 'STORE_LOCATION')
    validate_stage3 = stage in ('ALL', 'STAGE_3', '3', 'PRODUCTS')

    if validate_stage1:
        if not get('companyName'):
            errors['companyName'] = 'Enter your business or store name.'
        if not (get('contactName') or get('applicantName')):
            errors['contactName'] = 'Enter the name of the person applying.'
        phone_digits = re.sub(r'\D', '', get('phone'))
        if len(phone_digits) < 10:
            errors['phone'] = 'Enter a valid 10-digit phone number.'
        if '@' not in get('email'):
            errors['email'] = 'Enter a valid business email.'
        pan = get('pan').upper()
        if not pan or not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', pan):
            errors['pan'] = 'Enter a valid 10-character PAN (e.g. ABCDE1234F).'
        gstin = get('gstin').upper()
        if gstin and not re.fullmatch(GSTIN_REGEX, gstin):
            errors['gstin'] = 'GSTIN must be 15 characters, like 27ABCDE1234F1Z5.'

    if validate_stage2:
        if not get('address'):
            errors['address'] = 'Enter the store street address.'
        pincode = get('pincode')
        if not re.fullmatch(r'[1-9]\d{5}', pincode):
            errors['pincode'] = 'Enter a valid 6-digit Indian PIN code.'
        try:
            lat_val = data.get('storeLatitude')
            lng_val = data.get('storeLongitude')
            if lat_val is None or lng_val is None or str(lat_val).strip() == '' or str(lng_val).strip() == '':
                errors['location'] = 'Drop the store pin on the map or enter your PIN code.'
            else:
                lat, lng = float(lat_val), float(lng_val)
                if not (6 <= lat <= 38 and 68 <= lng <= 98):
                    errors['location'] = 'The store pin must be located inside India (lat 6-38, lng 68-98).'
        except (TypeError, ValueError):
            errors['location'] = 'Drop the store pin on the map where your store is located.'

    if validate_stage3:
        products = data.get('plannedProducts') or []
        valid_products = [
            p for p in products
            if isinstance(p, dict) and str(p.get('name', '')).strip()
        ]
        if not isinstance(products, list) or not valid_products:
            errors['plannedProducts'] = 'Add at least one product you plan to sell.'

    return errors


# ------------------------------------------------------------------- views --

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def seller_applications_view(request):
    """GET: admins see all (filter with ?status=), everyone else sees only their own. POST: start or update your application."""
    user, err = _require(request)
    if err:
        return err

    if request.method == 'GET':
        if _is_admin(user):
            apps = SellerApplication.objects.all().order_by('-createdAt')
            wanted = request.query_params.get('status') or request.query_params.get('state')
            if wanted:
                apps = apps.filter(status=wanted)
        else:
            apps = SellerApplication.objects.filter(ownerUserId=user.id).order_by('-createdAt')
        rows = []
        for a in apps:
            row = SellerApplicationSerializer(a).data
            row.pop('audit_logs', None)
            docs = list(a.documents.all())
            req_uploaded = sum(1 for d in docs if d.docType in ('AADHAAR', 'PAN') and d.ocrStatus != 'REJECTED')
            opt_uploaded = sum(1 for d in docs if d.docType not in ('AADHAAR', 'PAN') and d.ocrStatus != 'REJECTED')
            row['documentCount'] = len(docs)
            row['requiredDocumentCount'] = req_uploaded
            row['totalRequiredDocuments'] = 2
            row['optionalDocumentCount'] = opt_uploaded
            rows.append(row)
        return Response(rows)

    data = request.data
    stage = data.get('stage') or 'ALL'
    errors = _validate_form(data, stage=stage)
    if errors:
        return Response({'detail': 'Please fix the highlighted fields.', 'errors': errors}, status=http.HTTP_400_BAD_REQUEST)

    def _clean_coord(v):
        if v is None or str(v).strip() == '':
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    fields = {
        'companyName': str(data.get('companyName') or '').strip(),
        'storeName': str(data.get('storeName') or data.get('companyName') or '').strip(),
        'applicantName': str(data.get('contactName') or data.get('applicantName') or '').strip(),
        'email': str(data.get('email') or '').strip().lower(),
        'phone': str(data.get('phone') or '').strip(),
        'gstin': str(data.get('gstin') or '').strip().upper(),
        'pan': str(data.get('pan') or '').strip().upper(),
        'businessType': str(data.get('businessType') or 'Retailer'),
        'residentialAddress': str(data.get('residentialAddress') or '').strip(),
        'residentialPincode': str(data.get('residentialPincode') or '').strip(),
        'residentialCity': str(data.get('residentialCity') or '').strip(),
        'residentialState': str(data.get('residentialState') or '').strip(),
        'address': str(data.get('address') or '').strip(),
        'city': str(data.get('city') or '').strip(),
        'addressState': str(data.get('state') or data.get('addressState') or '').strip(),
        'pincode': str(data.get('pincode') or '').strip(),
        'storeLatitude': _clean_coord(data.get('storeLatitude')),
        'storeLongitude': _clean_coord(data.get('storeLongitude')),
        'productCategories': data.get('productCategories') or [],
        'plannedProducts': [
            {'name': str(p.get('name')).strip(), 'category': str(p.get('category') or '').strip(), 'approxPrice': p.get('approxPrice') or 0,
             'stock': max(0, int(p.get('stock') or 0)) if str(p.get('stock') or '0').isdigit() else 0, 'image': str(p.get('image') or '')[:500]}
            for p in data.get('plannedProducts', []) if str(p.get('name', '')).strip()
        ],
    }
    existing = SellerApplication.objects.filter(ownerUserId=user.id).exclude(status__in=FINAL_STATES).first()
    if existing and existing.status not in EDITABLE_STATES:
        return Response({'detail': 'You already have an application under review.', 'applicationId': existing.id},
                        status=http.HTTP_409_CONFLICT)
    if existing:
        for k, v in fields.items():
            # If a field is not provided in a step payload, don't overwrite existing non-empty value with empty
            if stage != 'ALL' and (v is None or v == '' or v == []) and getattr(existing, k, None):
                continue
            setattr(existing, k, v)
        existing.save()
        return Response(_profile(existing, user))

    app = SellerApplication.objects.create(id=f"app-{uuid.uuid4().hex[:8]}", ownerUserId=user.id, status='DRAFT', **fields)
    _audit(app, '', 'DRAFT', 'APPLICATION_STARTED', user.email, 'Seller started an application.')
    return Response(_profile(app, user), status=http.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def seller_application_start_view(request):
    """Someone created a seller account: open a draft application straight away so the admin can see the sign-up and the seller can resume."""
    user, err = _require(request)
    if err:
        return err
    existing = SellerApplication.objects.filter(ownerUserId=user.id).exclude(status__in=FINAL_STATES).first()
    if existing:
        return Response(_profile(existing, user))
    app = SellerApplication.objects.create(id=f"app-{uuid.uuid4().hex[:8]}", ownerUserId=user.id, status='DRAFT', applicantName=user.name, email=user.email.lower(),
                                           phone=user.phone or '', companyName=f"{user.name} (store not named yet)", city='Mumbai')
    _audit(app, '', 'DRAFT', 'SELLER_ACCOUNT_CREATED', user.email, 'Created a seller account. Application not submitted yet.')
    return Response(_profile(app, user), status=http.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([AllowAny])
def seller_application_detail_view(request, pk):
    """The full seller profile: identity, store location, products, documents, checks and history."""
    user, err = _require(request)
    if err:
        return err
    app = _load(pk)
    if not app or not (_is_admin(user) or _owns(user, app)):
        return Response({'detail': 'Application not found.'}, status=http.HTTP_404_NOT_FOUND)
    if request.method in ('PUT', 'PATCH'):
        if app.status not in EDITABLE_STATES:
            return Response({'detail': 'This application can no longer be changed.'}, status=http.HTTP_409_CONFLICT)
        data = request.data
        field_map = {
            'companyName': 'companyName',
            'storeName': 'storeName',
            'contactName': 'applicantName',
            'applicantName': 'applicantName',
            'email': 'email',
            'phone': 'phone',
            'gstin': 'gstin',
            'pan': 'pan',
            'businessType': 'businessType',
            'residentialAddress': 'residentialAddress',
            'residentialPincode': 'residentialPincode',
            'residentialCity': 'residentialCity',
            'residentialState': 'residentialState',
            'address': 'address',
            'city': 'city',
            'state': 'addressState',
            'addressState': 'addressState',
            'pincode': 'pincode',
            'storeLatitude': 'storeLatitude',
            'storeLongitude': 'storeLongitude',
            'productCategories': 'productCategories',
            'plannedProducts': 'plannedProducts',
        }
        for in_key, model_attr in field_map.items():
            if in_key in data:
                val = data[in_key]
                if model_attr in ('storeLatitude', 'storeLongitude') and val is not None:
                    try:
                        val = float(val) if str(val).strip() != '' else None
                    except (ValueError, TypeError):
                        val = None
                setattr(app, model_attr, val)
        app.save()
        _audit(app, app.status, app.status, 'APPLICATION_UPDATED', user.email, 'Seller updated application details.')
    return Response(_profile(app, user))


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def seller_application_documents_view(request, pk):
    """Upload one document. It is read straight away and the details are returned."""
    user, err = _require(request)
    if err:
        return err
    app = _load(pk)
    if not app or not _owns(user, app):
        return Response({'detail': 'Application not found.'}, status=http.HTTP_404_NOT_FOUND)
    if app.status not in EDITABLE_STATES:
        return Response({'detail': 'This application can no longer be changed.'}, status=http.HTTP_409_CONFLICT)

    doc_type = str(request.data.get('docType') or '').upper()
    upload = request.FILES.get('file')
    if doc_type not in seller_docs.ALL_DOC_TYPES:
        return Response({'detail': 'Unknown document type.'}, status=http.HTTP_400_BAD_REQUEST)
    if not upload:
        return Response({'detail': 'Choose a file to upload.'}, status=http.HTTP_400_BAD_REQUEST)
    file_bytes = upload.read(64)
    upload.seek(0)
    check = DocumentOCRService.validate_document_upload(
        upload.name, upload.size, upload.content_type or '', file_bytes=file_bytes
    )
    if not check['valid']:
        return Response({'detail': check['error']}, status=http.HTTP_400_BAD_REQUEST)
    if doc_type in IMAGE_ONLY and not (upload.content_type or '').startswith('image/'):
        return Response({'detail': 'The store photo must be an image.'}, status=http.HTTP_400_BAD_REQUEST)

    for old in app.documents.filter(docType=doc_type):  # one file per type: a new upload replaces the old one
        old.file.delete(save=False)
        old.delete()
    doc = SellerDocument(id=f"doc-{uuid.uuid4().hex[:8]}", application=app, docType=doc_type, fileName=upload.name[:255],
                         mimeType=upload.content_type or '', sizeBytes=upload.size)
    doc.file.save(upload.name, upload, save=False)
    doc.save()

    context = {
        'applicantName': app.applicantName,
        'aadhaarName': (app.identityDetails or {}).get('name') or (app.ocrExtractedData or {}).get('AADHAAR', {}).get('name'),
        'userName': getattr(user, 'name', ''),
    }
    result = seller_docs.process_document(doc_type, doc.file.path, doc.mimeType, context=context)
    doc.ocrStatus, doc.extractedFields = result['ocrStatus'], dict(result['extractedFields'])
    if result.get('fieldConfidences'):
        doc.extractedFields['fieldConfidences'] = result['fieldConfidences']
    doc.redactedText, doc.confidence, doc.warnings = result['redactedText'], result['confidence'], result['warnings']
    doc.save()

    app_updates = []
    fields = doc.extractedFields or {}
    if doc.ocrStatus == 'DONE':
        if doc_type == 'AADHAAR':
            if fields.get('aadhaarLast4'):
                app.aadhaarLast4 = fields['aadhaarLast4']
                app_updates.append('aadhaarLast4')
            if fields.get('name') and (not app.applicantName or app.applicantName in (user.name, user.email) or (fields.get('fatherName') and app.applicantName == fields['fatherName'])):
                app.applicantName = fields['name']
                app_updates.append('applicantName')
            res_addr = fields.get('residentialAddress') or fields.get('address')
            if res_addr:
                app.residentialAddress = res_addr
                app_updates.append('residentialAddress')
            res_pin = fields.get('residentialPincode') or fields.get('pincode')
            if res_pin:
                app.residentialPincode = res_pin
                app_updates.append('residentialPincode')
            res_city = fields.get('residentialCity') or fields.get('city')
            if res_city:
                app.residentialCity = res_city
                app_updates.append('residentialCity')
            res_state = fields.get('residentialState') or fields.get('state')
            if res_state:
                app.residentialState = res_state
                app_updates.append('residentialState')
        elif doc_type == 'PAN':
            if fields.get('pan') and not app.pan:
                app.pan = fields['pan']
                app_updates.append('pan')
            if fields.get('name') and (not app.applicantName or app.applicantName in (user.name, user.email) or (fields.get('fatherName') and app.applicantName == fields['fatherName'])):
                app.applicantName = fields['name']
                app_updates.append('applicantName')
        elif doc_type == 'GST_CERTIFICATE':
            if fields.get('gstin') and not app.gstin:
                app.gstin = fields['gstin']
                app_updates.append('gstin')
            if fields.get('pan') and not app.pan:
                app.pan = fields['pan']
                app_updates.append('pan')
            biz_name = fields.get('companyName') or fields.get('businessName')
            if biz_name and (not app.companyName or 'store not named yet' in app.companyName.lower()):
                app.companyName = biz_name
                app_updates.append('companyName')

        all_docs = list(app.documents.all())
        app.identityDetails = seller_docs.merge_identity(all_docs)
        app.ocrExtractedData = {d.docType: d.extractedFields for d in all_docs if d.ocrStatus == 'DONE'}
        app_updates.extend(['identityDetails', 'ocrExtractedData'])
        app.save(update_fields=list(set(app_updates)))
    elif doc_type == 'AADHAAR' and fields.get('aadhaarLast4'):
        app.aadhaarLast4 = fields['aadhaarLast4']
        app.save(update_fields=['aadhaarLast4'])

    if doc.ocrStatus == 'REJECTED':  # an unmasked Aadhaar is not kept at all
        doc.file.delete(save=False)
        doc.file = ''
        doc.save()
    return Response(_doc_json(doc, _is_admin(user)), status=http.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def seller_application_submit_view(request, pk):
    """Finish the application. The status depends on what was uploaded and whether it matches the form."""
    user, err = _require(request)
    if err:
        return err
    app = _load(pk)
    if not app or not _owns(user, app):
        return Response({'detail': 'Application not found.'}, status=http.HTTP_404_NOT_FOUND)
    if app.status not in EDITABLE_STATES:
        return Response({'detail': 'This application was already submitted.'}, status=http.HTTP_409_CONFLICT)

    docs = list(app.documents.all())
    comparison = seller_docs.compare_application(app, docs)
    decision = seller_docs.decide_status(app, docs, comparison)
    previous = app.status
    app.status = decision['status']
    app.identityDetails = seller_docs.merge_identity(docs)
    app.verificationResults = comparison
    app.riskScore, app.riskCategory = comparison['riskScore'], comparison['riskCategory']
    app.missingFields = decision['missing']
    app.aiAssessment = f"{decision['reason']} Automatic risk score {comparison['riskScore']}/100. A person makes the final decision."
    app.save()
    _audit(app, previous, app.status, 'APPLICATION_SUBMITTED', user.email, decision['reason'])
    return Response(_profile(app, user))


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def seller_application_prepare_view(request, pk):
    """The Seller Onboarding Agent prepares an application summary, checks missing information, and evaluates risk."""
    user, err = _require(request)
    if err:
        return err
    app = _load(pk)
    if not app or not (_is_admin(user) or _owns(user, app)):
        return Response({'detail': 'Application not found.'}, status=http.HTTP_404_NOT_FOUND)

    from .agents.engine import agent_engine as orchestrator
    result = orchestrator.run_seller_onboarding_agent({'id': app.id}, user_role=user.role, user_email=user.email)
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def seller_document_file_view(request, pk, doc_id):
    """Streams a private document to the applicant or an admin. Never public."""
    user, err = _require(request)
    if err:
        return err
    app = _load(pk)
    doc = SellerDocument.objects.filter(id=doc_id, application_id=pk).first()
    if not app or not doc or not doc.file or not (_is_admin(user) or _owns(user, app)):
        return Response({'detail': 'Document not found or access denied.'}, status=http.HTTP_404_NOT_FOUND)

    import mimetypes
    content_type = doc.mimeType
    if not content_type or content_type == 'application/octet-stream':
        guessed, _ = mimetypes.guess_type(doc.fileName or str(doc.file.name))
        content_type = guessed or 'application/octet-stream'

    try:
        f = doc.file.open('rb')
    except Exception:
        return Response({'detail': 'Document file is missing or corrupted on disk.'}, status=http.HTTP_404_NOT_FOUND)

    response = FileResponse(f, filename=doc.fileName or 'document', content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{doc.fileName or "document"}"'
    return response


ACTIONS = {
    # action: (new status, allowed from, reason required)
    'APPROVE': ('APPROVED', ('PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW'), False),
    'REJECT': ('REJECTED', ('PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW', 'NEEDS_MORE_INFORMATION'), True),
    'REQUEST_INFO': ('NEEDS_MORE_INFORMATION', ('PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW'), True),
    'SUSPEND': ('SUSPENDED', ('APPROVED',), True),
}


def _activate_seller(app, admin_email):
    """Creates the Seller and the Store (so it shows on the nearby-store map) and upgrades the applicant's role."""
    today = datetime.date.today().isoformat()
    seller, _ = Seller.objects.update_or_create(
        id=f"sel-{app.id}",
        defaults={'name': app.applicantName, 'companyName': app.companyName, 'email': app.email, 'phone': app.phone,
                  'productsCount': len(app.plannedProducts or []), 'status': 'Approved', 'joinedDate': today, 'city': app.city},
    )
    lat, lng = app.storeLatitude, app.storeLongitude
    if lat is None or lng is None:
        found = resolve_coordinates(app.pincode) or resolve_coordinates(app.city)
        lat, lng = (found[0], found[1]) if found else (19.076, 72.8777)
    Store.objects.update_or_create(
        id=f"store-{app.id}",
        defaults={'name': app.storeName or app.companyName, 'seller': app.companyName, 'sellerId': seller.id, 'address': app.address,
                  'city': app.city or 'Mumbai', 'state': app.addressState, 'pincode': app.pincode, 'latitude': lat, 'longitude': lng,
                  'phone': app.phone, 'email': app.email, 'operatingStatus': 'Open', 'fulfillmentCapability': 'Pickup and Delivery'},
    )
    # The products the seller listed while applying go live with the stock and photo they gave, so the dashboard starts full.
    from django.utils.text import slugify
    for item in app.plannedProducts or []:
        price = float(item.get('approxPrice') or 0)
        name = str(item.get('name') or '').strip()
        if not name or price <= 0 or Product.objects.filter(seller=app.companyName, name=name).exists():
            continue
        pid = f"prod-{uuid.uuid4().hex[:8]}"
        stock = int(item.get('stock') or 0)
        Product.objects.create(
            id=pid, name=name, slug=f"{slugify(name)[:200]}-{pid[-4:]}", category=item.get('category') or (app.productCategories or ['Home & Kitchen'])[0],
            price=price, originalPrice=0, discount=0, stock=stock, stockStatus='Out of Stock' if stock <= 0 else ('Low Stock' if stock <= 10 else 'In Stock'),
            images=[item['image']] if item.get('image') else [], seller=app.companyName, createdAt=today, newArrival=True)
    Seller.objects.filter(id=seller.id).update(productsCount=Product.objects.filter(seller=app.companyName).count())
    owner = User.objects.filter(id=app.ownerUserId).first()
    if owner and owner.role == 'CUSTOMER':
        owner.role = 'SELLER'
        owner.save(update_fields=['role'])
    app.sellerId = seller.id
    app.reviewedBy = admin_email


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_seller_application_action_view(request, pk):
    """Admin decision on an application: APPROVE, REJECT, REQUEST_INFO or SUSPEND."""
    user, err = _require(request, ADMIN_ROLES)
    if err:
        return err
    app = _load(pk)
    if not app:
        return Response({'detail': 'Application not found.'}, status=http.HTTP_404_NOT_FOUND)

    action = str(request.data.get('action') or '').upper()
    reason = str(request.data.get('reason') or '').strip()
    if action not in ACTIONS:
        return Response({'detail': f"Unknown action. Use one of: {', '.join(ACTIONS)}."}, status=http.HTTP_400_BAD_REQUEST)
    new_status, allowed_from, needs_reason = ACTIONS[action]
    if app.status not in allowed_from:
        return Response({'detail': f"You can't {action.replace('_', ' ').lower()} an application that is {app.status.replace('_', ' ').lower()}."},
                        status=http.HTTP_400_BAD_REQUEST)
    if needs_reason and not reason:
        return Response({'detail': 'Write a reason. The applicant will see it.', 'errors': {'reason': 'Required'}},
                        status=http.HTTP_400_BAD_REQUEST)

    if action == 'APPROVE':  # never go live without the identity documents and a store location
        have = set(app.documents.values_list('docType', flat=True))
        gaps = [name for key, name in (('AADHAAR', 'Aadhaar'), ('PAN', 'PAN card')) if key not in have]
        if app.storeLatitude is None or app.storeLongitude is None:
            gaps.append('a store location on the map')
        if gaps:
            return Response({'detail': f"Cannot approve yet. Missing: {', '.join(gaps)}. Ask the seller for them."}, status=http.HTTP_400_BAD_REQUEST)

    previous = app.status
    app.status = new_status
    if action == 'APPROVE':
        app.rejectionReason = ''
        _activate_seller(app, user.email)
    elif action == 'REJECT':
        app.rejectionReason, app.reviewedBy = reason, user.email
    elif action == 'REQUEST_INFO':
        app.adminNotes, app.reviewedBy = reason, user.email
    elif action == 'SUSPEND':
        app.rejectionReason, app.reviewedBy = reason, user.email
        Seller.objects.filter(id=app.sellerId).update(status='Suspended')
        Store.objects.filter(sellerId=app.sellerId).update(operatingStatus='Closed')
    app.save()
    _audit(app, previous, new_status, action, user.email, reason)
    return Response({'success': True, 'applicationId': app.id, 'previousStatus': previous, 'currentStatus': new_status,
                     'profile': _profile(app, user)})


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_seller_detail_view(request, seller_id):
    """One seller in full for the admin: contact, live numbers worked out from real orders, and the onboarding application with its documents."""
    from .models import Order
    from .seller_analytics import analytics
    user, err = _require(request, ADMIN_ROLES)
    if err:
        return err
    seller = Seller.objects.filter(id=seller_id).first()
    if not seller:
        return Response({'detail': 'Seller not found.'}, status=http.HTTP_404_NOT_FOUND)
    app = SellerApplication.objects.filter(sellerId=seller.id).first() or SellerApplication.objects.filter(companyName=seller.companyName or seller.name).first()
    products = list(Product.objects.filter(seller__in=[x for x in (seller.companyName, seller.name) if x]))
    ids = {p.id for p in products}
    orders = [o for o in Order.objects.exclude(status='Cancelled') if any(str(i.get('id')) in ids for i in (o.items or []))]
    earn = analytics(products)['earnings'] if products else {'gross': 0, 'commission': 0, 'youKeep': 0}
    return Response({
        'seller': {'id': seller.id, 'name': seller.name, 'companyName': seller.companyName, 'email': seller.email, 'phone': seller.phone,
                   'city': seller.city, 'status': seller.status, 'joinedDate': seller.joinedDate, 'rating': seller.rating},
        'live': {'products': len(products), 'orders': len(orders), 'revenue': earn['gross'], 'commission': earn['commission'],
                 'lowStock': sum(1 for p in products if 0 < p.stock <= 10), 'outOfStock': sum(1 for p in products if p.stock <= 0)},
        'products': [{'id': p.id, 'name': p.name, 'price': p.price, 'stock': p.stock} for p in products[:12]],
        'application': _profile(app, user) if app else None,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def seller_application_product_image_view(request, pk):
    """An applicant uploads a photo for one of their planned products. Returns the public URL to store on the product."""
    from .product_images import save_photo
    user, err = _require(request)
    if err:
        return err
    app = _load(pk)
    if not app or not _owns(user, app):
        return Response({'detail': 'Application not found.'}, status=http.HTTP_404_NOT_FOUND)
    photo = request.FILES.get('image')
    if not photo:
        return Response({'detail': 'Choose a photo first.'}, status=http.HTTP_400_BAD_REQUEST)
    url, problem = save_photo(photo, request)
    if problem:
        return Response({'detail': problem}, status=http.HTTP_400_BAD_REQUEST)
    return Response({'url': url})
