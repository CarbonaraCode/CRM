import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# --- BASE MODEL CONDIVISO ---
class TimeStampedModel(models.Model):
    """
    Modello astratto usato da TUTTE le app per garantire ID UUID
    e tracciamento temporale (created_at, updated_at).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# --- UTENTI & RUOLI ---
class User(AbstractUser):
    """
    Estendiamo l'utente base di Django.
    I 'Ruoli' possono essere gestiti tramite i 'Groups' di Django 
    o campi specifici qui se servono logiche custom veloci.
    """
    phone = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, verbose_name="Dipartimento")
    is_manager = models.BooleanField(default=False, verbose_name="È Manager")

    def __str__(self):
        return self.username

# --- CONFIGURAZIONE SISTEMA ---
class SMTPServer(TimeStampedModel):
    name = models.CharField(max_length=100, default="Default SMTP")
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255) # Nota: In prod usare campi cifrati!
    use_tls = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Server SMTP"
        verbose_name_plural = "Server SMTP"

    def __str__(self):
        return f"{self.name} ({self.host})"
