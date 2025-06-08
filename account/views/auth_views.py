from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from account.forms import UserRegistrationForm, UserUpdateForm

class RegisterView(CreateView):
    """View for user registration."""
    template_name = 'Account/signup.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('account:profile')

    def form_valid(self, form):
        """Save user and authenticate."""
        response = super().form_valid(form)
        form.save()
        return response

class CustomLoginView(LoginView):
    """View for user login."""
    template_name = 'Account/login.html'
    success_url = reverse_lazy('shop:index')

class CustomLogoutView(LogoutView):
    """View for user logout."""
    next_page = reverse_lazy('shop:index')
    http_method_names = ['get', 'post']  # Allow both GET and POST methods

class ProfileView(LoginRequiredMixin, UpdateView):
    """View for user profile."""
    template_name = 'Account/profile.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('account:profile')

    def get_object(self, queryset=None):
        """Get profile for current user."""
        return self.request.user 