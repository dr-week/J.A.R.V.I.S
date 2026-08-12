from backend.app.hands.registry import register

def mm_draft_outreach(target_name: str, objective: str) -> dict:
    """
    Drafts an outreach email or message. 
    Because this simulates sending communication, it uses a high risk level.
    """
    # In a full implementation, this would call the LLM to write the email
    # and potentially use an SMTP library to send it.
    
    draft = f"Subject: Exploring Synergies\n\nHi {target_name},\n\nI noticed your recent work and wanted to connect regarding {objective}. Let's chat."
    
    return {
        "status": "success",
        "action_taken": f"Drafted outreach to {target_name}",
        "draft_content": draft
    }

# Register the tool with Jarvis's built-in registry
register(
    {
        "name": "mm_draft_outreach",
        "description": "Drafts and sends personalized outreach messages to leads.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "confirm_always",  # Critical: Requires explicit user approval
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "target_name": {
                    "type": "string",
                    "description": "Name or company of the lead"
                },
                "objective": {
                    "type": "string",
                    "description": "The goal of the outreach (e.g., 'freelance web dev project')"
                }
            },
            "required": ["target_name", "objective"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "action_taken": {"type": "string"},
                "draft_content": {"type": "string"}
            }
        },
        "scopes": [],
        "tags": ["marketing", "money_maker", "communication"],
    },
    mm_draft_outreach,
)
