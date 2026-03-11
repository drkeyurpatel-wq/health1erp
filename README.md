# Health1ERP

A full-stack hospital management system with AI-powered clinical decision support, real-time bed management, and multilingual capabilities.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, SQLAlchemy (async), PostgreSQL 16, Redis 7, Celery |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Radix UI, Recharts |
| **Mobile** | Expo SDK 50, React Native, React Native Paper |
| **Infrastructure** | Docker Compose, Nginx, Alembic |
| **AI/ML** | OpenAI GPT-4 (with template fallback), NEWS2, CDSS Engine |

## Modules

| Module | Description |
|--------|------------|
| **Authentication** | JWT auth with 8 roles (SuperAdmin, Admin, Doctor, Nurse, Pharmacist, LabTech, Receptionist, Accountant) and granular permissions |
| **Patients** | UHID-based registration, demographics, allergies, insurance, timeline aggregation |
| **Appointments** | Slot management, token queue, check-in, teleconsultation support |
| **IPD** | Admissions, bed management (General/ICU/NICU/PICU/HDU), doctor rounds, nursing assessments, discharge workflow, AI risk scoring, NEWS2 early warning, real-time WebSocket bed status |
| **Billing** | Auto-calculated bills, payments, insurance claims, revenue reports |
| **Inventory** | Stock tracking, batch/expiry management, low-stock & expiring-soon alerts, purchase orders |
| **Pharmacy** | Prescriptions, dispensation with stock deduction, drug interaction checks |
| **Laboratory** | Test catalog, orders, results, verification workflow, AI interpretation |
| **Radiology** | Exam types, orders, reports, AI findings |
| **Operation Theatre** | OT room management, surgical bookings |
| **Reports** | PDF generation (bills, discharge summaries, prescriptions, lab reports), Excel exports |
| **AI & CDSS** | Risk analysis, drug interactions, diagnosis suggestions, length-of-stay prediction, discharge summary generation, medical translation |

## Project Structure

```
health1erp/
├── backend/
│   ├── app/
│   │   ├── ai/                  # CDSS engine, medical translator
│   │   ├── api/v1/endpoints/    # 12 endpoint modules
│   │   ├── core/                # Config, database, security, deps, WebSocket
│   │   ├── middleware/           # Request context, audit logging
│   │   ├── models/              # 11 SQLAlchemy model files
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Notification service
│   │   └── utils/               # PDF generator, HL7/FHIR handler
│   ├── migrations/              # Alembic migrations
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/                 # Next.js pages (dashboard, IPD, patients, etc.)
│       ├── components/          # UI components, charts, layout
│       ├── hooks/               # WebSocket real-time hook
│       ├── i18n/                # en, hi, ar translations
│       ├── lib/                 # API client, utilities
│       ├── store/               # Zustand auth store
│       └── types/               # TypeScript type definitions
├── mobile/
│   └── src/
│       ├── screens/             # 8 screens (Dashboard, IPD, Patients, etc.)
│       ├── navigation/          # Bottom tabs + stack navigators
│       ├── i18n/                # en, hi translations
│       ├── services/            # API client
│       └── store/               # Zustand auth store (expo-secure-store)
├── docker/                      # Dockerfiles, nginx.conf
├── scripts/                     # Seed data, dev startup
├── docker-compose.yml           # Production setup
├── docker-compose.dev.yml       # Dev overrides (hot reload, pgAdmin)
└── .env.example                 # All environment variables
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- (Optional) Expo CLI for mobile development

### Quick Start with Docker

```bash
# Clone and configure
git clone https://github.com/drkeyurpatel-wq/health1erp.git
cd health1erp
cp .env.example .env

# Start all services (backend, frontend, postgres, redis, celery, nginx)
docker compose up -d

# Or use the dev script for local development
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
cd ..
python scripts/seed_data.py
uvicorn backend.app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Mobile:**
```bash
cd mobile
npm install
npx expo start
```

### Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/docs |
| API Docs (ReDoc) | http://localhost:8000/api/redoc |
| pgAdmin (dev) | http://localhost:5050 |
| Nginx (production) | http://localhost:80 |

