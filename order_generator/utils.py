import io
from reportlab.pdfgen import canvas
from order_generator.models import Order, OrderProduct


def get_order_detail(order_id):
    order = Order.objects.get(id=order_id)
    tape_of_delivery = order.tape_of_delivery
    creation_date = order.creation_date
    order_products = OrderProduct.objects.filter(order_id=order_id)
    data_to_print_order = {"not_damage": None, "damage": None, "tape_of_delivery": None}
    sku_qty_damage = []
    sku_qty_not_damage = []

    for product in order_products:
        if product.product.quantity_not_damaged:
            value_sku = product.product.sku.sku
            value_not_damage_product = product.product.quantity_not_damaged
            sku_qty_not_damage.append([value_sku, value_not_damage_product])

        if product.product.quantity_damage:
            value_sku = product.product.sku.sku
            value_damage_product = product.product.quantity_damage
            sku_qty_damage.append([value_sku, value_damage_product])

    data_to_print_order["not_damage"] = sku_qty_not_damage
    data_to_print_order["damage"] = sku_qty_damage
    data_to_print_order["tape_of_delivery"] = str(tape_of_delivery)
    data_to_print_order["nr_order"] = order.nr_order
    data_to_print_order["date_writes"] = creation_date
    return data_to_print_order


def generate_one_order_pdf(order_id):
    order_detail = get_order_detail(order_id)
    list_not_damage_product = order_detail["not_damage"]
    list_damage_product = order_detail["damage"]
    buffer = io.BytesIO()
    my_canvas = canvas.Canvas(buffer)
    step = 0
    for i in range(
        (max(len(list_damage_product), len(list_not_damage_product)) // 15) + 1
    ):
        my_canvas.drawImage(
            "static/img/protocol_lm.jpg", -30, -100, width=652, height=960
        )
        my_canvas.setFont("Helvetica", 16)  # розмір шрифту і вид шрифту
        step += 15
        Y = 729  # початкова точка по Y для цілих
        if list_not_damage_product[step - 15 : step]:
            for sku_val in list_not_damage_product[step - 15 : step]:
                my_canvas.drawString(235, Y, str(sku_val[0]))  # координати потім текст
                my_canvas.drawString(500, Y, str(sku_val[1]))
                Y -= 22  # Крок між рядками
        Y = 355  # точка початку по Y для пощкоджених
        if list_damage_product[step - 15 : step]:
            for sku in list_damage_product[step - 15 : step]:
                my_canvas.drawString(235, Y, str(sku[0]))  # координати потім текст
                my_canvas.drawString(500, Y, str(sku[1]))
                Y -= 22  # Крок між рядками
        my_canvas.showPage()
    my_canvas.save()
    buffer.seek(0)
    return buffer
