from django.db import models
from django.db.models.fields import CharField


class Product(models.Model):
    sku = models.ForeignKey("SkuInformation", on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    quantity_not_damaged = models.IntegerField()
    quantity_damage = models.IntegerField()

    def __str__(self):
        return f"{self.sku.name_of_product} {self.sku.sku}"


class Order(models.Model):
    # Constants for delivery type
    PALLET = "P"
    BOX = "C"

    # Choices for tape_of_delivery field
    TAPE_OF_DELIVERY_CHOICES = [
        (PALLET, "Pallet"),
        (BOX, "Box"),
    ]

    creation_date = models.DateField(auto_now_add=True)
    nr_order = models.IntegerField()
    tape_of_delivery = models.CharField(
        max_length=1,
        choices=TAPE_OF_DELIVERY_CHOICES,
        default=BOX,
        verbose_name="tape_of_delivery",
    )

    def __str__(self):
        return f"Order {self.nr_order}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class SkuInformation(models.Model):
    sku = models.IntegerField()
    name_of_product = CharField(max_length=100)
    barcode = models.ForeignKey("Barcode", on_delete=models.CASCADE)

    def __str__(self):
        return self.name_of_product


class Barcode(models.Model):
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = "barcode"

    def __str__(self):
        return self.code
