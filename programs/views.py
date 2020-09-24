from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, Http404
from programs.models import Program, Level, LevelMilestoneAssociation
from django.urls import reverse_lazy
from milestones.models import Milestone
from django.contrib import messages


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

    def get_context_data(self, **kwargs):
        c = super(ProgramDetailView, self).get_context_data()
        c['levels'] = self.object.level_set.all()[:5]
        return c


class ProgramCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'programs.add_program'
    model = Program
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description', 'languages')

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
    fields = ('name', 'description', 'languages')
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


class LevelListView(PermissionRequiredMixin, ListView):
    permission_required = 'programs.view_level'
    model = Level
    login_url = reverse_lazy('pages:login')
    paginate_by = 10

    def get_queryset(self):
        qs = super(LevelListView, self).get_queryset()
        print(qs)
        qs = qs.filter(program_id=self.kwargs['program_id'])
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(LevelListView, self).get_context_data()
        c['program'] = get_object_or_404(Program, id=self.kwargs['program_id'])
        return c


class LevelDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'programs.view_level'
    model = Level
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'level_id'

    def get_context_data(self, **kwargs):
        c = super(LevelDetailView, self).get_context_data()
        if self.object.program_id != self.kwargs['program_id']:
            raise Http404
        c['program'] = get_object_or_404(Program, id=self.kwargs['program_id'])
        return c


class LevelCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'programs.add_level'
    model = Level
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description', 'assign_min', 'assign_max')

    def get_context_data(self, **kwargs):
        c = super(LevelCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['program'] = get_object_or_404(Program, id=self.kwargs['program_id'])
        return c

    def form_valid(self, form):
        form.instance.program = get_object_or_404(Program, id=self.kwargs['program_id'])
        return super(LevelCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Level with name: "%s" has been added.' % self.object.name)
        return reverse_lazy('programs:level_detail', kwargs=dict(level_id=self.object.pk,
                                                                 program_id=self.object.program_id))


class LevelUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'programs.change_level'
    model = Level
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description', 'assign_min', 'assign_max')
    pk_url_kwarg = 'level_id'

    def get_context_data(self, **kwargs):
        c = super(LevelUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        if self.object.program_id != self.kwargs['program_id']:
            raise Http404
        c['program'] = get_object_or_404(Program, id=self.kwargs['program_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, 'Level with name: "%s" has been updated.' % self.object.name)
        return reverse_lazy('programs:level_detail', kwargs=dict(level_id=self.object.pk,
                                                                 program_id=self.object.program_id))


class LevelDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'programs.delete_level'
    template_name = 'programs/level_form.html'
    model = Level
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'level_id'

    def get_context_data(self, **kwargs):
        c = super(LevelDeleteView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete: "%s" ?' % self.object.name
        if self.object.program_id != self.kwargs['program_id']:
            raise Http404
        c['program'] = get_object_or_404(Program, id=self.kwargs['program_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, 'Level with name: "%s" has been deleted.' % self.object.name)
        return reverse_lazy('programs:level_list', kwargs=dict(program_id=self.object.program_id))


class LevelMilestoneCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'programs.add_levelmilestoneassociation'
    model = LevelMilestoneAssociation
    fields = ('milestone',)

    def get_context_data(self, **kwargs):
        c = super(LevelMilestoneCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['level'] = Level.objects.get(id=self.kwargs['level_id'])
        return c

    def get_form(self, form_class=None):
        form = super(LevelMilestoneCreateView, self).get_form()
        level = Level.objects.get(id=self.kwargs['level_id'])
        form.fields['milestone'].queryset = form.fields['milestone'].queryset\
            .filter(value__gte=level.assign_min, value__lte=level.assign_max)\
            .exclude(id__in=[m.pk for m in level.milestones.all()])
        return form

    def form_valid(self, form):
        form.instance.level_id = self.kwargs['level_id']
        return super(LevelMilestoneCreateView, self).form_valid(form)

    def get_success_url(self):
        level = Level.objects.get(id=self.kwargs['level_id'])
        messages.success(self.request, "Milestone to level added.")
        return reverse_lazy('programs:level_detail', kwargs=dict(level_id=level.pk, program_id=level.program_id))
