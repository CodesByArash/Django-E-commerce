from django.http.response import Http404
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView,UpdateView,DeleteView
from shop.models import Product, Order, OrderDetails, Cart, CartItem
from .models import User
from django.shortcuts import get_object_or_404
from .mixins import FieldMixins,SuperUserMixin
from django.http import Http404
from django.shortcuts import redirect
from django.contrib.auth import authenticate,login
import json
from .forms import SignUpForm
from django.urls import reverse_lazy
from django.http import JsonResponse


class orderListview (LoginRequiredMixin,ListView):
    
    template_name = "registration/home.html"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        else:
            return Order.objects.filter(costumer = self.request.user)

        
@login_required
def orderDetailView(request,order):
    
    order_obj  = get_object_or_404(Order,id = order)
    
    
    qs = OrderDetails.objects.filter(order = order_obj )
    
    for item in qs:
        print(item.Item.image.url)
    return render(request,"registration/detail.html",{'qs': qs})


class ProductCreate(LoginRequiredMixin,FieldMixins,CreateView):
    model    =   Product
    template_name="registration/article-create.html"


class ProductUpdate(LoginRequiredMixin,FieldMixins,UpdateView):
    model    =   Product
    template_name="registration/article-update.html"

@login_required
def productlistview(request):
    if request.user.is_superuser:
        
        qs  = Product.objects.all()
    else:
        raise Http404("مجاز به دسترسی نیستید")
    return render(request,"registration/productlist.html",{'qs': qs})



class ProductDelete(SuperUserMixin,DeleteView):
    model = Product
    success_url=reverse_lazy('account:home')
    template_name='registration/article_confirm_delete.html'



class Profile(UpdateView):
    model    =   User
    fields   =   ['username','email','first_name', 'last_name','zipcode','address','phone','city',]
    template_name="registration/profile.html"
    
    def get_success_url(self):
        # Get the user's PK
        user_pk = self.request.user.pk
        # Construct the success URL with the user's PK as a parameter
        success_url = reverse_lazy("account:profile", kwargs={"pk": user_pk})
        return success_url

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('account:home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})