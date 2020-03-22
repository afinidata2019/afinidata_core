from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=2, unique=True)
    description = models.TextField()
    available = models.BooleanField(default=True, blank=True)
    redirect = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LanguageCode(models.Model):
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    code = models.CharField(max_length=5)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
