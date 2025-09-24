
class AuthRepository:
    def __init__(self, users: list):
        self.users = users
        self.current_user = None

    def login(self, pseudo: str, password: str) -> bool:
        for user in self.users:
            if user.pseudo == pseudo and user.password == password:
                self.current_user = user
                return True
        return False
    
    def logout(self):
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def authorize(self, required_role: str) -> bool:
        return self.is_authenticated() and self.current_user.role == required_role