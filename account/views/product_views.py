from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from shop.models import Product
from shop.forms import ProductForm

class ProductListView(LoginRequiredMixin, ListView):
    """View for displaying all products."""
    model = Product
    template_name = 'registration/productlist.html'
    context_object_name = 'qs'

    def get_queryset(self):
        """Get all products."""
        return Product.objects.all()

class ProductCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new product."""
    model = Product
    template_name = 'registration/product-create.html'
    form_class = ProductForm
    success_url = reverse_lazy('account:products')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating a product."""
    model = Product
    template_name = 'registration/product-update.html'
    form_class = ProductForm
    success_url = reverse_lazy('account:products')

    def get_object(self, queryset=None):
        """Get product by ID."""
        return get_object_or_404(Product, id=self.kwargs['pk'])

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a product."""
    model = Product
    template_name = 'registration/product_confirm_delete.html'
    success_url = reverse_lazy('account:products')

    def get_object(self, queryset=None):
        """Get product by ID."""
        return get_object_or_404(Product, id=self.kwargs['pk']) 