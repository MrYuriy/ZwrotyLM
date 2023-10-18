from django.contrib import admin
from order_generator.models import (
    Order,
    OrderProduct,
    SkuInformation,
    Product,
    Barcode,
    SkuInformationBarcode
)

admin.site.register(OrderProduct)
admin.site.register(Product)
admin.site.register(Barcode)
admin.site.register(SkuInformationBarcode)


class SkuInformationAdmin(admin.ModelAdmin):
    list_display = ("sku", "name_of_product")
    search_fields = ("sku", "name_of_product")


admin.site.register(SkuInformation, SkuInformationAdmin)


class OrderedProductInline(admin.TabularInline):
    exclude = []
    model = OrderProduct
    classes = ["collapse"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderedProductInline,
    ]
