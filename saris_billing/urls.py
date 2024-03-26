from django.urls import path
from .apps import SarisBillingConfig
from .views import *

app_name = SarisBillingConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('invoice/create', CreateInvoiceView.as_view(), name='invoice.create'),
    path('invoice/bulk_create', CreateBulkInvoiceView.as_view(), name='invoice.bulk_create'),
    path('invoice/browse', InvoiceListView.as_view(), name='invoice.browse'),
    path('invoice/search', SearchInvoiceView.as_view(), name='invoice.search'),
    path('invoice/<uuid:pk>', InvoiceDetailsView.as_view(), name='invoice.details'),
    path('invoice/<uuid:pk>/cancel', CancelInvoiceView.as_view(), name='invoice.cancel'),
    path('invoice/payment', InvoicePaymentView.as_view(), name='invoice.payment'),
    
    path('transaction/credit', CreditStudentView.as_view(), name='transaction.credit'),
    path('transaction/debit', DebitStudentView.as_view(), name='transaction.debit'),
    path('transaction/import', ImportTransactionView.as_view(), name='transaction.import'),
    path('transaction/excel', ExcelTemplateView.as_view(),name='transaction.excel'),
    
    path('wallet', SearchWalletView.as_view(), name='wallet.search'),
    path('wallet/<uuid:pk>', WalletView.as_view(), name='wallet.browse'),
   
]
