from typing import TypedDict, List, Optional, Dict

class ApplicantDetails(TypedDict, total=False):
    name: str
    email: str
    phone: str
    summary: str
    top_skills: List[str]
    projects: List[str]
    education: List[Dict[str, str]]
    experience: List[Dict[str, str]]
    skills: Dict[str, List[str]]

class CompanyDetails(TypedDict, total=False):
    name: str
    location: str
    industry: str
    size: str
    website: str
    recipient_name: str
    recipient_email: str
    jd: str

class State(TypedDict):
    
    company_details: CompanyDetails

    applicant_details: ApplicantDetails

    company_details_enhanced: List[str]  # extracted facts/hooks
    cover_note: str
    email_subject: str
    email_status: str           # "pending" | "sent" | "skipped"
    approval: str               # "pending" | "approved" | "revise"
