from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from account.forms import UserRegistrationForm, UserUpdateForm

class RegisterView(CreateView):
    template_name = 'Account/signup.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('account:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        return response

class CustomLoginView(LoginView):
    template_name = 'Account/login.html'
    success_url = reverse_lazy('shop:index')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('shop:index')
    http_method_names = ['get', 'post']

class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'Account/profile.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('account:profile')

    def get_object(self, queryset=None):
        return self.request.user 