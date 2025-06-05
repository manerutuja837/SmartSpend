from django.contrib import admin
from .models import Wallet, Transaction, WithdrawalRequest
import logging
from django.conf import settings
from userProfile.models import UserProfile
from django.core.mail import EmailMessage
from django.core.mail import send_mail
import threading

class EmailThread(threading.Thread):
    def __init__(self, email_subject, email_body, from_email, recipient_list):
        self.email_subject = email_subject
        self.email_body = email_body
        self.from_email = from_email
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.email_subject, self.email_body, self.from_email, self.recipient_list)


logger = logging.getLogger(__name__)
# Register your models here.

admin.site.register(Wallet)
admin.site.register(Transaction)
@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'status', 'timestamp')
    actions = ['approve_withdrawals']

    def approve_withdrawals(self, request, queryset):
        for withdrawal in queryset:
            logger.info(f"Processing withdrawal request for {withdrawal.user.username}: {withdrawal.amount}")
            if withdrawal.status == WithdrawalRequest.PENDING:
                wallet = Wallet.objects.get(user=withdrawal.user)
                user = withdrawal.user
                user_profile = UserProfile.objects.get(user=request.user)
                recipient = user_profile.email
                logger.info(f"Current wallet balance: {wallet.balance}")
                
                if wallet.balance >= withdrawal.amount:
                    wallet.balance -= withdrawal.amount
                    wallet.save()
                    logger.info(f"New wallet balance after withdrawal: {wallet.balance}")

                    Transaction.objects.create(
                        wallet=wallet,
                        transaction_type='WITHDRAWAL',
                        amount=withdrawal.amount
                    )
                    logger.info(f"Withdrawal transaction created for {withdrawal.amount}")

                    withdrawal.status = WithdrawalRequest.APPROVED
                    withdrawal.save()
                    logger.info(f"Withdrawal request status updated to APPROVED")
                    email_subject = 'SmartSpend Withdrawal Request Approved'
                    amount = str(withdrawal.amount)
                    email_body = 'Hi '+ user.username +' Your request for withdrawal for amount Rs.'+amount+' has been approved.\nThe amount will be credited to your account within 2 hours.\nThank you'
                    
                    from_email = settings.EMAIL_HOST_USER
                    email = recipient
                    recipient_list = [email]
                    #send_mail(email_subject,email_body,from_email,recipient_list)
                    email_thread = EmailThread(email_subject, email_body, from_email, recipient_list)
                    email_thread.start()
                else:
                    logger.error(f"Insufficient funds for {withdrawal.user.username}.")
    logger.info("All withdrawal requests processed.")