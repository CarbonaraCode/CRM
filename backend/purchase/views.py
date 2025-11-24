from rest_framework import filters, viewsets

from .models import Supplier, PurchaseOrder, PurchaseInvoice
from .serializers import SupplierSerializer, PurchaseOrderSerializer, PurchaseInvoiceSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "vat_number", "email", "phone"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related("supplier").all()
    serializer_class = PurchaseOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "supplier__name", "status"]
    ordering_fields = ["created_at", "updated_at", "date"]
    ordering = ["-created_at"]


class PurchaseInvoiceViewSet(viewsets.ModelViewSet):
    queryset = PurchaseInvoice.objects.select_related("supplier", "order").all()
    serializer_class = PurchaseInvoiceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "supplier__name", "order__number", "status"]
    ordering_fields = ["created_at", "updated_at", "date", "due_date"]
    ordering = ["-created_at"]
