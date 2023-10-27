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
    list_per_page = 20
    list_display = ("sku", "name_of_product")
    search_fields = ("sku", "name_of_product")


admin.site.register(SkuInformation, SkuInformationAdmin)


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1  # Кількість порожніх форм для додавання ліній замовлення

class OrderAdmin(admin.ModelAdmin):
    list_display = ('nr_order', 'get_delivery_type', 'creation_date', 'recorded_to_ds')
    list_filter = ('tape_of_delivery', 'recorded_to_ds')
    search_fields = ('nr_order', 'tape_of_delivery', 'creation_date')
    inlines = [OrderProductInline]  # Додайте цей інлайн для відображення ліній замовлення

    def get_delivery_type(self, obj):
        return obj.get_delivery_type()
    get_delivery_type.short_description = 'Delivery Type'

admin.site.register(Order, OrderAdmin)

# class OrderedProductInline(admin.TabularInline):
#     exclude = []
#     model = OrderProduct
#     classes = ["collapse"]
#
#
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_per_page = 20
#     search_fields = ("nr_order",)
#     inlines = [
#         OrderedProductInline,
#     ]
