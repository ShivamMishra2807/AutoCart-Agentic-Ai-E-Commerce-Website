from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, name, password, **extra_fields)

def generate_user_id():
    return f"user-{uuid.uuid4().hex[:8]}"

class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=64, primary_key=True, default=generate_user_id)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True, default='')
    role = models.CharField(max_length=20, default='CUSTOMER') # CUSTOMER, ADMIN, SELLER
    status = models.CharField(max_length=20, default='Active')
    joinedDate = models.DateField(auto_now_add=True)
    ordersCount = models.IntegerField(default=0)
    totalSpent = models.FloatField(default=0.0)
    addresses = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"


class Category(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    icon = models.CharField(max_length=50, blank=True, default='')
    image = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    productCount = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Active')
    createdAt = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.CharField(max_length=100)
    categoryId = models.CharField(max_length=64, blank=True, default='')
    brand = models.CharField(max_length=100, blank=True, default='')
    price = models.FloatField(default=0.0)
    originalPrice = models.FloatField(default=0.0)
    discount = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    reviewCount = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    stockStatus = models.CharField(max_length=30, default='In Stock')
    featured = models.BooleanField(default=False)
    bestSeller = models.BooleanField(default=False)
    newArrival = models.BooleanField(default=False)
    images = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True, default='')
    specifications = models.JSONField(default=dict, blank=True)
    seller = models.CharField(max_length=150, blank=True, default='')
    createdAt = models.CharField(max_length=50, blank=True, default='')
    # Seller-set stock rule: when the shelf count falls to reorderLevel, add restockQty (the seller's usual supplier top-up).
    costPrice = models.FloatField(default=0.0)  # what the seller pays per unit; 0 means not entered
    autoRestock = models.BooleanField(default=False)
    reorderLevel = models.IntegerField(default=5)
    restockQty = models.IntegerField(default=20)

    def __str__(self):
        return self.name


class StockLog(models.Model):
    """Every change to a product's stock and why (sale, manual edit, auto-restock rule), so a seller can always see what happened."""
    productId = models.CharField(max_length=64, db_index=True)
    change = models.IntegerField()
    stockAfter = models.IntegerField()
    reason = models.CharField(max_length=40)  # sale | manual | auto-restock | cancelled-order
    by = models.CharField(max_length=150, blank=True, default='')
    createdAt = models.DateTimeField(auto_now_add=True)


class Coupon(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    discountType = models.CharField(max_length=30, default='Percentage') # Percentage, Fixed Amount
    discountValue = models.FloatField(default=0.0)
    minOrderAmount = models.FloatField(default=0.0)
    maxDiscount = models.FloatField(default=0.0)
    startDate = models.CharField(max_length=30, blank=True, default='')
    expiryDate = models.CharField(max_length=30, blank=True, default='')
    usageLimit = models.IntegerField(default=1000)
    usedCount = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Active')
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.code


class Seller(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=150)
    companyName = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    productsCount = models.IntegerField(default=0)
    ordersCount = models.IntegerField(default=0)
    totalRevenue = models.FloatField(default=0.0)
    rating = models.FloatField(default=0.0)
    status = models.CharField(max_length=30, default='Approved')
    joinedDate = models.CharField(max_length=30, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    customerName = models.CharField(max_length=150)
    customerEmail = models.EmailField()
    customerPhone = models.CharField(max_length=30, blank=True, default='')
    date = models.CharField(max_length=30, blank=True, default='')
    totalAmount = models.FloatField(default=0.0)
    subtotal = models.FloatField(default=0.0)
    tax = models.FloatField(default=0.0)
    shippingFee = models.FloatField(default=0.0)
    discountAmount = models.FloatField(default=0.0)
    paymentMethod = models.CharField(max_length=50, default='Cash on Delivery')
    paymentStatus = models.CharField(max_length=30, default='Pending')
    status = models.CharField(max_length=40, default='Confirmed')
    shippingAddress = models.JSONField(default=dict, blank=True)
    items = models.JSONField(default=list, blank=True)
    timeline = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.id} - {self.customerName}"


# ==================== LOCATION & STORE MODELS ====================

class Store(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=200)
    seller = models.CharField(max_length=150, blank=True, default='')
    sellerId = models.CharField(max_length=64, blank=True, default='')
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, default='')
    pincode = models.CharField(max_length=20)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    phone = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    operatingStatus = models.CharField(max_length=30, default='Open') # Open, Closed, Busy
    serviceCoverageRadiusKm = models.FloatField(default=15.0)
    fulfillmentCapability = models.CharField(max_length=50, default='Pickup and Delivery') # Pickup and Delivery, Delivery Only, Pickup Only
    openingHours = models.CharField(max_length=100, default='9:00 AM - 9:00 PM')
    rating = models.FloatField(default=4.5)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.city})"


