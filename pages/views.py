from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from groups.models import RoleGroupUser
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone


class HomeView(RedirectView):
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse_lazy('pages:login')

        return reverse_lazy('pages:dashboard')


class LoginView(AuthLoginView):
    template_name = 'pages/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, "Se inició sesión correctamente")
        return super(LoginView, self).get_success_url()


class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('pages:index')

    def dispatch(self, request, *args, **kwargs):
        messages.success(self.request, "Se finalizó sesión correctamente")
        return super(LogoutView, self).dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, RedirectView):
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        roles = RoleGroupUser.objects.filter(user_id=self.request.user.pk)
        if self.request.user.is_superuser:
            return reverse_lazy('groups:groups')
        if roles.count() == 1:
            return reverse_lazy('groups:group_dashboard', kwargs=dict(group_id=roles.first().group_id))
        return reverse_lazy('groups:my_groups')


class PasswordResetView(TemplateView):
    template_name = 'pages/password_reset.html'

class PasswordResetDoneView(TemplateView):
    template_name = 'pages/password_reset_done.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        print(context)
        return super(TemplateView, self).render_to_response(context)

class PasswordResetConfirmView(TemplateView):
    template_name = 'pages/password_reset_confirm.html'

class PasswordResetCompleteView(TemplateView):
    template_name = 'pages/password_reset_complete.html'
