class BaseSkill:
    """Base class for all Jarvis skills to ensure standard execution."""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self, *args, **kwargs):
        """Must be implemented by subclasses."""
        raise NotImplementedError("Skill must implement the execute method.")

    def log_action(self, action):
        """Standardized logging for all skills."""
        print(f"[{self.name.upper()}] {action}")
