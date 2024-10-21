import io
from reportlab.pdfgen import canvas
from order_generator.models import Order, OrderProduct, SkuInformation
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import apiclient.discovery


def get_order_detail(order_products):
    data_to_print_order = {
        "not_damage": [
            [product.product.sku.sku, product.product.quantity_not_damaged]
            for product in order_products
            if product.product.quantity_not_damaged
        ],
        "damage": [
            [product.product.sku.sku, product.product.quantity_damage]
            for product in order_products
            if product.product.quantity_damage
        ],
        "date_writes": order_products[0].order.creation_date,
        "nr_order": order_products[0].order.nr_order,
        "tape_of_delivery": order_products[0].order.tape_of_delivery,
    }
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
        if list_not_damage_product[step - 15: step]:
            for sku_val in list_not_damage_product[step - 15: step]:
                my_canvas.drawString(235, Y, str(sku_val[0]))
                my_canvas.drawString(500, Y, str(sku_val[1]))
                Y -= 22  # make step between rows
        Y = 355  # Y coordinate for damage products
        if list_damage_product[step - 15: step]:
            for sku in list_damage_product[step - 15: step]:
                my_canvas.drawString(235, Y, str(sku[0]))
                my_canvas.drawString(500, Y, str(sku[1]))
                Y -= 22  # step between row
        my_canvas.setFont("Helvetica", 10)
        my_canvas.drawString(500, 63, str(date_order_creation))
        my_canvas.showPage()
    my_canvas.save()
    buffer.seek(0)
    return buffer


def get_total_order_list(target_date):
    total_order_list = []
    order_products = OrderProduct.objects.filter(order__creation_date=target_date).prefetch_related("order",
                                                                                                    "product__sku")
    order_list = []
    for order_product in order_products:
        sku = order_product.product.sku.sku
        name_of_product = order_product.product.sku.name_of_product
        if len(name_of_product) > 21:
            name_of_product = name_of_product[:20]
        quantity_not_damaged = order_product.product.quantity_not_damaged
        quantity_damage = order_product.product.quantity_damage
        tape_of_delivery = order_product.order.tape_of_delivery
        nr_order = order_product.order.nr_order
        if nr_order == 0:
            nr_order = "Brak nr.zam."

        order_id = order_product.order.id
        if quantity_not_damaged:
            order_row = [
                sku, name_of_product, quantity_not_damaged,
                "P",
                f"{tape_of_delivery if order_id not in order_list else ''}",
                f"{nr_order if order_id not in order_list else ''}"]

            total_order_list.append(order_row)
            order_list.append(order_id)
        if quantity_damage:
            order_row = [
                sku, name_of_product, quantity_damage,
                "U",
                f"{tape_of_delivery if order_id not in order_list else ''}",
                f"{nr_order if order_id not in order_list else ''}"]
            total_order_list.append(order_row)
            order_list.append(order_id)
    return total_order_list


def generate_all_orders_pdf(work_day):
    order_product_list = get_total_order_list(work_day)

    buffer = io.BytesIO()

    pdfmetrics.registerFont(TTFont("FreeSans", "freesans/FreeSans.ttf"))
    my_canvas = canvas.Canvas(buffer)
    my_canvas.drawImage(
        "static/img/zwroty od klijenta.jpg", -10, 0, width=622, height=850
    )
    my_canvas.setFont("FreeSans", 12)

    Y = 615
    counter = 0
    X_coordinates = [55, 125, 310, 380, 440, 485]

    for order_row in order_product_list:
        for x, info in zip(X_coordinates, order_row):

            if counter == 17:
                my_canvas.showPage()
                my_canvas.setFont("FreeSans", 12)
                my_canvas.drawImage(
                    "static/img/zwroty od klijenta.jpg", -10, 0, width=622, height=850
                )
                Y = 615
                counter = 0
            my_canvas.drawString(x, Y, str(info))

        counter += 1
        Y -= 26
    my_canvas.showPage()
    my_canvas.save()
    buffer.seek(0)
    return buffer


