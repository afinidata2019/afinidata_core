from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from groups import models


class CreateCodeView(PermissionRequiredMixin, CreateView):
    model = models.Code
    fields = ('code', 'available')
    permission_required = 'groups.add_code'

    def get_context_data(self, **kwargs):
        c = super(CreateCodeView, self).get_context_data()
        c['action'] = 'Crear'
        c['group'] = get_object_or_404(models.Group, id=self.kwargs['group_id'])
        return c

    def form_valid(self, form):
        form.instance.group = get_object_or_404(models.Group, id=self.kwargs['group_id'])
        return super(CreateCodeView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Código: "%s" ha sido añadido al grupo: "%s".' % (
            self.object.code, self.object.group.name
        ))
        return reverse_lazy('groups:group', kwargs={'group_id': self.object.group.pk})
