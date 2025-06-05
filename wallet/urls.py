from django.urls import path
from . import views


urlpatterns = [
    path('', views.wallet_dashboard, name='wallet_dashboard'),
    path('add-funds/', views.add_funds, name='add_funds'),
    path('withdraw/', views.withdrawal_request_view, name='withdraw_funds'),
    path('fund_success/', views.fund_success, name='fund_success'),
]