class StoreInventory(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventories')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_inventories')
    availableQuantity = models.IntegerField(default=0)
    reservedQuantity = models.IntegerField(default=0)
    storePrice = models.FloatField(default=0.0)
    isAvailable = models.BooleanField(default=True)
    lastRestocked = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'product')

    def __str__(self):
        return f"{self.store.name} - {self.product.name} (Qty: {self.availableQuantity})"


class InventoryReservation(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='reservations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reservations')
    quantity = models.IntegerField(default=1)
    reservationToken = models.CharField(max_length=100, unique=True)
    userEmail = models.EmailField()
    status = models.CharField(max_length=30, default='Active') # Active, Confirmed, Released, Expired
    expiresAt = models.DateTimeField()
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Res {self.reservationToken[:8]} - {self.product.name} (Store: {self.store.id})"


# ==================== SELLER ONBOARDING & AUDIT ====================

class SellerApplication(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('DOCUMENT_PROCESSING', 'Document Processing (OCR)'),
        ('NEEDS_MORE_INFORMATION', 'Needs More Information'),
        ('NEEDS_MANUAL_REVIEW', 'Needs Manual Review'),
        ('PENDING_ADMIN_APPROVAL', 'Pending Admin Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    ]

    id = models.CharField(max_length=64, primary_key=True)
    sellerId = models.CharField(max_length=64, blank=True, default='')
    ownerUserId = models.CharField(max_length=64, blank=True, default='')  # the logged-in user who applied
    applicantName = models.CharField(max_length=150)
    companyName = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True, default='')
    pincode = models.CharField(max_length=20, blank=True, default='')
    addressState = models.CharField(max_length=100, blank=True, default='')
    residentialAddress = models.TextField(blank=True, default='')
    residentialPincode = models.CharField(max_length=20, blank=True, default='')
    residentialCity = models.CharField(max_length=100, blank=True, default='')
    residentialState = models.CharField(max_length=100, blank=True, default='')
    storeName = models.CharField(max_length=200, blank=True, default='')
    storeLatitude = models.FloatField(null=True, blank=True)
    storeLongitude = models.FloatField(null=True, blank=True)
    plannedProducts = models.JSONField(default=list, blank=True) # [{ name, category, approxPrice }]
    identityDetails = models.JSONField(default=dict, blank=True) # masked fields read from Aadhaar / PAN
    aadhaarLast4 = models.CharField(max_length=4, blank=True, default='') # never store the full Aadhaar number
    businessType = models.CharField(max_length=50, default='Retailer')
    productCategories = models.JSONField(default=list, blank=True)
    gstin = models.CharField(max_length=30, blank=True, default='')
    pan = models.CharField(max_length=20, blank=True, default='')
    yearsInBusiness = models.CharField(max_length=20, blank=True, default='0')
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='SUBMITTED')
    upiId = models.CharField(max_length=80, blank=True, default='')  # where customers' UPI payments go (set by the seller)
    riskScore = models.IntegerField(default=0)
    riskCategory = models.CharField(max_length=30, default='Low') # Low, Medium, High
    documentUploads = models.JSONField(default=dict, blank=True) # { docType: { url, fileName, uploadedAt, mimeType } }
    ocrExtractedData = models.JSONField(default=dict, blank=True) # { gstin, pan, name, confidence, fields }
    verificationResults = models.JSONField(default=dict, blank=True) # { gstinVerified, nameMatched, warnings }
    missingFields = models.JSONField(default=list, blank=True)
    aiAssessment = models.TextField(blank=True, default='')
    adminNotes = models.TextField(blank=True, default='')
    rejectionReason = models.TextField(blank=True, default='')
    reviewedBy = models.CharField(max_length=150, blank=True, default='')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.companyName} [{self.status}]"


def seller_document_upload_path(instance, filename):
    # Kept under private/ and only streamed through an owner/admin-checked view
    return f"private/seller_docs/{instance.application_id}/{instance.id}_{filename}"


