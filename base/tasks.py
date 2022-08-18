from base.models import User

def is_authenticated(self):
    user_id = self.request.user.id
    valid_user = User.objects.filter(id=user_id, is_active=True)
    
    if not valid_user:
        return ({'error' : 'access deny'}, 403)
    return valid_user.first()

def is_superuser(self):
    user_id = self.request.user.id
    valid_superuser = User.objects.filter(id=user_id, is_active=True, is_superuser=True)
    
    if not valid_superuser:
        return ({'error' : 'access deny'}, 403)
    return valid_superuser.first()