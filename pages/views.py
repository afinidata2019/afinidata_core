from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/dashboard.html'
    login_url = reverse_lazy('pages:login')

