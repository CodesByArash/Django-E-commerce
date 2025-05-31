from typing import Optional, List
from django.core.paginator import Paginator
from .base_repository import BaseRepository
from shop.models import Cart, CartItem, Product

class CartRepository(BaseRepository[Cart]):
    """Repository for Cart model database operations."""

    def get_by_id(self, cart_id: int) -> Optional[Cart]:
        """Get a cart by its ID."""
        try:
            return Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return None

    def get_by_user(self, user_id: int) -> Optional[Cart]:
        """Get active cart by user ID."""
        try:
            return Cart.objects.get(user_id=user_id, is_active=True)
        except Cart.DoesNotExist:
            return None

    def get_all(self, page: int = None, per_page: int = None) -> List[Cart]:
        """Get all carts, optionally paginated."""
        carts = Cart.objects.all()
        if page is not None and per_page is not None:
            paginator = Paginator(carts, per_page)
            return list(paginator.get_page(page))
        return list(carts)

    def create(self, **kwargs) -> Cart:
        """Create a new cart."""
        return Cart.objects.create(**kwargs)

    def update(self, cart_id: int, **kwargs) -> Optional[Cart]:
        """Update an existing cart."""
        try:
            cart = Cart.objects.get(id=cart_id)
            for key, value in kwargs.items():
                setattr(cart, key, value)
            cart.save()
            return cart
        except Cart.DoesNotExist:
            return None

    def delete(self, cart_id: int) -> bool:
        """Delete a cart by its ID."""
        try:
            cart = Cart.objects.get(id=cart_id)
            cart.delete()
            return True
        except Cart.DoesNotExist:
            return False

    def filter(self, **kwargs) -> List[Cart]:
        """Filter carts by given criteria."""
        return list(Cart.objects.filter(**kwargs))

    def get_or_create_cart(self, user_id: int) -> Cart:
        """Get existing active cart for user or create a new one."""
        try:
            cart = Cart.objects.get(user_id=user_id, is_active=True)
            return cart
        except Cart.DoesNotExist:
            # غیرفعال کردن تمام سبدهای خرید قبلی
            Cart.objects.filter(user_id=user_id).update(is_active=False)
            # ایجاد سبد خرید جدید
            return Cart.objects.create(user_id=user_id, is_active=True)

    def add_item(self, cart_id: int, product_id: int, quantity: int = 1) -> Optional[CartItem]:
        """Add an item to the cart."""
        try:
            cart = Cart.objects.get(id=cart_id)
            product = Product.objects.get(id=product_id)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={
                    'quantity': quantity,
                    'price': product.price
                }
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.price = product.price  # بروزرسانی قیمت در صورت تغییر
                cart_item.save()
            
            return cart_item
        except (Cart.DoesNotExist, Product.DoesNotExist):
            return None

    def update_item_quantity(self, cart_id: int, product_id: int, quantity: int) -> Optional[CartItem]:
        """Update the quantity of an item in the cart."""
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            return None

    def remove_item(self, cart_id: int, product_id: int) -> bool:
        """Remove an item from the cart."""
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def clear_cart(self, cart_id: int) -> bool:
        """Remove all items from the cart."""
        try:
            cart = Cart.objects.get(id=cart_id)
            cart.items.all().delete()
            return True
        except Cart.DoesNotExist:
            return False

    def get_cart_total(self, cart_id: int) -> float:
        """Calculate the total price of all items in the cart."""
        try:
            cart = Cart.objects.get(id=cart_id)
            return sum(item.total_price for item in cart.items.all())
        except Cart.DoesNotExist:
            return 0.0 