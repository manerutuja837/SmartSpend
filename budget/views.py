from django.shortcuts import render, redirect,get_object_or_404
from django.forms import formset_factory
from .forms import IncomeForm,MonthSelectionForm, SavingsForm, BillForm, DailyExpenseForm, LoanForm, PaycheckPeriodForm
from .models import Income, Savings, Bill, DailyExpense, Loan, PaycheckPeriod
from django.db.models import Sum
from django.forms import modelformset_factory 
from django.http import JsonResponse
from ai21.models.chat import ChatMessage as AI21ChatMessage
from ai21 import AI21Client
import os

client = AI21Client(api_key=os.getenv("AI21_API_KEY"))

IncomeFormSet = formset_factory(IncomeForm, extra=0, can_delete=True)
SavingsFormSet = formset_factory(SavingsForm, extra=0, can_delete=True)
BillFormSet = formset_factory(BillForm, extra=0, can_delete=True)
DailyExpenseFormSet = formset_factory(DailyExpenseForm, extra=0, can_delete=True)
LoanFormSet = formset_factory(LoanForm, extra=0, can_delete=True)

def manage_finances(request):
    # Define formsets
    income_form_count = request.POST.get('income_form_count', 1)
    savings_form_count = request.POST.get('savings_form_count', 1)
    bill_form_count = request.POST.get('bill_form_count', 1)
    daily_expense_form_count = request.POST.get('expense_form_count', 1)
    loan_form_count = request.POST.get('loan_form_count', 1)

    if request.method == 'POST':
        paycheck_form = PaycheckPeriodForm(request.POST)
        income_formset = IncomeFormSet(request.POST, prefix='income')
        savings_formset = SavingsFormSet(request.POST, prefix='saving', initial=[{}] * int(savings_form_count))
        bill_formset = BillFormSet(request.POST, prefix='bills', initial=[{}] * int(bill_form_count))
        daily_expense_formset = DailyExpenseFormSet(request.POST, prefix='expenses', initial=[{}] * int(daily_expense_form_count))
        loan_formset = LoanFormSet(request.POST, prefix='loans', initial=[{}] * int(loan_form_count))

        # print("Paycheck Form Errors:", paycheck_form.errors)
        # print("Income Formset Errors:", income_formset.errors)
        # print("Savings Formset Errors:", savings_formset.errors)
        # print("Bills Formset Errors:", bill_formset.errors)
        # print("Expense Formset Errors:", daily_expense_formset.errors)
        # print("Loan Formset Errors:", loan_formset.errors)



        if (paycheck_form.is_valid() and income_formset.is_valid() and savings_formset.is_valid() and bill_formset.is_valid() and daily_expense_formset.is_valid() and loan_formset.is_valid()):
            # Save everything to the database
            start_date = paycheck_form.cleaned_data['start_date']
            end_date = paycheck_form.cleaned_data['end_date']

            if PaycheckPeriod.objects.filter(start_date=start_date, end_date=end_date).exists():
                print(request, "A budget for this time period already exists.")
                redirect(manage_finances)
            else:
                paycheck = paycheck_form.save(commit=False)
                paycheck.user = request.user
                paycheck.save()

                for form in income_formset:
                    if form.cleaned_data:
                        income = form.save(commit=False)
                        income.user = request.user
                        income.paycheck_period = paycheck
                        income.save()

                for form in savings_formset:
                    if form.cleaned_data:
                        saving = form.save(commit=False)
                        saving.user = request.user
                        saving.paycheck_period = paycheck
                        saving.save()

                for form in bill_formset:
                    if form.cleaned_data:
                        bill = form.save(commit=False)
                        bill.user = request.user
                        bill.paycheck_period = paycheck
                        bill.save()

                for form in daily_expense_formset:
                    if form.cleaned_data:
                        expense = form.save(commit=False)
                        expense.user = request.user
                        expense.paycheck_period = paycheck
                        expense.save()

                for form in loan_formset:
                    if form.cleaned_data:
                        loan = form.save(commit=False)
                        loan.user = request.user
                        loan.paycheck_period = paycheck
                        loan.save()

                return redirect('view_budget')  # Replace with your success URL

    else:
        paycheck_form = PaycheckPeriodForm()
        income_formset = IncomeFormSet(prefix='income', initial=[{}] * int(income_form_count))
        savings_formset = SavingsFormSet(prefix='saving', initial=[{}] * int(savings_form_count))
        bill_formset = BillFormSet(prefix='bills', initial=[{}] * int(bill_form_count))
        daily_expense_formset = DailyExpenseFormSet(prefix='expenses', initial=[{}] * int(daily_expense_form_count))
        loan_formset = LoanFormSet(prefix='loans', initial=[{}] * int(loan_form_count))

    return render(request, 'budget/manage_finances.html', {
        'paycheck_form': paycheck_form,
        'income_formset': income_formset,
        'saving_formset': savings_formset,
        'bill_formset': bill_formset,
        'daily_expense_formset': daily_expense_formset,
        'loan_formset': loan_formset,
        'income_form_count': income_form_count,
        'savings_form_count': savings_form_count,
        'bill_form_count': bill_form_count,
        'expense_form_count': daily_expense_form_count,
        'loan_form_count': loan_form_count,
    })


