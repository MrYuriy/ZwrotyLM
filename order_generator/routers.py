class SkuRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "order_generator":
            if model._meta.model_name in ["skuinformation", "barcode"]:
                return "sku_db"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "order_generator":
            print(model._meta.model_name)
            if model._meta.model_name in ["skuinformation", "barcode"]:
                return "sku_db"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == "order_generator"
            and obj2._meta.app_label == "order_generator"
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "order_generator":
            if model_name in ["skuinformation", "barcode"]:
                return db == "sku_db"
        return db == "default"
