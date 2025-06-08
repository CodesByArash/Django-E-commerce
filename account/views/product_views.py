from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from shop.models import Product
from shop.forms import ProductForm

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'Account/productlist.html'
    context_object_name = 'qs'

    def get_queryset(self):
        return Product.objects.all()

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'Account/product-create.html'
    form_class = ProductForm
    success_url = reverse_lazy('account:products')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'Account/product-update.html'
    form_class = ProductForm
    success_url = reverse_lazy('account:products')

    def get_object(self, queryset=None):
        return get_object_or_404(Product, id=self.kwargs['pk'])

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'Account/product_confirm_delete.html'
    success_url = reverse_lazy('account:products')

    def get_object(self, queryset=None):
        return get_object_or_404(Product, id=self.kwargs['pk']) 