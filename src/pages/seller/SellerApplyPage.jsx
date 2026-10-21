import HowItWorks from './HowItWorks';
import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Check,
  Plus,
  Trash2,
  Upload,
  FileText,
  Sparkles,
  Bot,
  ShieldCheck,
  AlertCircle,
  RefreshCw,
  MapPin,
  Copy,
  Search,
  ArrowRight,
  ArrowLeft,
  Eye,
  X,
} from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import LocationPinMap, { findOnMap, lookupPincode, reverseGeocode, geocodeAddress } from '../../storefront/LocationPinMap';
import { asList } from '../../storefront/parts';
import '../../storefront/storefront.css';
import '../../storefront/forms.css';

const STAGES = [
  { id: 0, label: '1. Identity & Documents' },
  { id: 1, label: '2. Store Location & Map' },
  { id: 2, label: '3. Products & Stock' },
  { id: 3, label: '4. Review & Submit' },
];

const DOCS = [
  {
    type: 'PAN',
    label: 'PAN Card',
    required: true,
    hint: 'Clear photo or PDF of the business owner’s PAN card. Supported: JPG, PNG, PDF (up to 10 MB).',
  },
  {
    type: 'AADHAAR',
    label: 'Aadhaar (Masked Copy Only)',
    required: true,
    hint: 'Download masked Aadhaar from myAadhaar (first 8 digits hidden, last 4 digits kept). Full 12-digit unmasked Aadhaar documents are automatically rejected.',
  },
  {
    type: 'GST_CERTIFICATE',
    label: 'Business Licence / GST Certificate',
    required: false,
    hint: 'Optional trade licence, Shop & Establishment certificate, or GST registration showing your GSTIN.',
  },
];

const FINAL = ['PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW', 'APPROVED', 'REJECTED', 'SUSPENDED'];

const STATUS_COPY = {
  PENDING_ADMIN_APPROVAL: [
    'info',
    'Waiting for review',
    'All your documents are in and the details match. An administrator on our team will review your application next.',
  ],
  NEEDS_MANUAL_REVIEW: [
    'warn',
    'A person will check your details',
    'Some details did not match your documents, or a document could not be read automatically. Our team will review it manually.',
  ],
  NEEDS_MORE_INFORMATION: [
    'warn',
    'We need a little more from you',
    'Please add what is missing below and submit again.',
  ],
  APPROVED: [
    'ok',
    'You are approved',
    'Your store is live and displays on the nearby-store map.',
  ],
  REJECTED: [
    'bad',
    'Application not approved',
    'See the reason below. You can contact support if you think this is a mistake.',
  ],
  SUSPENDED: [
    'bad',
    'Store suspended',
    'Your store is paused. See the reason below.',
  ],
  DRAFT: [
    'info',
    'Draft',
    'Upload your documents, review extracted details, and submit.',
  ],
};

const Field = ({ id, label, hint, error, children }) => (
  <div className="ac-field" id={`field-${id}`}>
    <label htmlFor={id}>{label}</label>
    {children}
    {hint && !error && <small>{hint}</small>}
    {error && <span className="ac-err" role="alert">{error}</span>}
  </div>
);

