from rest_framework import filters, viewsets

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
from .serializers import (
    ClientSerializer,
    ContactSerializer,
    OpportunitySerializer,
    OfferSerializer,
    OfferItemSerializer,
    SaleOrderSerializer,
    InvoiceSerializer,
    ContractSerializer,
)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().prefetch_related("contacts")
    serializer_class = ClientSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "phone", "city", "vat_number", "tax_code"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.select_related("client").all()
    serializer_class = ContactSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "phone", "role"]
    ordering_fields = ["created_at", "updated_at", "first_name", "last_name"]
    ordering = ["-created_at"]


class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.select_related("client").all()
    serializer_class = OpportunitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "client__name"]
    ordering_fields = ["created_at", "updated_at", "expected_close_date"]
    ordering = ["-created_at"]


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.select_related("client", "opportunity").prefetch_related("items")
    serializer_class = OfferSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "client__name", "status"]
    ordering_fields = ["created_at", "updated_at", "date", "valid_until"]
    ordering = ["-created_at"]


class OfferItemViewSet(viewsets.ModelViewSet):
    queryset = OfferItem.objects.select_related("offer").all()
    serializer_class = OfferItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product_code", "description", "offer__number"]
    ordering_fields = ["quantity", "unit_price"]


class SaleOrderViewSet(viewsets.ModelViewSet):
    queryset = SaleOrder.objects.select_related("client", "from_offer").all()
    serializer_class = SaleOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "client__name", "status"]
    ordering_fields = ["created_at", "updated_at", "date"]
    ordering = ["-created_at"]


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("client", "order").all()
    serializer_class = InvoiceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "client__name", "status", "payment_method"]
    ordering_fields = ["created_at", "updated_at", "date", "due_date"]
    ordering = ["-created_at"]


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related("client").all()
    serializer_class = ContractSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "client__name", "status"]
    ordering_fields = ["created_at", "updated_at", "start_date", "end_date"]
    ordering = ["-created_at"]
