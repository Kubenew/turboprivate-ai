class RBACManager:
    def __init__(self):
        self.roles: dict[str, list[str]] = {
            "admin": ["*"],
            "operator": ["inference:run", "models:list", "safety:view"],
            "viewer": ["inference:run"],
        }

    def check_permission(self, role: str, action: str) -> bool:
        permissions = self.roles.get(role, [])
        return "*" in permissions or action in permissions
