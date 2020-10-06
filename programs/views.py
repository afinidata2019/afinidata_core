from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView,TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, Http404
from user_sessions.models import Session
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from programs import models, forms
from topics.models import Topic
from areas.models import Area
from posts.models import Post


class ProgramListView(PermissionRequiredMixin, ListView):
    permission_required = 'programs.view_program'
    model = models.Program
    login_url = reverse_lazy('pages:login')
    paginate_by = 10


class ProgramDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'programs.view_program'
    model = models.Program
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'program_id'

    def get_context_data(self, **kwargs):
        c = super(ProgramDetailView, self).get_context_data()
        c['levels'] = self.object.levels.all()[:5]
        return c


class ProgramCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'programs.add_program'
    model = models.Program
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
    model = models.Program
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
    model = models.Program
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
    model = models.Level
    login_url = reverse_lazy('pages:login')
    paginate_by = 10

    def get_queryset(self):
        return models.Program.objects.get(id=self.kwargs['program_id']).levels.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        c = super(LevelListView, self).get_context_data()
        c['program'] = get_object_or_404(models.Program, id=self.kwargs['program_id'])
        return c


class LevelDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'programs.view_level'
    model = models.Level
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'level_id'

    def get_context_data(self, **kwargs):
        c = super(LevelDetailView, self).get_context_data()
        c['program'] = get_object_or_404(models.Program, id=self.kwargs['program_id'])
        return c


class LevelCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'programs.add_level'
    model = models.Level
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description', 'assign_min', 'assign_max')

    def get_context_data(self, **kwargs):
        c = super(LevelCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['program'] = get_object_or_404(models.Program, id=self.kwargs['program_id'])
        return c

    def form_valid(self, form):
        form.instance.program = get_object_or_404(models.Program, id=self.kwargs['program_id'])
        return super(LevelCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Level with name: "%s" has been added.' % self.object.name)
        return reverse_lazy('programs:level_detail', kwargs=dict(level_id=self.object.pk,
                                                                 program_id=self.object.program_id))


class LevelUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'programs.change_level'
    model = models.Level
    login_url = reverse_lazy('pages:login')
    fields = ('name', 'description', 'assign_min', 'assign_max')
    pk_url_kwarg = 'level_id'

    def get_context_data(self, **kwargs):
        c = super(LevelUpdateView, self).get_context_data()
        c['action'] = 'Edit'
        if self.object.program_id != self.kwargs['program_id']:
            raise Http404
        c['program'] = get_object_or_404(models.Program, id=self.kwargs['program_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, 'Level with name: "%s" has been updated.' % self.object.name)
        return reverse_lazy('programs:level_detail', kwargs=dict(level_id=self.object.pk,
                                                                 program_id=self.object.program_id))


class LevelDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'programs.delete_level'
    template_name = 'programs/level_form.html'
    model = models.Level
    login_url = reverse_lazy('pages:login')
    pk_url_kwarg = 'level_id'

    def get_context_data(self, **kwargs):
        c = super(LevelDeleteView, self).get_context_data()
        c['action'] = 'Delete'
        c['delete_message'] = 'Are you sure to delete: "%s" ?' % self.object.name
        if self.object.program_id != self.kwargs['program_id']:
            raise Http404
        c['program'] = get_object_or_404(models.Program, id=self.kwargs['program_id'])
        return c

    def get_success_url(self):
        messages.success(self.request, 'Level with name: "%s" has been deleted.' % self.object.name)
        return reverse_lazy('programs:level_list', kwargs=dict(program_id=self.object.program_id))


class LevelMilestoneCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'programs.add_levelmilestoneassociation'
    model = models.LevelMilestoneAssociation
    fields = ('milestone',)

    def get_context_data(self, **kwargs):
        c = super(LevelMilestoneCreateView, self).get_context_data()
        c['action'] = 'Create'
        c['level'] = models.Level.objects.get(id=self.kwargs['level_id'])
        return c

    def get_form(self, form_class=None):
        form = super(LevelMilestoneCreateView, self).get_form()
        level = models.Level.objects.get(id=self.kwargs['level_id'])
        form.fields['milestone'].queryset = form.fields['milestone'].queryset\
            .filter(value__gte=level.assign_min, value__lte=level.assign_max)\
            .exclude(id__in=[m.pk for m in level.milestones.all()])
        return form

    def form_valid(self, form):
        form.instance.level_id = self.kwargs['level_id']
        return super(LevelMilestoneCreateView, self).form_valid(form)

    def get_success_url(self):
        level = models.Level.objects.get(id=self.kwargs['level_id'])
        messages.success(self.request, "Milestone to level added.")
        return reverse_lazy('programs:level_detail', kwargs=dict(level_id=level.pk, program_id=level.program_id))


class CreateGroupProgramView(PermissionRequiredMixin, CreateView):
    permission_required = 'programs.add_program'
    login_url = reverse_lazy('pages:login')
    model = models.Program
    form_class = forms.GroupProgramForm

    def get_context_data(self, **kwargs):
        c = super(CreateGroupProgramView, self).get_context_data(**kwargs)
        c['action'] = 'Create Group'
        return c

    def get_success_url(self):
        messages.success(self.request, 'Program has been created')
        return reverse_lazy('programs:program_set_areas', kwargs=dict(program_id=self.object.pk))


class ProgramDetailContentView(PermissionRequiredMixin, DetailView):
    permission_required = 'programs.view_program'
    login_url = reverse_lazy('pages:login')
    template_name = 'programs/program_content.html'
    model = models.Program
    pk_url_kwarg = 'program_id'

    def get_context_data(self, **kwargs):
        c = super(ProgramDetailContentView, self).get_context_data(**kwargs)
        c['levels'] = self.object.levels.all()
        c['total'] = 0
        for l in c['levels']:
            l.post_count = self.object.post_set.filter(status='published', min_range__lte=l.assign_max,
                                                       max_range__gte=l.assign_min).count()
            l.post_count += self.object.session_set.filter(min__lte=l.assign_max, max__gte=l.assign_min).count()
            c['total'] += l.post_count
        return c


class ProgramSetAreasView(PermissionRequiredMixin, TemplateView):
    permission_required = 'programs.change_program'
    login_url = reverse_lazy('pages:login')
    template_name = 'programs/program_areas.html'

    def get_context_data(self, **kwargs):
        c = super(ProgramSetAreasView, self).get_context_data(**kwargs)
        c['program'] = models.Program.objects.get(id=self.kwargs['program_id'])
        c['form'] = forms.GroupProgramAreasForm(self.request.POST or None)
        return c

    def post(self, request, *args, **kwargs):
        form = forms.GroupProgramAreasForm(self.request.POST)
        program = models.Program.objects.get(id=self.kwargs['program_id'])
        session_ids = set()
        for key in form.data:
            if key != 'csrfmiddlewaretoken':
                areas = Area.objects.filter(id__in=form.data.getlist(key))
                result = [program.areas.add(a) for a in areas]

        for l in program.levels.all():
            posts = Post.objects.filter(status='published', min_range__lte=l.assign_max, max_range__gte=l.assign_min,
                                        area__in=program.areas.all())
            lp = lambda program: [p.programs.add(program) for p in posts]
            lp(program)

            session_ids.update([s.pk for s in Session.objects.filter(min__lte=l.assign_max, max__gte=l.assign_min,
                                                                     areas__in=program.areas.all())])
            print(session_ids)

        sessions = Session.objects.filter(id__in=session_ids)
        results = [s.programs.add(program) for s in sessions]
        print(results)
        return redirect('programs:program_content_detail', program_id=self.kwargs['program_id'])


class LevelContentView(PermissionRequiredMixin, DetailView):
    permission_required = 'programs.view_level'
    model = models.Level
    pk_url_kwarg = 'level_id'
    login_url = reverse_lazy('pages:login')
    template_name = 'programs/level_content.html'

    def get_context_data(self, **kwargs):
        c = super(LevelContentView, self).get_context_data(**kwargs)
        c['program'] = models.Program.objects.get(id=self.kwargs['program_id'])
        c['topics'] = Topic.objects.all()
        c['total'] = 0
        for t in c['topics']:
            t.areas = [a for a in c['program'].areas.filter(topic_id=t.pk)]
            post_count = set(p.pk for p in Post.objects.filter(min_range__lte=self.object.assign_max,
                                                               programs__in=[c['program']], status='published',
                                                               max_range__gte=self.object.assign_min,
                                                               area__in=[a.pk for a in t.areas]))

            session_count = set(s.pk for s in Session.objects.filter(min__lte=self.object.assign_max,
                                                                     programs__in=[c['program']],
                                                                     max__gte=self.object.assign_min,
                                                                     areas__in=[a.pk for a in t.areas]))
            print(session_count)
            c['total'] += len(post_count) + len(session_count)
            t.session_count = len(session_count)
        return c


class ProgramLevelTopicDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'topics.view_topic'
    model = Topic
    pk_url_kwarg = 'topic_id'
    login_url = reverse_lazy('pages:login')
    template_name = 'programs/topic_detail.html'

    def get_context_data(self, **kwargs):
        c = super(ProgramLevelTopicDetailView, self).get_context_data(**kwargs)
        c['program'] = models.Program.objects.get(id=self.kwargs['program_id'])
        c['level'] = models.Level.objects.get(id=self.kwargs['level_id'])
        c['sessions'] = Session.objects.filter(id__in=set(s.pk for s in
                                                          Session.objects.filter(programs=c['program'],
                                                                                 min__lte=c['level'].assign_max,
                                                                                 max__gte=c['level'].assign_min,
                                                                                 areas__topic=self.object)))
        return c
