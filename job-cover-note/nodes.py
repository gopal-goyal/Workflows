# nodes.py
from llm import OllamaLLM
from emailer import send_email
import re, json

llm = OllamaLLM(model="llama3.1:latest", temperature=0.3)

def _strip_fences(text: str) -> str:
    return re.sub(r"^```.*?\n|\n```$", "", text.strip(), flags=re.DOTALL).strip()

def extract_company_details(state):
    """
    Input: state["company_details"] as a single rich dict (name, jd, recipient, etc.)
    Output: state["company_details_enhanced"] = list of {"hook","category"} derived ONLY from the JD
    """
    company_details = state.get("company_details", {}) or {}

    prompt = f"""
    You are given a single object called company_details that contains all information about the target company,
    including a 'jd' field with the job description text.

    Return ONLY a JSON array of 5–7 objects.
    Each object must have exactly two fields:
    - "hook": a concrete fact extracted STRICTLY from company_details.jd (do not invent)
    - "category": a short label like "Overview", "Culture", "Work Model", "Products"

    Do NOT add prose or code fences. Valid JSON array only.

    company_details:
    {json.dumps(company_details, ensure_ascii=False)}
    """

    raw = _strip_fences(llm.invoke(prompt))
    parsed = []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            if all(isinstance(x, dict) for x in data):
                parsed = [
                    {"hook": str(x.get("hook", "")).strip(),
                     "category": str(x.get("category", "Other")).strip()}
                    for x in data if str(x.get("hook", "")).strip()
                ]
            elif all(isinstance(x, str) for x in data):
                parsed = [{"hook": x.strip(), "category": "General"} for x in data if x.strip()]
    except Exception:
        lines = [l.strip(" -•\t") for l in raw.splitlines() if l.strip()]
        parsed = [{"hook": l, "category": "General"} for l in lines[:7]]

    state["company_details_enhanced"] = parsed
    return state


def draft_cover_note(state):
    """
    Input: full applicant_details dict + full company_details dict
    Output: state["cover_note"] = email body text only
    """
    company_details = state.get("company_details", {}) or {}
    applicant_details = state.get("applicant_details", {}) or {}
    hooks = state.get("company_details_enhanced", [])

    prompt = f"""
    Write the **final email body only** for a job application (120–160 words).
    
    Use only information from these objects:
    - company_details: {json.dumps(company_details, ensure_ascii=False)}
    - applicant_details: {json.dumps(applicant_details, ensure_ascii=False)}
    - jd_hooks: {json.dumps(hooks, ensure_ascii=False)}

    Rules:
    - Start the response DIRECTLY with "Hi <recipient_name or 'Hiring Team'>,"
    - Do NOT add any introduction like "Here is the cover note" or "Body:".
    - Open with a JD hook (from jd_hooks) tied directly to the role.
    - Use up to 2 quantified applicant achievements if available.
    - Include exactly this line: "I have attached my resume for your review."
    - End with a clear next step (e.g., short call or referral to formal application).
    - Finish ONLY with: "Regards," on one line, then applicant_details.name and applicant_details.phone (if provided).
    - No extra text, no formatting, no markdown, no explanations — just the email body as it would be sent.
    """

    body = _strip_fences(llm.invoke(prompt))
    state["cover_note"] = body.strip()
    return state


def draft_subject(state):
    """
    Input: full company_details + applicant_details
    Output: state["email_subject"] (model must extract role & company from the provided objects)
    """
    company_details = state.get("company_details", {}) or {}
    applicant_details = state.get("applicant_details", {}) or {}

    prompt = f"""
    Generate a concise professional email subject line for a job application.

    Constraints:
    - Must start with the word "Application".
    - Include a clear role title (extract from company_details.jd or infer a standard title from it).
    - Include the company name (extract from company_details).
    - Under 80 characters total.
    - Return ONLY the subject line; no quotes or extra text.

    Inputs:
    - company_details: {json.dumps(company_details, ensure_ascii=False)}
    - applicant_details: {json.dumps(applicant_details, ensure_ascii=False)}
    """

    subject = _strip_fences(llm.invoke(prompt))
    state["email_subject"] = subject
    return state


def send_email_node(state):
    """
    Sends the email only if approval == 'approved'.
    Pulls recipient_email from company_details (single source of truth).
    """
    print("Sending email...")

    if state.get("approval") != "approved":
        state["email_status"] = "skipped"
        return state

    company_details = state.get("company_details", {}) or {}
    to_address = company_details.get("recipient_email") or ""
    subject = state.get("email_subject", "").strip()
    body = state.get("cover_note", "").strip()

    if not to_address or not subject or not body:
        state["email_status"] = "skipped"
        return state

    send_email(
        to_address=to_address,
        subject=subject,
        body=body,
        attachment_path="examples/Gopal_Goyal_Resume.pdf"
    )
    state["email_status"] = "sent"
    return state
