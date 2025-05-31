from typing import Optional, List
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from ..models import User

class UserRepository:
    """Repository for User model database operations."""

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by their ID."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_all(self, page: int = None, per_page: int = None) -> List[User]:
        """Get all users, optionally paginated."""
        users = User.objects.all()
        if page is not None and per_page is not None:
            paginator = Paginator(users, per_page)
            return list(paginator.get_page(page))
        return list(users)

    def create(self, **kwargs) -> User:
        """Create a new user."""
        return User.objects.create_user(**kwargs)

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update an existing user."""
        try:
            user = User.objects.get(id=user_id)
            for key, value in kwargs.items():
                if key == 'password':
                    user.set_password(value)
                else:
                    setattr(user, key, value)
            user.save()
            return user
        except User.DoesNotExist:
            return None

    def delete(self, user_id: int) -> bool:
        """Delete a user by their ID."""
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return True
        except User.DoesNotExist:
            return False

    def filter(self, **kwargs) -> List[User]:
        """Filter users by given criteria."""
        return list(User.objects.filter(**kwargs))

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        return authenticate(username=username, password=password)

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change a user's password."""
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            return True
        except User.DoesNotExist:
            return False 