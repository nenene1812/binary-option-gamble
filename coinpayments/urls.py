from django.urls import path
from . import views


urlpatterns = [
    path('coin-address',views.WalletAddressAPIView.as_view(),name="walletaddress"),
    path('update-address',
            views.UpdateWaddressAPI.as_view(),name="update-address"),
    path('deposit',
            views.DepositAPI.as_view(),name="deposit"),
    path('withdraw',
            views.WithdrawAPI.as_view(),name="withdraw"),
    path('invoice',
            views.InvoiceViewAPI.as_view(),name="invoice"),
    path('balance',
            views.BalancesViewAPI.as_view(),name="balance"),
    path('ipn-view', views.IPNView.as_view(),
          name="ipn-view"),
]