# MediClaim AI

India's first Clinical Documentation Standardization Platform.

MediClaim AI turns unstructured hospital records into standardized ISCS reports, medical codes, claim-ready packets, and insurer-facing validation outputs.

## Repository layout

- `web/` - Next.js 15 frontend experience with landing page, dashboards, workflow screens, and copilot.
- `api/` - FastAPI backend scaffold with claim, copilot, analytics, and validation contracts.
- `docs/` - Product, schema, and API notes.
- `infra/k8s/` - Kubernetes-ready deployment manifests.

## Core mission flow

Hospital Records -> AI Standardization -> ISCS (Indian Standard Clinical Summary) -> Medical Coding -> Claim Readiness -> Insurance Processing

## Product coverage

- Premium landing page with enterprise healthcare visual system
- Full 8-step workflow modules:
	- Document Upload
	- OCR Processing
	- Clinical Extraction
	- Medical Coding Engine
	- Validation Engine
	- ISCS Generator
	- Claim Generation
	- Fraud Detection
- Executive analytics dashboard with charts and claim pipeline
- MediClaim Copilot conversational assistant
- Role-based model for Hospital Admin, Doctor, Medical Coder, Insurance Reviewer, TPA Executive, Super Admin
- Micro-SaaS operations module: notifications, activity logs, audit trails, version history, organization controls, API keys, webhook management
- Auth.js-based sign-in flow for role-aware demo sessions

## Frontend

```bash
cd web
npm install
npm run dev
```

Frontend routes of interest:

- `/`
- `/dashboard`
- `/copilot`
- `/workflow/upload`
- `/workflow/processing`
- `/workflow/extraction`
- `/workflow/coding`
- `/workflow/validation`
- `/workflow/iscs`
- `/workflow/claims`
- `/workflow/fraud`
- `/settings`
- `/auth/sign-in`

## Backend

```bash
cd api
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API base URL: `http://localhost:8000/api/v1`

Key endpoints:

- `/claims`
- `/claims/upload`
- `/claims/{claim_id}/processing`
- `/claims/{claim_id}/extraction`
- `/claims/{claim_id}/coding`
- `/claims/{claim_id}/validation`
- `/claims/{claim_id}/iscs`
- `/claims/{claim_id}/fraud`
- `/claims/packets`
- `/claims/insurers`
- `/claims/process`
- `/copilot/chat`
- `/analytics/overview`
- `/auth/roles`
- `/operations/overview`

## Environment

Copy `.env.example` to `.env` and set:

- API/database/redis/openai credentials
- S3-compatible storage credentials
- Auth.js secret and app URL for frontend auth flow

## Platform story

Hospital records -> AI standardization -> ISCS -> medical coding -> claim readiness -> insurance processing
## Claim #1001
│
├── discharge_summary.pdf
├── prescription.pdf
├── OCR output
├── ICD I21.9
├── Validation Score 92
├── ISCS Report
└── Submitted to insurer
Updated readme file with new feature and multiple sprints.