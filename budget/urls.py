from django.urls import path
from .views import manage_finances,view_budget, edit_budget, analyze_budget

urlpatterns = [
    path('', manage_finances, name='manage_finances'),
    path('view-budget/', view_budget, name='view_budget'),
    path('edit-budget/<int:budget_id>/', edit_budget, name='edit_budget'),
    path('analyze_budget/', analyze_budget, name='analyze_budget'),
]
