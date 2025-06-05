from .views import RegisterationView, UsernameValidationView, EmailValidationView, VerificationView, LoginView, LogoutView, RequestPasswordResetEmail, CompletePassswordReset
from django.views.decorators.csrf import csrf_exempt
from django.urls import path,include

urlpatterns = [
    path('register/', RegisterationView.as_view(), name = 'register'),
    path('validate-username/', csrf_exempt(UsernameValidationView.as_view()),name = 'validate-username'),
    path('validate-email/', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('activate/<uidb64>/<token>/',VerificationView.as_view(), name="activate"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('request-reset-link/', RequestPasswordResetEmail.as_view(), name="request_reset_link"),
     path('reset/<uidb64>/<token>/',CompletePassswordReset.as_view(), name="reset-user-password"),
]
