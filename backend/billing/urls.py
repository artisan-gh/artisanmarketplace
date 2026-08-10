# billing/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InvoiceViewSet,
    PaymentViewSet,
    CreditNoteViewSet,
    RecurringInvoiceViewSet,
    LedgerAccountViewSet,
    JournalEntryViewSet,
    BillingConfigViewSet,
    TaxViewSet,
    InvoiceTagViewSet,
    PaymentIntentViewSet,
)

app_name = 'billing'

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'credit-notes', CreditNoteViewSet, basename='credit-note')
router.register(r'recurring-invoices', RecurringInvoiceViewSet, basename='recurring-invoice')
router.register(r'ledger-accounts', LedgerAccountViewSet, basename='ledger-account')
router.register(r'journal-entries', JournalEntryViewSet, basename='journal-entry')
router.register(r'config', BillingConfigViewSet, basename='billing-config')
router.register(r'taxes', TaxViewSet, basename='tax')
router.register(r'tags', InvoiceTagViewSet, basename='invoice-tag')
router.register(r'payment-intents', PaymentIntentViewSet, basename='payment-intent')

urlpatterns = [
    path('', include(router.urls)),
]