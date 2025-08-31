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
    You are drafting a professional, concise cover note/email (120–160 words).  
    Audience: the hiring contact {state['recipient_name']} at {state['company_name']}.  

    Inputs:  
    - Company JD highlights/hooks: {state['company_details']}  
    - Applicant profile: {state['applicant_profile']}  

    Rules:  
    - Start with Hi followed with either hiring team or if the name of a person is provided as the reipient name.
    - Open with a hook that ties directly to the company JD (avoid generic phrases).  
    - Use applicant achievements if available; include up to 2 with measurable outcomes (no fabrication).  
    - If no metrics are in profile, emphasize skills relevant to the JD.  
    - Keep tone crisp, confident, and professional (avoid fluff).  
    - Explicitly mention: "I have attached my resume for your review." 
    - End with a clear next step (short call or referral to formal application).  
    - Word count: 120–160. 
    - Output ONLY the body text (no greetings, no “Here is the cover note:”).  
    - Sign off with “Regards, and extract name present in the applicant_profile”.

    =================== Cover Note ========================
    """

    response = llm.invoke(prompt)
    state["cover_note"] = response.strip()
    return state



def draft_subject(state):
    prompt = f"""
    Generate a concise, professional email subject line for a job application.

    Constraints:
    Subject line must start with the word "Application".
    Must include a clear job/role title (either extract from JOB DESCRIPTION or infer/create one based on the description using industry-accepted role names).
    Must include the company name "{state.get('company_name','')}".
    Keep it under 80 characters.
    Avoid generic phrases like "Job", "Request", and avoid repetition.
    Use a formal tone suitable for professional recruitment communication.
    Do not include quotes, markdown, or explanations — return only the subject line.

    JOB DESCRIPTION:
    {state.get('job_description','')}
    """
    response = llm.invoke(prompt).strip()
    # Strip any fences or stray characters
    # subject = re.sub(r"^```.*?\n|\n```$", "", response, flags=re.DOTALL).strip()
    state["email_subject"] = response
    return state


def send_email_node(state):
    print("Sending email...")
    if state.get("approval") != "approved":
        state["email_status"] = "skipped"
        return state

    to_address = state["recipient_email"]
    # ✅ Use subject from draft_subject if available
    subject = state["email_subject"]
    body = state["cover_note"]

    send_email(to_address, subject, body, attachment_path="examples/Gopal_Goyal_Resume.pdf")
    state["email_status"] = "sent"  
    return state