from .models import Cart, Category

def active_cart(request):
    """Context processor to provide the active cart to all templates."""
    if request.user.is_authenticated:
        try:
            active_cart = Cart.objects.get(user=request.user, is_active=True)
            return {'active_cart': active_cart}
        except Cart.DoesNotExist:
            return {'active_cart': None}
    return {'active_cart': None}

def categories_tree(request):
    """Context processor to provide nested categories to all templates."""
    categories = Category.objects.filter(parent__isnull=True, status=True).prefetch_related('children')
    return {'categories_tree': categories} 