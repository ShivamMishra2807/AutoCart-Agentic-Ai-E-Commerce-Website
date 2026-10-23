# AutoCart

A marketplace for **local stores in Mumbai**, with three separate experiences (customer, seller, admin) and AI assistants that answer only from the real database.

- **Customers** find what is in stock in nearby stores, buy for delivery or pickup, track orders on a map, and get help from **Saathi**, the shopping assistant, which can also place an order from the chat.
- **Sellers** create an account, apply with their documents, list products with photos, manage stock by hand or automatically, see sales, earnings and profit, and ask **Munim**, the seller assistant, about their own shop.
- **Admins** review seller applications with every document and check, approve or reject, and see a daily briefing of what needs attention.

Everything runs on free tools. **There is no payment gateway**: customers pay on delivery, at the store, or straight to the seller by UPI (the seller confirms the money arrived).

---

## Production Deployment Guide

AutoCart is production-configured for:
- **Backend:** [Render](https://render.com) (Python Web Service + Managed PostgreSQL)
- **Frontend:** [Vercel](https://vercel.com) (Vite SPA with rewrites)

### 1. Backend on Render

#### Option A: One-Click Render Blueprint
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Blueprint**.
2. Connect your GitHub repository (`AutoCart-Agentic-Ai-E-Commerce-Website`).
3. Render reads `render.yaml` and provisions:
   - A free managed **PostgreSQL** database (`autocart-db`).
   - A **Web Service** (`autocart-backend`) running Gunicorn and WhiteNoise.
4. Set optional secret environment variables in the Render Dashboard:
   - `GEMINI_API_KEY`: Your Gemini API key from Google AI Studio.
   - `GROQ_API_KEY`: Optional Groq API key for Llama 3.3.
5. Deploy. Render runs `build.sh` (collects static files, runs migrations).
6. Note your backend URL (e.g., `https://autocart-backend.onrender.com`). Verify health at `/health/`.

#### Option B: Manual Render Service Setup
1. Create a **PostgreSQL Database** on Render: Name: `autocart-db`. Copy its **Internal Database URL**.
2. Create a **Web Service**:
   - **Repository:** AutoCart GitHub repository
   - **Environment:** `Python`
   - **Build Command:** `./build.sh` (or `pip install -r backend/requirements.txt && python backend/manage.py collectstatic --no-input && python backend/manage.py migrate`)
   - **Start Command:** `gunicorn --chdir backend autocart_core.wsgi:application --bind 0.0.0.0:$PORT`
   - **Health Check Path:** `/health/`
3. Add Environment Variables:
   - `DEBUG`: `False`
   - `SECRET_KEY`: (Generate secure key or let Render generate)
   - `DATABASE_URL`: (Paste your Render PostgreSQL connection string)
   - `ALLOWED_HOSTS`: `localhost,127.0.0.1,.onrender.com,.vercel.app`
   - `CORS_ALLOWED_ORIGINS`: `https://<your-vercel-site>.vercel.app`
   - `CSRF_TRUSTED_ORIGINS`: `https://<your-vercel-site>.vercel.app,https://<your-render-backend>.onrender.com`
   - `GEMINI_API_KEY`: (optional)
   - `AUTOCART_DISABLE_EMBEDDINGS`: `0` (or `1` if running on very low memory plan)

#### Seeding Initial Production Data
In the Render Web Service shell (or via local connection to the Postgres database):
```bash
python backend/seed_db.py
python backend/seed_mumbai_network.py
python backend/seed_300_products.py
python backend/seed_demo_seller.py
```
*(All seed scripts use `update_or_create` and are idempotent - safe to rerun without creating duplicates).*

---

### 2. Frontend on Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New...** -> **Project**.
2. Import your GitHub repository (`AutoCart-Agentic-Ai-E-Commerce-Website`).
3. Project Settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** `./` (Repository root)
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add Environment Variable:
   - **`VITE_API_BASE_URL`**: `https://<your-backend-name>.onrender.com/api`
     *(Ensure there is NO trailing slash after `/api`)*
5. Click **Deploy**. Vercel will build the frontend and serve it with the included `vercel.json` SPA rewrite rules.

---

## Local Development (Windows, macOS or Linux)

You need **Python 3.12+** and **Node 20+**.

### 1. Environment file

Copy `.env.example` to `.env` in the project root. Everything is optional:

| Variable | What it does |
|---|---|
| `GEMINI_API_KEY` | Free key from Google AI Studio. Without it the assistants still work, using database-only answers. |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Gmail app password. Without them, emails are printed in the server console. |

Never commit `.env`. It is in `.gitignore`.

### 2. Backend (Django, port 8000)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt     # includes gunicorn, whitenoise, dj-database-url, langgraph and fastembed
python manage.py migrate
python seed_db.py
python seed_more_products.py
python seed_stores_and_inventory.py
python seed_mumbai_network.py
python seed_demo_seller.py
python manage.py runserver 127.0.0.1:8000
```

Restart the server after pulling backend changes (new routes are only loaded at start).

### 3. Frontend (React + Vite, port 5173)

```bash
npm install
npm run dev
```

Open http://localhost:5173.

### Demo accounts (local testing only)

| Role | Sign in at | Email | Password |
|---|---|---|---|
| Admin | `/admin/login` | admin@auracart.com | admin123 |
| Seller | `/seller/login` | seller@example.com | seller123 |
| Customer | `/login` | create one on `/register` | any (6+ characters) |

Change these before putting the site anywhere public. To try **Pay now with UPI**, the seller must first add a UPI ID in the Seller centre ("Get paid by UPI").

### Tests

```bash
cd backend
python manage.py test        # 285 tests; the AI model is switched off so tests never use the network
npm run build                # frontend production build
```

---

## What is built

**Customer**
- Home, a compact shop (five products per row, price and Add to cart visible without scrolling), filter pills and sorting, product pages with photos, reviews, instant "Quick answers", a comparison table, **Buy now** and a sticky buy bar.
- **Only customer accounts can buy.** A visitor who presses Buy now goes straight to the customer sign-in, and the item is added to their cart after they sign in. Sellers and admins are told buying is for customers (and the server refuses their orders).
- Checkout: the server works out price, coupon, delivery fee and stock. The address can be filled from your **current location** (street, area, city and PIN, looked up with free OpenStreetMap). Incomplete forms say what is missing and jump to the first empty field.
- Payment methods: **Cash on delivery**, **UPI or card on delivery**, **Pay at the store**, and **Pay now with UPI** (scan a QR that pays the seller directly, then enter the 12-digit UPI reference; the seller confirms). UPI is offered only when the whole cart is from one seller who has added a UPI ID, and checkout says why when it is not available.
- Orders, cancel, return, wishlist, profile, support tickets and a contact form. The order page shows the steps and a **road-route map** from the seller's store to you, with distance and drive time.
- **Saathi** chat, built as a **LangGraph agent** (classify, retrieve, answer, buy):
  - Retrieval (RAG) uses a free local Hugging Face embedding model (BAAI/bge-small-en-v1.5, via fastembed) over products and a small policy FAQ.
  - Gemini (free tier) words the reply using only what was retrieved. If Gemini or the model is unavailable it falls back to templates and keyword search.
  - Every product card has **Buy now**. Say "buy the first one" and a confirm step appears in the chat; a customer with a past address confirms in one tap (cash on delivery), others go to checkout.
  - Greets you by first name, answers "where is my order" with the store, distance and status, and hands over to a person. It remembers only categories, a usual budget and your last few searches, which you can see and delete in the chat.

**Seller**
- **Create a seller account** on the seller sign-in page. This opens a draft application straight away, so the admin can see the sign-up.
- Application wizard in a seller-only frame (no shop header): business details, store location pin, **products with stock and a photo**, documents (masked Aadhaar, PAN, GST, address and bank proof) and review. The list of required documents is shown on every step. **You can submit without all documents**; the application is saved and marked incomplete until they are added.
- Documents are read locally (free OCR). The system shows what it read, compares it with the form and computes a risk score.
- On approval, the products from the application go live with their stock and photo.
- Seller centre: sales charts, earnings after commission, and **profit** once you enter a cost price per product. Add products with photos, edit price, **stock by hand (+1, +10) or with an auto-restock rule** (after a sale, if stock is at or below N, add M), and a stock history showing sales, manual edits and auto-restocks.
- **Orders to pack**: confirm a UPI payment, one click **Confirm & pack**, then a route map to the customer.
- **Get paid by UPI**: the seller's own UPI ID. AutoCart never touches the money.
- **Munim**, the seller assistant, answers from the seller's own data: low stock, best sellers, revenue, orders, ratings, waiting questions, and **profit**. Gemini words the answer; the numbers always come from the database.

**Admin**
- Separate login with a profile menu (Seller applications, Settings, View the store, Sign out). Needs-attention cards and a plain-language daily briefing.
- **Seller applications** with tabs including **Still filling in** (sign-ups that have not submitted). Each application shows a risk badge ("Incomplete" while documents are missing), a "before you approve" checklist, Aadhaar and PAN cards, documents you can open, the store on a map, and a decision bar. **Approve stays locked until Aadhaar, PAN and a store location exist** (enforced on the server too).
- **Sellers**: click a seller for contact details, live numbers worked out from real orders, their products and their application.
- **Payments**: how customers pay, and UPI payments waiting for confirmation.
- Support inbox and enquiries with suggested answers.

**Business model** (`backend/api/commission.py`, public at `/api/commission`): free to join and list, no monthly fee, commission only on a sale (Electronics 5%, Fashion 10%, Home & Kitchen 8%, Beauty 8%, Sports 7%, Books 4%, Grocery 3%, Toys 7%, other 6%). **These are proposed launch rates, not a signed price list and not any company's actual rates.**

**Privacy and safety rules**
- A customer never sees admin or seller screens or data. A seller never sees admin data and sees only their own products and orders.
- Uploaded documents are private files, only visible to the owner and admins. Product photos are checked, resized and served publicly.
- "Paid" for UPI only ever means a seller or admin confirmed the money arrived. The same UPI reference cannot be used on two orders.
- Assistants answer from database rows only. They are told not to invent prices, stock or reviews.

---

## What is not built, and why

| Not built | Reason |
|---|---|
| **Looking up a person's details by typing an Aadhaar number** | This will not be built. Aadhaar data is private. There is no free, legal public service for it, and the Aadhaar Act does not allow a private business to look people up or to store full Aadhaar numbers. Instead, a seller uploads their **own masked Aadhaar**. The system reads the name, date of birth and address, stores **only the last 4 digits**, and rejects an upload that shows all 12 digits. |
| A payment gateway (cards and net banking online) | Removed on purpose. It needs a business account and keys. UPI scan-and-pay to the seller and pay-on-delivery are used instead. Scanning the QR with a real UPI app was **not tested**. |
| Recognising a returning seller from their documents | Planned. It must only ever show a seller their own record after they sign in. |
| Live GPS tracking of a delivery rider | The map shows the road route and distance from store to customer, not a moving rider. The route comes from the free public OSRM service and can be unavailable (a straight line is drawn then). |
| Seller order updates beyond "Packed" (shipped, delivered) | Planned. |
| Personalised "picked for you", fraud detection, photo reviews | Planned. |
| Legal pages (terms, privacy, refund policy) | Missing. |
| Real Gmail sending | Built, but needs your own app password in `.env`. Not tested with real credentials. |

**Known data quality issue:** some sample products have an unrelated photo (for example a phone shown for a mouse). The shop shows a branded tile instead of a photo it can tell is reused, but a few wrong photos remain. Sellers can replace any photo of their own products.

**AI behaviour to expect:** Gemini is a free service and sometimes answers "503 high demand". When that happens the assistants fall back to database-only answers (still correct, just less conversational) and try Gemini again after a few minutes. Gemini wording was not confirmed during testing for this reason.

---

## Project layout

```
backend/            Django REST API (api/ holds views, models, agents, tests)
src/storefront/     Customer site (Sunset theme, scoped under .ac)
src/pages/seller/   Seller application wizard and Seller centre
src/pages/admin/    Admin console
PROJECT_REQUIREMENTS.md, README_FREE_STACK.md, PROMPTS.md, COMPLETE_PLAN.md
                    Planning documents. The sections titled "updated" reflect what is built today; older sections describe the original plan.
```
