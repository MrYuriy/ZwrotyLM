import csv
from django.core.management.base import BaseCommand


def write_final_csv(data_to_write):
    with open("supplier_sku_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data_to_write)


def replace_polish_characters(text):
    # Створюємо словник для заміни польських символів на латинські
    translation = {
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ź": "z",
        "ż": "z",
        "Ą": "A",
        "Ć": "C",
        "Ę": "E",
        "Ł": "L",
        "Ń": "N",
        "Ó": "O",
        "Ś": "S",
        "Ź": "Z",
        "Ż": "Z",
    }

    # Замінюємо польські символи на латинські еквіваленти
    for char, replacement in translation.items():
        text = text.replace(char, replacement)

    return text


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("supplier_sku_utf8_test.csv", "r", encoding="utf-8") as csv_file:
            data_to_write = [["SUPPLIER_SKU_ID", "SKU_ID", "DESCRIPTION"]]

            barcode_set = set()

            csv_reader = csv.DictReader(csv_file)
            next(csv_reader)
            for row in csv_reader:
                sku_id = row["SKU_ID"]
                description = row["DESCRIPTION"]
                try:
                    barcode_value = str(int(row["SUPPLIER_SKU_ID"]))
                except ValueError:
                    continue

                if barcode_value not in barcode_set:
                    barcode_set.add(barcode_value)
                    data_to_write.append(
                        [barcode_value, sku_id, replace_polish_characters(description)]
                    )

            write_final_csv(data_to_write)
