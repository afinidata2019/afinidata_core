from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from topics import models


class TopicListView(PermissionRequiredMixin, ListView):
    permission_required = 'topics.view_topic'
    model = models.Topic
    paginate_by = 10
    login_url = reverse_lazy('pages:login')


class TopicDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'topics.view_topic'
    model = models.Topic
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'topic_id'

