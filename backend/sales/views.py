from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
    queryset = Invoice.objects.select_related("client", "order").prefetch_related("items").all()
    serializer_class = InvoiceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "client__name", "status", "payment_method"]
    ordering_fields = ["created_at", "updated_at", "date", "due_date"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        invoice = self.get_object()
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Fattura {invoice.number}")
        p.setFont("Helvetica", 10)
        y -= 20
        p.drawString(50, y, f"Cliente: {invoice.client.name}")
        y -= 15
        p.drawString(50, y, f"Data: {invoice.date}")
        y -= 15
        p.drawString(50, y, f"Scadenza: {invoice.due_date}")
        y -= 30
        p.drawString(50, y, "Prodotto")
        p.drawString(200, y, "Descrizione")
        p.drawString(380, y, "Q.ta")
        p.drawString(430, y, "Prezzo")
        p.drawString(500, y, "Totale")
        y -= 15
        p.line(50, y, width - 50, y)
        y -= 10
        for item in invoice.items.all():
            if y < 80:
                p.showPage()
                y = height - 50
            p.drawString(50, y, str(item.product))
            p.drawString(200, y, str(item.description))
            p.drawRightString(420, y, f"{item.quantity}")
            p.drawRightString(500, y, f"{item.unit_price}")
            p.drawRightString(width - 50, y, f"{item.total_line}")
            y -= 15
        y -= 20
        p.drawRightString(width - 50, y, f"Totale: {invoice.total_amount}")
        if invoice.terms_and_conditions:
            y -= 30
            p.drawString(50, y, "Termini e condizioni:")
            y -= 15
            text_obj = p.beginText(50, y)
            text_obj.setFont("Helvetica", 9)
            for line in invoice.terms_and_conditions.splitlines():
                text_obj.textLine(line)
            p.drawText(text_obj)
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"invoice-{invoice.number}.pdf")


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related("client").all()
    serializer_class = ContractSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "client__name", "status"]
    ordering_fields = ["created_at", "updated_at", "start_date", "end_date"]
    ordering = ["-created_at"]
