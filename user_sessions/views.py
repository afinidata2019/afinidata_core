from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from user_sessions import models


class SessionListView(PermissionRequiredMixin, ListView):
    permission_required = 'user_sessions.view_session'
    model = models.Session
    paginate_by = 30


class SessionDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'user_sessions.view_session'
    model = models.Session
    pk_url_kwarg = 'session_id'


class SessionCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_session'
    model = models.Session
    fields = ('name', 'parent_session')

    def get_context_data(self, **kwargs):
        c = super(SessionCreateView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has created." % self.object.pk)
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.object.pk))


class SessionUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_session'
    model = models.Session
    fields = ('name', 'parent_session')
    pk_url_kwarg = 'session_id'


class SessionDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_session'
    model = models.Session
    pk_url_kwarg = 'session_id'
