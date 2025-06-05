from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wallet, Transaction, WithdrawalRequest
from .forms import WithdrawalForm
from django.contrib import messages
from decimal import Decimal 
from django.contrib import admin
from django.conf import settings
from userProfile.models import UserProfile
from django.core.mail import EmailMessage
from django.core.mail import send_mail
import threading
from django.http import HttpResponseRedirect
from django.urls import reverse
from decimal import Decimal, InvalidOperation


class EmailThread(threading.Thread):
    def __init__(self, email_subject, email_body, from_email, recipient_list):
        self.email_subject = email_subject
        self.email_body = email_body
        self.from_email = from_email
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.email_subject, self.email_body, self.from_email, self.recipient_list)



def wallet_dashboard(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)  # Get or create a wallet for the user
    transactions = wallet.transactions.all()  # Get all wallet transactions

    user_requests = WithdrawalRequest.objects.filter(user=request.user)
    return render(request, 'wallet/dashboard.html', {
        'wallet': wallet,
        'transactions': transactions,
        'user_requests': user_requests,
    })


def add_funds(request):
    user = request.user 
    wallet, created = Wallet.objects.get_or_create(user=user)
    user_profile = UserProfile.objects.get(user=request.user)
    recipient = user_profile.email
    print(recipient)
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))  # Convert the input to Decimal
        except (ValueError, InvalidOperation):
            amount = Decimal(0)  # Handle invalid input

        if amount > 0:
            # Add funds to the wallet (both are Decimals now)
            wallet.balance += amount
            wallet.save()

            # Record a transaction
            Transaction.objects.create(wallet=wallet, transaction_type='DEPOSIT', amount=amount)
            email_subject = 'SmartSpend Wallet'
            amount = str(amount)
            email_body = 'Hi '+ user.username +' You have deposited amount Rs.'+amount+' to your SmartSpend Wallet.\n The amount will be credited to your Wallet within 2 hours.\n Thank you'
            
            from_email = settings.EMAIL_HOST_USER
            email = recipient
            recipient_list = [email]
            #send_mail(email_subject,email_body,from_email,recipient_list)
            email_thread = EmailThread(email_subject, email_body, from_email, recipient_list)
            email_thread.start()

            messages.success(request, f"Successfully added {amount} to the wallet!")
            url = reverse('wallet_dashboard')  # Reverse lookup for the wallet dashboard URL
            query_string = '?success=true'
            return HttpResponseRedirect(f"{url}{query_string}")

    return render(request, 'wallet/add_funds.html')

# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

# def add_funds(request):
#     user = request.user if request.user.is_authenticated else get_demo_user()
#     wallet, created = Wallet.objects.get_or_create(user=user)
    
#     if request.method == 'POST':
#         amount = Decimal(request.POST.get('amount', '0'))

#         if amount > 0:
#             # Create an order with Razorpay
#             amount_in_paisa = int(amount * 100)  # Razorpay expects amount in paisa (not rupees)
#             razorpay_order = razorpay_client.order.create({
#                 "amount": amount_in_paisa,
#                 "currency": "INR",
#                 "payment_capture": "1",  # Auto capture payment
#             })

#             # Pass these values to the template for the Razorpay checkout form
#             context = {
#                 'order_id': razorpay_order['id'],
#                 'razorpay_key': settings.RAZORPAY_API_KEY,
#                 'amount': amount_in_paisa,
#                 'wallet': wallet,
#             }
#             return render(request, 'wallet/razorpay_payment.html', context)

#     return render(request, 'wallet/add_funds.html')


# def verify_payment(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         payment_id = data.get('payment_id')
#         order_id = data.get('order_id')
#         amount = Decimal(data.get('amount'))

#         try:
#             razorpay_client.payment.capture(payment_id, int(amount * 100))
#             # Payment successful, update wallet balance
#             wallet = Wallet.objects.get(user=request.user)
#             wallet.balance += amount
#             wallet.save()

#             # Record transaction
#             Transaction.objects.create(wallet=wallet, transaction_type='DEPOSIT', amount=amount)

#             # Send confirmation email
#             email_subject = 'SmartSpend Wallet'
#             email_body = f"Hi {request.user.username}, you have deposited amount Rs. {amount} to your SmartSpend Wallet."
#             from_email = settings.EMAIL_HOST_USER
#             recipient_list = [request.user.email]
#             email_thread = EmailThread(email_subject, email_body, from_email, recipient_list)
#             email_thread.start()

#             return JsonResponse({'status': 'success'})
#         except razorpay.errors.BadRequestError:
#             return JsonResponse({'status': 'failure'}, status=400)
#     return JsonResponse({'status': 'invalid'}, status=400)


# def razorpay_callback(request):
#     if request.method == 'POST':
#         try:
#             # Extract the Razorpay payment details from the POST request
#             razorpay_payment_id = request.POST.get('razorpay_payment_id')
#             razorpay_order_id = request.POST.get('razorpay_order_id')
#             razorpay_signature = request.POST.get('razorpay_signature')
            
#             # Verify the Razorpay signature
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': razorpay_payment_id,
#                 'razorpay_signature': razorpay_signature
#             }
#             result = razorpay_client.utility.verify_payment_signature(params_dict)

#             if result is None:  # If signature verification is successful
#                 amount = Decimal(request.POST.get('amount'))  # Get the amount from the form
                
#                 # Retrieve the corresponding wallet
#                 wallet = Wallet.objects.get(user=request.user)

#                 # Add funds to the wallet
#                 wallet.balance += amount
#                 wallet.save()

#                 # Record the transaction
#                 Transaction.objects.create(wallet=wallet, transaction_type='DEPOSIT', amount=amount)

#                 messages.success(request, f"Successfully added {amount} to your wallet!")
#                 return redirect('wallet_success_page')  # Redirect to a success page
#             else:
#                 # Signature verification failed
#                 messages.error(request, "Payment verification failed!")
#                 return redirect('wallet_failure_page')
#         except Exception as e:
#             print(e)
#             return HttpResponseBadRequest()
#     else:
#         return HttpResponseBadRequest()


def fund_success(request):
    return render(request, 'fund_success.html')

def withdrawal_request_view(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        reason = request.POST.get('reason')
        wallet = Wallet.objects.get(user=request.user)

        user = request.user
        user_profile = UserProfile.objects.get(user=request.user)
        recipient = user_profile.email

        # Check if the requested amount is greater than the available balance
        if wallet.balance >= float(amount):
            # Create a withdrawal request
            withdrawal_request = WithdrawalRequest.objects.create(
                user=request.user,
                amount=amount,
                reason=reason,
            )
            email_subject = 'Withdrawal Request'
            email_body = 'Hi '+ user.username +' You have requested a withdrawal of amount Rs.'+amount+' from your SmartSpend Wallet.\n The amount will be credited to your account within 2 hours.\n Thank you'
            
            from_email = settings.EMAIL_HOST_USER
            email = recipient
            recipient_list = [email]
            #send_mail(email_subject,email_body,from_email,recipient_list)
            email_thread = EmailThread(email_subject, email_body, from_email, recipient_list)
            email_thread.start()
            messages.success(request, 'Withdrawal request submitted successfully.')
            return redirect('withdraw_funds')
        else:
            messages.error(request, 'Insufficient funds for this withdrawal request.')

    # Fetch the user's withdrawal requests
    user_requests = WithdrawalRequest.objects.filter(user=request.user)
    return render(request, 'wallet/withdrawal_funds.html', {'user_requests': user_requests})