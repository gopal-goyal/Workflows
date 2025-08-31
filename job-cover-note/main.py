from graph import build_graph
from nodes import send_email_node

if __name__ == "__main__":
    # User Input
    jd = open("examples/kimberly-clark.txt").read()
    company_name = "Kimberly-Clark"
    recipient_email = "goyal11.gopal@gmail.com"
    recipient_name = "Gopal"
    applicant_profile = {
        "summary": "ML/AI developer with 2+ years across LLMs, RAG, and AWS; "
                   "built YOLOv8 analytics (~95% accuracy, <500ms latency) and "
                   "document AI (~98% accuracy, 80% manual time reduction).",
        "top_skills": ["LLMs", "RAG", "LangGraph", "AWS", "Python"],
        "name": "Raju"
    }

    graph = build_graph()

    init_state = {
        "job_description": jd,
        "company_name": company_name,
        "recipient_email": recipient_email,
        "recipient_name": recipient_name,
        "applicant_profile": applicant_profile,
        "company_details": [],
        "cover_note": "",
        "email_status": "pending",
        "approval": "pending",
    }

    # ✅ stable thread id so the checkpointer can find this run
    config = {"configurable": {"thread_id": "kc-application-001"}}

    print("🚀 Starting workflow…\n")

    last_state = None

    # Now every "event" is just the full state at this step
    for state_snapshot in graph.stream(init_state, config=config, stream_mode="values"):
        last_state = state_snapshot
        print("📢 Current state keys:", list(state_snapshot.keys()), flush=True)

        # You can log specific fields if present
        if state_snapshot.get("company_details"):
            print("   Company details:", state_snapshot["company_details"])
        if state_snapshot.get("cover_note"):
            print("   Draft cover note:\n", state_snapshot["cover_note"])

    # Approval step
    approve = input("\n⏸  Send email? Type 'y' to approve, anything else to skip: ").strip().lower() == "y"

    # 1) Write your delta into the checkpointed state
    graph.update_state(config, {"approval": "approved" if approve else "revise"})

    # 2) Resume (no additional input needed)
    final = graph.invoke(None, config=config, resume=True)

    print("\n=================== Cover Note ========================")
    print(final.get("cover_note", ""))
    print("\n=================== Email Status ======================")
    print(final.get("email_status", ""))