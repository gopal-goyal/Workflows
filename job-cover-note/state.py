from typing import TypedDict, List, Optional, Dict

class ApplicantProfile(TypedDict, total=False):
    summary: str                # 3–5 lines about you
    top_skills: List[str]       # e.g., ["LLMs", "RAG", "AWS"]
    projects: List[str]         # short slugs to mention

class State(TypedDict):
    job_description: str
    company_name: str
    company_email: str
    applicant_profile: ApplicantProfile

    company_details: List[str]  # extracted facts/hooks
    cover_note: str
    email_status: str           # "pending" | "sent" | "skipped"
    approval: str               # "pending" | "approved" | "revise"
