from app.entity.User import User

class UserService:
    def __init__(self, session):
        self.session = session
    