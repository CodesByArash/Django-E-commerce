from typing import Optional, List
from django.core.paginator import Paginator
from .base_repository import BaseRepository
from shop.models import Category

class CategoryRepository(BaseRepository[Category]):
    """Repository for Category model database operations."""

    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get a category by its ID."""
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return None

    def get_all(self, page: int = None, per_page: int = None) -> List[Category]:
        """Get all categories, optionally paginated."""
        categories = Category.objects.all()
        if page is not None and per_page is not None:
            paginator = Paginator(categories, per_page)
            return list(paginator.get_page(page))
        return list(categories)

    def create(self, **kwargs) -> Category:
        """Create a new category."""
        return Category.objects.create(**kwargs)

    def update(self, category_id: int, **kwargs) -> Optional[Category]:
        """Update an existing category."""
        try:
            category = Category.objects.get(id=category_id)
            for key, value in kwargs.items():
                setattr(category, key, value)
            category.save()
            return category
        except Category.DoesNotExist:
            return None

    def delete(self, category_id: int) -> bool:
        """Delete a category by its ID."""
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return True
        except Category.DoesNotExist:
            return False

    def filter(self, **kwargs) -> List[Category]:
        """Filter categories by given criteria."""
        return list(Category.objects.filter(**kwargs))

    def get_with_products(self, category_id: int) -> Optional[Category]:
        """Get a category with its related products."""
        try:
            return Category.objects.prefetch_related('products').get(id=category_id)
        except Category.DoesNotExist:
            return None 