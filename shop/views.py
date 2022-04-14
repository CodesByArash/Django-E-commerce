from django.core import paginator
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import OrderDetails, Product,Order,Category
import json
from django.shortcuts  import get_object_or_404
from django.core.paginator import Paginator

# Create your views here.



def index(request):


    product_obj     = Product.objects.all()

    item_name       = request.GET.get('item_name')
    
    if item_name   != '' and item_name is not None:
        product_obj = Product.objects.filter(title__icontains=item_name)

    paginator       = Paginator(product_obj,8)
    page            = request.GET.get('page')
    product_obj     = paginator.get_page(page)

    return render(request,'shop/index.html',{'product_obj':product_obj,'category':Category.objects.all()})
    

def detail(request,id):
    product_obj     = Product.objects.get(id=id)


    return render(request,'shop/detail.html',{'product_obj':product_obj})

@login_required
def checkout(request):

    if request.method == "POST" :
        items = request.POST.get('items','')
        total = request.POST.get('total','')
        

        itemjson=json.loads(items)
        costumer  = request.user
        order = Order(items=items ,total=total,status='p', costumer=costumer)
        order.save()
        for key in itemjson:
            key = key
            quantity = itemjson[key][0]
            name     = itemjson[key][1]
            price    = itemjson[key][2]
            product=get_object_or_404(Product , id=key)
            orderDetails = OrderDetails(order = order , Item = product , price=price , quantity=quantity)
            orderDetails.save()
        return render(request,'shop/success.html')


    return render(request,'shop/checkout.html')


def success(request):

    return render(request,"shop/success.html")


def category(request,slug):
    context={
        "category":get_object_or_404(Category,slug=slug , status=True)
    }
    product = Product.objects.filter(category)

    return render(request, "shop/category.html")