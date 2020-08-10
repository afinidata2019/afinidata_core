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

    def get_context_data(self, **kwargs):
        c = super(SessionDetailView, self).get_context_data()
        c['fields'] = self.object.field_set.order_by('position')
        return c


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

    def get_context_data(self, **kwargs):
        c = super(SessionUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has updated." % self.object.pk)
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.object.pk))


class SessionDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'user_sessions.delete_session'
    model = models.Session
    pk_url_kwarg = 'session_id'

    def get_success_url(self):
        messages.success(self.request, "the session with ID: %s has deleted." % self.object.pk)
        return reverse_lazy('sessions:session_list')


class FieldCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_field'
    model = models.Field
    fields = ('field_type', )

    def get_context_data(self, **kwargs):
        c = super(FieldCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        return c

    def form_valid(self, form):
        session = models.Session.objects.get(id=self.kwargs['session_id'])
        form.instance.session_id = self.kwargs['session_id']
        form.instance.position = session.field_set.count()
        return super(FieldCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Field added to session.')
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class MessageCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'user_sessions.add_message'
    model = models.Message
    fields = ('text', )

    def form_valid(self, form):
        form.instance.field_id = self.kwargs['field_id']
        return super(MessageCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        c = super(MessageCreateView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, "Message added in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))


class MessageEditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'user_sessions.change_message'
    model = models.Message
    fields = ('text', )
    pk_url_kwarg = 'message_id'

    def get_context_data(self, **kwargs):
        c = super(MessageEditView, self).get_context_data()
        c['session'] = models.Session.objects.get(id=self.kwargs['session_id'])
        c['field'] = models.Field.objects.get(id=self.kwargs['field_id'])
        c['action'] = 'Update'
        return c

    def get_success_url(self):
        messages.success(self.request, "Message changed in field.")
        return reverse_lazy('sessions:session_detail', kwargs=dict(session_id=self.kwargs['session_id']))

