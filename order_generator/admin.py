from django.contrib import admin
from order_generator.models import Order, OrderProduct, SkuInformation, Product, Barcode

admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(SkuInformation)
admin.site.register(Product)
admin.site.register(Barcode)
