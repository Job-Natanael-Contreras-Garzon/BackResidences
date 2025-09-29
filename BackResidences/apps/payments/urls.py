from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('payments/update/<int:pk>/', views.PaymentUpdateView.as_view(), name='payment-update'),
    path('payments/delete/<int:pk>/', views.PaymentDeleteView.as_view(), name='payment-delete'),
]