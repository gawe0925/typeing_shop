from members.models import User

def valid_member(members):
    new_users = []
    for member in members:
        try:
            email = member['email']
        except:
            return ({'error':'none data'}, 400)
        try:
            password = member['password']
        except:
            return ({'error':'none data'}, 400)
        
        exist_user = User.objects.filter(email=email)

        if exist_user:
            return ({'error':'account already exist'}, 400)

        try:
            staff = member['is_staff']
        except:
            staff = False
        
        try:
            superuser = member['is_superuser']
        except:
            superuser = False

        new_users.append(User(email=email, 
                            password=password,
                            # is_staff=staff,
                            is_superuser=superuser,
                            is_active=True))
    
    new_user_obj = User.objects.bulk_create(new_users)

    if not new_user_obj:
        return False
    return True