from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from shop.models import Order, OrderItem

class OrderListView(LoginRequiredMixin, ListView):
    """View for displaying user's orders."""
    template_name = 'shop/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        """Get orders for current user."""
        return Order.objects.filter(costumer=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    """View for displaying order details."""
    template_name = 'shop/order_detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        """Get order by ID for current user."""
        return get_object_or_404(
            Order,
            id=self.kwargs['order'],
            costumer=self.request.user
        )

    def get_context_data(self, **kwargs):
        """Add order details to context."""
        context = super().get_context_data(**kwargs)
        context['order_details'] = OrderDetails.objects.filter(order=self.object)
        return context 