def view_budget(request):
    incomes_sum = savings_sum = bills_sum = daily_expenses_sum = loans_sum = 0
    left_to_spend = spent_amount = left_to_budget = budgeted_amount = 0
    if request.method == 'POST':
        form = MonthSelectionForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            month = form.cleaned_data['month']


        if month:
            # Parse the 'month' into a datetime object (assuming 'YYYY-MM' format)
            year, month = map(int, month.split('-'))
            # Filter the PaycheckPeriod objects by the selected year and month
            paycheck_periods = PaycheckPeriod.objects.filter(start_date__year=year,start_date__month=month)
            # Assuming a single paycheck period per month
            if paycheck_periods.exists():
                paycheck_period = paycheck_periods.first()
                incomes_sum = Income.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
                savings_sum = Savings.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
                bills_sum = Bill.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
                daily_expenses_sum = DailyExpense.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
                loans_sum = Loan.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
             

                incomes = Income.objects.filter(paycheck_period=paycheck_period)
                savings = Savings.objects.filter(paycheck_period=paycheck_period)
                bills = Bill.objects.filter(paycheck_period=paycheck_period)
                daily_expenses = DailyExpense.objects.filter(paycheck_period=paycheck_period)
                loans = Loan.objects.filter(paycheck_period=paycheck_period)

                spent_amount = bills_sum + daily_expenses_sum + loans_sum + savings_sum
         
                current_balance = 2000
                # Calculate the remaining budget
                left_to_spend = (current_balance + incomes_sum) - spent_amount
        
                # Calculate budgeted amount (savings + expenses)
                budgeted_amount =  spent_amount

                # Calculate remaining income after all deductions
                left_to_budget = incomes_sum - budgeted_amount


                paycheck_period = get_object_or_404(PaycheckPeriod, id=paycheck_period.id)


                
                context = {
                    'paycheck_period': paycheck_period,
                    'incomes': incomes,
                    'savings': savings,
                    'bills': bills,
                    'daily_expenses': daily_expenses,
                    'loans': loans,
                    'incomes_sum': incomes_sum,
                    'savings_sum': savings_sum,
                    'bills_sum': bills_sum,
                    'daily_expenses_sum': daily_expenses_sum,
                    'loans_sum': loans_sum,
                    'left_to_spend': left_to_spend,
                    'spent_amount': spent_amount,
                    'left_to_budget': left_to_budget,
                    'budgeted_amount': budgeted_amount,
                    'month_form': MonthSelectionForm()
                }
                return render(request, 'budget/view_budget.html', context)
    
    # Default to showing the form
    form = MonthSelectionForm()
    return render(request, 'budget/view_budget.html', {'month_form': form})

