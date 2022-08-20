from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class BaseModel(models.Model):
    create_date_time = models.DateTimeField(db_column='CREATE_DATE_TIME', unique=False, db_index=True, primary_key=False, choices=None, null=False, blank=False, auto_now_add=True, verbose_name='Create Date Time')
    last_update_date_time = models.DateTimeField(db_column='LAST_UPDATE_DATE_TIME', unique=False, db_index=True, primary_key=False, choices=None, null=False, blank=False, auto_now=True, verbose_name='Last Update Date Time')

    class Meta:
        abstract = True


class ProductBaseModel(BaseModel):
    product_type_name = models.CharField(db_column='TYPE_NAME', unique=False, db_index=True, primary_key=False, default=None, choices=None, null=False, blank=False, max_length=128, verbose_name='Prodcut Type Name')
    is_available = models.BooleanField(db_column='IS_AVAILABLE', unique=False, db_index=True, primary_key=False, default=True, choices=None, null=False, blank=False, verbose_name='Is Available')

    class Meta:
        abstract = True


class OrderBaseModel(BaseModel):
    cancel = models.BooleanField(default=False, null=False, blank=False, verbose_name='Cancel')

    class Meta:
        abstract = True


class ASNBaseModel(BaseModel):
    is_return = models.BooleanField(default=False, null=False, blank=False, verbose_name='Return')
    received = models.BooleanField(default=False, null=False, blank=False, verbose_name='Received')

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def _create_user(self, password, email, **kwargs):
        # if not username:
        #     raise ValueError('Enter your username')
        if not password:
            raise ValueError('Enter your password')
        if not email:
            raise ValueError('Enter your email')
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, password, email, **kwargs):
        kwargs['is_staff'] = True
        kwargs['is_superuser'] = True
        return self._create_user(password, email, **kwargs)

    def create_user(self, password, email, **kwargs):
        kwargs['is_staff'] = False
        kwargs['is_superuser'] = False
        return self._create_user(password, email, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    # username = models.CharField(null=True, blank=True, max_length=20, verbose_name='User Name')
    phone = models.CharField(null=True, blank=False, max_length=10, verbose_name='Phone Number')
    is_staff = models.BooleanField(default=False, verbose_name='Is Staff')
    is_superuser = models.BooleanField(default=False, verbose_name='Is Admin')
    date_joined = models.DateField(auto_now_add=True, verbose_name='Date Joined')
    last_login = models.DateTimeField(auto_now=True, verbose_name='Last Login Time')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = UserManager()

    # use user's email as login account
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'User Table'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.email

    def get_user(self):
        return self.email

    def is_staff(self):
        return self.is_staff

    def is_admin(self):
        return self.is_superuser