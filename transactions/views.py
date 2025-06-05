from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category, BankAccount
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
# from userpreferences.models import UserPreference
import datetime
from datetime import datetime, timedelta
import csv
import pandas as pd
import re
import xml.etree.ElementTree as ET
from .utils import parse_sms_xml, save_transactions
from django.db.models import Q
import uuid
from django.db.models import Sum, F
from django.utils.timezone import now, timedelta


def Search_Expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        bank_account = BankAccount.objects.get(user=request.user)

        expenses = Transaction.objects.filter(
            Q(amount__icontains=search_str) |  # Use icontains in case of numeric string
            Q(timestamp__icontains=search_str) |   # This assumes date is being compared as a string
            Q(category__icontains=search_str) |
            Q(description__icontains=search_str),
            account=bank_account  # Corrected typo
        )

        data = list(expenses.values())  # Ensure data is converted to a list
        return JsonResponse(data, safe=False)

# Create your views here.
@login_required(login_url='/authentication/login/')
def Index(request):
    bank_account = BankAccount.objects.get(user=request.user)
    expenses = Transaction.objects.filter(account = bank_account)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    # currency = UserPreference.objects.get(user=request.user).currency
    context={
        'expenses' : expenses,
        'page_obj' : page_obj,
        # 'currency': currency,
        'bank_account' : bank_account,
    }
    return render(request,'expenses/index.html',context)

def Add_Expense(request):
    categories = Category.objects.all()
    bank_account = BankAccount.objects.get(user=request.user)
    
    context = {
        'categories' : categories,
        'values' : request.POST,
    }
    if request.method=='GET':
        return render(request,'expenses/add_expenses.html',context)
    if request.method=='POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        payment_type = request.POST['payment_type']

        if not amount:
            messages.error(request,"Amount is required...")
            return render(request,'expenses/add_expenses.html',context)

        if not description:
            messages.error(request,"Description is required...")
            return render(request,'expenses/add_expenses.html',context)
    transaction_id = str(uuid.uuid4())
    Transaction.objects.create(transaction_id=transaction_id,amount=amount, timestamp=date, description=description,account = bank_account, category=category, transaction_type='debit')
    expenses = Transaction.objects.filter(account=bank_account)
    for expense in expenses:
        if expense.is_debited == False:
            if expense.transaction_type == 'debit':
                bank_account.current_balance -= expense.amount
                expense.is_debited = True
                expense.save()
            elif expense.transaction_type == 'credit':
                bank_account.current_balance += expense.amount
                expense.is_debited = True
                expense.save()
    bank_account.save()
    messages.success(request,"Expense Saved Successfully")

    return redirect('expenses')

def Edit_Expense(request,id):
    expense = Transaction.objects.get(pk = id)
    bank_account = BankAccount.objects.get(user=request.user)
    # expense = get_object_or_404(Transaction, id=transaction_id)
    categories = Category.objects.all()
    context = {
        'expense' : expense,
        'values' : expense,
        'categories' : categories,
    }
    if request.method == 'GET':
        return render(request,'expenses/edit-expense.html',context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not amount:
            messages.error(request,"Amount is required...")
            return render(request,'expenses/add_expenses.html',context)

        if not description:
            messages.error(request,"Description is required...")
            return render(request,'expenses/add_expenses.html',context)

        expense.amount=amount
        expense.timestamp=date 
        expense.description=description
        expense.account= bank_account
        expense.category=category

        expense.save()

        messages.success(request,"Expense Updated Successfully")

        return redirect('expenses')

def Delete_Expense(request,id):
    expense = Transaction.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense deleted successfully')
    return redirect('expenses')
    
def Expense_category_summary(request):
    today = datetime.today()
    todays_date = today.date()
    six_months_ago = todays_date - timedelta(days = 30*6)
    bank_account = BankAccount.objects.get(user=request.user)
    expenses = Transaction.objects.filter(account= bank_account, date__gte = six_months_ago, date__lte = todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category,expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount

        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)
    return JsonResponse({'expense_category_data': finalrep},safe=False)


def stats_view(request):
    today = now().date()

    # Calculate the start of the current week (Monday) and month
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Weekly transactions
    weekly_transactions = Transaction.objects.filter(timestamp__date__gte=start_of_week)

    # Monthly transactions
    monthly_transactions = Transaction.objects.filter(timestamp__date__gte=start_of_month)

    
    # Group by category and payment type, sum the amounts
    weekly_analysis = weekly_transactions.values(
        grouped_category=F('category'),
        grouped_payment_type=F('payment_type')
    ).annotate(total_amount=Sum('amount'))


    monthly_analysis = monthly_transactions.values(
        grouped_category=F('category'),
        grouped_payment_type=F('payment_type')
    ).annotate(total_amount=Sum('amount'))

    context = {
        'weekly_analysis': weekly_analysis,
        'monthly_analysis': monthly_analysis,
    }
    return render(request,'expenses/stats.html',context)

def export_csv(request):
    bank_account = BankAccount.objects.get(user=request.user)
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename+Expenses' + str(datetime.now()) +'.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])

    expenses = Transaction.objects.filter(account= bank_account)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.timestamp])
    return response

def import_sms(request):
    if request.method == 'POST':
        file = request.FILES['xml_file']
        bank_account = BankAccount.objects.get(user=request.user)

        if file :
            # Parse the XML file
            transactions = parse_sms_xml(file,request.user)

            # Save transactions without duplicates
            save_transactions(transactions,bank_account)

            messages.success(request, 'SMS file uploaded and transactions processed successfully!')
            expenses = Transaction.objects.filter(account=bank_account)
            for expense in expenses:
                if expense.is_debited == False:
                    if expense.transaction_type == 'debit':
                        bank_account.current_balance -= expense.amount
                        expense.is_debited = True
                        expense.save()
                    elif expense.transaction_type == 'credit':
                        bank_account.current_balance += expense.amount
                        expense.is_debited = True
                        expense.save()
            bank_account.save()
            return redirect('expenses')
        else:
            form = FileUploadForm()  
    return render(request, 'expenses/index.html',{'form':form})