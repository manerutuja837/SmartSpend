from django.shortcuts import render, redirect
from django.views import View
import json
from transactions.models import BankAccount
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator

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

# Create your views he
class UsernameValidationView(View):
    def post(self,request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'Username should only contain alphanumeric values'},status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Sorry username is in use'},status=409)

        return JsonResponse({'username_valid':True})

class EmailValidationView(View):
    def post(self,request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'},status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Sorry email is in use'},status=409)

        return JsonResponse({'email_valid':True})

class RegisterationView(View):
    def get(self,request):
        return render(request,'authentication/register.html')

    def post(self,request):

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues':request.POST,
        }

        if not User.objects.filter(username = username).exists():
            if not User.objects.filter(email = email).exists():
                if len(password) < 6:
                    messages.error(request,'Password is too short...')
                    return render(request,'authentication/register.html',context)

                user = User.objects.create_user(username=username, email=email)
                
                user.set_password(password)
                user.is_active = False
                user.save()

                bank_account = BankAccount.objects.create(user=user,account_number="",current_balance=0)
            
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain
                link = reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
                activate_url = 'http://'+domain+link

                email_subject = 'Activate your SmartSpend account'
                email_body = 'Hi '+ user.username +'Please use this link to activate your account\n'+activate_url
                # email = EmailMessage(
                # email_subject,
                # email_body,
                # "noreply@semicolon.com",
                # [email],
                # )
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]
                #send_mail(email_subject,email_body,from_email,recipient_list)
                email_thread = EmailThread(email_subject, email_body, from_email, recipient_list)
                email_thread.start()
                messages.success(request,'Account created Successfully...')
                return render(request,'authentication/register.html')

        return render(request,'authentication/register.html')

class VerificationView(View):
    def get(self,request,uidb64,token):

        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk = id)
            if not token_generator.check_token(user,token):
                return redirect('login'+'?message'+'User already activated')

            if user.is_active :
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request,"Account activatedd Successfully...")
            return redirect('login')

        except Exception as ex:
            pass
    
        return redirect('login')

class LoginView(View):
    def get(self,request):
        return render(request,'authentication/login.html')

    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password :
            user = auth.authenticate(username=username,password=password)

            if user:
                if user.is_active:
                    auth.login(request,user)
                    messages.success(request,'Welcome '+user.username+' you are now logged in...')
                    return redirect('expenses')

                messages.error(request,'Account is not active, please check your email and activate it.')
                return render(request,'authentication/login.html')
            
            messages.error(request,'Invalid Credentials...')
            return render(request,'authentication/login.html')

        messages.error(request,'Please fill all fields.')
        return render(request,'authentication/login.html')


class LogoutView(View):
    def post(self,request):
        auth.logout(request)
        messages.success(request,'You have logged out successfully...')
        return redirect('login')


class RequestPasswordResetEmail(View):
    def get(self,request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):

        email = request.POST['email']
        context = {
            'values' : request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please submit a valid email')
            return render(request, 'authentication/reset-password.html',context)

        domain = get_current_site(request).domain

        user = User.objects.filter(email=email)

        if user.exists():
            user = user[0]
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            link = reverse('reset-user-password',kwargs={'uidb64':uidb64,'token':PasswordResetTokenGenerator().make_token(user)})
            reset_url = 'http://'+domain+link

            email_subject = 'Reset password of SmartSpend Account'
            email_body = 'Hi '+ user.username +' Please use this link to reset your account password \n'+reset_url
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            email_thread = EmailThread(email_subject, email_body, from_email, recipient_list)
            email_thread.start()
            
        messages.success(request,'We have sent you an email')

        

        return render(request, 'authentication/reset-password.html',context)


class CompletePassswordReset(View):
    def get(self, request, uidb64, token):

        context = {
            'uidb64' : uidb64,
            'token' : token,
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk = user_id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request,'Link is invalid, Please request a new link')
                return render(request, 'authentication/reset-password.html')
        except Exception  as identifier:
            import pdb
            pdb.set_trace()
            messages.info(request,'Something went wrong')
            return render(request, 'authentication/set-new-password.html',context)

        return render(request, 'authentication/set-new-password.html',context)

    def post(self, request, uidb64, token):

        context = {
            'uidb64' : uidb64,
            'token' : token,
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2 :
            messages.error(request,'Passwords do not match, Please re-enter')
            return render(request, 'authentication/set-new-password.html',context)

        if len(password) < 6 :
            messages.error(request,'Password too short')
            return render(request, 'authentication/set-new-password.html',context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk = user_id)
            user.set_password(password)
            user.save()

            messages.success(request,'Password reset successfully')
            return redirect('login')
        except Exception  as identifier:
            messages.info(request,'Something went wrong')
            return render(request, 'authentication/set-new-password.html',context)
        

        #return render(request, 'authentication/set-new-password.html',context)


