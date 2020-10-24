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
        messages.success(self.request, "Login successfully")
        return super(LoginView, self).get_success_url()


class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('pages:index')

    def dispatch(self, request, *args, **kwargs):
        messages.success(self.request, "Logout successfully")
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
        # TODO: generar token para cambio de constraseña
        # TODO: guardar en base de datos
        # TODO: enviar email
        return super(TemplateView, self).render_to_response(self.get_context_data())

class PasswordResetConfirmView(TemplateView):
    # TODO: comprobar token
    # TODO: mostrar formulario de cambio constraseña
    # TODO: validar nueva contraseña y actualizar en base de datos.
    template_name = 'pages/password_reset_confirm.html'


class PasswordResetCompleteView(TemplateView):
    # TODO: mensaje de confirmacion de contraseña actualizada.
    template_name = 'pages/password_reset_complete.html'

    def post(self, request, *args, **kwargs):
        return super(TemplateView, self).render_to_response(self.get_context_data())
