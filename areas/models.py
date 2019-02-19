from django.db import models


class Area(models.Model):

    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'areas'

    def __str__(self):
        return self.name
