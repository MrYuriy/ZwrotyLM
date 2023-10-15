from django.urls import path
from order_generator.views import (
    create_order,
    add_product,
    home,
    get_product_name,
    generate_one_order_form,
    generate_reports_for_day,
)


urlpatterns = [
    path("", home, name="home"),
    path("create_order/", create_order, name="create_order"),
    path("add-product/<int:order_nr>/", add_product, name="add_product"),
    path("get-product-name/", get_product_name, name="get_product_name"),
    path("generate-one-order-form/", generate_one_order_form, name="generate_one_order_pdf"),
    path("generate-reports-for-day/", generate_reports_for_day, name="generate_reports_for_day")
]

app_name = "order_generator"
