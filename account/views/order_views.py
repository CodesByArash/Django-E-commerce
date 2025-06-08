from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from shop.models import Order, OrderItem
from django.http import Http404
from account.forms import OrderUpdateForm

class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'Account/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
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
        context = super().get_context_data(**kwargs)
        print(f"Debug - Context data: {context}")
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'Account/order_detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        order = get_object_or_404(Order, id=self.kwargs['order'])
        if not self.request.user.is_staff and order.user != self.request.user:
            raise Http404("Order not found")
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_details'] = OrderItem.objects.filter(order=self.object)
        return context

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = 'Account/order_update.html'
    success_url = reverse_lazy('account:orders')

    def get_object(self, queryset=None):
        order = get_object_or_404(Order, id=self.kwargs['pk'])
        if not self.request.user.is_staff:
            raise Http404("دسترسی ندارید")
        return order

    def form_valid(self, form):
        messages.success(self.request, 'سفارش با موفقیت بروزرسانی شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'خطا در بروزرسانی سفارش. لطفاً دوباره تلاش کنید.')
        return super().form_invalid(form)