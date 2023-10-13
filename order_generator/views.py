from django.shortcuts import render, redirect
from .models import Order, Product, OrderProduct, SkuInformation, Barcode
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.core.exceptions import ObjectDoesNotExist
from order_generator.utils import generate_one_order_pdf, generate_all_orders_pdf
from datetime import date, datetime
from django.db import transaction


def home(request):
    return render(request, "order_generator/home.html")


def create_order(request):
    if request.method == "POST":
        order_number = request.POST.get("order_number")
        tape_of_delivery = request.POST.get("tape_of_delivery")
        Order.objects.create(nr_order=order_number, tape_of_delivery=tape_of_delivery)
        return redirect("order_generator:add_product", order_nr=order_number)

    return render(request, "order_generator/create_order.html")


def get_sku_or_create_empty(sku_or_ean):
    sku = SkuInformation.objects.filter(
        Q(sku__exact=sku_or_ean) | Q(barcode__code__icontains=sku_or_ean)
    ).last()
    if not sku:
        # Check if a Barcode with the code already exists
        barcode, created = Barcode.objects.get_or_create(code="Brak codu")

        sku = SkuInformation(
            sku=sku_or_ean,
            name_of_product="name not found"
        )
        sku.save()
        sku.barcode.add(barcode)
    return sku


def add_product(request, order_nr):
    order = Order.objects.filter(nr_order=order_nr).last()

    if request.method == "POST":
        sku_or_ean = request.POST.get("sku")
        quantity = int(request.POST.get("quantity"))
        quantity_not_damaged = int(request.POST.get("quantity_not_damaged"))
        quantity_damage = int(quantity) - int(quantity_not_damaged)

        sku = get_sku_or_create_empty(sku_or_ean)

        with transaction.atomic():
            # Check if an OrderProduct with the same order and product exists
            order_product = OrderProduct.objects.filter(order=order, product__sku__sku=sku.sku).first()

            if order_product:
                # If it exists, update the quantities
                order_product.product.quantity += quantity
                order_product.product.quantity_not_damaged += quantity_not_damaged
                order_product.product.quantity_damage += quantity_damage
                order_product.product.save()  # Save the updated Product
            else:
                # If it doesn't exist, create a new OrderProduct
                product = Product.objects.create(
                    sku=sku, quantity=quantity,
                    quantity_not_damaged=quantity_not_damaged,
                    quantity_damage=quantity_damage)
                OrderProduct.objects.create(order=order, product=product)

        # #order_product, created = OrderProduct.objects.get_or_create(order=order, product__sku__sku=sku.sku)
        # order_product = OrderProduct.objects.filter(order=order, product__sku__sku=sku.sku)
        # if order_product:
        #     order_product.product.quantity += quantity
        #     order_product.product.quantity_not_damaged += quantity_not_damaged
        #     order_product.product.quantity_damage += quantity_damage
        # print(order_product)
        # product = Product.objects.create(
        #     sku=sku,
        #     quantity=quantity,
        #     quantity_not_damaged=quantity_not_damaged,
        #     quantity_damage=quantity_damage,
        # )
        #
        # OrderProduct.objects.create(order=order, product=product)

    return render(request, "order_generator/add_product.html", {"order": order})


def get_product_name(request):
    if request.method == "POST":
        sku_or_ean = request.POST.get("sku")
        try:
            sku_info = SkuInformation.objects.filter(
                Q(sku__exact=sku_or_ean) | Q(barcode__code__icontains=sku_or_ean)
            ).last()
            if sku_info:
                product_name = sku_info.name_of_product
                return JsonResponse({"product_name": product_name})
            return JsonResponse({"product_name": "Not found"})
        except ObjectDoesNotExist:
            return JsonResponse({"product_name": "Not found"})


def generate_one_order_form(request):
    if request.method == "POST":
        order_number = request.POST.get("order_number")
        order = Order.objects.filter(nr_order=order_number).last()
        order_pdf = generate_one_order_pdf(order.id)
        response = FileResponse(order_pdf, as_attachment=False, filename="Zwrot_LM.pdf")
        return response

    return render(request, "order_generator/one_order_form.html")


def generate_reports_for_day(request):
    if request.method == "POST":
        work_day = request.POST.get("date_to_print")
        work_day_order_pdf = generate_all_orders_pdf(work_day)
        resource = FileResponse(work_day_order_pdf, as_attachment=False, filename="Zwrotu_od_klientow.pdf")
        return resource
    return render(request, "order_generator/reports_for_day.html", {"data_today": date.today().strftime("%Y-%m-%d")})
