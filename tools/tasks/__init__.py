from backend.app.hands.registry import register

def tasks_ping() -> str:
    return "Tasks plugin is loaded and responding."

register(
    {
        "name": "tasks_ping",
        "description": "A stub tool to verify the tasks plugin is registered and working.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "returns": {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        },
        "scopes": [],
        "tags": ["tasks", "test"],
    },
    tasks_ping,
)