def edit_budget(request, budget_id):
    incomes_sum = savings_sum = bills_sum = daily_expenses_sum = loans_sum = 0
    left_to_spend = spent_amount = left_to_budget = budgeted_amount = 0
    paycheck_period = get_object_or_404(PaycheckPeriod, id=budget_id)

    income_form_count = request.POST.get('income_form_count', 1)
    savings_form_count = request.POST.get('savings_form_count', 1)
    bill_form_count = request.POST.get('bill_form_count', 1)
    daily_expense_form_count = request.POST.get('expense_form_count', 1)
    loan_form_count = request.POST.get('loan_form_count', 1)

    IncomeFormSet = modelformset_factory(Income, form=IncomeForm, extra=0, can_delete=True)
    SavingsFormSet = modelformset_factory(Savings, form=SavingsForm, extra=0, can_delete=True)
    BillFormSet = modelformset_factory(Bill, form=BillForm, extra=0, can_delete=True)
    DailyExpenseFormSet = modelformset_factory(DailyExpense, form=DailyExpenseForm, extra=0, can_delete=True)
    LoanFormSet = modelformset_factory(Loan, form=LoanForm, extra=0, can_delete=True)

    incomes_sum = Income.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
    savings_sum = Savings.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
    bills_sum = Bill.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
    daily_expenses_sum = DailyExpense.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
    loans_sum = Loan.objects.filter(paycheck_period=paycheck_period).aggregate(Sum('amount'))['amount__sum'] or 0
    
    spent_amount = bills_sum + daily_expenses_sum + loans_sum + savings_sum

    current_balance = 2000
    # Calculate the remaining budget
    left_to_spend = (current_balance + incomes_sum) - spent_amount

    # Calculate budgeted amount (savings + expenses)
    budgeted_amount =  spent_amount

    # Calculate remaining income after all deductions
    left_to_budget = incomes_sum - budgeted_amount


    if request.method == 'POST':
        paycheck_form = PaycheckPeriodForm(request.POST)
        income_formset = IncomeFormSet(request.POST, prefix='income', initial=[{}] * int(income_form_count))
        savings_formset = SavingsFormSet(request.POST, prefix='saving', initial=[{}] * int(savings_form_count))
        bill_formset = BillFormSet(request.POST, prefix='bills', initial=[{}] * int(bill_form_count))
        daily_expense_formset = DailyExpenseFormSet(request.POST, prefix='expenses', initial=[{}] * int(daily_expense_form_count))
        loan_formset = LoanFormSet(request.POST, prefix='loans', initial=[{}] * int(loan_form_count))


        if (paycheck_form.is_valid() and income_formset.is_valid() and savings_formset.is_valid() and bill_formset.is_valid() and daily_expense_formset.is_valid() and loan_formset.is_valid()):
            # Save everything to the database
            # start_date = paycheck_form.cleaned_data['start_date']
            # end_date = paycheck_form.cleaned_data['end_date']

            paycheck = paycheck_form.save(commit=False)
            paycheck.paycheck_period = paycheck_period 
            paycheck.id = budget_id
            paycheck_id = budget_id
   
            paycheck.user = request.user # Associate with the retrieved instance
            paycheck.save()

            for form in income_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    income = form.save(commit=False)
                    income.user = request.user
                    income.paycheck_period = paycheck
                    income.save()
                elif form.cleaned_data.get('DELETE', False):
                    form.instance.delete()

            for form in savings_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    saving = form.save(commit=False)
                    saving.user = request.user
                    saving.paycheck_period = paycheck
                    saving.save()
                elif form.cleaned_data.get('DELETE', False):
                    form.instance.delete()

            for form in bill_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    bill = form.save(commit=False)
                    bill.user = request.user
                    bill.paycheck_period = paycheck
                    bill.save()
                elif form.cleaned_data.get('DELETE', False):
                    form.instance.delete()

            for form in daily_expense_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    expense = form.save(commit=False)
                    expense.user = request.user
                    expense.paycheck_period = paycheck
                    expense.save()
                elif form.cleaned_data.get('DELETE', False):
                    form.instance.delete()

            for form in loan_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    loan = form.save(commit=False)
                    loan.user = request.user
                    loan.paycheck_period = paycheck
                    loan.save()
                elif form.cleaned_data.get('DELETE', False):
                    form.instance.delete()

            return redirect('view_budget')

    else:
        paycheck_form = PaycheckPeriodForm(instance=paycheck_period)
        income_formset = IncomeFormSet(queryset=Income.objects.filter(paycheck_period=paycheck_period),prefix='income', initial=[{}] * int(income_form_count))
        savings_formset = SavingsFormSet(queryset=Savings.objects.filter(paycheck_period=paycheck_period),prefix='saving', initial=[{}] * int(savings_form_count))
        bill_formset = BillFormSet(queryset=Bill.objects.filter(paycheck_period=paycheck_period),prefix='bills', initial=[{}] * int(bill_form_count))
        daily_expense_formset = DailyExpenseFormSet(queryset=DailyExpense.objects.filter(paycheck_period=paycheck_period),prefix='expenses', initial=[{}] * int(daily_expense_form_count))
        loan_formset = LoanFormSet(queryset=Loan.objects.filter(paycheck_period=paycheck_period),prefix='loans', initial=[{}] * int(loan_form_count))


    context = {
        'paycheck_form': paycheck_form,
        'income_formset': income_formset,
        'savings_formset': savings_formset,
        'bill_formset': bill_formset,
        'daily_expense_formset': daily_expense_formset,
        'loan_formset': loan_formset,
        'paycheck_period': paycheck_period,
        'income_form_count': income_form_count,
        'savings_form_count': savings_form_count,
        'bill_form_count': bill_form_count,
        'expense_form_count': daily_expense_form_count,
        'loan_form_count': loan_form_count,
        'incomes_sum': incomes_sum,
        'savings_sum': savings_sum,
        'bills_sum': bills_sum,
        'daily_expenses_sum': daily_expenses_sum,
        'loans_sum': loans_sum,
        'left_to_spend': left_to_spend,
        'spent_amount': spent_amount,
        'left_to_budget': left_to_budget,
        'budgeted_amount': budgeted_amount,
    }


    return render(request,'budget/edit_budget.html',context)

