from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

class Supplier(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Ragione Sociale")
    vat_number = models.CharField(max_length=50, blank=True, verbose_name="P.IVA")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    payment_terms = models.CharField(max_length=100, blank=True, help_text="Es. 30gg DFFM")

    def __str__(self):
        return self.name

class PurchaseOrder(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Bozza')
        SENT = 'SENT', _('Inviato')
        RECEIVED = 'RECEIVED', _('Merce Ricevuta')
        COMPLETED = 'COMPLETED', _('Completato')
        CANCELLED = 'CANCELLED', _('Annullato')

    number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"PO {self.number} - {self.supplier.name}"

class PurchaseInvoice(TimeStampedModel):
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', _('Ricevuta')
        PAID = 'PAID', _('Pagata')
        OVERDUE = 'OVERDUE', _('Scaduta')

    number = models.CharField(max_length=50) # Numero fattura del fornitore
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='invoices')
    order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    attachment = models.FileField(upload_to='purchase_invoices/', null=True, blank=True)

    def __str__(self):
        return f"Fattura {self.number} ({self.supplier.name})"