class SellerDocument(models.Model):
    DOC_TYPES = [
        ('AADHAAR', 'Aadhaar (masked)'),
        ('PAN', 'PAN Card'),
        ('GST_CERTIFICATE', 'GST Certificate'),
        ('ADDRESS_PROOF', 'Store Address Proof'),
        ('BANK_PROOF', 'Bank Proof (cancelled cheque / passbook)'),
        ('STORE_PHOTO', 'Store Photo'),
    ]
    OCR_STATUSES = [
        ('PENDING', 'Pending'),
        ('DONE', 'Done'),
        ('UNREADABLE', 'Unreadable'),
        ('OCR_UNAVAILABLE', 'OCR Unavailable'),
        ('NOT_REQUIRED', 'Not Required'),
    ]

    id = models.CharField(max_length=64, primary_key=True)
    application = models.ForeignKey(SellerApplication, on_delete=models.CASCADE, related_name='documents')
    docType = models.CharField(max_length=30, choices=DOC_TYPES)
    file = models.FileField(upload_to=seller_document_upload_path)
    fileName = models.CharField(max_length=255)
    mimeType = models.CharField(max_length=100, blank=True, default='')
    sizeBytes = models.IntegerField(default=0)
    ocrStatus = models.CharField(max_length=30, choices=OCR_STATUSES, default='PENDING')
    extractedFields = models.JSONField(default=dict, blank=True) # masked values only
    redactedText = models.TextField(blank=True, default='')
    confidence = models.FloatField(default=0.0)
    warnings = models.JSONField(default=list, blank=True)
    uploadedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application_id} - {self.docType} ({self.ocrStatus})"


class SellerApplicationAudit(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    application = models.ForeignKey(SellerApplication, on_delete=models.CASCADE, related_name='audit_logs')
    fromStatus = models.CharField(max_length=40)
    toStatus = models.CharField(max_length=40)
    action = models.CharField(max_length=100)
    performedBy = models.CharField(max_length=150)
    reason = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.id}: {self.fromStatus} -> {self.toStatus} by {self.performedBy}"


# ==================== FULFILLMENT & AGENT TASK TRACKING ====================

