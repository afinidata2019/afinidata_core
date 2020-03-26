from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from programs.models import Program


class ProgramListView(PermissionRequiredMixin, ListView):
    permission_required = 'programs.view_program'
    model = Program
    login_url = reverse_lazy('pages:login')
    paginate_by = 10


class ProgramDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'programs.view_program'
    model = Program
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'program_id'


class ProgramCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'programs.add_program'
    model = Program
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description')

    def get_context_data(self, **kwargs):
        c = super(ProgramCreateView, self).get_context_data()
        c['action'] = 'Create'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Program with name: "%s" has been added.' % self.object.name)
        return reverse_lazy('programs:program_detail', kwargs=dict(program_id=self.object.pk))


class ProgramUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'programs.change_program'
    model = Program
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description')
    pk_url_kwarg = 'program_id'

    def get_context_data(self, **kwargs):
        c = super(ProgramUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Program with name: "%s" has been updated.' % self.object.name)
        return reverse_lazy('programs:program_detail', kwargs=dict(program_id=self.object.pk))


class ProgramDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'programs.change_program'
    model = Program
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'program_id'
    template_name = 'programs/program_form.html'

    def get_context_data(self, **kwargs):
        c = super(ProgramDeleteView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete program with name: "%s"?' % self.object.name
        return c

    def get_success_url(self):
        messages.success(self.request, 'Program with name: "%s" has been deleted.' % self.object.name)
        return reverse_lazy('programs:program_list')
