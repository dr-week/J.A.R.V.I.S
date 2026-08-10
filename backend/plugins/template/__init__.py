from backend.app.hands import registry


def _say_hello(name: str = "world") -> str:
    return f"Hello, {name}! This is a custom plugin."

registry.register(
    {
        "name": "plugin_hello_world",
        "description": "A template plugin tool.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet"}
            },
            "required": [],
        },
        "returns": {
            "type": "object",
            "properties": {"result": {"type": "string"}}
        },
        "scopes": [],
        "tags": ["plugin", "demo"],
    },
    _say_hello,
)
