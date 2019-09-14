def check_authenticated_user(user_id):
    from user.models import User
    user = User.objects.get_user(user_id)
    if not user:
        return False
    return True

def check_unique_username(username):
    from user.models import User
    user = User.objects.get_user_by_username(username)
    if not user:
        return True
    return False


def check_unique_email(email):
    from user.models import User
    user = User.objects.get_user_by_email(email)
    if not user:
        return True
    return False
