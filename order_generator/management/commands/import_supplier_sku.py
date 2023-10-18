import csv
from django.core.management.base import BaseCommand
from order_generator.models import SkuInformation, Barcode, SkuInformationBarcode
from tqdm import tqdm


class Command(BaseCommand):
    help = "Import data from supplier_sku.csv"

    def handle(self, *args, **options):
        file_path = "supplier_sku_data.csv"
        # file_path = "test.csv"
        sku_information_dict = {}
        barcode_list = []
        sku_list = []
        sku_list_exist = []
        with open(file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            total_rows = sum(1 for _ in csv_reader)  # Count total rows for tqdm

            csv_file.seek(0)
            next(csv_reader)
            for row in tqdm(csv_reader, total=total_rows, unit="row"):
                sku_id = row["SKU_ID"]
                description = row["DESCRIPTION"]
                barcode_value = row["SUPPLIER_SKU_ID"]

                barcode_instance = Barcode(barcode=barcode_value)
                barcode_list.append(barcode_instance)

                sku_instance = SkuInformation(sku=sku_id, name_of_product=description)

                if sku_id not in sku_information_dict:
                    sku_information_dict[sku_id] = {
                        "barcodes": [],
                        "sku_instance": None,
                    }
                sku_information_dict[sku_id]["barcodes"].append(barcode_instance)
                sku_information_dict[sku_id]["sku_instance"] = sku_instance

            Barcode.objects.bulk_create(barcode_list)
            SkuInformation.objects.bulk_create(
                [
                    sku_information_dict[sku]["sku_instance"]
                    for sku in sku_information_dict
                ]
            )

            sku_information_barcode_list = []

            for sku_id in tqdm(
                    sku_information_dict, total=len(sku_information_dict), unit="sku"
            ):
                sku_info = sku_information_dict[sku_id]
                for barcode in sku_info["barcodes"]:
                    sku_information_barcode = SkuInformationBarcode(
                        sku_information=sku_info["sku_instance"],
                        barcode=barcode
                    )
                    sku_information_barcode_list.append(sku_information_barcode)

                # sku_instance = sku_info["sku_instance"]
                # sku_instance.barcodes.set(sku_info["barcodes"])
            SkuInformationBarcode.objects.bulk_create(
                sku_information_barcode_list
            )
        self.stdout.write(self.style.SUCCESS("Successfully imported data"))
