from django.urls import path
from order_generator.views import create_order, add_product, home, get_product_name


urlpatterns = [
    path('', home, name='home'),
    path('create_order/', create_order, name='create_order'),
    path('add_product/<int:order_nr>/', add_product, name='add_product'),
    path('get_product_name/', get_product_name, name='get_product_name'),
]

app_name = "order_generator"
