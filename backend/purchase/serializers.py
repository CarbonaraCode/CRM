from rest_framework import serializers

from .models import Supplier, PurchaseOrder, PurchaseInvoice


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "vat_number",
            "email",
            "phone",
            "address",
            "payment_terms",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "number",
            "supplier",
            "supplier_name",
            "date",
            "status",
            "total_amount",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = [
            "id",
            "number",
            "supplier",
            "supplier_name",
            "order",
            "order_number",
            "date",
            "due_date",
            "total_amount",
            "status",
            "attachment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "supplier": {"required": False},
            "attachment": {"required": False, "allow_null": True},
        }

    def validate(self, attrs):
        order = attrs.get("order")
        if not attrs.get("supplier"):
            if not order:
                raise serializers.ValidationError("supplier o order sono obbligatori")
            attrs["supplier"] = order.supplier
        elif order and order.supplier != attrs["supplier"]:
            raise serializers.ValidationError("supplier deve coincidere con quello dell'ordine")
        return attrs
