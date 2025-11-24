from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Client,
    Contact,
    Opportunity,
    Offer,
    OfferItem,
    SaleOrder,
    Invoice,
    Contract,
)


def _generate_number(model, prefix: str) -> str:
    """Generate sequential numbers like PREFIX-YYYY-XXX with padding."""
    year = timezone.now().year
    base = f"{prefix}-{year}-"
    with transaction.atomic():
        last = (
            model.objects.select_for_update()
            .filter(number__startswith=base, number__isnull=False)
            .order_by("-number")
            .values_list("number", flat=True)
            .first()
        )
        try:
            last_seq = int(last.split("-")[-1]) if last else 0
        except Exception:
            last_seq = 0
        return f"{base}{last_seq + 1:03d}"


class ContactSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "client",
            "client_name",
            "first_name",
            "last_name",
            "role",
            "email",
            "phone",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClientSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "vat_number",
            "tax_code",
            "email",
            "phone",
            "address",
            "city",
            "status",
            "assigned_to",
            "contacts",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "contacts"]


class OpportunitySerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "client",
            "client_name",
            "number",
            "name",
            "description",
            "stage",
            "inserted_date",
            "close_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "inserted_date"]

    def create(self, validated_data):
        if not validated_data.get("number"):
            validated_data["number"] = _generate_number(Opportunity, "OPP")
        return super().create(validated_data)


class OfferItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)
    discount = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0"), max_value=Decimal("100")
    )

    class Meta:
        model = OfferItem
        fields = [
            "id",
            "offer",
            "product_code",
            "description",
            "quantity",
            "unit_price",
            "discount",
            "total_line",
        ]
        read_only_fields = ["id", "total_line"]


class OfferItemInlineSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)
    discount = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0"), max_value=Decimal("100")
    )

    class Meta:
        model = OfferItem
        fields = [
            "id",
            "product_code",
            "description",
            "quantity",
            "unit_price",
            "discount",
            "total_line",
        ]
        read_only_fields = ["id", "total_line"]


class OfferSerializer(serializers.ModelSerializer):
    items = OfferItemInlineSerializer(many=True, required=False)
    client_name = serializers.CharField(source="client.name", read_only=True)
    opportunity_name = serializers.CharField(source="opportunity.name", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "number",
            "client",
            "client_name",
            "opportunity",
            "opportunity_name",
            "date",
            "description",
            "issued_date",
            "accepted_date",
            "valid_until",
            "type",
            "status",
            "total_amount",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_amount", "created_at", "updated_at"]
        extra_kwargs = {"client": {"required": False}}

    def validate(self, attrs):
        # Offerta deve essere legata almeno a un'opportunità
        if not attrs.get("opportunity"):
            raise serializers.ValidationError("opportunity è obbligatorio per creare un'offerta.")
        # Se non passiamo client lo impostiamo da opportunity
        attrs.setdefault("client", attrs["opportunity"].client)
        return attrs

    def _replace_items(self, offer: Offer, items_data):
        offer.items.all().delete()
        OfferItem.objects.bulk_create(
            [OfferItem(offer=offer, **item_data) for item_data in items_data]
        )

    def _update_total(self, offer: Offer):
        total = sum((item.total_line for item in offer.items.all()), Decimal("0"))
        offer.total_amount = total
        offer.save(update_fields=["total_amount"])

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        if not validated_data.get("number"):
            validated_data["number"] = _generate_number(Offer, "OFF")
        with transaction.atomic():
            offer = Offer.objects.create(**validated_data)
            if items_data:
                self._replace_items(offer, items_data)
            self._update_total(offer)
        return offer

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        with transaction.atomic():
            instance.save()
            if items_data is not None:
                self._replace_items(instance, items_data)
            self._update_total(instance)
        return instance


class SaleOrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    offer_number = serializers.CharField(source="from_offer.number", read_only=True)

    class Meta:
        model = SaleOrder
        fields = [
            "id",
            "number",
            "client",
            "client_name",
            "from_offer",
            "offer_number",
            "date",
            "status",
            "invoicing_date",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"total_amount": {"required": False}, "client": {"required": False}}

    def validate(self, attrs):
        offer = attrs.get("from_offer")
        if not offer:
            raise serializers.ValidationError("from_offer è obbligatorio per creare un ordine di vendita.")
        attrs.setdefault("client", offer.client)
        if not attrs.get("total_amount"):
            attrs["total_amount"] = offer.total_amount
        return attrs

    def create(self, validated_data):
        if not validated_data.get("number"):
            validated_data["number"] = _generate_number(SaleOrder, "ORD")
        return super().create(validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "number",
            "client",
            "client_name",
            "order",
            "order_number",
            "date",
            "due_date",
            "status",
            "total_amount",
            "payment_method",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"total_amount": {"required": False}, "client": {"required": False}}

    def validate(self, attrs):
        order = attrs.get("order")
        if not order:
            raise serializers.ValidationError("order è obbligatorio per creare una fattura.")
        attrs.setdefault("client", order.client)
        if not attrs.get("total_amount"):
            attrs["total_amount"] = order.total_amount
        return attrs

    def create(self, validated_data):
        if not validated_data.get("number"):
            validated_data["number"] = _generate_number(Invoice, "INV")
        return super().create(validated_data)


class ContractSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Contract
        fields = [
            "id",
            "title",
            "client",
            "client_name",
            "start_date",
            "end_date",
            "value",
            "status",
            "document_file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
