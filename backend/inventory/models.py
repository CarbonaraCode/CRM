from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

# --- MAGAZZINO ---
class Product(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, verbose_name="Codice Articolo")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prezzo Vendita")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo Acquisto")
    stock_quantity = models.IntegerField(default=0)
    min_stock_alert = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.code} - {self.name}"

class SerialNumber(TimeStampedModel):
    """
    Gestione delle Matricole specifiche per prodotti tracciabili.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='serials')
    serial_code = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, default='IN_STOCK') # IN_STOCK, SOLD, RMA
    purchase_date = models.DateField(null=True, blank=True)
    warranty_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"S/N: {self.serial_code} ({self.product.name})"

# --- SUPPORTO & TICKET ---
class Ticket(TimeStampedModel):
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Bassa')
        MEDIUM = 'MEDIUM', _('Media')
        HIGH = 'HIGH', _('Alta')
        CRITICAL = 'CRITICAL', _('Critica')

    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Aperto')
        IN_PROGRESS = 'IN_PROGRESS', _('In Lavorazione')
        WAITING = 'WAITING', _('In Attesa')
        RESOLVED = 'RESOLVED', _('Risolto')
        CLOSED = 'CLOSED', _('Chiuso')

    subject = models.CharField(max_length=255)
    description = models.TextField()
    # Usiamo string references 'app.Model' per evitare import circolari
    client = models.ForeignKey('sales.Client', on_delete=models.CASCADE, related_name='tickets', null=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_tickets')
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    def __str__(self):
        return f"Ticket #{self.id.hex[:6]} - {self.subject}"

# --- CONTROLLO DI GESTIONE & AMMINISTRAZIONE ---
class ExpenseReport(TimeStampedModel):
    """Nota Spese Dipendenti"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='DRAFT') # DRAFT, SUBMITTED, APPROVED, REIMBURSED
    submission_date = models.DateField()

    def __str__(self):
        return f"Nota Spese: {self.title}"

class CreditNote(TimeStampedModel):
    """Nota di Credito (collegata a Fattura Vendita)"""
    client = models.ForeignKey('sales.Client', on_delete=models.CASCADE)
    invoice = models.ForeignKey('sales.Invoice', on_delete=models.SET_NULL, null=True, related_name='credit_notes')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    date = models.DateField()

    def __str__(self):
        return f"Nota Credito per {self.client.name}"

class ManagementControl(TimeStampedModel):
    """
    Tabella generica per centri di costo o budget.
    """
    year = models.IntegerField()
    cost_center = models.CharField(max_length=100) # Es. "IT", "Marketing"
    budget_allocated = models.DecimalField(max_digits=14, decimal_places=2)
    budget_spent = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"Budget {self.cost_center} {self.year}"
