from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Client, Opportunity, Offer, SaleOrder, Invoice


API_BASE = "/api/sales"


class SalesApiTests(APITestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(name="Test Client", email="client@test.com")

    def tearDown(self):
        Invoice.objects.all().delete()
        SaleOrder.objects.all().delete()
        Offer.objects.all().delete()
        Opportunity.objects.all().delete()
        Client.objects.all().delete()

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

    def _create_opportunity(self):
        return self.client.post(
            f"{API_BASE}/opportunities/",
            {"client": str(self.client_obj.id), "name": "Main Opp"},
            format="json",
        ).data

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