class OrderFulfillment(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='fulfillment')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, related_name='fulfillments')
    fulfillmentType = models.CharField(max_length=50, default='Store Delivery') # Store Delivery, Store Pickup, Standard Logistics
    deliveryPartner = models.CharField(max_length=100, default='AutoCart Hyperlocal Express (Dev)')
    trackingNumber = models.CharField(max_length=100, blank=True, default='')
    currentStatus = models.CharField(max_length=50, default='Order Allocated') # Order Allocated, Preparing at Store, Out for Delivery, Delivered
    distanceKm = models.FloatField(default=0.0)
    estimatedDeliveryMinutes = models.IntegerField(default=35)
    deliveryAddress = models.JSONField(default=dict, blank=True)
    timeline = models.JSONField(default=list, blank=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fulfillment for Order {self.order.id} ({self.currentStatus})"


class AgentTask(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    taskType = models.CharField(max_length=50) # AUTONOMOUS_SHOPPING, SELLER_ONBOARDING, STORE_FULFILLMENT, SELLER_ASSISTANT, ADMIN_AUDIT
    sessionId = models.CharField(max_length=100, blank=True, default='')
    userEmail = models.EmailField(blank=True, default='')
    goal = models.TextField()
    status = models.CharField(max_length=40, default='IN_PROGRESS') # IN_PROGRESS, WAITING_USER_CONFIRMATION, COMPLETED, FAILED
    plan = models.JSONField(default=list, blank=True)
    currentStep = models.IntegerField(default=0)
    resultData = models.JSONField(default=dict, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task {self.id} [{self.taskType}] - {self.status}"


class AgentExecutionLog(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    task = models.ForeignKey(AgentTask, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    agentName = models.CharField(max_length=100)
    toolName = models.CharField(max_length=100)
    inputs = models.JSONField(default=dict, blank=True)
    outputs = models.JSONField(default=dict, blank=True)
    executionTimeMs = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='SUCCESS')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agentName} -> {self.toolName} ({self.status})"



# ==================== CUSTOMER SUPPORT ====================

class ChatSession(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    userEmail = models.EmailField(blank=True, default='')
    anonKey = models.CharField(max_length=100, blank=True, default='')
    language = models.CharField(max_length=20, blank=True, default='')
    rating = models.IntegerField(null=True, blank=True)  # 1-5 satisfaction after the chat
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat {self.id} ({self.userEmail or 'guest'})"


class ChatMessage(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)  # user | assistant | system
    content = models.TextField()
    agent = models.CharField(max_length=60, blank=True, default='')
    cards = models.JSONField(default=list, blank=True)  # product / order cards shown in the chat
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['createdAt']


class SupportTicket(models.Model):
    STATUS = [('OPEN', 'Open'), ('IN_PROGRESS', 'In progress'), ('WAITING_CUSTOMER', 'Waiting for customer'),
              ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed')]
    PRIORITY = [('LOW', 'Low'), ('NORMAL', 'Normal'), ('HIGH', 'High'), ('URGENT', 'Urgent')]

    id = models.CharField(max_length=64, primary_key=True)
    session = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    customerEmail = models.EmailField()
    customerName = models.CharField(max_length=150, blank=True, default='')
    subject = models.CharField(max_length=200)
    category = models.CharField(max_length=40, default='GENERAL')  # ORDER, RETURN, PRODUCT, PAYMENT, SELLER, GENERAL
    orderId = models.CharField(max_length=64, blank=True, default='')
    status = models.CharField(max_length=30, choices=STATUS, default='OPEN')
    priority = models.CharField(max_length=20, choices=PRIORITY, default='NORMAL')
    assignedTo = models.CharField(max_length=150, blank=True, default='')
    collectedDetails = models.JSONField(default=dict, blank=True)  # what the customer agreed to share
    dueAt = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} [{self.status}] {self.subject}"


class TicketMessage(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    author = models.CharField(max_length=20)  # customer | support | assistant
    authorName = models.CharField(max_length=150, blank=True, default='')
    body = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['createdAt']


# ==================== CUSTOMER ENQUIRIES ====================

class Enquiry(models.Model):
    """A question from a visitor or customer: about one product, or a general question for the store."""
    STATUS = [('OPEN', 'Open'), ('ANSWERED', 'Answered'), ('CLOSED', 'Closed')]

    id = models.CharField(max_length=64, primary_key=True)
    productId = models.CharField(max_length=64, blank=True, default='')
    productName = models.CharField(max_length=255, blank=True, default='')
    sellerName = models.CharField(max_length=200, blank=True, default='')  # who sells the product, so the right seller sees it
    customerName = models.CharField(max_length=150)
    customerEmail = models.EmailField()
    customerPhone = models.CharField(max_length=30, blank=True, default='')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='OPEN')
    answer = models.TextField(blank=True, default='')
    answeredBy = models.CharField(max_length=150, blank=True, default='')
    answeredAt = models.DateTimeField(null=True, blank=True)
    isPublic = models.BooleanField(default=False)  # a public answer shows on the product page (first name only)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-createdAt']

    def __str__(self):
        return f"{self.id} [{self.status}] {self.productName or 'general'}"


# ==================== PAYMENTS ====================

class Payment(models.Model):
    """One payment attempt for an order. The amount always comes from the stored order, never from the browser."""
    id = models.CharField(max_length=64, primary_key=True)
    orderId = models.CharField(max_length=64, db_index=True)
    provider = models.CharField(max_length=30)  # razorpay | razorpay-demo
    providerOrderId = models.CharField(max_length=100, db_index=True)
    providerPaymentId = models.CharField(max_length=100, blank=True, default='')
    amount = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, default='CREATED')  # CREATED, PAID, FAILED
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} {self.orderId} {self.status}"


# ==================== REVIEWS ====================

class Review(models.Model):
    """One customer's review of one product. `verified` means they really bought it."""
    productId = models.CharField(max_length=64, db_index=True)
    userEmail = models.EmailField()
    userName = models.CharField(max_length=150)
    rating = models.IntegerField()  # 1 to 5
    title = models.CharField(max_length=120, blank=True, default='')
    body = models.TextField()
    verified = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-createdAt']
        unique_together = ('productId', 'userEmail')

    def __str__(self):
        return f"{self.productId} {self.rating} stars by {self.userEmail}"


class UserMemory(models.Model):
    """What the shopping assistant (Saathi) remembers about a signed-in customer so it can help faster.
    The customer can read it and delete it at any time."""
    userEmail = models.EmailField(unique=True)
    interests = models.JSONField(default=list, blank=True)       # product categories they asked about
    budgetMax = models.IntegerField(null=True, blank=True)       # the last budget they mentioned, in rupees
    recentSearches = models.JSONField(default=list, blank=True)  # last few things they searched for
    chatCount = models.IntegerField(default=0)
    updatedAt = models.DateTimeField(auto_now=True)
