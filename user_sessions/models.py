from django.db import models
import uuid


class Session(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_session = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)


class Field(models.Model):
    position = models.IntegerField()
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    field_type = models.CharField(max_length=50, choices=(('text', 'Text'), ('quick_replies', 'Quick Replies'),
                                           ('save_values_block', 'Save Values Block')))

