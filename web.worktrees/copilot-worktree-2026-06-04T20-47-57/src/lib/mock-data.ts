import {
  Activity,
  BrainCircuit,
  FileText,
  ScanSearch,
  ShieldAlert,
  Stethoscope,
  FileCheck2,
  HeartPulse,
} from "lucide-react";

export const landingStats = [
  { label: "Average claim readiness", value: "94", description: "Claims are validated before handoff to insurers." },
  { label: "OCR extraction accuracy", value: "99.1%", description: "Structured from PDFs, scans, and hospital documents." },
  { label: "Roles supported", value: "6", description: "Permissioned workflows for the entire care network." },
];

export const productCapabilities = [
  {
    title: "AI document standardization",
    description: "Turn unstructured Indian hospital records into a clean, traceable medical timeline with OCR and NLP.",
    icon: ScanSearch,
  },
  {
    title: "Clinical coding engine",
    description: "Map diagnoses and procedures to ICD-10, SNOMED CT, CPT, and RxNorm with manual override support.",
    icon: FileCheck2,
  },
  {
    title: "Validation and fraud signals",
    description: "Detect missing documentation, inconsistencies, and suspicious patterns before claim submission.",
    icon: ShieldAlert,
  },
];

export const workflowSteps = [
  { title: "Document upload", description: "PDFs, scans, prescriptions, lab reports, and discharge summaries enter a single intake queue." },
  { title: "OCR processing", description: "Stage-by-stage extraction keeps reviewers informed while AI identifies entities and procedures." },
  { title: "ISCS generation", description: "Hospital records become an Indian Standard Clinical Summary with a clean clinical timeline." },
  { title: "Claim readiness", description: "Validation gates, coding suggestions, and insurer-specific packet assembly happen automatically." },
];

export const pricingPlans = [
  {
    name: "Starter",
    price: "For clinics and pilot hospitals",
    description: "Launch the workflow with core OCR, summary generation, and manual review support.",
    features: ["Upload and OCR intake", "ISCS generation", "Basic role controls", "Email support"],
    featured: false,
  },
  {
    name: "Growth",
    price: "For multi-hospital networks",
    description: "Add claim validation, coding assistance, dashboards, and collaboration features.",
    features: ["Medical coding review", "Claim readiness scoring", "Analytics dashboard", "Webhook + API access"],
    featured: true,
  },
  {
    name: "Enterprise",
    price: "For insurers and large TPAs",
    description: "Deploy with SSO, audit trails, custom policies, and private infrastructure support.",
    features: ["SSO and policy controls", "Advanced audit logs", "Dedicated deployment", "Priority onboarding"],
    featured: false,
  },
];

export const testimonials = [
  {
    name: "Dr. Ananya Rao",
    title: "Medical Superintendent, multispecialty hospital",
    quote:
      "MediClaim AI gives our team a shared source of truth for documentation, coding, and insurer communication without slowing the clinical workflow.",
  },
  {
    name: "Karthik Menon",
    title: "Claims Operations Lead, TPA",
    quote:
      "The claim readiness score and missing evidence checks cut review time before packets ever reach our analyst queue.",
  },
];

export const faqs = [
  {
    question: "Is MediClaim AI only a claim tool?",
    answer:
      "No. It is positioned as India's first Clinical Documentation Standardization Platform, with claim preparation as the downstream outcome.",
  },
  {
    question: "Can we control permissions by role?",
    answer:
      "Yes. Hospital admins, doctors, coders, TPAs, insurers, and super admins all have distinct permission layers and audit trails.",
  },
  {
    question: "How does the copilot help?",
    answer:
      "MediClaim Copilot explains codes, identifies missing documents, summarizes records, and helps reviewers understand rejection reasons.",
  },
  {
    question: "Can this be deployed privately?",
    answer:
      "The scaffold is Kubernetes-ready and includes Docker-friendly backend and frontend layout for private cloud or managed deployment.",
  },
];

export const dashboardMetrics = [
  { label: "Total claims", value: "12,480", delta: "+18.4%" },
  { label: "Approval rate", value: "91.6%", delta: "+2.1%" },
  { label: "Avg. processing time", value: "14m 32s", delta: "-24%" },
  { label: "Fraud alerts", value: "27", delta: "-11%" },
];

export const claimPipeline = ["Draft", "Ready", "Submitted", "Under Review", "Approved", "Rejected"];

export const claimStatuses = [
  { label: "Draft", count: 128, color: "bg-slate-200" },
  { label: "Ready", count: 312, color: "bg-sky-400" },
  { label: "Submitted", count: 241, color: "bg-cyan-400" },
  { label: "Under Review", count: 84, color: "bg-amber-400" },
  { label: "Approved", count: 558, color: "bg-emerald-400" },
  { label: "Rejected", count: 31, color: "bg-rose-400" },
];

