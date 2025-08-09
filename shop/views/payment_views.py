import logging
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from django.http import HttpResponse, Http404
from shop.models import Cart, Order, OrderItem
from shop.models import Payment
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from shop.repositories import CartRepository

def go_to_gateway_view(request):

    # خواندن مبلغ از هر جایی که مد نظر است
    cart_repository = CartRepository()
    cart = cart_repository.get_active_cart(request.user)
    total_price = cart.total_price
    
    factory = bankfactories.BankFactory()
    try:
        bank = (factory.auto_create()) # or factory.create(bank_models.BankType.BMI) or set identifier
        bank.set_request(request)
        bank.set_amount(total_price)
        # یو آر ال بازگشت به نرم افزار برای ادامه فرآیند
        bank.set_client_callback_url(reverse("call-back-gateway"))
        # در صورت تمایل اتصال این رکورد به رکورد فاکتور یا هر چیزی که بعدا بتوانید ارتباط بین محصول یا خدمات را با این
        # پرداخت برقرار کنید.
        print("3")

        bank_record = bank.ready()
        print("3")
        # هدایت کاربر به درگاه بانک
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        print(e)
        # TODO: redirect to failed page.
        # cart_repository.clear_cart(cart)
        messages.error(request, 'خطای سیستمی در هدایت به درگاه بانکی...')
        return redirect('shop:checkout')
        raise e

def callback_gateway_view(request):

    current_user = request.user
    cart_repository = CartRepository()  
    cart = cart_repository.get_active_cart(request.user)


    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404
    
    print('bank_record', bank_record.__dict__)


    # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
    if bank_record.is_success:
        shipping_address = request.session.pop('shipping_address', '')
        if not shipping_address:
            messages.error(request, 'لطفا آدرس ارسال را وارد کنید.')
            return redirect('shop:checkout')
        
        new_payment = Payment()
        new_payment.user = current_user
        new_payment.payment_number = bank_record.tracking_code
        new_payment.payment_method = bank_record.bank_type
        new_payment.amount_paid = bank_record.amount
        new_payment.status = bank_record.status
        new_payment.save()
        # پرداخت با موفقیت انجام پذیرفته است و بانک تایید کرده است.
        # می توانید کاربر را به صفحه نتیجه هدایت کنید یا نتیجه را نمایش دهید.
        try:
            order = cart_repository.create_order(cart, shipping_address)
            order.payment = new_payment
            order.save()
            messages.success(request, 'سفارش شما با موفقیت ثبت شد.')
            cart_repository.clear_cart(cart)
            return redirect('shop:success')
        except Exception as e:
            cart_repository.clear_cart(cart)
            messages.error(request, 'خطای سیستمی در ثبت سفارش. با پشتیبانی تماس گیرید..')
            return redirect('shop:failure')
    else:
        cart_repository.clear_cart(cart)
        messages.error(request, 'پرداخت با شکست مواجه شد. اگر مبلغ کسر شده است، ظرف ۴۸ ساعت بازخواهد گشت.')
        return redirect('shop:failure')
