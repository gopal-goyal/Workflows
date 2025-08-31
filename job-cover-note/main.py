from graph import build_graph
from state import ApplicantDetails, CompanyDetails, State

if __name__ == "__main__":
    # ---- User Inputs ----
    applicant_details: ApplicantDetails = {
        "name": "chef",
        "summary": (
            "ML/AI developer with 2+ years across LLMs, RAG, and AWS; "
            "built YOLOv8 analytics (~95% accuracy, <500ms latency) and "
            "document AI (~98% accuracy, 80% manual time reduction)."
        ),
        "top_skills": ["LLMs", "RAG", "LangGraph", "AWS", "Python", "Context Engineering", "Agentic Workflows"],
        "email": "chef@gmail.com",
        "phone": "+91-9494949494",
    }

    company_details: CompanyDetails = {
        "name": "x",
        "location": "y",   # optional; adjust if unknown
        "industry": "z",
        "size": "3",                                # optional
        "website": "alpha.com",                             # optional
        "recipient_name": "scrapper",
        "recipient_email": "scrapper@gmail.com",
        "jd": open("examples/mkp.txt").read(),
    }

    # ---- Build Graph ----
    graph = build_graph()

    # ---- Initial State (matches your new State) ----
    init_state: State = {
        "company_details": company_details,
        "applicant_details": applicant_details,
        "company_details_enhanced": [],
        "cover_note": "",
        "email_subject": "",
        "email_status": "pending",
        "approval": "pending",
    }

    # Stable thread id so the checkpointer can find this run
    config = {"configurable": {"thread_id": "kc-application-001"}}

    print("🚀 Starting workflow…\n")

    # Stream the graph; each event is the full state snapshot
    for state_snapshot in graph.stream(init_state, config=config, stream_mode="values"):
        print("📢 Current state keys:", list(state_snapshot.keys()), flush=True)

        if state_snapshot.get("company_details_enhanced"):
            print("   Extracted hooks:", state_snapshot["company_details_enhanced"])

        if state_snapshot.get("cover_note"):
            print("   Draft cover note:\n", state_snapshot["cover_note"])

        if state_snapshot.get("email_subject"):
            print("   Draft subject:", state_snapshot["email_subject"])

    # Approval step
    approve = input("\n⏸  Send email? Type 'y' to approve, anything else to skip: ").strip().lower() == "y"

    # Write the approval into the checkpointed state
    graph.update_state(config, {"approval": "approved" if approve else "revise"})

    # Resume (no new inputs)
    final: State = graph.invoke(None, config=config, resume=True)

    print("\n=================== Cover Note ========================")
    print(final.get("cover_note", ""))
    print("\n=================== Email Subject =====================")
    print(final.get("email_subject", ""))
    print("\n=================== Email Status ======================")
    print(final.get("email_status", ""))