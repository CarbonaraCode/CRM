from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ClientViewSet,
    ContactViewSet,
    OpportunityViewSet,
    OfferViewSet,
    OfferItemViewSet,
    SaleOrderViewSet,
    InvoiceViewSet,
    ContractViewSet,
)

router = DefaultRouter()
router.register(r"clients", ClientViewSet)
router.register(r"contacts", ContactViewSet)
router.register(r"opportunities", OpportunityViewSet)
router.register(r"offers", OfferViewSet)
router.register(r"offer-items", OfferItemViewSet)
router.register(r"orders", SaleOrderViewSet)
router.register(r"invoices", InvoiceViewSet)
router.register(r"contracts", ContractViewSet)

urlpatterns = [path("", include(router.urls))]
