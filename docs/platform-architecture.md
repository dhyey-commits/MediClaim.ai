# MediClaim AI Platform Architecture

## Story

Hospital Records -> AI Standardization -> ISCS -> Medical Coding -> Claim Readiness -> Insurance Processing

## Frontend

- Next.js 15 App Router
- TypeScript
- TailwindCSS
- Framer Motion for motion systems
- Recharts for analytics and fraud visuals
- React Query for data orchestration
- shadcn/ui-style primitives for buttons, cards, badges, and shells

### Product modules

- Landing: hero, features, how-it-works, benefits, testimonials, pricing, FAQ, contact CTA
- Executive dashboard: claims KPIs, approval trends, fraud visuals, hospital performance, pipeline
- Workflow steps:
	- `/workflow/upload`
	- `/workflow/processing`
	- `/workflow/extraction`
	- `/workflow/coding`
	- `/workflow/validation`
	- `/workflow/iscs`
	- `/workflow/claims`
	- `/workflow/fraud`
- Copilot: ChatGPT-style assistant at `/copilot`
- Operations settings: notifications, activity logs, audit trails, version history, org controls, API keys, webhooks
- Authentication: Auth.js credential flow with role-aware session payload

## Backend

- FastAPI for API contracts
- PostgreSQL for transactional claim and organization data
- Redis for queue state and caching
- Celery for OCR, coding, and report-generation jobs
- OCR abstraction layer for vendor selection
- AI service boundary for GPT-based extraction, coding, and explanation

### API modules

- Health:
	- `GET /api/v1/health`
- Claims:
	- `GET /api/v1/claims`
	- `GET /api/v1/claims/{claim_id}`
	- `POST /api/v1/claims/upload`
	- `GET /api/v1/claims/{claim_id}/processing`
	- `GET /api/v1/claims/{claim_id}/extraction`
	- `GET /api/v1/claims/{claim_id}/coding`
	- `GET /api/v1/claims/{claim_id}/validation`
	- `GET /api/v1/claims/{claim_id}/iscs`
	- `GET /api/v1/claims/{claim_id}/fraud`
	- `GET /api/v1/claims/packets`
	- `GET /api/v1/claims/insurers`
	- `POST /api/v1/claims/process`
- Analytics:
	- `GET /api/v1/analytics/overview`
- Copilot:
	- `POST /api/v1/copilot/chat`
- Auth:
	- `GET /api/v1/auth/roles`
- Operations:
	- `GET /api/v1/operations/overview`

### Async processing

- Celery workers process OCR, extraction, coding, validation, and ISCS generation in queue stages.
- Redis brokers background jobs and stores short-lived state for progress streaming.
- S3-compatible storage keeps uploads and generated packet exports.

## Security and operations

- Role-based access controls for hospital, coding, insurer, and admin users
- Audit trail and version history for edits and overrides
- S3-compatible storage for uploads and generated exports
- Docker and Kubernetes-ready deployment layout

## Role model

- Hospital Admin
- Doctor
- Medical Coder
- Insurance Reviewer
- TPA Executive
- Super Admin
