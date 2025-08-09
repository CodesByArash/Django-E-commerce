from typing import Optional, List, Tuple
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db import transaction
from .base_repository import BaseRepository
from shop.models import Cart, CartItem, Product, Order, OrderItem

class CartRepository(BaseRepository[Cart]):
    """Repository for Cart and CartItem model database operations."""

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

    def get_active_cart(self, user) -> Optional[Cart]:
        """Get user's active cart or None if it doesn't exist."""
        try:
            return Cart.objects.get(user=user, is_active=True)
        except Cart.DoesNotExist:
            return None

    def get_or_create_cart(self, user) -> Cart:
        """Get user's active cart or create a new one if it doesn't exist."""
        cart, created = Cart.objects.get_or_create(
            user=user,
            is_active=True
        )
        return cart

    def add_item(self, cart: Cart, product: Product, quantity: int) -> Tuple[CartItem, bool]:
        """Add an item to cart."""
        # Lock the product to check quantity
        product = Product.objects.select_for_update().get(id=product.id)
        
        if quantity > product.quantity:
            raise ValueError(f"Insufficient quantity for product: {product.title}")
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item, created

    def update_item_quantity(self, cart: Cart, product_id: int, quantity: int) -> Optional[CartItem]:
        """Update cart item quantity or remove it if quantity is 0."""
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                return cart_item
            else:
                cart_item.delete()
                return None
        except CartItem.DoesNotExist:
            return None

    def remove_item(self, cart: Cart, product_id: int) -> bool:
        """Remove an item from cart."""
        deleted, _ = CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return deleted > 0

    def clear_cart(self, cart: Cart) -> None:
        """Remove all items from cart."""
        cart.items.all().delete()

    def create_order(self, cart: Cart, shipping_address: str) -> Order:
        """Create an order from cart items and clear the cart."""
        with transaction.atomic():
            # Lock the cart to prevent concurrent modifications
            cart = Cart.objects.select_for_update().get(id=cart.id)
            
            # Check if cart is still active and has items
            if not cart.is_active or not cart.items.exists():
                raise ValueError("Cart is empty or inactive")
            
            # Check product quantities before creating order
            for item in cart.items.all():
                product = Product.objects.select_for_update().get(id=item.product.id)
                if product.quantity < item.quantity:
                    raise ValueError(f"Insufficient quantity for product: {product.title}")
            
            # Create order
            order = Order.objects.create(
                user=cart.user,
                total_price=cart.total_price,
                status='processing',
                shipping_address=shipping_address
            )
            
            # Create order items and update product quantities
            for item in cart.items.all():
                product = Product.objects.select_for_update().get(id=item.product.id)
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=item.price
                )
                
                # Update product quantity
                product.quantity -= item.quantity
                product.save()
            
            # Clear cart
            self.clear_cart(cart)
            cart.is_active = False
            cart.save()
            
            return order

    def get_cart_total(self, cart_id: int) -> float:
        try:
            cart = Cart.objects.get(id=cart_id)
            return sum(item.total_price for item in cart.items.all())
        except Cart.DoesNotExist:
            return 0.0