### Default Credentials

| Role | Email | Password |
|------|-------|----------|
| SuperAdmin | admin@health1erp.com | Admin@123 |
| Doctor | doctor@health1erp.com | Doctor@123 |
| Nurse | nurse@health1erp.com | Nurse@123 |

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Prefix | Tag | Key Endpoints |
|--------|-----|--------------|
| `/auth` | Authentication | Login, register, refresh token, me |
| `/patients` | Patients | CRUD, search, patient timeline |
| `/appointments` | Appointments | CRUD, available slots, check-in, live queue, complete |
| `/ipd` | IPD - Inpatient | Admit, transfer bed, doctor rounds, nursing assessments, discharge workflow (initiate/approve/complete), bed management dashboard, AI insights, WebSocket `/ws/bed-status` |
| `/billing` | Billing | Generate bill, record payment, insurance claims, revenue report |
| `/inventory` | Inventory | CRUD, stock-in/out, low-stock alerts, expiring-soon, suppliers |
| `/pharmacy` | Pharmacy | Prescriptions, pending queue, dispense, drug interactions |
| `/laboratory` | Laboratory | Tests, orders, results, verification, AI interpretation |
| `/radiology` | Radiology | Exams, orders, reports |
| `/ot` | Operation Theatre | OT rooms, bookings |
| `/reports` | Reports | PDF/Excel generation, daily summaries |
| `/ai` | AI & CDSS | CDSS recommend, predict LOS, drug interactions, diagnosis suggest, discharge summary, translate |

## AI Features

The AI subsystem uses OpenAI GPT-4 with graceful fallback to rule-based templates when the API key is not configured.

- **Risk Scoring** — Calculates patient risk on admission based on age, diagnosis, and vitals
- **NEWS2 Early Warning** — National Early Warning Score 2 auto-calculated from nursing vitals (temperature, BP, pulse, SpO2, respiratory rate, consciousness)
- **CDSS Recommendations** — Clinical decision support with drug interaction checks and diagnosis suggestions
- **Length of Stay Prediction** — AI-estimated days based on diagnosis, comorbidities, and admission type
- **Discharge Summary Generation** — AI-generated multilingual summaries with medication instructions
- **Medical Translation** — Translates clinical text to patient-friendly language in 6 languages (en, hi, ar, es, fr, zh)

## Interoperability

- **HL7 v2.x** — ADT message parsing/creation for admission, discharge, transfer events
- **FHIR R4** — Patient, Encounter, and DiagnosticReport resource conversion
- Configurable via `FHIR_SERVER_URL` and `HL7_ENABLED` environment variables

## Role-Based Access Control

| Role | Access |
|------|--------|
| SuperAdmin | Full access to all modules |
| Admin | All modules (read/write) except system config |
| Doctor | Patients, appointments, IPD, prescribe, order labs/radiology, OT |
| Nurse | Patients (read), IPD nursing, appointments (read) |
| Pharmacist | Pharmacy, inventory, patients (read) |
| LabTech | Laboratory, patients (read) |
| Receptionist | Patients, appointments, billing |
| Accountant | Billing, reports, inventory (read) |

## Seed Data

The seed script (`scripts/seed_data.py`) creates:

- 15 departments (Emergency, ICU, General Medicine, Cardiology, etc.)
- 7 wards with 91 beds (General, Semi-Private, Private, ICU, NICU, HDU)
- 3 users (SuperAdmin, Doctor, Nurse)
- 13 lab test types (CBC, LFT, KFT, Thyroid, Lipid, etc.)
- 6 OT rooms

## Environment Variables

See [`.env.example`](.env.example) for all configurable variables including:

- Database, Redis, and Celery connection strings
- JWT secret and token expiry
- OpenAI API key and CDSS settings
- SMTP (email) and Twilio (SMS) for notifications
- Stripe and Razorpay for payments
- S3 or local file storage
- FHIR/HL7 server configuration
- i18n language settings

## License

Proprietary. All rights reserved.
