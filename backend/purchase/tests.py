from pathlib import Path
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Supplier, PurchaseOrder, PurchaseInvoice


API_BASE = "/api/purchase"


@override_settings(MEDIA_ROOT=settings.BASE_DIR / "test_media")
class PurchaseApiTests(APITestCase):
    def tearDown(self):
        PurchaseInvoice.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        Supplier.objects.all().delete()

    def _storage_name(self, url):
        path = url
        if path.startswith(settings.MEDIA_URL):
            path = path[len(settings.MEDIA_URL):]
        return path.lstrip("/")

    def _supplier(self):
        resp = self.client.post(
            f"{API_BASE}/suppliers/",
            {"name": "Fornitore Uno", "vat_number": "IT123"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.data

    def _order(self, supplier_id):
        resp = self.client.post(
            f"{API_BASE}/orders/",
            {
                "number": "PO-001",
                "supplier": supplier_id,
                "date": timezone.now().date(),
                "status": "DRAFT",
                "total_amount": "100.00",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.data

    def test_create_order_requires_supplier(self):
        resp = self.client.post(
            f"{API_BASE}/orders/",
            {"number": "PO-FAIL", "date": timezone.now().date()},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invoice_inherits_supplier_from_order(self):
        supplier = self._supplier()
        order = self._order(supplier["id"])
        invoice_resp = self.client.post(
            f"{API_BASE}/invoices/",
            {
                "number": "INV-01",
                "order": order["id"],
                "date": "2025-01-10",
                "due_date": "2025-02-10",
                "total_amount": "100.00",
            },
            format="json",
        )
        self.assertEqual(invoice_resp.status_code, status.HTTP_201_CREATED)
        invoice = invoice_resp.data
        self.assertEqual(str(invoice["supplier"]), str(supplier["id"]))
        self.assertEqual(str(invoice["order"]), str(order["id"]))

    def test_invoice_requires_supplier_if_no_order(self):
        resp = self.client.post(
            f"{API_BASE}/invoices/",
            {
                "number": "INV-02",
                "date": "2025-01-10",
                "due_date": "2025-02-10",
                "total_amount": "50.00",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_attachment_on_purchase_invoice(self):
        supplier = self._supplier()
        invoice_resp = self.client.post(
            f"{API_BASE}/invoices/",
            {
                "number": "INV-03",
                "supplier": supplier["id"],
                "date": "2025-01-10",
                "due_date": "2025-02-10",
                "total_amount": "75.00",
                "attachment": SimpleUploadedFile(
                    "invoice.pdf", b"content", content_type="application/pdf"
                ),
            },
            format="multipart",
        )
        self.assertEqual(invoice_resp.status_code, status.HTTP_201_CREATED)
        data = invoice_resp.data
        from urllib.parse import urlparse

        parsed = urlparse(data["attachment"])
        path = parsed.path
        self.assertTrue(path.startswith(settings.MEDIA_URL + "purchase_invoices/"))
        self.assertTrue(path.endswith(".pdf"))
