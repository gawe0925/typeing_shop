from sys import maxunicode
from django.db import models

from base.models import User


class MemberManager(models.Manager):
    pass


class Member(User):
    default_address = models.CharField(null=True, blank=True, max_length=1024, verbose_name='Default Shipping Address')
    city = models.CharField(null=True, blank=False, max_length=20, verbose_name='City')
    post_code = models.CharField(null=True, blank=False, max_length=6, verbose_name='Post Code')
    user_image = models.ImageField(upload_to='templates/user_pictures')

    object = MemberManager()

    class Meta:
        verbose_name = 'Member Header'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s' user information" %self.username