from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
