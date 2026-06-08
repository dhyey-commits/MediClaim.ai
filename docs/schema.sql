create table organizations (
  id uuid primary key,
  name text not null,
  type text not null,
  created_at timestamptz not null default now()
);

create table users (
  id uuid primary key,
  organization_id uuid references organizations(id),
  email text unique not null,
  full_name text not null,
  role text not null,
  created_at timestamptz not null default now()
);

create table claims (
  id uuid primary key,
  organization_id uuid references organizations(id),
  patient_name text not null,
  insurer_name text not null,
  status text not null,
  claim_value numeric(12,2) not null,
  readiness_score integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table patients (
  id uuid primary key,
  organization_id uuid references organizations(id),
  full_name text not null,
  age integer not null,
  gender text not null,
  phone text,
  created_at timestamptz not null default now()
);

create table claim_patients (
  claim_id uuid references claims(id),
  patient_id uuid references patients(id),
  primary key (claim_id, patient_id)
);

create table documents (
  id uuid primary key,
  claim_id uuid references claims(id),
  file_name text not null,
  file_type text not null,
  storage_key text not null,
  ocr_status text not null,
  created_at timestamptz not null default now()
);

create table ocr_stage_progress (
  id uuid primary key,
  claim_id uuid references claims(id),
  stage text not null,
  progress integer not null,
  state text not null,
  created_at timestamptz not null default now()
);

create table clinical_extractions (
  id uuid primary key,
  claim_id uuid references claims(id),
  payload jsonb not null,
  confidence jsonb not null,
  created_at timestamptz not null default now()
);

create table coding_suggestions (
  id uuid primary key,
  claim_id uuid references claims(id),
  coding_system text not null,
  code text not null,
  label text not null,
  confidence numeric(5,4) not null,
  source text not null,
  overridden boolean not null default false,
  created_at timestamptz not null default now()
);

create table validation_results (
  id uuid primary key,
  claim_id uuid references claims(id),
  readiness_score integer not null,
  issues jsonb not null,
  compliance_flags jsonb not null,
  created_at timestamptz not null default now()
);

create table iscs_reports (
  id uuid primary key,
  claim_id uuid references claims(id),
  title text not null,
  sections jsonb not null,
  share_link text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table claim_packets (
  id uuid primary key,
  claim_id uuid references claims(id),
  insurer_name text not null,
  packet_status text not null,
  packet_payload jsonb not null,
  created_at timestamptz not null default now()
);

create table fraud_analyses (
  id uuid primary key,
  claim_id uuid references claims(id),
  risk_score integer not null,
  anomalies jsonb not null,
  missing_evidence jsonb not null,
  suspicious_patterns jsonb not null,
  created_at timestamptz not null default now()
);

create table role_permissions (
  id uuid primary key,
  role text not null,
  permissions jsonb not null,
  created_at timestamptz not null default now()
);

create table audit_events (
  id uuid primary key,
  organization_id uuid references organizations(id),
  actor_user_id uuid references users(id),
  action text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table activity_logs (
  id uuid primary key,
  organization_id uuid references organizations(id),
  actor_user_id uuid references users(id),
  category text not null,
  message text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table version_history (
  id uuid primary key,
  entity_type text not null,
  entity_id uuid not null,
  version_number integer not null,
  diff jsonb not null,
  created_by uuid references users(id),
  created_at timestamptz not null default now()
);

create table api_keys (
  id uuid primary key,
  organization_id uuid references organizations(id),
  name text not null,
  token_hash text not null,
  scopes jsonb not null,
  last_used_at timestamptz,
  created_at timestamptz not null default now()
);

create table webhooks (
  id uuid primary key,
  organization_id uuid references organizations(id),
  target_url text not null,
  event_name text not null,
  signing_secret text not null,
  active boolean not null default true,
  created_at timestamptz not null default now()
);
