from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from languages.models import Language, LanguageCode
from django.urls import reverse_lazy
from django.contrib import messages


