from pydantic import BaseModel
from typing import List, Optional

class ReportSection(BaseModel):
    title: str
    content: List[str]

class ISCSReportData(BaseModel):
    report_type: str = "ISCS"
    generated_at: str
    claim_id: str
    claim_number: str
    sections: List[ReportSection]
