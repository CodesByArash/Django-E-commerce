from django.views.generic import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from typing import Any, Dict
from ..repositories import UserRepository
from ..forms import UserRegistrationForm, UserUpdateForm, PasswordChangeForm

class RegisterView(CreateView):
    """View for user registration."""
    form_class = UserRegistrationForm
    template_name = 'shop/register.html'
    success_url = reverse_lazy('shop:index')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_repository = UserRepository()

    def form_valid(self, form):
        """Handle valid form submission."""
        user = self.user_repository.create(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            first_name=form.cleaned_data.get('first_name', ''),
            last_name=form.cleaned_data.get('last_name', '')
        )
        login(self.request, user)
        messages.success(self.request, 'Registration successful!')
        return super().form_valid(form)

class LoginView(FormView):
    """View for user login."""
    template_name = 'shop/login.html'
    success_url = reverse_lazy('shop:index')
    form_class = None  # Using Django's built-in AuthenticationForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_repository = UserRepository()

    def form_valid(self, form):
        """Handle valid form submission."""
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = self.user_repository.authenticate(username, password)
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Login successful!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid username or password.')
            return self.form_invalid(form)

class LogoutView(LoginRequiredMixin, FormView):
    """View for user logout."""
    template_name = 'shop/logout.html'
    success_url = reverse_lazy('shop:index')

    def post(self, request, *args, **kwargs):
        """Handle POST request for logout."""
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect(self.success_url)

class ProfileView(LoginRequiredMixin, UpdateView):
    """View for user profile management."""
    template_name = 'shop/profile.html'
    success_url = reverse_lazy('account:profile')
    form_class = UserUpdateForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_repository = UserRepository()

    def get_object(self, queryset=None):
        """Get the current user."""
        return self.request.user

    def form_valid(self, form):
        """Handle valid form submission."""
        user = self.user_repository.update(
            self.request.user.id,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email']
        )
        if user:
            messages.success(self.request, 'Profile updated successfully!')
        else:
            messages.error(self.request, 'Failed to update profile.')
        return super().form_valid(form)

class ChangePasswordView(LoginRequiredMixin, FormView):
    """View for changing user password."""
    template_name = 'shop/change_password.html'
    success_url = reverse_lazy('account:profile')
    form_class = PasswordChangeForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_repository = UserRepository()

    def form_valid(self, form):
        """Handle valid form submission."""
        if self.user_repository.change_password(
            self.request.user.id,
            form.cleaned_data['new_password1']
        ):
            messages.success(self.request, 'Password changed successfully!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Failed to change password.')
            return self.form_invalid(form) 