class Parser:
    def user_profile(self, user):
        return {
            "name": user.name,
            "username": user.username,
            "email": user.email
        }
