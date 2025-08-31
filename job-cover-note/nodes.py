from llm import OllamaLLM
from emailer import send_email
import re, json

llm = OllamaLLM(model="llama3.1:latest", temperature=0.3)

def extract_company_details(state):
    prompt = f"""
    Return ONLY a JSON array of 5–7 objects. 
    Each object should have exactly two fields:
    - "hook": a short concrete fact about the company **{state['company_name']}**, based ONLY on this job description.
    - "category": a label for the hook (e.g., "Company Overview", "Culture", "Work Model", "Products").

    Format example:
    [
    {{"hook": "Kimberly-Clark is a global brand with 150+ years of history", "category": "Company Overview"}},
    {{"hook": "Strong focus on sustainability and inclusion", "category": "Culture"}}
    ]

    Do NOT wrap in triple backticks or add explanations. 
    Do NOT include headings like 'Here are…'. Output must be valid JSON only.

    JOB DESCRIPTION:
    {state['job_description']}
    """

    raw = llm.invoke(prompt).strip()

    # Strip accidental markdown code fences
    raw = re.sub(r"^```.*?\n|\n```$", "", raw, flags=re.DOTALL).strip()

    parsed = []
    try:
        data = json.loads(raw)

        # Case 1: correct list of dicts
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            parsed = [
                {"hook": str(x.get("hook", "")).strip(),
                 "category": str(x.get("category", "Other")).strip()}
                for x in data if x.get("hook")
            ]
        # Case 2: list of strings (fallback) → wrap into dicts
        elif isinstance(data, list) and all(isinstance(x, str) for x in data):
            parsed = [{"hook": x.strip(), "category": "General"} for x in data if x.strip()]
    except Exception:
        # Final fallback: line split
        lines = [l.strip(" -•\t") for l in raw.splitlines() if l.strip()]
        parsed = [{"hook": l, "category": "General"} for l in lines[:7]]

    state["company_details"] = parsed
    return state

def draft_cover_note(state):
    prompt = f"""
    Write a crisp, professional cover note (3–4 sentences) to the hiring contact {state['company_email']} at {state['company_name']}.
    Use these company hooks from the JD:
    {state['company_details']}

    Applicant profile (optional context):
    {state['applicant_profile']}
    
    Constraints:
    - 120–160 words max.
    - Open with a specific hook referencing the JD (not generic).
    - Include 1–2 quantified outcomes from the applicant if present in profile; if none, keep it skill-based, no fabrication.
    - Close with a clear next step (short call or referral to formal application).
    Return ONLY the body text.
    """

    response = llm.invoke(prompt)
    state["cover_note"] = response
    return state

def send_email_node(state):
    print("Sending email...")
    # Require approval flag
    if state.get("approval") != "approved":
        state["email_status"] = "skipped"
        return state

    to_address = state["company_email"]
    # Subject built from first 1–2 hooks if available
    hooks = state.get("company_details", [])
    subject_bits = ", ".join([h["hook"] for h in hooks[:2]]) if hooks else state["company_name"]
    subject = f"Application – {subject_bits}"
    body = state["cover_note"]

    send_email(to_address, subject, body)
    state["email_status"] = "sent"
    return state
