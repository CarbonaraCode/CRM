import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel


# --- 1. CLIENT & CONTACTS ---
class Client(TimeStampedModel):
    class Status(models.TextChoices):
        LEAD = "LEAD", _("Lead")
        ACTIVE = "ACTIVE", _("Attivo")
        INACTIVE = "INACTIVE", _("Inattivo")
        BAD_DEBT = "BAD_DEBT", _("Cattivo Pagatore")

    name = models.CharField(max_length=255, unique=True, verbose_name="Ragione Sociale")
    vat_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Partita IVA")
    tax_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Codice Fiscale")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LEAD)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="clients",
    )

    def __str__(self):
        return self.name


class Contact(TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.client.name})"


# --- 2. OPPORTUNITIES (Pipeline) ---
class Opportunity(TimeStampedModel):
    class Stage(models.TextChoices):
        NEW = "NEW", _("Nuova")
        QUALIFICATION = "QUALIFICATION", _("Qualificazione")
        PROPOSAL = "PROPOSAL", _("Proposta")
        NEGOTIATION = "NEGOTIATION", _("Negoziazione")
        WON = "WON", _("Chiusa Vinta")
        LOST = "LOST", _("Chiusa Persa")

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="opportunities")
    number = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Es. OPP-2024-001
    name = models.CharField(max_length=255, verbose_name="Nome Opportunita")
    description = models.TextField(blank=True)
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.NEW)
    inserted_date = models.DateField(default=timezone.localdate)
    close_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.number} - {self.client.name}"


# --- 3. OFFERS (Preventivi) ---
class Offer(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Bozza")
        SENT = "SENT", _("Inviata")
        ACCEPTED = "ACCEPTED", _("Accettata")
        REJECTED = "REJECTED", _("Rifiutata")
        EXPIRED = "EXPIRED", _("Scaduta")

    number = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Es. OFF-2024-001
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="offers")
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name="offers"
    )
    date = models.DateField()  # data creazione
    description = models.TextField(blank=True)
    issued_date = models.DateField(null=True, blank=True)
    accepted_date = models.DateField(null=True, blank=True)
    valid_until = models.DateField()
    type = models.CharField(max_length=50, blank=True)  # tipologia
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Offerta {self.number}"


class OfferItem(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="items")
    product_code = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    @property
    def total_line(self):
        return (self.quantity * self.unit_price) * (1 - (self.discount / 100))


# --- 4. ORDERS (Ordini di Vendita) ---
class SaleOrder(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("In Attesa")
        CONFIRMED = "CONFIRMED", _("Confermato")
        SHIPPED = "SHIPPED", _("Spedito")
        DELIVERED = "DELIVERED", _("Consegnato")
        CANCELLED = "CANCELLED", _("Annullato")

    number = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Es. ORD-2024-001
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="sale_orders")
    from_offer = models.OneToOneField(
        Offer, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_order"
    )
    date = models.DateField()
    invoicing_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Ordine {self.number}"


# --- 5. INVOICES (Fatture) ---
class Invoice(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Bozza")
        ISSUED = "ISSUED", _("Emessa")
        PAID = "PAID", _("Pagata")
        OVERDUE = "OVERDUE", _("Scaduta")
        CANCELLED = "CANCELLED", _("Annullata")

    number = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Es. FAT-2024-001
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="invoices")
    order = models.ForeignKey(SaleOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    date = models.DateField()
    due_date = models.DateField(verbose_name="Data Scadenza")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Fattura {self.number}"


# --- 6. CONTRACTS (Contratti) ---
class Contract(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Attivo")
        EXPIRED = "EXPIRED", _("Scaduto")
        RENEWED = "RENEWED", _("Rinnovato")
        TERMINATED = "TERMINATED", _("Terminato")

    title = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="contracts")
    start_date = models.DateField()
    end_date = models.DateField()
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    document_file = models.FileField(upload_to="contracts/", null=True, blank=True)

    def __str__(self):
        return f"Contratto {self.title} - {self.client.name}"
