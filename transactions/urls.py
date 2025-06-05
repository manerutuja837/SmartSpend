from django.contrib import admin
from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.Index, name = 'expenses'),
    path('add-expenses/', views.Add_Expense, name='add_expenses'),
    path('expense_edit/<int:id>', views.Edit_Expense, name='edit_expense'),
    path('expense_delete/<int:id>', views.Delete_Expense, name='delete_expense'),
    path('search_expenses/', csrf_exempt(views.Search_Expenses), name='search_expenses'),
    path('expense_category_summary/', views.Expense_category_summary, name='expense_category_summary'),
    path('stats/', views.stats_view, name='stats'),
    path('download/', views.export_csv, name='export_csv'),
    path('import_sms/', views.import_sms, name='import_sms'),
]
