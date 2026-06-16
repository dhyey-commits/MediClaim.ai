# TODO - Production-grade SaaS conversion

## Backend (FastAPI)
- [ ] Add DB layer (SQLAlchemy async engine/session) under `api/app/db/`.
- [ ] Add ORM models for: Users, Organizations, Patients, Claims, Documents, Diagnoses, Procedures, ICD_Codes, Reports, AuditLogs.
- [ ] Implement repository layer for CRUD + workflow queries under `api/app/repositories/`.
- [ ] Implement workflow state machine for Claim status transitions.
- [ ] Add/replace FastAPI endpoints to be DB-backed (replace demo/mock usages):
  - [ ] `GET /claims`
  - [ ] `POST /claims`
  - [ ] `GET /claims/{id}`
  - [ ] `POST /claims/{id}/actions/...` for workflow transitions
  - [ ] `GET /documents`
  - [ ] `GET /documents/{id}`
  - [ ] `GET /analytics/overview`
  - [ ] Notifications/operations endpoints backed by DB.
- [ ] Remove demo service wiring from routers.

## Database schema
- [ ] Replace `docs/schema.sql` with schema matching requirements and updated relationships.

## Frontend (Next.js)
- [ ] Create app-wide layout with persistent Sidebar + TopNav + Profile + Notifications + Breadcrumbs.
- [ ] Ensure sidebar nav links cover required routes:
  - /dashboard
  - /claims
  - /claims/new
  - /claims/[id]
  - /documents
  - /documents/[id]
  - /coding
  - /reports
  - /analytics
  - /settings
- [ ] Add “Dashboard” navigation from anywhere (topnav + breadcrumbs).
- [ ] Implement React Query API client + hooks to call FastAPI endpoints.
- [ ] Replace mock-data workflow pages with real DB-backed pages:
  - [ ] `/claims`, `/claims/new`, `/claims/[id]`
  - [ ] `/documents`, `/documents/[id]`
  - [ ] `/coding`, `/reports`, `/analytics`, `/settings`
- [ ] Ensure clicking a claim/document opens detail pages.

## Workflow state in UI
- [ ] Render claim status and progress using DB workflow state.
- [ ] Ensure workflow actions call endpoints and invalidate queries.

## Integration testing
- [ ] Start stack with docker compose.
- [ ] Verify: claim transitions persist; pages navigate via sidebar; actions update DB.

update local dev auth .