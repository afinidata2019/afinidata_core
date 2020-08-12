from programs.models import Level
from django.db import models
import uuid


class Session(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_session = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    value = models.IntegerField(verbose_name='Months')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class Field(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    position = models.IntegerField()
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    field_type = models.CharField(max_length=50, choices=(('text', 'Text'), ('quick_replies', 'Quick Replies'),
                                           ('save_values_block', 'Save Values Block')))

    def __str__(self):
        return "%s" % self.identifier


class Message(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Reply(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    label = models.CharField(max_length=30)
    attribute = models.CharField(max_length=30, null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    redirect_block = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label


class RedirectBlock(models.Model):
    field = models.OneToOneField(Field, on_delete=models.CASCADE)
    block = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.block
