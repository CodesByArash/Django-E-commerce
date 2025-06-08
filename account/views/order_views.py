from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from shop.models import Order, OrderItem
from django.http import Http404
from account.forms import OrderUpdateForm

class OrderListView(LoginRequiredMixin, ListView):
    """View for displaying user's orders."""
    template_name = 'Account/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        """Get orders for current user or all orders for staff."""
        if self.request.user.is_staff:
            queryset = Order.objects.all()
            print(f"Debug - Staff user {self.request.user.email} - Total orders: {queryset.count()}")
            for order in queryset:
                print(f"Debug - Order ID: {order.id}, User: {order.user.email}, Status: {order.status}")
        else:
            queryset = Order.objects.filter(user=self.request.user)
            print(f"Debug - Regular user {self.request.user.email} - Total orders: {queryset.count()}")
            for order in queryset:
                print(f"Debug - Order ID: {order.id}, Status: {order.status}")
        return queryset

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        print(f"Debug - Context data: {context}")
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    """View for displaying order details."""
    template_name = 'Account/order_detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        """Get order by ID for current user or staff."""
        order = get_object_or_404(Order, id=self.kwargs['order'])
        if not self.request.user.is_staff and order.user != self.request.user:
            raise Http404("Order not found")
        return order

    def get_context_data(self, **kwargs):
        """Add order details to context."""
        context = super().get_context_data(**kwargs)
        context['order_details'] = OrderItem.objects.filter(order=self.object)
        return context

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating order status and tracking code."""
    model = Order
    form_class = OrderUpdateForm
    template_name = 'Account/order_update.html'
    success_url = reverse_lazy('account:orders')

    def get_object(self, queryset=None):
        """Get order by ID and check staff permission."""
        order = get_object_or_404(Order, id=self.kwargs['pk'])
        if not self.request.user.is_staff:
            raise Http404("Permission denied")
        return order

    def form_valid(self, form):
        """Handle successful form submission."""
        messages.success(self.request, 'سفارش با موفقیت بروزرسانی شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form submission."""
        messages.error(self.request, 'خطا در بروزرسانی سفارش. لطفاً دوباره تلاش کنید.')
        return super().form_invalid(form)