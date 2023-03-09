from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
     path('<str:room_name>/', views.room, name='room'),
     path('transaction',
            views.WfxTransactionAPIView.as_view(),name="transaction"),
    path('newtransaction',
            views.WfxTransactionAPI.as_view(),name="newtransaction"),
]