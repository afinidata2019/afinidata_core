from django.db import models
from django.contrib.auth.hashers import make_password


USER_TYPE_CHOICES = (('facebook', 'facebook'), ('google', 'google'), ('custom', 'custom'))


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.TextField(blank=True, null=True)
    type = models.CharField(choices=USER_TYPE_CHOICES, default='custom', max_length=50)
    token = models.CharField(blank=True, unique=True, null=True, max_length=255)
    identifier = models.CharField(blank=True, unique=True, max_length=100)
    beta = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.password = make_password(self.password)
        return super(User, self).save(force_insert, force_update, using, update_fields)
