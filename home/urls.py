from django.urls import path
from home import views

urlpatterns = [
    path('', views.index, name="Home"),
    path('contact', views.contact, name="Contact"),
    # path('fixme', views.fixme, name="Fix"),
    path('login', views.handleLogin, name="Login"),
    path('forget-password', views.forget_password, name="ForgetPassword"),
    path('logout', views.handleLogout, name="Logout"),
    path('signup', views.signup, name="Signup"),
    path('plans', views.pricing_plans, name="PricingPlans"),
    path('verify', views.verify_email, name="VerifyEmail"),
    path('verify_email', views.verifyemail, name="VerifyEmail2"),
    path('password_change', views.password_change, name="PasswordChange"),
    path('checkout', views.checkout, name="Checkout"),
    path('resend_code', views.resend_code, name="ResendCode"),
    # path('payment', views.payment, name="Payment"),
    path('callback', views.callback, name="Callback"),
]