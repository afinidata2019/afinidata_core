from django.contrib import admin
from languages.models import Language, LanguageCode


admin.site.register(Language)
admin.site.register(LanguageCode)
