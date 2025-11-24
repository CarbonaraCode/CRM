from decimal import Decimal
import shutil
import tempfile
from django.conf import settings
from django.test import override_settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Client, Opportunity, Offer, SaleOrder, Invoice, Contract


API_BASE = "/api/sales"


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class SalesApiTests(APITestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(name="Test Client", email="client@test.com")

    def tearDown(self):
        Invoice.objects.all().delete()
        SaleOrder.objects.all().delete()
        Offer.objects.all().delete()
        Opportunity.objects.all().delete()
        Client.objects.all().delete()

    def _file(self, name="allegato.txt", content=b"demo"):
        return SimpleUploadedFile(name, content, content_type="text/plain")

    def _path_from_url(self, url):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.path or url
        except Exception:
            return url

    def _storage_name(self, url):
        path = self._path_from_url(url)
        prefix = settings.MEDIA_URL
        if prefix and path.startswith(prefix):
            path = path[len(prefix):]
        return path.lstrip('/')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_opportunity_auto_numbers_and_sequence(self):
        url = f"{API_BASE}/opportunities/"
        resp1 = self.client.post(url, {"client": str(self.client_obj.id), "name": "Opp A"}, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        first_num = resp1.data["number"]
        year = timezone.now().year
        self.assertTrue(first_num.startswith(f"OPP-{year}-"))

        resp2 = self.client.post(url, {"client": str(self.client_obj.id), "name": "Opp B"}, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        second_num = resp2.data["number"]
        self.assertNotEqual(first_num, second_num)
        self.assertTrue(second_num.endswith("002"))

    def _create_opportunity(self, with_file=False):
        payload = {"client": str(self.client_obj.id), "name": "Main Opp"}
        if with_file:
            payload["attachment"] = self._file("opp.txt")
        resp = self.client.post(
            f"{API_BASE}/opportunities/",
            payload,
            format="multipart" if with_file else "json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.data

    def test_offer_requires_opportunity_and_sets_client_and_total(self):
        opp = self._create_opportunity()
        payload = {
            "opportunity": opp["id"],
            "date": "2025-01-01",
            "valid_until": "2025-01-31",
            "items": [
                {"product_code": "P1", "description": "Prod 1", "quantity": 2, "unit_price": "100.00", "discount": "0"},
                {"product_code": "P2", "description": "Prod 2", "quantity": 1, "unit_price": "50.00", "discount": "10.00"},
            ],
        }
        resp = self.client.post(f"{API_BASE}/offers/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        offer = resp.data
        self.assertEqual(offer["client"], opp["client"])
        self.assertTrue(offer["number"].startswith(f"OFF-{timezone.now().year}-"))
        self.assertEqual(Decimal(offer["total_amount"]), Decimal("245.00"))  # 2*100 + 1*50*0.9

    def test_sale_order_requires_offer_and_inherits_totals(self):
        opp = self._create_opportunity()
        offer = self.client.post(
            f"{API_BASE}/offers/",
            {
                "opportunity": opp["id"],
                "date": "2025-01-01",
                "valid_until": "2025-01-31",
                "items": [{"product_code": "P", "description": "Prod", "quantity": 1, "unit_price": "200.00", "discount": "0"}],
            },
            format="json",
        ).data

        resp = self.client.post(
            f"{API_BASE}/orders/",
            {"from_offer": offer["id"], "date": "2025-02-01"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order = resp.data
        self.assertTrue(order["number"].startswith(f"ORD-{timezone.now().year}-"))
        self.assertEqual(Decimal(order["total_amount"]), Decimal("200.00"))
        self.assertEqual(order["client"], offer["client"])

    def test_invoice_requires_order_and_inherits_totals(self):
        opp = self._create_opportunity()
        offer = self.client.post(
            f"{API_BASE}/offers/",
            {
                "opportunity": opp["id"],
                "date": "2025-01-01",
                "valid_until": "2025-01-31",
                "items": [{"product_code": "P", "description": "Prod", "quantity": 1, "unit_price": "120.00", "discount": "0"}],
            },
            format="json",
        ).data
        order = self.client.post(
            f"{API_BASE}/orders/",
            {"from_offer": offer["id"], "date": "2025-02-01"},
            format="json",
        ).data

        resp = self.client.post(
            f"{API_BASE}/invoices/",
            {"order": order["id"], "date": "2025-02-15", "due_date": "2025-03-15"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        invoice = resp.data
        self.assertTrue(invoice["number"].startswith(f"INV-{timezone.now().year}-"))
        self.assertEqual(Decimal(invoice["total_amount"]), Decimal("120.00"))
        self.assertEqual(invoice["client"], order["client"])

    def test_upload_attachments_on_sales_entities(self):
        opp = self._create_opportunity(with_file=True)
        self.assertIn("opp.txt", opp["attachment"])
        self.assertTrue(default_storage.exists(self._storage_name(opp["attachment"])))

        offer_resp = self.client.post(
            f"{API_BASE}/offers/",
            {
                "opportunity": opp["id"],
                "date": "2025-01-01",
                "valid_until": "2025-01-31",
                "attachment": self._file("offer.pdf"),
            },
            format="multipart",
        )
        self.assertEqual(offer_resp.status_code, status.HTTP_201_CREATED)
        offer = offer_resp.data
        self.assertIn("offer.pdf", offer["attachment"])
        self.assertTrue(default_storage.exists(self._storage_name(offer["attachment"])))

        order_resp = self.client.post(
            f"{API_BASE}/orders/",
            {"from_offer": offer["id"], "date": "2025-02-01", "attachment": self._file("order.docx")},
            format="multipart",
        )
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        order = order_resp.data
        self.assertIn("order.docx", order["attachment"])
        self.assertTrue(default_storage.exists(self._storage_name(order["attachment"])))

        invoice_resp = self.client.post(
            f"{API_BASE}/invoices/",
            {
                "order": order["id"],
                "date": "2025-02-15",
                "due_date": "2025-03-15",
                "attachment": self._file("invoice.txt"),
            },
            format="multipart",
        )
        self.assertEqual(invoice_resp.status_code, status.HTTP_201_CREATED)
        invoice = invoice_resp.data
        self.assertIn("invoice.txt", invoice["attachment"])
        self.assertTrue(default_storage.exists(self._storage_name(invoice["attachment"])))

        contract_resp = self.client.post(
            f"{API_BASE}/contracts/",
            {
                "client": str(self.client_obj.id),
                "title": "Contratto Demo",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "attachment": self._file("contract.pdf"),
            },
            format="multipart",
        )
        self.assertEqual(contract_resp.status_code, status.HTTP_201_CREATED)
        contract_url = contract_resp.data["attachment"]
        self.assertIn("contract.pdf", contract_url)
        self.assertTrue(default_storage.exists(self._storage_name(contract_url)))

    def test_invoice_items_and_pdf(self):
        opp = self._create_opportunity()
        offer = self.client.post(
            f"{API_BASE}/offers/",
            {
                "opportunity": opp["id"],
                "date": "2025-01-01",
                "valid_until": "2025-01-31",
                "items": [{"product_code": "X", "description": "Prod", "quantity": 1, "unit_price": "50.00", "discount": "0"}],
            },
            format="json",
        ).data
        order = self.client.post(
            f"{API_BASE}/orders/",
            {"from_offer": offer["id"], "date": "2025-02-01"},
            format="json",
        ).data
        inv_payload = {
            "order": order["id"],
            "date": "2025-02-10",
            "due_date": "2025-03-10",
            "items": [
                {"product": "Prod1", "description": "Desc1", "quantity": 2, "unit_price": "10.00", "tax_rate": "5.00"},
                {"product": "Prod2", "description": "Desc2", "quantity": 1, "unit_price": "30.00", "tax_rate": "20.00"},
            ],
            "terms_and_conditions": "Pagamento a 30gg",
        }
        resp = self.client.post(f"{API_BASE}/invoices/", inv_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        inv = resp.data
        self.assertEqual(len(inv["items"]), 2)
        self.assertEqual(Decimal(inv["total_amount"]), Decimal("50.00"))

        pdf_resp = self.client.get(f"{API_BASE}/invoices/{inv['id']}/pdf/")
        self.assertEqual(pdf_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_resp["Content-Type"], "application/pdf")

    def test_missing_links_return_400(self):
        # Offer without opportunity
        resp_offer = self.client.post(
            f"{API_BASE}/offers/",
            {"date": "2025-01-01", "valid_until": "2025-01-31"},
            format="json",
        )
        self.assertEqual(resp_offer.status_code, status.HTTP_400_BAD_REQUEST)

        # Order without offer
        resp_order = self.client.post(
            f"{API_BASE}/orders/",
            {"date": "2025-02-01"},
            format="json",
        )
        self.assertEqual(resp_order.status_code, status.HTTP_400_BAD_REQUEST)

        # Invoice without order
        resp_invoice = self.client.post(
            f"{API_BASE}/invoices/",
            {"date": "2025-02-15", "due_date": "2025-03-15"},
            format="json",
        )
        self.assertEqual(resp_invoice.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_offer_and_opportunity(self):
        opp = self._create_opportunity()
        offer = self.client.post(
            f"{API_BASE}/offers/",
            {"opportunity": opp["id"], "date": "2025-01-01", "valid_until": "2025-01-31"},
            format="json",
        ).data
        del_resp = self.client.delete(f"{API_BASE}/offers/{offer['id']}/")
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        del_opp = self.client.delete(f"{API_BASE}/opportunities/{opp['id']}/")
        self.assertEqual(del_opp.status_code, status.HTTP_204_NO_CONTENT)

    def test_edit_client(self):
        resp = self.client.post(f"{API_BASE}/clients/", {"name": "Edit Me"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        cid = resp.data["id"]
        patch = self.client.patch(f"{API_BASE}/clients/{cid}/", {"city": "Roma"}, format="json")
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["city"], "Roma")
