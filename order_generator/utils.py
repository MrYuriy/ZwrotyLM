import io
from reportlab.pdfgen import canvas
from order_generator.models import Order, OrderProduct, SkuInformation
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def get_order_detail(order_products):
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
    data_to_print_order["date_writes"] = order_products[0].order.creation_date
    data_to_print_order["nr_order"] = order_products[0].order.nr_order
    data_to_print_order["tape_of_delivery"] = order_products[0].order.tape_of_delivery
    return data_to_print_order


def generate_one_order_pdf(order_id):
    order_products = OrderProduct.objects.filter(order_id=order_id)
    order_detail = get_order_detail(order_products)

    list_not_damage_product = order_detail["not_damage"]
    list_damage_product = order_detail["damage"]
    date_order_creation = order_detail["date_writes"]
    buffer = io.BytesIO()
    my_canvas = canvas.Canvas(buffer)
    step = 0
    for i in range(
        (max(len(list_damage_product), len(list_not_damage_product)) // 15) + 1
    ):
        my_canvas.drawImage(
            "static/img/protocol_lm.jpg", -30, -100, width=652, height=960
        )
        my_canvas.setFont("Helvetica", 16)  # size and type font
        step += 15
        Y = 729  # Y coordinate for not damage products
        if list_not_damage_product[step - 15 : step]:
            for sku_val in list_not_damage_product[step - 15 : step]:
                my_canvas.drawString(235, Y, str(sku_val[0]))
                my_canvas.drawString(500, Y, str(sku_val[1]))
                Y -= 22  # make step between rows
        Y = 355  # Y coordinate for damage products
        if list_damage_product[step - 15 : step]:
            for sku in list_damage_product[step - 15 : step]:
                my_canvas.drawString(235, Y, str(sku[0]))
                my_canvas.drawString(500, Y, str(sku[1]))
                Y -= 22  # step between row
        my_canvas.setFont("Helvetica", 10)
        my_canvas.drawString(500, 63, str(date_order_creation))
        my_canvas.showPage()
    my_canvas.save()
    buffer.seek(0)
    return buffer


def get_total_sorted_orders(order_products_today):
    order_product_list = []
    current_order_id = None
    current_order_products = []

    for order_product in order_products_today:
        if order_product.order_id != current_order_id:
            if current_order_id is not None:
                order_product_list.append((current_order_id, current_order_products))
            current_order_id = order_product.order_id
            current_order_products = []
        current_order_products.append(order_product)

    if current_order_id is not None:
        order_product_list.append((current_order_id, current_order_products))

    return order_product_list


def return_name_of_product(sku_r):
    try:
        sku_info = SkuInformation.objects.filter(sku=int(sku_r)).last()
        if sku_info:
            name_of_product = sku_info.name_of_product
            if len(name_of_product) > 24:
                name_of_product = name_of_product[:24]
                if name_of_product[-1] != " ":
                    name_of_product = name_of_product.rsplit(" ", 1)[0]
        return name_of_product
    except SkuInformation.DoesNotExist:
        return "name not found"


def generate_all_orders_pdf(work_day):
    buffer = io.BytesIO()

    pdfmetrics.registerFont(TTFont("FreeSans", "freesans/FreeSans.ttf"))
    my_canvas = canvas.Canvas(buffer)
    my_canvas.drawImage(
        "static/img/returned_products_order.jpg", -10, 0, width=622, height=850
    )
    my_canvas.setFont("FreeSans", 12)  # розмір шрифту і вид шрифту

    Y = 610
    counter = 0

    order_products_today = OrderProduct.objects.filter(order__creation_date=work_day)
    order_products_list = get_total_sorted_orders(order_products_today)

    for _, order_products in order_products_list:
        order_number = order_products[0].order.nr_order

        if counter == 21:
            my_canvas.showPage()
            my_canvas.setFont("FreeSans", 12)
            my_canvas.drawImage(
                "static/img/returned_products_order.jpg", -10, 0, width=622, height=850
            )
            Y = 610
            counter = 0
        all_about_order = get_order_detail(order_products)
        my_canvas.drawString(440, Y, str(all_about_order["tape_of_delivery"]))

        if str(order_number) == "0":
            my_canvas.drawString(495, Y, "Brak nr.zam.")
        else:
            my_canvas.drawString(500, Y, str(order_number))

        for dicts in [
            [all_about_order["not_damage"], "P"],
            [all_about_order["damage"], "U"],
        ]:
            for product in dicts[0]:
                if counter == 21:
                    my_canvas.showPage()
                    my_canvas.setFont("FreeSans", 12)
                    my_canvas.drawImage(
                        "static/img/returned_products_order.jpg",
                        -10,
                        0,
                        width=622,
                        height=850,
                    )
                    Y = 610
                    counter = 0
                my_canvas.drawString(55, Y, str(product[0]))
                name_of_product = str(return_name_of_product(product[0]))[:25]
                my_canvas.drawString(131, Y, name_of_product)
                my_canvas.drawString(310, Y, str(product[1]))
                my_canvas.drawString(380, Y, str(dicts[1]))
                counter += 1
                Y -= 21

    my_canvas.showPage()
    my_canvas.save()
    buffer.seek(0)
    return buffer
