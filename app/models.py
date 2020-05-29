from django.contrib.auth.hashers import make_password
from instances.models import Instance
from django.db import models


USER_TYPE_CHOICES = (('facebook', 'facebook'), ('google', 'google'), ('custom', 'custom'))
USER_ROLE_CHOICES = (('parent', 'parent'),)


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.TextField(blank=True, null=True)
    type = models.CharField(choices=USER_TYPE_CHOICES, default='custom', max_length=50)
    token = models.CharField(blank=True, unique=True, null=True, max_length=255)
    identifier = models.CharField(blank=True, unique=True, max_length=100)
    beta = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    instances = models.ManyToManyField(Instance, through='UserInstanceAssociation')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.password = make_password(self.password)
        return super(User, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return "%s %s " % (self.first_name, self.last_name)


class UserInstanceAssociation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='parent')
