from colorfield.fields import ColorField
from topics.models import Topic
from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    background_color = ColorField(default='#ff0000', null=True, blank=True)
    point_color = ColorField(default='#ff0000', null=True, blank=True)
    another_color = ColorField(default='#ff0000', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_all_areas', 'User can view all areas.'),
        )
