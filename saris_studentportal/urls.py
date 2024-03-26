from django.urls import path
from .apps import SarisStudentportalConfig
from .views import *

app_name = SarisStudentportalConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view() , name='home'),
    path('finance/mywallet', WalletView.as_view() , name='wallet'),
    path('finance/invoices', InvoiceListView.as_view() , name='invoices'),
    path('finance/invoices/clearbalance', ClearBalanceView.as_view() , name='clear_balance'),
    path('finance/invoices/<uuid:pk>', InvoiceDetailsView.as_view(), name='invoice'),
    path('finance/invoices/payment', InvoicePaymentView.as_view(), name='settle_invoice'),
    path('finance/payments', PaymentListView.as_view() , name='payments'),
    path('finance/payments/<uuid:pk>', PaymentDetailsView.as_view(), name='payment'),

    path('dpo/payment/create', DPOCreatePaymentView.as_view(), name='dpo_create_payment'),
    path('dpo/payment/verify', DPOVerifyPaymentView.as_view(), name='dpo_verify_payment'),
    path('dpo/payment/cancel', DPOCancelPaymentView.as_view(), name='dpo_cancel_payment'),

    path('registration', RegistrationView.as_view() , name='registration'),
    path('registration/register', RegisterView.as_view() , name='register'),
    path('registration/register/checkout', RegisterCheckoutView.as_view() , name='register_checkout'),
    path('supplementary', SupplementaryView.as_view() , name='supplementary'),
    path('supplementary/checkout', SupplementaryCheckoutView.as_view() , name='supplementary_checkout'),
    
    path('courses', CourseListView.as_view() , name='courses'),
    path('exams/permit', ExamPermitView.as_view() , name='exam_permit'),
    path('exams/permit/download', DownloadExamPermitView.as_view() , name='download_exam_permit'),
    path('exams/results', ExamResultsView.as_view() , name='exam_results'),

    path('academics/statement', ResultStatementView.as_view() , name='result_statement'),

    path('transfers', TransferListView.as_view(), name='transfers'),
    path('transfers/change_campus', ChangeCampusView.as_view(), name='change_campus'),
    path('transfers/change_program', ChangeProgramView.as_view(), name='change_program'),
    path('transfers/<uuid:pk>', TransferDetailsView.as_view(), name='transfer_details'),
    path('transfers/<uuid:pk>/cancel', CancelTransferView.as_view(), name='cancel_transfer'),

    path('appeals', CourseAppealListView.as_view(), name='course_appeals'),
    path('appeals/<uuid:pk>', CourseAppealDetailsView.as_view(), name='course_appeal_details'),
    path('appeals/grade_correction', GradeCorrectionView.as_view(), name='grade_correction'),
    path('appeals/course_remark', CourseRemarkView.as_view(), name='course_remark'),
    path('appeals/course_remark/checkout', CourseRemarkCheckoutView.as_view(), name='course_remark_checkout'),
    path('appeals/course_remark/cancel', CourseRemarkCancelView.as_view(), name='course_remark_cancel'),

    path('withdrawals', WithdrawaListView.as_view(), name='withdrawals'),
    path('withdrawals/<uuid:pk>', WithdrawalDetailsView.as_view(), name='withdrawal_details'),

]