# def generate_all_orders_pdf(work_day):
#     buffer = io.BytesIO()
#
#     pdfmetrics.registerFont(TTFont("FreeSans", "freesans/FreeSans.ttf"))
#     my_canvas = canvas.Canvas(buffer)
#     my_canvas.drawImage(
#         "static/img/returned_products_order.jpg", -10, 0, width=622, height=850
#     )
#     my_canvas.setFont("FreeSans", 12)  # розмір шрифту і вид шрифту
#
#     Y = 610
#     counter = 0
#
#     order_products_today = OrderProduct.objects.filter(order__creation_date=work_day)
#     order_products_list = get_total_sorted_orders(order_products_today)
#
#     for _, order_products in order_products_list:
#         order_number = order_products[0].order.nr_order
#
#         if counter == 21:
#             my_canvas.showPage()
#             my_canvas.setFont("FreeSans", 12)
#             my_canvas.drawImage(
#                 "static/img/returned_products_order.jpg", -10, 0, width=622, height=850
#             )
#             Y = 610
#             counter = 0
#         all_about_order = get_order_detail(order_products)
#         my_canvas.drawString(440, Y, str(all_about_order["tape_of_delivery"]))
#
#         if str(order_number) == "0":
#             my_canvas.drawString(495, Y, "Brak nr.zam.")
#         else:
#             my_canvas.drawString(500, Y, str(order_number))
#
#         for dicts in [
#             [all_about_order["not_damage"], "P"],
#             [all_about_order["damage"], "U"],
#         ]:
#             for product in dicts[0]:
#                 if counter == 21:
#                     my_canvas.showPage()
#                     my_canvas.setFont("FreeSans", 12)
#                     my_canvas.drawImage(
#                         "static/img/returned_products_order.jpg",
#                         -10,
#                         0,
#                         width=622,
#                         height=850,
#                     )
#                     Y = 610
#                     counter = 0
#                 my_canvas.drawString(55, Y, str(product[0]))
#                 name_of_product = str(return_name_of_product(product[0]))[:25]
#                 my_canvas.drawString(131, Y, name_of_product)
#                 my_canvas.drawString(310, Y, str(product[1]))
#                 my_canvas.drawString(380, Y, str(dicts[1]))
#                 counter += 1
#                 Y -= 21
#
#     my_canvas.showPage()
#     my_canvas.save()
#     buffer.seek(0)
#     return buffer


def connect_to_gs():
    creds_file = settings.CREDENTIALS_FILE_PATH

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        creds_file,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
    return service


def write_to_gs(body):
    sheet_name = "Zwroty_LM"
    spreadsheet_id = settings.SPREADSHEET_ID
    service = connect_to_gs()
    response = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id, range=sheet_name
        )
        .execute()
    )

    values = response.get("values", [])

    start_row = len(values) + 1
    finish_row = start_row + len(body['values'][0])
    range_to_write = f"{sheet_name}!A{start_row}:G{finish_row}"
    response = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_to_write,
        valueInputOption="RAW",
        body=body,
    ).execute()


def write_one_order_to_gs(order_id: int):
    print(order_id)
    # ["data zwrotu" "zamówienie" "referencja/EAN" "uwagi" "ilość" "Nośnik" "klasyfikacja towaru"]
    order_products = OrderProduct.objects.filter(order__id=order_id)
    data_to_write = []
    body = {"values": []}

    creation_data_order = order_products[0].order.creation_date.strftime("%Y-%m-%d")
    nr_order = order_products[0].order.nr_order
    delivery_type = order_products[0].order.get_delivery_type()

    for order_product in order_products:
        sku = order_product.product.sku.sku
        qty_not_damage = order_product.product.quantity_not_damaged
        qty_damage = order_product.product.quantity_damage

        if qty_not_damage > 0:
            data_to_write.append(
                [f"{creation_data_order}", f"{nr_order}", f"{sku}", "", f"{qty_not_damage}", f"{delivery_type}",
                 "pełnowartościowy"]
            )
            nr_order = ""
        if qty_damage > 0:
            data_to_write.append(
                [f"{creation_data_order}", f"{nr_order}", f"{sku}", "", f"{qty_damage}", f"{delivery_type}",
                 "uszkodzony"]
            )
        nr_order = ""
    body["values"] = data_to_write
    write_to_gs(body)
