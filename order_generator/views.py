from django.shortcuts import render, redirect
from .models import Order, Product, OrderProduct, SkuInformation
from django.db.models import Q
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

def home(request):
    return render(request, "order_generator/home.html")

def create_order(request):
    if request.method == 'POST':
        order_number = request.POST.get("order_number")
        tape_of_delivery = request.POST.get('tape_of_delivery')
        Order.objects.create(nr_order = order_number ,tape_of_delivery=tape_of_delivery)
        return redirect('order_generator:add_product', order_nr=order_number)

    return render(request, 'order_generator/create_order.html')

def add_product(request, order_nr):
    order = Order.objects.filter(nr_order=order_nr).latest('creation_date')

    if request.method == 'POST':
        sku_or_ean = request.POST.get('sku')
        quantity = request.POST.get('quantity')
        quantity_not_damaged = request.POST.get('quantity_not_damaged')
        quantity_damage = int(quantity) - int(quantity_not_damaged)

        if sku_or_ean and quantity:
            sku = SkuInformation.objects.filter(
                Q(sku__exact=sku_or_ean)|
                Q(barcode__code__icontains=sku_or_ean)
            ).last()
            product = Product.objects.create(
                sku=sku,
                quantity=quantity,
                quantity_not_damaged=quantity_not_damaged,
                quantity_damage=quantity_damage,
            )

            OrderProduct.objects.create(order=order, product=product)

    return render(request, 'order_generator/add_product.html', {'order': order})


def get_product_name(request):
    if request.method == 'POST':
        sku_or_ean = request.POST.get('sku')
        try:
            sku_info = SkuInformation.objects.filter(
                Q(sku__exact=sku_or_ean) |
                Q(barcode__code__icontains=sku_or_ean)
            ).last()
            if sku_info:
                product_name = sku_info.name_of_product
                return JsonResponse({'product_name': product_name})
            return JsonResponse({"product_name": "Not found"})
        except ObjectDoesNotExist:
            return JsonResponse({"product_name": "Not found"})