export const chartData = [
  { month: "Jan", approvals: 74, claims: 96, fraud: 9 },
  { month: "Feb", approvals: 79, claims: 104, fraud: 12 },
  { month: "Mar", approvals: 82, claims: 118, fraud: 10 },
  { month: "Apr", approvals: 86, claims: 125, fraud: 14 },
  { month: "May", approvals: 90, claims: 138, fraud: 11 },
  { month: "Jun", approvals: 92, claims: 146, fraud: 8 },
];

export const medicalTimeline = [
  { time: "09:20", label: "Admission registered", detail: "Emergency intake for dengue fever with dehydration symptoms." },
  { time: "10:05", label: "Diagnostics uploaded", detail: "CBC, platelet count, and chest X-ray routed into the OCR pipeline." },
  { time: "12:30", label: "Coding review", detail: "ICD-10 and CPT suggestions ready for coder override." },
  { time: "16:45", label: "Claim packet generated", detail: "ISCS report and insurer-ready packet assembled with validation notes." },
];

export const fraudSignals = [
  { title: "Duplicate lab pattern", value: "Medium", score: 68 },
  { title: "Missing signature", value: "Low", score: 22 },
  { title: "Unexpected LOS deviation", value: "High", score: 82 },
];

export const inboxItems = [
  { role: "Hospital Admin", text: "2 submissions waiting on discharge summary upload" },
  { role: "Medical Coder", text: "4 ICD suggestions need manual review" },
  { role: "Insurance Reviewer", text: "1 claim flagged for missing evidence" },
  { role: "TPA Executive", text: "Webhook delivered to partner system successfully" },
];

export const copilotThreads = [
  {
    role: "MediClaim Copilot",
    message: "I can explain the ICD-10 mapping, identify missing documents, and draft insurer notes from the uploaded record.",
  },
  {
    role: "Insurance Reviewer",
    message: "Why was the claim marked low confidence?",
  },
  {
    role: "MediClaim Copilot",
    message: "The discharge summary lacks signature verification and the diagnosis has no supporting investigation note.",
  },
];

export const auditEvents = [
  { user: "Super Admin", action: "Updated organization policy for TPA routing", time: "2m ago" },
  { user: "Medical Coder", action: "Overrode ICD-10 suggestion to a more specific code", time: "8m ago" },
  { user: "Insurance Reviewer", action: "Added note to claim validation record", time: "17m ago" },
  { user: "Doctor", action: "Submitted discharge summary for review", time: "31m ago" },
];

export const stakeholders = [
  "Hospital Admin",
  "Doctor",
  "Medical Coder",
  "Insurance Reviewer",
  "TPA Executive",
  "Super Admin",
];

export const workflowNav = [
  { href: "/workflow/upload", label: "1. Upload" },
  { href: "/workflow/processing", label: "2. OCR" },
  { href: "/workflow/extraction", label: "3. Extraction" },
  { href: "/workflow/coding", label: "4. Coding" },
  { href: "/workflow/validation", label: "5. Validation" },
  { href: "/workflow/iscs", label: "6. ISCS" },
  { href: "/workflow/claims", label: "7. Claims" },
  { href: "/workflow/fraud", label: "8. Fraud" },
];

export const uploadDocumentTypes = [
  "PDF",
  "Image",
  "Scanned document",
  "Discharge summary",
  "Prescription",
  "Lab report",
  "Radiology report",
];

export const uploadQueue = [
  { name: "rahul-mehta-discharge-summary.pdf", progress: 100, status: "OCR Complete" },
  { name: "platelet-report.jpg", progress: 83, status: "Entity detection" },
  { name: "prescription-scan-3.png", progress: 64, status: "Diagnosis extraction" },
  { name: "consent-form.pdf", progress: 38, status: "OCR extraction" },
];

export const ocrStages = [
  "OCR Extraction",
  "Medical Entity Detection",
  "Diagnosis Extraction",
  "Procedure Extraction",
  "ICD Mapping",
  "Validation",
  "Report Generation",
];

export const extractionConfidence = [
  { field: "Patient details", confidence: 0.98 },
  { field: "Symptoms", confidence: 0.95 },
  { field: "Diagnosis", confidence: 0.93 },
  { field: "Procedures", confidence: 0.9 },
  { field: "Investigations", confidence: 0.96 },
  { field: "Medications", confidence: 0.94 },
  { field: "Admission details", confidence: 0.97 },
  { field: "Discharge details", confidence: 0.91 },
];

