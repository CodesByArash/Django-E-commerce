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

    def get_root_categories(self) -> List[Category]:
        """Get only root categories (categories without parent)."""
        return list(Category.objects.filter(parent__isnull=True, status=True))

    def get_children(self, parent_id: int) -> List[Category]:
        """Get direct children of a category."""
        return list(Category.objects.filter(parent_id=parent_id, status=True))

    def get_all_children_recursive(self, parent_id: int) -> List[Category]:
        """Get all children of a category recursively."""
        try:
            parent = Category.objects.get(id=parent_id)
            return parent.get_all_children()
        except Category.DoesNotExist:
            return []

    def get_category_tree(self) -> List[Category]:
        """Get categories organized in a tree structure (only root categories with prefetched children)."""
        return list(Category.objects.filter(parent__isnull=True, status=True).prefetch_related('children'))

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