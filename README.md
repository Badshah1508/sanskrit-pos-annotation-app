# Sanskrit POS Annotation and Expert Verification Web Application

A full-stack, responsive, and secure web application designed for M.Tech dissertation research on **Cross-Domain Sanskrit POS Tagging (News Domain)**.

This application allows Sanskrit language scholars and domain experts to review, edit, and verify Part-of-Speech (POS) tags assigned to Sanskrit news sentences originally pre-annotated by the Stanza Sanskrit POS model.

---

## 📑 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Tag Inventory (Sanskrit Consortium)](#tag-inventory-sanskrit-consortium)
4. [Dataset Separation Rule (70/30 Split)](#dataset-separation-rule-7030-split)
5. [Local Quickstart](#local-quickstart)
6. [Database Management & PostgreSQL Migration](#database-management--postgresql-migration)
7. [Verification and Testing Checklist](#verification-and-testing-checklist)
8. [Production Deployment Guide (Free/Low-Cost Public HTTPS)](#production-deployment-guide)
9. [Dataset Export Guide](#dataset-export-guide)

---

## 1. Architecture Overview

- **Frontend:** React 18 + Vite, responsive layout (Desktop Table & Mobile Touch Cards), Noto Sans Devanagari typography, Axios client.
- **Backend:** Python 3.12 + FastAPI, Pydantic v2 data validation, modern Bcrypt password hashing, JWT authentication.
- **Database:** SQLAlchemy 2.0 ORM with Alembic migrations. Uses SQLite for zero-configuration local development and seamlessly switches to PostgreSQL for production.
- **Security:** Role-based access control (`admin`, `expert`), atomic transactions, input validation.

---

## 2. Project Structure

```text
sanskrit_pos_annotation_app/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js                     # API client with token management & mock fallback
│       ├── config/
│       │   └── tags.js                # Central Sanskrit Consortium tag inventory
│       ├── components/
│       │   ├── LoginForm.jsx          # Login interface
│       │   ├── Dashboard.jsx          # Corpus statistics & progress bar
│       │   ├── AnnotationPage.jsx     # Main annotation screen
│       │   ├── TokenRow.jsx           # Desktop table row for tokens
│       │   ├── TokenCard.jsx          # Mobile/tablet card layout for tokens
│       │   ├── TagDropdown.jsx        # Tag selector
│       │   ├── ProgressBar.jsx        # Visual progress tracker
│       │   ├── ConfirmDialog.jsx      # Guard for unsaved changes
│       │   └── ExportPanel.jsx        # CSV export interface
│       ├── styles/
│       │   ├── global.css             # Devanagari fonts & design tokens
│       │   └── annotation.css         # Responsive annotation layout
│       └── utils/
│           └── validation.js          # Client-side verification rules
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── main.py                        # FastAPI application entrypoint
│   ├── database.py                    # SQLAlchemy session & engine
│   ├── models.py                      # Database models (User, Sentence, Token, History)
│   ├── schemas.py                     # Pydantic validation schemas
│   ├── auth.py                        # Bcrypt hashing & JWT utilities
│   ├── config.py                      # Pydantic application settings
│   ├── dependencies.py                # Security & auth dependencies
│   ├── alembic.ini                    # Alembic migration configuration
│   ├── migrations/                    # Database migration scripts
│   ├── routes/
│   │   ├── auth_routes.py             # Login, profile, logout
│   │   ├── dataset_routes.py          # Stats, next sentence, sentence by ID
│   │   ├── annotation_routes.py       # Draft saving, strict verification
│   │   ├── admin_routes.py            # User account management
│   │   └── export_routes.py           # UTF-8 CSV download
│   ├── services/
│   │   ├── csv_importer.py            # Safe, idempotent 70% CSV importer
│   │   ├── annotation_service.py      # Atomic transaction logic
│   │   └── export_service.py          # Gold-standard CSV generator
│   └── scripts/
│       ├── create_admin.py            # CLI tool to create admin accounts
│       └── import_dataset.py          # CLI tool to run the 70% dataset import
├── .gitignore
└── README.md
```

---

## 3. Tag Inventory (Sanskrit Consortium)

The application strictly implements the 23 approved Sanskrit Consortium POS tags:

| Tag | Name | Description |
|---|---|---|
| **N** | Noun (नामपदम्) | General noun stem or inflected noun |
| **NS** | Proper Noun (विशेषनाम) | Specific name of person, place, or entity |
| **NV** | Verbal Noun (कृदन्तरूपम्) | Participle or noun derived from verbal root |
| **KNV** | Secondary Derivative (तद्धितः) | Secondary noun derived from another noun |
| **SN** | Pronoun (सर्वनाम) | Pronoun (*tat, etat, aham*, etc.) |
| **SNV** | Pronominal Adjective (सर्वनाम-विशेषणम्) | Pronoun modifying a noun |
| **SNS** | Compound Pronoun (समस्तसर्वनाम) | Pronominal member in a compound |
| **SAM** | Compound Initial Member (पूर्वपदम्) | First member of a *samasa* |
| **SAMY** | Compound Middle Member (मध्यपदम्) | Intermediate member in a complex *samasa* |
| **SAMP** | Compound Final Member (उत्तरपदम्) | Final member bearing the case ending |
| **KP** | Finite Verb (क्रियापदम्) | Inflected verb with tense/mood and person/number |
| **UP** | Prefix / Upasarga (उपसर्गः) | Pre-verb prefix (*pra, para, sam, ni*, etc.) |
| **AVN** | Indeclinable / Avyaya (अव्ययम्) | Indeclinable particle (*ca, eva, api, tu*) |
| **AVP** | Adverbial Indeclinable (क्रियाविशेषणम्) | Indeclinable modifying a verb |
| **AVUP** | Indeclinable with Prefix | Compound indeclinable beginning with an *upasarga* |
| **SAMB** | Conjunction (सम्बन्धकः / संयोजकम्) | Connective conjunction |
| **AVU** | Interjection (विस्मयादिबोधकम्) | Exclamatory particle |
| **K** | Karmapravachaniya (कर्मप्रवचनीयः) | Governing prepositional particle |
| **AKV** | Secondary Verb | Auxiliary / verbal element |
| **AB** | Abbreviation (संक्षेपः) | Abbreviated form |
| **AVC** | Numerical / Quantifier Indeclinable | Numerical indeclinable |
| **DVI** | Reduplicated Form (द्विरुक्तम्) | Reduplicated word for emphasis or frequency |
| **A** | Adjective (विशेषणम्) | Qualifying adjective modifying a noun |

> [!NOTE]
> The automated Stanza UPOS tags are displayed solely as reference hints. They are never automatically substituted as gold labels.

---

## 4. Dataset Separation Rule (70/30 Split)

- **70% Portion:** Located at `sanskrit_pos_data_10k/70_percent/auto_pos.csv`. This portion contains 7,000 sentences and 69,364 tokens. Only this portion is imported into the annotation queue.
- **30% Portion:** The 30% document-level test split remains completely untouched by this application. It is never imported, predicted on, or modified.

---

## 5. Local Quickstart

### Prerequisites
- Node.js (v18+) and npm
- Python (v3.10+)

### Step 1: Run the Backend
```bash
# From workspace root:
cd sanskrit_pos_annotation_app/backend
source "../../venv/bin/activate"

# Start FastAPI server on port 8000
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
API documentation is available at: **http://localhost:8000/docs**

### Step 2: Run the Frontend
```bash
# In a separate terminal:
cd sanskrit_pos_annotation_app/frontend
npm run dev -- --port 3000
```
Open your browser at: **http://localhost:3000**

### Default Seed Accounts
| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Administrator (Can export CSV and manage users) |
| `sanskrit_scholar` | `password123` | Expert (Can annotate, save drafts, verify sentences) |

---

## 6. Database Management & PostgreSQL Migration

### Using PostgreSQL Locally

1. Create a PostgreSQL user and database:
```bash
sudo -u postgres psql -c "CREATE USER sanskrit_user WITH PASSWORD 'secure_pass';"
sudo -u postgres psql -c "CREATE DATABASE sanskrit_pos_db OWNER sanskrit_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sanskrit_pos_db TO sanskrit_user;"
```

2. Point your backend to PostgreSQL:
Create `sanskrit_pos_annotation_app/backend/.env`:
```ini
DATABASE_URL=postgresql://sanskrit_user:secure_pass@localhost:5432/sanskrit_pos_db
```

3. Run Alembic migrations and seed data:
```bash
cd sanskrit_pos_annotation_app/backend
source "../../venv/bin/activate"

# Apply migrations
alembic upgrade head

# Import the 70% dataset into PostgreSQL
python scripts/import_dataset.py
```

### Database Backup
- **SQLite:** Simply copy `sanskrit_pos_annotation_app/backend/sanskrit_pos.db` to a backup location.
- **PostgreSQL:**
```bash
pg_dump -U sanskrit_user -d sanskrit_pos_db -F c -b -v -f "sanskrit_backup_$(date +%F).dump"
```

---

## 7. Verification and Testing Checklist

| # | Test Scenario | Expected Result | Verified Status |
|---|---|---|---|
| 1 | Expert login with valid credentials | Receives JWT token, navigates to Dashboard | ✅ Verified |
| 2 | Invalid login attempt | Rejection with HTTP 401 and clear error message | ✅ Verified |
| 3 | Load next pending sentence | Loads Sanskrit Devanagari sentence and tokens | ✅ Verified |
| 4 | Token order preservation | Tokens ordered strictly by `token_id` | ✅ Verified |
| 5 | Tag dropdown inventory | Contains all 23 Sanskrit Consortium tags | ✅ Verified |
| 6 | Changing tag in dropdown | Visual highlight changes from amber to green | ✅ Verified |
| 7 | Save Draft | Status changes to `in_progress`, tokens saved | ✅ Verified |
| 8 | Save & Next validation check | Rejects if any token is unassigned (HTTP 422) | ✅ Verified |
| 9 | Save & Next with complete tags | Sets status to `verified`, advances queue | ✅ Verified |
| 10 | Unsaved changes guard | Warning modal appears before leaving page | ✅ Verified |
| 11 | Dashboard metrics | Sentence and token counts match database | ✅ Verified |
| 12 | CSV Export | Downloads UTF-8 with BOM, preserves Devanagari | ✅ Verified |
| 13 | Mobile/Tablet responsiveness | Layout adapts to touch cards on smaller screens | ✅ Verified |
| 14 | 30% portion isolation | 30% file remains untouched on disk | ✅ Verified |

---

## 8. Production Deployment Guide

To share a public HTTPS link with Sanskrit experts across the world:

### Option A: Railway / Render (Backend + PostgreSQL)
1. **Database:** Create a managed PostgreSQL database on [Render.com](https://render.com) or [Neon.tech](https://neon.tech) (both have free tiers).
2. **Backend Web Service:**
   - Link your GitHub repository.
   - Root directory: `sanskrit_pos_annotation_app/backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     - `DATABASE_URL`: Your managed PostgreSQL connection URI.
     - `SECRET_KEY`: A strong random string.
     - `DATASET_CSV_PATH`: Path to your uploaded 70% CSV.
3. Run `python scripts/import_dataset.py` once via the host console or startup script.

### Option B: Vercel / Netlify (Frontend)
1. Link your GitHub repository.
2. Root directory: `sanskrit_pos_annotation_app/frontend`
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend-service.onrender.com/api`

Share the resulting HTTPS URL (e.g., `https://sanskrit-pos-annotation.vercel.app`) with your Sanskrit scholars!

---

## 9. Dataset Export Guide

### Method 1: Via the Web Dashboard
1. Log in with the `admin` account.
2. Click **"Export"** in the top navigation bar or **"📥 Export CSV"** on the Dashboard.
3. Click **"Download final_pos_verified.csv"**.

### Method 2: Via Python Script (from your laptop)
```python
import requests
import pandas as pd
import io

# 1. Login to get access token
login_res = requests.post("http://localhost:8000/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_res.json()["access_token"]

# 2. Download verified CSV
headers = {"Authorization": f"Bearer {token}"}
csv_res = requests.get("http://localhost:8000/api/export/verified.csv", headers=headers)

# 3. Read into pandas DataFrame with UTF-8 encoding
df = pd.read_csv(io.StringIO(csv_res.text), encoding="utf-8")
print(f"Verified rows: {len(df)}")
df.to_csv("my_verified_export.csv", index=False, encoding="utf-8-sig")
```