export default function SellerApplyPage() {
  const { user } = useAuth();
  const [stage, setStage] = useState(0);
  const [justSubmitted, setJustSubmitted] = useState(false);
  const [categories, setCategories] = useState([]);
  const [app, setApp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState('');
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [agree, setAgree] = useState(false);
  const [pin, setPin] = useState({ lat: null, lng: null });
  const [agentSummary, setAgentSummary] = useState(null);
  const [agentLoading, setAgentLoading] = useState(false);

  // PIN lookup and reverse geocode state
  const [pinLookupBusy, setPinLookupBusy] = useState(false);
  const [pinLookupError, setPinLookupError] = useState('');
  const [pinLocalities, setPinLocalities] = useState([]);
  const [pinLocalityCoords, setPinLocalityCoords] = useState({});
  const [reverseGeocodeInfo, setReverseGeocodeInfo] = useState(null);

  // Document preview state
  const [docPreview, setDocPreview] = useState(null);
  const [docPreviewLoading, setDocPreviewLoading] = useState(false);
  const [docPreviewError, setDocPreviewError] = useState('');

  // Residential PIN lookup state
  const [resPinLookupBusy, setResPinLookupBusy] = useState(false);
  const [resPinLookupError, setResPinLookupError] = useState('');
  const [resLocalities, setResLocalities] = useState([]);
  const [resIsAmbiguous, setResIsAmbiguous] = useState(false);

  const [form, setForm] = useState({
    companyName: '',
    storeName: '',
    contactName: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    businessType: 'Retailer',
    gstin: '',
    pan: '',
    residentialAddress: '',
    residentialPincode: '',
    residentialCity: '',
    residentialState: '',
    address: '',
    city: 'Mumbai',
    state: 'Maharashtra',
    pincode: '',
    productCategories: [],
    plannedProducts: [{ name: '', category: '', approxPrice: '', stock: '', image: '' }],
  });
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  useEffect(() => {
    document.title = 'Sell on AutoCart';
  }, []);

  useEffect(() => {
    api.get('/categories').then((r) => setCategories(asList(r.data))).catch(() => {});
  }, []);

  // Initialize draft immediately upon loading so upload controls are active right away
  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }
    api
      .get('/seller/applications')
      .then(async (r) => {
        let mine =
          (r.data || []).find((a) => a.ownerUserId === user.id && !['REJECTED'].includes(a.status)) ||
          (r.data || [])[0];
        if (!mine && user.role === 'CUSTOMER') {
          try {
            const initRes = await api.post('/seller/applications/start');
            mine = initRes.data;
          } catch (e) {
            console.warn('Auto-start application failed', e);
          }
        }
        if (!mine) return;
        return api.get(`/seller/applications/${mine.id}`).then((d) => {
          const a = d.data;
          setApp(a);
          setForm((f) => ({
            ...f,
            companyName: /store not named yet/.test(a.companyName || '') ? '' : a.companyName || '',
            storeName: /store not named yet/.test(a.storeName || a.companyName || '') ? '' : a.storeName || '',
            contactName: a.applicantName || f.contactName,
            email: a.email || f.email,
            phone: a.phone || '',
            businessType: a.businessType || 'Retailer',
            gstin: a.gstin || '',
            pan: a.pan || '',
            residentialAddress: a.residentialAddress || a.residential?.address || '',
            residentialPincode: a.residentialPincode || a.residential?.pincode || '',
            residentialCity: a.residentialCity || a.residential?.city || '',
            residentialState: a.residentialState || a.residential?.state || '',
            address: a.address || a.store?.address || '',
            city: a.city || a.store?.city || 'Mumbai',
            state: a.addressState || a.store?.state || 'Maharashtra',
            pincode: a.pincode || a.store?.pincode || '',
            productCategories: a.productCategories || [],
            plannedProducts: a.plannedProducts?.length ? a.plannedProducts : f.plannedProducts,
          }));
          if (a.storeLatitude && a.storeLongitude) {
            setPin({ lat: a.storeLatitude, lng: a.storeLongitude });
          }
          if (a.status === 'NEEDS_MORE_INFORMATION') setStage(0);
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user]);

  const docByType = useMemo(
    () => Object.fromEntries((app?.documents || []).map((d) => [d.docType, d])),
    [app]
  );
  const submitted =
    app && (FINAL.includes(app.status) || (justSubmitted && app.status === 'NEEDS_MORE_INFORMATION'));

  const reqDocs = DOCS.filter((d) => d.required);
  const reqDocsDone = reqDocs.filter(
    (d) => docByType[d.type] && docByType[d.type].ocrStatus !== 'REJECTED'
  ).length;
  const docsDone = DOCS.filter(
    (d) => docByType[d.type] && docByType[d.type].ocrStatus !== 'REJECTED'
  ).length;

  const scrollToFirstError = (errs) => {
    const firstKey = Object.keys(errs)[0];
    if (!firstKey) return;
    const el = document.getElementById(firstKey) || document.getElementById(`field-${firstKey}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.focus?.();
    }
  };

  const handlePincodeLookup = async (codeToLookup) => {
    const targetPin = (codeToLookup || form.pincode || '').trim();
    if (!/^[1-9]\d{5}$/.test(targetPin)) {
      setPinLookupError('Please enter a valid 6-digit Indian PIN code.');
      return;
    }
    setPinLookupBusy(true);
    setPinLookupError('');
    try {
      const data = await lookupPincode(targetPin);
      setForm((prev) => ({
        ...prev,
        pincode: targetPin,
        city: data.district || data.city || prev.city,
        state: data.state || prev.state,
      }));
      if (data.centroid?.lat && data.centroid?.lng) {
        setPin({ lat: data.centroid.lat, lng: data.centroid.lng });
      }
      if (data.localities && data.localities.length > 0) {
        setPinLocalities(data.localities);
      } else {
        setPinLocalities([]);
      }
      if (data.localityCoordinates) {
        setPinLocalityCoords(data.localityCoordinates);
      } else {
        setPinLocalityCoords({});
      }
      setErrors((prev) => {
        const next = { ...prev };
        delete next.pincode;
        delete next.location;
        return next;
      });
    } catch (e) {
      setPinLookupError(e.message || 'PIN code not found in postal records.');
      setPinLocalities([]);
      setPinLocalityCoords({});
    } finally {
      setPinLookupBusy(false);
    }
  };

  const handleLocalityClick = async (loc) => {
    // 1. Update street address
    setForm((prev) => {
      const cur = prev.address || '';
      if (!cur.toLowerCase().includes(loc.toLowerCase())) {
        return { ...prev, address: cur ? `${cur}, ${loc}` : loc };
      }
      return prev;
    });

    // 2. Clear location & address errors
    setErrors((prev) => {
      const next = { ...prev };
      delete next.location;
      delete next.address;
      return next;
    });

    // 3. Resolve and update coordinates immediately
    let coords = pinLocalityCoords?.[loc];
    if (!coords) {
      try {
        coords = await geocodeAddress(loc, form.pincode, form.city);
      } catch (_) {}
    }
    if (coords && coords.lat != null && coords.lng != null) {
      setPin({ lat: Number(coords.lat), lng: Number(coords.lng) });
    }
  };

  const openDocument = async (doc) => {
    if (!doc) return;
    setDocPreviewLoading(true);
    setDocPreviewError('');
    try {
      const fileUrl = doc.fileUrl ? doc.fileUrl.replace(/^\/api/, '') : `/seller/applications/${app?.id}/documents/${doc.id}/file`;
      const res = await api.get(fileUrl, { responseType: 'blob' });
      const blobUrl = URL.createObjectURL(res.data);
      setDocPreview({
        url: blobUrl,
        fileName: doc.fileName || 'document',
        mimeType: doc.mimeType || res.data.type || 'image/jpeg',
      });
    } catch (err) {
      console.error('Failed to open document:', err);
      setDocPreviewError('Unable to open document. Please ensure the file was saved correctly.');
    } finally {
      setDocPreviewLoading(false);
    }
  };

  const handleResidentialPincodeLookup = async (codeToLookup, addressContext, forceOverwrite = false) => {
    const targetPin = (codeToLookup || form.residentialPincode || '').trim();
    if (!/^[1-9]\d{5}$/.test(targetPin)) {
      setResPinLookupError('Please enter a valid 6-digit Indian PIN code.');
      return;
    }
    setResPinLookupBusy(true);
    setResPinLookupError('');
    try {
      const data = await lookupPincode(targetPin, addressContext || form.residentialAddress);
      setForm((prev) => ({
        ...prev,
        residentialPincode: targetPin,
        residentialCity: (!prev.residentialCity || forceOverwrite) ? (data.city || data.district || prev.residentialCity) : prev.residentialCity,
        residentialState: data.state || prev.residentialState || 'Maharashtra',
      }));
      if (data.localities && data.localities.length > 0) {
        setResLocalities(data.localities);
      } else {
        setResLocalities([]);
      }
      setResIsAmbiguous(Boolean(data.isAmbiguous));
      setErrors((prev) => {
        const next = { ...prev };
        delete next.residentialPincode;
        delete next.residentialCity;
        return next;
      });
    } catch (e) {
      setResPinLookupError(e.message || 'Residential PIN code not found in postal records.');
      setResLocalities([]);
    } finally {
      setResPinLookupBusy(false);
    }
  };

  const handlePinChange = async (lat, lng) => {
    setPin({ lat, lng });
    setErrors((prev) => {
      const next = { ...prev };
      delete next.location;
      return next;
    });
    try {
      const geo = await reverseGeocode(lat, lng);
      setReverseGeocodeInfo(geo);
    } catch (_) {}
  };

  const handleCopyResidentialAddress = async () => {
    if (!form.residentialAddress && !form.residentialPincode) {
      setMessage('No residential address found from Aadhaar yet. Upload your Masked Aadhaar first or enter your store address directly.');
      return;
    }
    const nextPin = form.residentialPincode || form.pincode;
    setForm((prev) => ({
      ...prev,
      address: prev.residentialAddress || prev.address,
      pincode: nextPin,
      city: prev.residentialCity || prev.city,
      state: prev.residentialState || prev.state,
    }));
    setMessage('Copied verified residential address to store fields.');
    if (nextPin && /^[1-9]\d{5}$/.test(nextPin)) {
      handlePincodeLookup(nextPin);
    }
  };

  const save = async (stepStage = 'ALL') => {
    setBusy('save');
    setErrors({});
    setMessage('');
    try {
      const payload = {
        ...form,
        stage: stepStage,
        storeLatitude: pin.lat != null ? pin.lat : null,
        storeLongitude: pin.lng != null ? pin.lng : null,
        plannedProducts: form.plannedProducts
          .filter((p) => p.name.trim())
          .map((p) => ({
            ...p,
            approxPrice: Number(p.approxPrice) || 0,
            stock: Number(p.stock) || 0,
          })),
      };
      const { data } = await api.post('/seller/applications', payload);
      setApp(data);
      return true;
    } catch (e) {
      const errs = e?.response?.data?.errors || {};
      setErrors(errs);
      setMessage(e?.response?.data?.detail || 'Please fix the highlighted fields below.');
      scrollToFirstError(errs);
      return false;
    } finally {
      setBusy('');
    }
  };

  const fetchAgentSummary = async (targetAppId) => {
    const id = targetAppId || app?.id;
    if (!id) return;
    setAgentLoading(true);
    try {
      const { data } = await api.get(`/seller/applications/${id}/prepare`);
      setAgentSummary(data);
    } catch (e) {
      if (app?.comparison) {
        setAgentSummary({
          riskScore: app.riskScore || app.comparison.riskScore,
          riskCategory: app.riskCategory || app.comparison.riskCategory,
          preliminaryStatus: app.status === 'DRAFT' ? 'Ready for review' : app.status,
          missingFields: app.missingDocuments || [],
          discrepancies: (app.comparison.checks || []).filter((c) => c.status === 'mismatch'),
          verifiedFacts: (app.comparison.checks || []).filter((c) => c.status === 'match').map((c) => c.label),
        });
      }
    } finally {
      setAgentLoading(false);
    }
  };

  const goToStep1 = async () => {
    // Validate Step 0: Identity & Documents
    const errs = {};
    if (!form.companyName.trim()) errs.companyName = 'Enter your business or store name.';
    if (!form.contactName.trim()) errs.contactName = 'Enter the name of the person applying.';
    const digits = form.phone.replace(/\D/g, '');
    if (digits.length < 10) errs.phone = 'Enter a valid 10-digit phone number.';
    if (!form.email || !form.email.includes('@')) errs.email = 'Enter a valid business email.';
    const panClean = form.pan.trim().toUpperCase();
    if (!panClean || !/^[A-Z]{5}[0-9]{4}[A-Z]$/.test(panClean)) {
      errs.pan = 'Enter a valid 10-character PAN (e.g. ABCDE1234F).';
    }
    if (
      form.gstin.trim() &&
      !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(form.gstin.trim().toUpperCase())
    ) {
      errs.gstin = 'GSTIN must be 15 characters, like 27ABCDE1234F1Z5.';
    }

    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      setMessage('Please fix the highlighted fields before proceeding.');
      scrollToFirstError(errs);
      return;
    }

    const ok = await save('STAGE_1');
    if (!ok) return;
    setStage(1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const goToStep2 = async () => {
    // Validate Step 1: Store Location & Map
    const errs = {};
    if (!form.address.trim()) errs.address = 'Enter the store street address.';
    if (!/^[1-9]\d{5}$/.test(form.pincode.trim())) errs.pincode = 'Enter a valid 6-digit Indian PIN code.';
    if (
      pin.lat == null ||
      pin.lng == null ||
      isNaN(pin.lat) ||
      isNaN(pin.lng) ||
      pin.lat < 6 ||
      pin.lat > 38 ||
      pin.lng < 68 ||
      pin.lng > 98
    ) {
      errs.location = 'Please place your store pin on the map within India.';
    }

    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      setMessage('Please fix the store address and map location before proceeding.');
      scrollToFirstError(errs);
      return;
    }

    const ok = await save('STAGE_2');
    if (!ok) return;
    setStage(2);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const goToStep3 = async () => {
    // Validate Step 2: Products & Stock
    const validProds = form.plannedProducts.filter((p) => p.name.trim());
    if (validProds.length === 0) {
      const errs = { plannedProducts: 'Add at least one product you plan to sell.' };
      setErrors(errs);
      setMessage('Please add at least one product with initial stock.');
      scrollToFirstError(errs);
      return;
    }

    const ok = await save('STAGE_3');
    if (!ok) return;
    setStage(3);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    fetchAgentSummary(app?.id);
  };

  const upload = async (type, file) => {
    if (!file) return;
    setBusy(type);
    setMessage('');
    try {
      let currentApp = app;
      if (!currentApp) {
        const initRes = await api.post('/seller/applications/start');
        currentApp = initRes.data;
        setApp(currentApp);
      }
      const body = new FormData();
      body.append('docType', type);
      body.append('file', file);
      const res = await api.post(`/seller/applications/${currentApp.id}/documents`, body, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const { data } = await api.get(`/seller/applications/${currentApp.id}`);
      setApp(data);
      const ext = res?.data?.extractedFields || {};

      setForm((prev) => {
        const nextForm = { ...prev };
        if (type === 'PAN') {
          if (ext.pan) nextForm.pan = ext.pan;
          if (ext.name && (!nextForm.contactName || nextForm.contactName === user?.name || (ext.fatherName && nextForm.contactName === ext.fatherName))) {
            nextForm.contactName = ext.name;
          }
        } else if (type === 'AADHAAR') {
          if (ext.name && (!nextForm.contactName || nextForm.contactName === user?.name || (ext.fatherName && nextForm.contactName === ext.fatherName))) {
            nextForm.contactName = ext.name;
          }
          // Aadhaar populates verified residential address (never overwrite store commercial address!)
          const resAddr = ext.residentialAddress || ext.address;
          const resPin = ext.residentialPincode || ext.pincode;
          if (resAddr) nextForm.residentialAddress = resAddr;
          if (resPin) nextForm.residentialPincode = resPin;
          if (ext.residentialCity || ext.city) nextForm.residentialCity = ext.residentialCity || ext.city;
          if (ext.residentialState || ext.state) nextForm.residentialState = ext.residentialState || ext.state;
        } else if (type === 'GST_CERTIFICATE') {
          if (ext.gstin) nextForm.gstin = ext.gstin;
          if (ext.pan && !nextForm.pan) nextForm.pan = ext.pan;
          if (ext.companyName || ext.businessName) {
            nextForm.companyName = ext.companyName || ext.businessName;
            if (!nextForm.storeName) nextForm.storeName = ext.companyName || ext.businessName;
          }
        }
        return nextForm;
      });

      if (type === 'AADHAAR') {
        const resAddr = ext.residentialAddress || ext.address || '';
        const resPin = ext.residentialPincode || ext.pincode || '';
        if (resPin && /^[1-9]\d{5}$/.test(resPin)) {
          handleResidentialPincodeLookup(resPin, resAddr, !ext.residentialCity && !ext.city);
        }
      }

      if (res?.data?.ocrStatus === 'REJECTED') {
        setMessage(`⚠️ Document rejected: ${res.data.warnings?.join(' ') || 'Unmasked Aadhaar or invalid document.'}`);
      } else {
        setMessage(`✓ ${type} uploaded and analyzed successfully.`);
      }
    } catch (e) {
      setMessage(
        e?.response?.data?.detail || 'Document upload failed. Ensure the file is a clean JPG, PNG, or PDF under 10 MB.'
      );
    } finally {
      setBusy('');
    }
  };

  const submit = async () => {
    if (!agree) {
      setSubmitNote('Please confirm the agreement checkbox below before submitting.');
      document.getElementById('agree-box')?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      return;
    }
    setSubmitNote('');
    setBusy('submit');
    setMessage('');
    try {
      const { data } = await api.post(`/seller/applications/${app.id}/submit`);
      setApp(data);
      setJustSubmitted(true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (e) {
      setMessage(e?.response?.data?.detail || 'We could not submit your application. Please check all steps.');
    } finally {
      setBusy('');
    }
  };

  const [photoBusy, setPhotoBusy] = useState(-1);
  const [submitNote, setSubmitNote] = useState('');
  const planPhoto = async (i, file) => {
    if (!file || !app) return;
    setPhotoBusy(i);
    setMessage('');
    const body = new FormData();
    body.append('image', file);
    try {
      const { data } = await api.post(`/seller/applications/${app.id}/product-image`, body);
      setProduct(i, 'image', data.url);
    } catch (e) {
      setMessage(e?.response?.data?.detail || 'Photo upload failed. Use a JPG or PNG under 5 MB.');
    } finally {
      setPhotoBusy(-1);
    }
  };
  const setProduct = (i, k, v) =>
    set(
      'plannedProducts',
      form.plannedProducts.map((p, n) => (n === i ? { ...p, [k]: v } : p))
    );

  if (loading) {
    return (
      <div className="ac ac-page">
        <div className="ac-wrap">
          <div className="ac-skel" style={{ height: 320 }} />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="ac ac-page">
        <div className="ac-wrap" style={{ maxWidth: 720 }}>
          <h1 className="ac-display">Sell on AutoCart</h1>
          <details className="ac-howfold">
            <summary>How selling works and what it costs (tap to open)</summary>
            <HowItWorks compact />
          </details>
          <p className="ac-sub">Reach shoppers near your store. Sign in or create an account first, then register your shop.</p>
          <div className="ac-row" style={{ marginTop: 24 }}>
            <Link to="/login" state={{ from: '/seller/apply' }} className="ac-btn ac-btn-blue">
              Sign in
            </Link>
            <Link to="/register" className="ac-btn ac-btn-outline">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ---- Already submitted: display status tracking ----
  if (submitted) {
    const [tone, title, text] = STATUS_COPY[app.status] || STATUS_COPY.DRAFT;
    return (
      <div className="ac ac-page">
        <div className="ac-wrap" style={{ maxWidth: 820 }}>
          <h1 className="ac-display">Your seller application</h1>
          <div className="ac-box" style={{ marginTop: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
              <span className="ac-chip-status" data-tone={tone}>
                {title}
              </span>
              <span style={{ fontSize: 13, color: '#64748b', fontWeight: 600 }}>
                Application ID: {app.id}
              </span>
            </div>
            <p style={{ margin: '14px 0 0', fontSize: 18 }}>{text}</p>
            {app.rejectionReason && <p className="ac-warn" style={{ fontSize: 16 }}>Reason: {app.rejectionReason}</p>}
            {app.status === 'NEEDS_MORE_INFORMATION' && app.adminNotes && (
              <p className="ac-warn" style={{ fontSize: 16 }}>Message from our team: {app.adminNotes}</p>
            )}
            {app.status === 'NEEDS_MORE_INFORMATION' && (app.missingDocuments || []).length > 0 && (
              <p className="ac-warn" style={{ fontSize: 16 }}>
                Still needed: {app.missingDocuments.map((t) => DOCS.find((d) => d.type === t)?.label || t).join(', ')}.
              </p>
            )}
            <p className="ac-muted">
              Store: {app.storeName || app.companyName} · {app.address}, {app.city} {app.pincode}
            </p>
            <div className="ac-row" style={{ marginTop: 20 }}>
              {app.status === 'NEEDS_MORE_INFORMATION' && (
                <button
                  className="ac-btn ac-btn-blue"
                  onClick={() => {
                    setJustSubmitted(false);
                    setStage(0);
                    window.scrollTo({ top: 0 });
                  }}
                >
                  Update documents
                </button>
              )}
              {app.status === 'APPROVED' && (
                <Link to="/seller/dashboard" className="ac-btn ac-btn-blue">
                  Go to your seller dashboard
                </Link>
              )}
              {['REJECTED', 'SUSPENDED'].includes(app.status) && (
                <Link to="/support" className="ac-btn ac-btn-blue">
                  Contact support
                </Link>
              )}
              <Link to="/" className="ac-btn ac-btn-outline">
                Back to the store
              </Link>
            </div>
          </div>
          {app.comparison?.checks?.length > 0 && (
            <div className="ac-box" style={{ marginTop: 20 }}>
              <h2>Automated Verification Summary</h2>
              <div className="ac-scroll-x">
                <table className="ac-table">
                  <tbody>
                    {app.comparison.checks.map((c) => (
                      <tr key={c.label}>
                        <td>{c.label}</td>
                        <td>
                          <span
                            className="ac-chip-status"
                            data-tone={c.status === 'match' ? 'ok' : c.status === 'mismatch' ? 'bad' : 'warn'}
                          >
                            {c.status === 'match' ? 'Matches' : c.status === 'mismatch' ? 'Mismatch' : 'Could not read'}
                          </span>
                        </td>
                        <td>
                          <small className="ac-muted">{c.detail}</small>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  const status = app?.status && STATUS_COPY[app.status];

  return (
    <div className="ac ac-page">
      <div className="ac-wrap" style={{ maxWidth: 940 }}>
        <h1 className="ac-display">Sell on AutoCart</h1>
        <details className="ac-howfold">
          <summary>How selling works and what it costs (tap to open)</summary>
          <HowItWorks compact />
        </details>
        <p className="ac-sub" style={{ marginTop: 14 }}>
          Agent-assisted seller onboarding with document OCR, separated residential & store addresses, PIN code lookup, and hyperlocal map placement. Final approval authority remains strictly with the human administrator.
        </p>

        {/* 4-Step Navigation Tabs */}
        <div
          style={{
            display: 'flex',
            gap: 8,
            margin: '24px 0 20px 0',
            borderBottom: '2px solid #e2e8f0',
            paddingBottom: 12,
            overflowX: 'auto',
          }}
        >
          {STAGES.map((s, idx) => {
            const isActive = stage === idx;
            const isDone = stage > idx;
            return (
              <button
                key={s.id}
                type="button"
                onClick={() => {
                  if (idx < stage) {
                    setStage(idx);
                  } else if (idx === 1) {
                    goToStep1();
                  } else if (idx === 2) {
                    goToStep2();
                  } else if (idx === 3) {
                    goToStep3();
                  }
                }}
                style={{
                  flex: 1,
                  minWidth: 160,
                  padding: '10px 14px',
                  borderRadius: '10px',
                  border: 'none',
                  background: isActive ? 'var(--brand, #2563eb)' : isDone ? '#eff6ff' : '#f8fafc',
                  color: isActive ? '#fff' : isDone ? '#1d4ed8' : '#64748b',
                  fontWeight: 700,
                  fontSize: 13,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 6,
                  transition: 'all 0.15s ease',
                }}
              >
                {isDone ? <Check size={16} /> : <span>{idx + 1}.</span>}
                <span>{s.label.split('. ')[1] || s.label}</span>
              </button>
            );
          })}
        </div>

        {status && app.status === 'NEEDS_MORE_INFORMATION' && (
          <div className="ac-box" style={{ marginBottom: 20, borderColor: 'var(--gold)' }}>
            <b>{status[1]}</b>
            <p style={{ margin: '6px 0 0' }}>{app.adminNotes || app.aiAssessment || status[2]}</p>
          </div>
        )}
        {message && (
          <div
            className="ac-box"
            role="alert"
            style={{
              marginBottom: 20,
              borderColor: message.startsWith('✓') ? '#22c55e' : 'var(--coral)',
              background: message.startsWith('✓') ? '#f0fdf4' : '#fff',
            }}
          >
            {message}
          </div>
        )}

        {/* =========================================================================
            STEP 0: IDENTITY DOCUMENTS & BUSINESS PROFILE
        ========================================================================= */}
        {stage === 0 && (
          <div className="space-y-6">
            <div className="ac-box">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, marginBottom: 8 }}>
                <h2 style={{ margin: 0 }}>Step 1: Identity Documents & Auto-Extraction</h2>
                <span style={{ fontSize: 13, fontWeight: 600, color: reqDocsDone >= reqDocs.length ? '#16a34a' : '#d97706' }}>
                  {reqDocsDone} of {reqDocs.length} required documents uploaded ({docsDone} total)
                </span>
              </div>
              <p className="ac-muted" style={{ margin: '0 0 16px 0', fontSize: 14 }}>
                Upload your PAN card and Masked Aadhaar. The Seller Onboarding Agent uses OCR to automatically extract your legal name, PAN number, and residential address.
              </p>

              <div style={{ background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '12px', padding: '12px 16px', marginBottom: 20 }}>
                <p style={{ margin: 0, fontSize: 13, color: '#334155', lineHeight: 1.5 }}>
                  🛡️ <strong>Aadhaar Privacy Compliance:</strong> Only masked Aadhaar documents (first 8 digits hidden, last 4 digits visible) are accepted. Full 12-digit numbers are automatically rejected. Raw identity documents and full identifiers are never sent to external LLMs.
                </p>
              </div>

              {/* Document Upload Cards */}
              <div style={{ display: 'grid', gap: 16 }}>
                {DOCS.map((d) => {
                  const doc = docByType[d.type];
                  const fields = doc?.extractedFields || {};
                  const rejected = doc?.ocrStatus === 'REJECTED';
                  const isReading = busy === d.type;

                  return (
                    <div
                      key={d.type}
                      style={{
                        border: '1px solid #e2e8f0',
                        borderRadius: 12,
                        padding: '16px 20px',
                        background: rejected ? '#fef2f2' : '#ffffff',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
                        <div style={{ flex: 1, minWidth: 260 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                            <span style={{ fontWeight: 700, fontSize: 16, color: '#0f172a' }}>{d.label}</span>
                            <span
                              style={{
                                fontSize: 11,
                                padding: '2px 8px',
                                borderRadius: '12px',
                                fontWeight: 700,
                                background: d.required ? '#eff6ff' : '#f1f5f9',
                                color: d.required ? '#1d4ed8' : '#475569',
                                border: d.required ? '1px solid #bfdbfe' : '1px solid #cbd5e1',
                              }}
                            >
                              {d.required ? 'Required' : 'Optional'}
                            </span>
                            {doc && !rejected && (
                              <span className="ac-chip-status" data-tone={doc.ocrStatus === 'DONE' ? 'ok' : 'warn'}>
                                {doc.ocrStatus === 'DONE' ? 'Read by OCR' : 'Needs review'}
                              </span>
                            )}
                            {doc?.confidence != null && doc.confidence > 0 && (
                              <span style={{ fontSize: 11, background: '#f1f5f9', color: '#334155', borderRadius: '6px', padding: '2px 8px', fontWeight: 600 }}>
                                {doc.confidence}% confidence
                              </span>
                            )}
                          </div>
                          <p className="ac-muted" style={{ margin: '4px 0 8px 0', fontSize: 13 }}>{d.hint}</p>

                          {isReading && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#2563eb', fontSize: 13, fontWeight: 600, margin: '8px 0' }}>
                              <RefreshCw className="animate-spin" size={16} /> Reading document with OCR engine...
                            </div>
                          )}

                          {doc && doc.fileName && !isReading && (
                            <div style={{ fontSize: 12, color: '#64748b', display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                              <FileText size={14} /> <span>{doc.fileName}</span>
                            </div>
                          )}

                          {/* Extracted Fields Preview */}
                          {doc && Object.keys(fields).filter((k) => k !== 'fieldConfidences').length > 0 && !isReading && (
                            <div style={{ marginTop: 10, padding: '8px 12px', background: '#f8fafc', borderRadius: 8, border: '1px solid #e2e8f0' }}>
                              <div style={{ fontSize: 12, fontWeight: 700, color: '#475569', marginBottom: 4 }}>Extracted from document:</div>
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                {Object.entries(fields)
                                  .filter(([k, v]) => k !== 'fieldConfidences' && typeof v !== 'object' && v !== null && v !== '')
                                  .map(([k, v]) => {
                                    const score = doc?.fieldConfidences?.[k] ?? fields?.fieldConfidences?.[k];
                                    return (
                                      <span key={k} style={{ fontSize: 12, background: '#fff', border: '1px solid #cbd5e1', padding: '2px 8px', borderRadius: 6, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                                        <strong>{k.replace(/([A-Z])/g, ' $1').toLowerCase()}:</strong> {String(v)}
                                        {score != null && (
                                          <span style={{ fontSize: 10, color: '#047857', background: '#ecfdf5', padding: '1px 5px', borderRadius: 4, fontWeight: 700 }}>
                                            {score}%
                                          </span>
                                        )}
                                      </span>
                                    );
                                  })}
                              </div>
                            </div>
                          )}

                          {doc?.warnings?.map((w) => (
                            <div key={w} style={{ color: '#b91c1c', fontSize: 13, marginTop: 6, fontWeight: 500 }} role="alert">
                              ⚠️ {w}
                            </div>
                          ))}
                        </div>

                        {/* Upload & View Action Buttons */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end' }}>
                          <label className="ac-btn ac-btn-outline" style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                            <Upload size={16} /> {doc && !rejected ? 'Replace document' : 'Choose file'}
                            <input
                              type="file"
                              className="ac-sr"
                              accept="image/*,.pdf"
                              disabled={!!busy}
                              onChange={(e) => {
                                upload(d.type, e.target.files?.[0]);
                                e.target.value = '';
                              }}
                            />
                          </label>
                          {doc && !rejected && (
                            <button
                              type="button"
                              className="ac-btn ac-btn-soft ac-btn-small"
                              onClick={() => openDocument(doc)}
                              style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, padding: '4px 10px' }}
                            >
                              <Eye size={14} /> Open document
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Extracted Business & Contact Details */}
            <div className="ac-box">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <ShieldCheck size={20} className="text-blue-600" />
                <h2 style={{ margin: 0 }}>Business Profile & Legal Identifiers</h2>
              </div>
              <p className="ac-muted" style={{ margin: '0 0 16px 0', fontSize: 14 }}>
                Review details extracted from your documents. You can manually correct any uncertain fields.
              </p>
              <div className="ac-grid-2">
                <Field id="contactName" label="Legal Full Name (from identity document)" error={errors.contactName}>
                  <input
                    id="contactName"
                    className="ac-input"
                    aria-invalid={!!errors.contactName}
                    value={form.contactName}
                    onChange={(e) => set('contactName', e.target.value)}
                    placeholder="e.g. Rahul Sharma"
                  />
                </Field>
                <Field id="pan" label="PAN Number (from PAN card)" error={errors.pan} hint="10 uppercase characters, e.g. ABCDE1234F">
                  <input
                    id="pan"
                    className="ac-input"
                    maxLength={10}
                    aria-invalid={!!errors.pan}
                    value={form.pan}
                    onChange={(e) => set('pan', e.target.value.toUpperCase())}
                    placeholder="ABCDE1234F"
                  />
                </Field>
                <Field id="companyName" label="Business / Company Name" error={errors.companyName}>
                  <input
                    id="companyName"
                    className="ac-input"
                    aria-invalid={!!errors.companyName}
                    value={form.companyName}
                    onChange={(e) => set('companyName', e.target.value)}
                    placeholder="Sharma Electronics"
                  />
                </Field>
                <Field id="storeName" label="Store Name on AutoCart" hint="Customer-facing store name">
                  <input
                    id="storeName"
                    className="ac-input"
                    value={form.storeName}
                    onChange={(e) => set('storeName', e.target.value)}
                    placeholder="Sharma Electronics Store"
                  />
                </Field>
                <Field id="gstin" label="GSTIN (optional, if registered)" error={errors.gstin} hint="15 characters, e.g. 27ABCDE1234F1Z5">
                  <input
                    id="gstin"
                    className="ac-input"
                    maxLength={15}
                    aria-invalid={!!errors.gstin}
                    value={form.gstin}
                    onChange={(e) => set('gstin', e.target.value.toUpperCase())}
                    placeholder="27ABCDE1234F1Z5"
                  />
                </Field>
                <Field id="businessType" label="Business Type">
                  <select
                    id="businessType"
                    className="ac-select"
                    value={form.businessType}
                    onChange={(e) => set('businessType', e.target.value)}
                  >
                    {['Retailer', 'Wholesaler', 'Brand or manufacturer', 'Individual seller'].map((t) => (
                      <option key={t}>{t}</option>
                    ))}
                  </select>
                </Field>
                <Field id="phone" label="Contact Telephone" error={errors.phone}>
                  <input
                    id="phone"
                    className="ac-input"
                    inputMode="tel"
                    aria-invalid={!!errors.phone}
                    value={form.phone}
                    onChange={(e) => set('phone', e.target.value)}
                    placeholder="9820012345"
                  />
                </Field>
                <Field id="email" label="Contact Email" error={errors.email}>
                  <input
                    id="email"
                    type="email"
                    className="ac-input"
                    aria-invalid={!!errors.email}
                    value={form.email}
                    onChange={(e) => set('email', e.target.value)}
                  />
                </Field>
              </div>

              {/* Verified Residential Address Card (Extracted from Aadhaar) */}
              <div
                style={{
                  marginTop: 20,
                  background: '#f8fafc',
                  border: '1px solid #cbd5e1',
                  borderRadius: 10,
                  padding: '16px 20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, marginBottom: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <MapPin size={18} className="text-slate-600" />
                    <b style={{ fontSize: 15, color: '#1e293b' }}>Verified Residential Address (from Masked Aadhaar)</b>
                  </div>
                  <span style={{ fontSize: 12, color: '#64748b' }}>
                    Personal Identity Address
                  </span>
                </div>
                <p className="ac-muted" style={{ margin: '0 0 12px 0', fontSize: 13 }}>
                  This personal residential address was extracted from your identity document. It is stored separately from your customer-facing store address.
                </p>
                <div className="ac-grid-2">
                  <div style={{ gridColumn: '1 / -1' }}>
                    <Field id="residentialAddress" label="Residential Street Address">
                      <input
                        id="residentialAddress"
                        className="ac-input"
                        value={form.residentialAddress}
                        onChange={(e) => set('residentialAddress', e.target.value)}
                        placeholder="Residential address from Aadhaar"
                      />
                    </Field>
                  </div>
                  <Field id="residentialPincode" label="Residential PIN Code" error={errors.residentialPincode}>
                    <div style={{ position: 'relative' }}>
                      <input
                        id="residentialPincode"
                        className="ac-input"
                        maxLength={6}
                        value={form.residentialPincode}
                        onChange={(e) => {
                          const val = e.target.value.replace(/\D/g, '').slice(0, 6);
                          set('residentialPincode', val);
                          if (val.length === 6) {
                            handleResidentialPincodeLookup(val, form.residentialAddress, false);
                          }
                        }}
                        placeholder="e.g. 400069"
                      />
                      {resPinLookupBusy && (
                        <div style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#2563eb' }}>
                          <RefreshCw size={13} className="animate-spin" />
                          <span>Looking up...</span>
                        </div>
                      )}
                    </div>
                    {resPinLookupError && (
                      <p style={{ color: '#ef4444', fontSize: 12, marginTop: 4 }}>{resPinLookupError}</p>
                    )}
                  </Field>
                  <Field id="residentialCity" label="Residential City" error={errors.residentialCity}>
                    <input
                      id="residentialCity"
                      className="ac-input"
                      value={form.residentialCity}
                      onChange={(e) => set('residentialCity', e.target.value)}
                      placeholder="e.g. Mumbai"
                    />
                    {resLocalities && resLocalities.length > 1 && (
                      <div style={{ marginTop: 6 }}>
                        <span style={{ fontSize: 11, color: '#64748b' }}>Suggested localities for this PIN:</span>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 3 }}>
                          {resLocalities.slice(0, 6).map((loc) => (
                            <button
                              key={loc}
                              type="button"
                              onClick={() => set('residentialCity', loc)}
                              style={{
                                fontSize: 11,
                                padding: '2px 8px',
                                borderRadius: 4,
                                border: '1px solid #cbd5e1',
                                background: form.residentialCity === loc ? '#e0f2fe' : '#ffffff',
                                color: form.residentialCity === loc ? '#0369a1' : '#334155',
                                cursor: 'pointer',
                              }}
                            >
                              {loc}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </Field>
                  <Field id="residentialState" label="Residential State">
                    <input
                      id="residentialState"
                      className="ac-input"
                      value={form.residentialState}
                      onChange={(e) => set('residentialState', e.target.value)}
                      placeholder="e.g. Maharashtra"
                    />
                  </Field>
                </div>
              </div>

              <div style={{ marginTop: 24, display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="ac-btn ac-btn-blue"
                  disabled={!!busy}
                  onClick={goToStep1}
                  style={{ padding: '12px 24px', fontSize: 15 }}
                >
                  {busy === 'save' ? 'Saving details…' : 'Continue to Store Location →'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            STEP 1: STORE LOCATION, PIN CODE LOOKUP & HYPERLOCAL MAP
        ========================================================================= */}
        {stage === 1 && (
          <div className="space-y-6">
            <div className="ac-box">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 8 }}>
                <div>
                  <h2 style={{ margin: 0 }}>Step 2: Store Address & Hyperlocal Map</h2>
                  <p className="ac-muted" style={{ margin: '4px 0 0 0', fontSize: 14 }}>
                    Specify your customer-facing store location. Customers within delivery radius will discover your store.
                  </p>
                </div>
                <button
                  type="button"
                  className="ac-btn ac-btn-outline"
                  onClick={handleCopyResidentialAddress}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13 }}
                  title="Copy verified residential address into store address fields"
                >
                  <Copy size={15} /> Use residential address as store address
                </button>
              </div>

              <div className="ac-grid-2" style={{ marginTop: 16 }}>
                <div style={{ gridColumn: '1 / -1' }}>
                  <Field id="address" label="Store Street Address (Customer Facing)" error={errors.address}>
                    <input
                      id="address"
                      className="ac-input"
                      aria-invalid={!!errors.address}
                      value={form.address}
                      onChange={(e) => set('address', e.target.value)}
                      placeholder="Shop No. 4, Ground Floor, Linking Road"
                    />
                  </Field>
                </div>

                {/* Store PIN Code with Instant Lookup */}
                <Field
                  id="pincode"
                  label="Store PIN Code (6 Digits)"
                  error={errors.pincode || pinLookupError}
                  hint="Enter 6-digit Indian PIN code to locate postal area"
                >
                  <div style={{ display: 'flex', gap: 8 }}>
                    <input
                      id="pincode"
                      className="ac-input"
                      inputMode="numeric"
                      maxLength={6}
                      aria-invalid={!!errors.pincode || !!pinLookupError}
                      value={form.pincode}
                      onChange={(e) => {
                        const val = e.target.value.replace(/\D/g, '');
                        set('pincode', val);
                        if (val.length === 6) {
                          handlePincodeLookup(val);
                        }
                      }}
                      placeholder="e.g. 400069"
                    />
                    <button
                      type="button"
                      className="ac-btn ac-btn-outline"
                      disabled={pinLookupBusy || form.pincode.length !== 6}
                      onClick={() => handlePincodeLookup(form.pincode)}
                      style={{ padding: '0 14px', whiteSpace: 'nowrap' }}
                    >
                      {pinLookupBusy ? <RefreshCw className="animate-spin" size={16} /> : <Search size={16} />}
                      <span style={{ marginLeft: 6 }}>Lookup</span>
                    </button>
                  </div>
                </Field>

                <Field id="city" label="District / City">
                  <input
                    id="city"
                    className="ac-input"
                    value={form.city}
                    onChange={(e) => set('city', e.target.value)}
                  />
                </Field>

                <Field id="state" label="State">
                  <input
                    id="state"
                    className="ac-input"
                    value={form.state}
                    onChange={(e) => set('state', e.target.value)}
                  />
                </Field>

                {/* Postal Localities Dropdown if Multiple Found */}
                {pinLocalities.length > 0 && (
                  <div style={{ gridColumn: '1 / -1' }}>
                    <label style={{ fontSize: 13, fontWeight: 600, color: '#334155', display: 'block', marginBottom: 6 }}>
                      Postal Localities in {form.pincode} ({pinLocalities.length} found - select to append to store address):
                    </label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {pinLocalities.map((loc) => (
                        <button
                          key={loc}
                          type="button"
                          className="ac-btn ac-btn-soft ac-btn-small"
                          onClick={() => handleLocalityClick(loc)}
                          title={`Click to center map and pin store at ${loc}`}
                        >
                          📍 {loc}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Interactive Leaflet Map with AutoCART Store Marker */}
              <div style={{ marginTop: 24, paddingTop: 18, borderTop: '1px solid #e2e8f0' }}>
                <div className="ac-row-between" style={{ marginBottom: 10, flexWrap: 'wrap', gap: 8 }}>
                  <div>
                    <b>Store Entrance Pin on Map (Required for Hyperlocal Fulfillment)</b>
                    <p className="ac-muted" style={{ margin: '2px 0 0', fontSize: 13 }}>
                      Click on the map or drag the AutoCART store pin to position your shop entrance.
                    </p>
                  </div>
                  {pin.lat != null && pin.lng != null && (
                    <span style={{ fontSize: 12, background: '#eff6ff', color: '#1d4ed8', padding: '4px 8px', borderRadius: 6, fontWeight: 600 }}>
                      Coords: {pin.lat.toFixed(5)}, {pin.lng.toFixed(5)}
                    </span>
                  )}
                </div>

                <LocationPinMap
                  lat={pin.lat}
                  lng={pin.lng}
                  onChange={handlePinChange}
                  height={360}
                />

                {reverseGeocodeInfo && (
                  <div style={{ marginTop: 10, padding: '8px 12px', background: '#f8fafc', borderRadius: 6, border: '1px solid #e2e8f0', fontSize: 13 }}>
                    📍 <strong>Placed Area Confirmation:</strong> {reverseGeocodeInfo.area || reverseGeocodeInfo.neighborhood || reverseGeocodeInfo.city}
                    {reverseGeocodeInfo.pincode && <span> (PIN: {reverseGeocodeInfo.pincode})</span>}
                    {form.pincode && reverseGeocodeInfo.pincode && reverseGeocodeInfo.pincode !== form.pincode && (
                      <span style={{ color: '#d97706', marginLeft: 8 }}>
                        (Note: PIN on marker differs from {form.pincode})
                      </span>
                    )}
                  </div>
                )}

                {errors.location && (
                  <span className="ac-err ac-warn" role="alert" style={{ marginTop: 8, display: 'block' }}>
                    {errors.location}
                  </span>
                )}
              </div>

              <div className="ac-row-between" style={{ marginTop: 24 }}>
                <button
                  type="button"
                  className="ac-btn ac-btn-outline"
                  disabled={!!busy}
                  onClick={() => {
                    setStage(0);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                >
                  ← Back to Identity Details
                </button>
                <button
                  type="button"
                  className="ac-btn ac-btn-blue"
                  disabled={!!busy}
                  onClick={goToStep2}
                  style={{ padding: '12px 24px', fontSize: 15 }}
                >
                  {busy === 'save' ? 'Saving location…' : 'Continue to Products & Stock →'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            STEP 2: PRODUCTS, STOCK & INITIAL INVENTORY
        ========================================================================= */}
        {stage === 2 && (
          <div className="space-y-6">
            <div className="ac-box">
              <h2>Step 3: Product Listings & Initial Inventory</h2>
              <p className="ac-muted">
                Select your product categories and add at least one product with initial stock units. You can add more products anytime after your store is approved.
              </p>

              {/* Category selection */}
              <div className="ac-row" style={{ margin: '16px 0', flexWrap: 'wrap' }}>
                {categories.map((c) => {
                  const on = form.productCategories.includes(c.name);
                  return (
                    <button
                      type="button"
                      key={c.id}
                      className={`ac-act ${on ? 'ac-btn-blue' : ''}`}
                      style={on ? { background: 'var(--brand)', color: '#fff', borderColor: 'var(--brand)' } : {}}
                      aria-pressed={on}
                      onClick={() =>
                        set(
                          'productCategories',
                          on
                            ? form.productCategories.filter((x) => x !== c.name)
                            : [...form.productCategories, c.name]
                        )
                      }
                    >
                      {c.name}
                    </button>
                  );
                })}
              </div>

              {/* Product items */}
              {form.plannedProducts.map((p, i) => (
                <div className="ac-plan" key={i} style={{ marginBottom: 16 }}>
                  <div
                    className="ac-grid-2"
                    style={{
                      gridTemplateColumns: 'minmax(0,2fr) minmax(0,1.3fr) minmax(0,1fr) auto',
                      alignItems: 'end',
                    }}
                  >
                    <Field id={`pn${i}`} label="Product Name">
                      <input
                        id={`pn${i}`}
                        className="ac-input"
                        placeholder="e.g. Wireless Mouse"
                        value={p.name}
                        onChange={(e) => setProduct(i, 'name', e.target.value)}
                      />
                    </Field>
                    <Field id={`pc${i}`} label="Category">
                      <select
                        id={`pc${i}`}
                        className="ac-select"
                        value={p.category}
                        onChange={(e) => setProduct(i, 'category', e.target.value)}
                      >
                        <option value="">Choose category</option>
                        {categories.map((c) => (
                          <option key={c.id}>{c.name}</option>
                        ))}
                      </select>
                    </Field>
                    <Field id={`pp${i}`} label="Price (₹)">
                      <input
                        id={`pp${i}`}
                        className="ac-input"
                        inputMode="numeric"
                        value={p.approxPrice}
                        onChange={(e) => setProduct(i, 'approxPrice', e.target.value.replace(/\D/g, ''))}
                        placeholder="999"
                      />
                    </Field>
                    <button
                      type="button"
                      className="ac-btn ac-btn-outline ac-btn-small"
                      aria-label="Remove product"
                      disabled={form.plannedProducts.length === 1}
                      onClick={() => set('plannedProducts', form.plannedProducts.filter((_, n) => n !== i))}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                  <div className="ac-plan-row" style={{ marginTop: 10 }}>
                    <Field id={`ps${i}`} label="Initial Stock Units">
                      <input
                        id={`ps${i}`}
                        className="ac-input"
                        inputMode="numeric"
                        placeholder="e.g. 25"
                        value={p.stock ?? ''}
                        onChange={(e) => setProduct(i, 'stock', e.target.value.replace(/\D/g, ''))}
                      />
                    </Field>
                    <div>
                      <span className="ac-lbl">Product Photo (Optional)</span>
                      <label className="ac-photo-pick">
                        {p.image ? <img src={p.image} alt="" /> : <Upload size={18} />}
                        <span>{photoBusy === i ? 'Uploading…' : p.image ? 'Change photo' : 'Add photo'}</span>
                        <input
                          type="file"
                          accept="image/*"
                          className="ac-sr"
                          onChange={(e) => {
                            planPhoto(i, e.target.files?.[0]);
                            e.target.value = '';
                          }}
                        />
                      </label>
                    </div>
                  </div>
                </div>
              ))}
              {errors.plannedProducts && (
                <span className="ac-err ac-warn" role="alert">
                  {errors.plannedProducts}
                </span>
              )}

              <button
                type="button"
                className="ac-btn ac-btn-soft ac-btn-small"
                style={{ marginTop: 12 }}
                onClick={() =>
                  set('plannedProducts', [
                    ...form.plannedProducts,
                    { name: '', category: '', approxPrice: '', stock: '', image: '' },
                  ])
                }
              >
                <Plus size={16} /> Add another product
              </button>

              <div className="ac-row-between" style={{ marginTop: 24 }}>
                <button
                  type="button"
                  className="ac-btn ac-btn-outline"
                  disabled={!!busy}
                  onClick={() => {
                    setStage(1);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                >
                  ← Back to Store Location
                </button>
                <button
                  type="button"
                  className="ac-btn ac-btn-blue"
                  disabled={!!busy}
                  onClick={goToStep3}
                  style={{ padding: '12px 24px', fontSize: 15 }}
                >
                  {busy === 'save' ? 'Saving products…' : 'Continue to Review & Submit →'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            STEP 3: REVIEW, ADVISORY RISK SCORE & SUBMISSION
        ========================================================================= */}
        {stage === 3 && (
          <div className="space-y-6">
            <div className="ac-box" style={{ background: '#f8fafc', border: '1px solid #cbd5e1' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Bot size={22} className="text-indigo-600" />
                  <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#0f172a' }}>
                    Step 4: Prepared Application Summary (Agent D)
                  </h3>
                </div>
                {agentSummary?.riskScore != null && (
                  <div
                    style={{
                      padding: '4px 12px',
                      borderRadius: '16px',
                      fontWeight: 700,
                      fontSize: 13,
                      background: agentSummary.riskScore <= 35 ? '#dcfce7' : '#fef3c7',
                      color: agentSummary.riskScore <= 35 ? '#166534' : '#92400e',
                      border: '1px solid currentColor',
                    }}
                  >
                    Preliminary Risk: {agentSummary.riskScore}/100 ({agentSummary.riskCategory || 'Low'} Risk)
                  </div>
                )}
              </div>

              <p className="ac-muted" style={{ margin: '0 0 16px 0', fontSize: 13 }}>
                The Seller Onboarding Agent has pre-screened your uploaded documents, residential address, store coordinates, and product inventory for human administrator review.
              </p>

              <div className="ac-scroll-x" style={{ marginBottom: 16 }}>
                <table className="ac-table">
                  <tbody>
                    <tr>
                      <th style={{ width: 190 }}>Business & Owner</th>
                      <td>
                        {form.companyName || '(Unspecified)'} {form.storeName ? `(${form.storeName})` : ''} · {form.contactName || '(Name pending)'}
                      </td>
                    </tr>
                    <tr>
                      <th>Contact Details</th>
                      <td>{form.phone || '-'} · {form.email || '-'}</td>
                    </tr>
                    <tr>
                      <th>Residential Address</th>
                      <td>
                        {form.residentialAddress ? (
                          <span>{form.residentialAddress}, {form.residentialCity} {form.residentialPincode} (from Aadhaar)</span>
                        ) : (
                          <span className="ac-muted">Not extracted</span>
                        )}
                      </td>
                    </tr>
                    <tr>
                      <th>Store Address & Pin</th>
                      <td>
                        {form.address || '-'}, {form.city} {form.pincode}{' '}
                        {pin.lat != null && pin.lng != null ? `(${pin.lat.toFixed(4)}, ${pin.lng.toFixed(4)})` : '(Pin pending)'}
                      </td>
                    </tr>
                    <tr>
                      <th>Tax Identifiers</th>
                      <td>PAN: {form.pan || '(Pending)'} · GSTIN: {form.gstin || 'Not registered'}</td>
                    </tr>
                    <tr>
                      <th>Identity Documents</th>
                      <td>
                        {reqDocsDone >= reqDocs.length ? (
                          <span style={{ color: '#16a34a', fontWeight: 600 }}>
                            ✓ All required documents uploaded ({reqDocsDone}/{reqDocs.length})
                          </span>
                        ) : (
                          <span style={{ color: '#d97706', fontWeight: 600 }}>
                            ⚠️ Required documents missing ({reqDocsDone}/{reqDocs.length} uploaded)
                          </span>
                        )}
                      </td>
                    </tr>
                    <tr>
                      <th>Products Listed</th>
                      <td>
                        {form.plannedProducts.filter((p) => p.name.trim()).length} product(s) with initial stock units
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '12px 16px' }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#334155', marginBottom: 4 }}>
                  ⚖️ Human Administrator Authority Disclosure
                </div>
                <p style={{ margin: 0, fontSize: 13, color: '#64748b', lineHeight: 1.5 }}>
                  Submitting this application places it in the admin review queue. The AI risk assessment is advisory only. An authorized human administrator inspects all documents and makes the final approval decision.
                </p>
              </div>

              {/* Agreement checkbox */}
              <label className="ac-check" id="agree-box" style={{ marginTop: 20 }}>
                <input
                  type="checkbox"
                  checked={agree}
                  onChange={(e) => {
                    setAgree(e.target.checked);
                    if (e.target.checked) setSubmitNote('');
                  }}
                />
                <span>
                  I confirm that all provided details and uploaded documents are accurate. I understand that my documents are read automatically and reviewed by an authorized AutoCart administrator. Only the last 4 digits of Aadhaar are retained.
                </span>
              </label>

              {submitNote && <div className="ac-warn" role="alert" style={{ marginTop: 12 }}>{submitNote}</div>}

              <div className="ac-row-between" style={{ marginTop: 24 }}>
                <button
                  type="button"
                  className="ac-btn ac-btn-outline"
                  disabled={!!busy}
                  onClick={() => {
                    setStage(2);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                >
                  ← Back to Products & Stock
                </button>
                <button
                  type="button"
                  className="ac-btn ac-btn-blue"
                  disabled={!!busy || !app}
                  onClick={submit}
                  style={{ padding: '12px 24px', fontSize: 15 }}
                >
                  {busy === 'submit' ? 'Submitting for admin review…' : <><Check size={18} /> Submit application</>}
                </button>
              </div>
            </div>
          </div>
        )}
        {/* Document Preview Modal */}
        {docPreview && (
          <div
            className="fixed inset-0 z-[90] bg-black/70 flex items-center justify-center p-4"
            onClick={() => setDocPreview(null)}
            role="dialog"
            aria-modal="true"
          >
            <div
              className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 border-b flex justify-between items-center bg-gray-50">
                <div className="font-bold text-gray-800 text-sm truncate flex items-center gap-2">
                  <FileText size={16} className="text-blue-600" /> {docPreview.fileName}
                </div>
                <div className="flex items-center gap-2">
                  <a
                    href={docPreview.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs px-2.5 py-1 rounded bg-blue-50 text-blue-700 font-semibold hover:bg-blue-100"
                  >
                    Open in new tab ↗
                  </a>
                  <button
                    onClick={() => setDocPreview(null)}
                    className="p-1 rounded-lg hover:bg-gray-200 text-gray-600"
                    aria-label="Close"
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>
              <div className="p-4 flex-1 overflow-auto bg-slate-900 flex items-center justify-center min-h-[300px]">
                {docPreview.mimeType?.includes('pdf') || docPreview.fileName?.toLowerCase().endsWith('.pdf') ? (
                  <iframe
                    title={docPreview.fileName}
                    src={docPreview.url}
                    className="w-full h-[65vh] rounded-lg border-0 bg-white"
                  />
                ) : (
                  <img
                    src={docPreview.url}
                    alt={docPreview.fileName}
                    className="max-w-full max-h-[65vh] object-contain rounded-lg"
                  />
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
