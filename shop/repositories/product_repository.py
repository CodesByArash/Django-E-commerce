from typing import Optional, List
from django.core.paginator import Paginator
from django.db.models import QuerySet
from .base_repository import BaseRepository
from shop.models import Product, Category

class ProductRepository(BaseRepository[Product]):
    """Repository for Product model database operations."""

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get a product by its ID."""
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def get_all(self, page: int = None, per_page: int = 8) -> List[Product]:
        """Get all products, optionally paginated."""
        products = Product.objects.all()
        if page is not None:
            paginator = Paginator(products, per_page)
            return list(paginator.get_page(page))
        return list(products)

    def create(self, **kwargs) -> Product:
        """Create a new product."""
        return Product.objects.create(**kwargs)

    def update(self, product_id: int, **kwargs) -> Optional[Product]:
        """Update an existing product."""
        try:
            product = Product.objects.get(id=product_id)
            for key, value in kwargs.items():
                setattr(product, key, value)
            product.save()
            return product
        except Product.DoesNotExist:
            return None

    def delete(self, product_id: int) -> bool:
        """Delete a product by its ID."""
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return True
        except Product.DoesNotExist:
            return False

    def filter(self, **kwargs) -> List[Product]:
        """Filter products by given criteria."""
        return list(Product.objects.filter(**kwargs))

    def filter_by_category(self, category: Category, page: int = None, per_page: int = 8) -> List[Product]:
        """Get products filtered by category, optionally paginated."""
        products = Product.objects.filter(category=category)
        if page is not None:
            paginator = Paginator(products, per_page)
            return list(paginator.get_page(page))
        return list(products)

    def search_by_title(self, query: str, page: int = None, per_page: int = 8) -> List[Product]:
        """Search products by title, optionally paginated."""
        products = Product.objects.filter(title__icontains=query)
        if page is not None:
            paginator = Paginator(products, per_page)
            return list(paginator.get_page(page))
        return list(products) 