def handle_conversation(prompt):
    # Create completions using AI21Client
    response = client.chat.completions.create(
        model="jamba-instruct-preview",
        messages=[AI21ChatMessage(   # Single message with a single prompt
            role="user",
            content=prompt
    )],
        n=1,
        max_tokens=500,
        temperature=0.7,
        stop=[],
    )
    return response.choices[0].message.content

def prepare_detailed_data(detailed_data):
    prompt = """
    Please analyze the following budget details:

    Income: {}
    Expenses: {}
    Bills: {}
    Savings: {}
    Loans/Debts: {}
    Based on this information, I would like recommendations on:

    1. Areas where I can cut down on expenses.
    2. How I can adjust my savings to better meet my financial goals.
    3. Opportunities to save more on bills or loan payments.
    4. General financial strategies to increase my savings over time.(Recommend InvestAI for getting investment plans.)

    Please provide the analysis and recommendations in HTML format. Use ordered or unordered lists for clarity. Highlight key points with <b> tags, and use <br> for line breaks between sections. Ensure the HTML is well-structured and readable.
    <ul> for bullet points.
    <ol> for numbered steps.
    <b> to highlight important information.
    <br> for line breaks between sections.
    dont use any css for it.
    """.format(
        "\n".join(detailed_data.get('Income', [])),
        "\n".join(detailed_data.get('Expenses', [])),
        "\n".join(detailed_data.get('Bills', [])),
        "\n".join(detailed_data.get('Savings', [])),
        "\n".join(detailed_data.get('Loans', []))
    )

    return prompt

def analyze_budget(request):
    
    if request.method == 'POST':
       
        # Get formset data from the request
        income_formset = IncomeFormSet(request.POST, prefix='income')
        expense_formset = DailyExpenseFormSet(request.POST, prefix='expenses')
        saving_formset = SavingsFormSet(request.POST, prefix='saving')
        bill_formset = BillFormSet(request.POST, prefix='bills')
        loan_formset = LoanFormSet(request.POST, prefix='loans')

        detailed_data = {
            'Income': [],
            'Expenses': [],
            'Savings': [],
            'Bills': [],
            'Loans': []
        }

        if income_formset.is_valid():
            for form in income_formset:
                if form.cleaned_data:
                    amount = form.cleaned_data.get('amount', 0)
                    source = form.cleaned_data.get('source', 'Unknown Source')
                    detailed_data['Income'].append(f"{source}: Rs {amount:.2f}")
        
        # Collect expense data
        if expense_formset.is_valid():
            for form in expense_formset:
                if form.cleaned_data:
                    amount = form.cleaned_data.get('amount', 0)
                    description = form.cleaned_data.get('description', 'Unknown Description')
                    detailed_data['Expenses'].append(f"{description}: Rs {amount:.2f}")

        # Collect saving data
        if saving_formset.is_valid():
            for form in saving_formset:
                if form.cleaned_data:
                    amount = form.cleaned_data.get('amount', 0)
                    purpose = form.cleaned_data.get('purpose', 'Unknown Purpose')
                    detailed_data['Savings'].append(f"{purpose}: Rs {amount:.2f}")

        # Collect bill data
        if bill_formset.is_valid():
            for form in bill_formset:
                if form.cleaned_data:
                    amount = form.cleaned_data.get('amount', 0)
                    description = form.cleaned_data.get('description', 'Unknown Description')
                    detailed_data['Bills'].append(f"{description}: Rs {amount:.2f}")

        # Collect loan data
        if loan_formset.is_valid():
            for form in loan_formset:
                if form.cleaned_data:
                    amount = form.cleaned_data.get('amount', 0)
                    description = form.cleaned_data.get('description', 'Unknown Description')
                    detailed_data['Loans'].append(f"{description}: Rs {amount:.2f}")

    
        prompt = prepare_detailed_data(detailed_data)


        # messages = []
        # messages.append(AI21ChatMessage(content=prompt, role="assistant"))
        # print("Messages:", messages)

        try:
            ai_response = handle_conversation(prompt)
         
            return JsonResponse({'result': ai_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'budget/manage_finances.html')