export const codingReviewRows = [
  { diagnosis: "Viral fever", system: "ICD-10", code: "A09", confidence: 0.89, override: "No" },
  { diagnosis: "Viral fever", system: "SNOMED CT", code: "186747009", confidence: 0.87, override: "No" },
  { diagnosis: "Hydration therapy", system: "CPT", code: "96360", confidence: 0.91, override: "Yes" },
  { diagnosis: "Paracetamol", system: "RxNorm", code: "198440", confidence: 0.96, override: "No" },
];

export const validationChecks = [
  { title: "Missing information", status: "Passed", detail: "All required sections detected." },
  { title: "Conflicting diagnoses", status: "Passed", detail: "No conflict between diagnosis and labs." },
  { title: "Missing signatures", status: "Warning", detail: "1 consultant signature needs verification." },
  { title: "Documentation completeness", status: "Passed", detail: "ISCS narrative fully populated." },
  { title: "Insurance compliance", status: "Passed", detail: "Mapped to policy and package rules." },
];

export const insurers = [
  "Star Health",
  "Niva Bupa",
  "ICICI Lombard",
  "HDFC Ergo",
  "Care Health",
  "Government Schemes",
];

export const claimPackets = [
  { id: "PKT-1408", insurer: "Star Health", status: "Ready", amount: "INR 84,500" },
  { id: "PKT-1409", insurer: "Niva Bupa", status: "Submitted", amount: "INR 112,000" },
  { id: "PKT-1410", insurer: "HDFC Ergo", status: "Under Review", amount: "INR 124,000" },
  { id: "PKT-1411", insurer: "Care Health", status: "Approved", amount: "INR 72,300" },
  { id: "PKT-1412", insurer: "Government Schemes", status: "Rejected", amount: "INR 55,900" },
];

export const fraudHeatmap = [
  { area: "Documentation", score: 72 },
  { area: "Length of stay", score: 81 },
  { area: "Drug utilization", score: 58 },
  { area: "Procedure frequency", score: 66 },
  { area: "Billing outliers", score: 79 },
];

export const microsaasFeatures = [
  { title: "Notifications", detail: "Priority queues, reviewer alerts, and insurer updates." },
  { title: "Activity logs", detail: "Chronological actions across users and claim entities." },
  { title: "Audit trails", detail: "Immutable compliance-grade events with export." },
  { title: "Version history", detail: "Track ISCS edits, coding overrides, and reviewer notes." },
  { title: "Organization management", detail: "Multi-hospital control with role templates." },
  { title: "API keys", detail: "Scoped tokens for integration and automations." },
  { title: "Settings panel", detail: "Policy rules, SLA timers, and insurer mappings." },
  { title: "Webhook management", detail: "Retry handling and payload insights for partner systems." },
];

export const demoHospitals = [
  { name: "Apex Care Hospital", city: "Bengaluru", claims: 1880 },
  { name: "Narayana Multispecialty", city: "Hyderabad", claims: 1570 },
  { name: "City Medical Center", city: "Chennai", claims: 1320 },
];

export const demoDoctors = [
  { name: "Dr. Meera Kulkarni", specialty: "Internal Medicine" },
  { name: "Dr. Arjun Deshpande", specialty: "General Surgery" },
  { name: "Dr. Nidhi Sharma", specialty: "Critical Care" },
];

export const demoPatients = [
  { name: "Rahul Mehta", age: 42, diagnosis: "Viral fever" },
  { name: "Ananya Rao", age: 31, diagnosis: "Appendicitis" },
  { name: "Sandeep Iyer", age: 54, diagnosis: "Pneumonia" },
];

export const demoIcdCodes = [
  { code: "A09", label: "Infectious gastroenteritis and colitis, unspecified" },
  { code: "K35.80", label: "Acute appendicitis" },
  { code: "J18.9", label: "Pneumonia, unspecified organism" },
];

export const featureBlocks = [
  {
    title: "OCR + NLP pipeline",
    icon: Activity,
    description: "Process scans, PDFs, and hospital notes into structured patient and claim artifacts.",
  },
  {
    title: "Diagnosis extraction",
    icon: Stethoscope,
    description: "Identify symptoms, diagnosis, procedures, and medication patterns from complex records.",
  },
  {
    title: "AI validation",
    icon: BrainCircuit,
    description: "Track confidence scores, missing evidence, and insurer rules in one review surface.",
  },
  {
    title: "ISCS generation",
    icon: FileText,
    description: "Create Indian Standard Clinical Summary outputs with export and share actions.",
  },
  {
    title: "Claim workflow",
    icon: HeartPulse,
    description: "Move claims through Draft, Ready, Submitted, Under Review, Approved, and Rejected states.",
  },
];