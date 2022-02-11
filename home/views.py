from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import send_mail
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from home.models import Contact, User, Order, Profile
from home.decorators import is_not_logged_in, payment_started, user_email_verified, user_email_not_verified, user_email_in_session
import math, random
import json
from datetime import datetime, timedelta
import razorpay

from user.resources import create_s3_bucket

@is_not_logged_in
def index(request):
    return render(request, 'home/index.html')

# def fixme(request):
#     users = User.objects.all()
#     for user in users:
#         userp = Profile.objects.get(user=user)
#         userp.storage_limit = 5
#         print(user.email,' : ',userp.storage_limit)
#     print("all done")
#     return HttpResponse("It's done.")

def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        print(name, email, message)
        if len(name)<2 or len(email)<3 or len(message)<10:
            messages.error(request, 'Please fill the form correctly.')
            return redirect('Home')
        else:
            contact = Contact(name=name, email=email, message=message)
            contact.save()
            messages.success(request, ('Thank you for contacting us. We will get back to you soon.'))
            return redirect('Home')
    else:
        return redirect('Home')


def handleLogin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        print(email, password)

        if len(email)<3 or len(password)<3:
            messages.error(request, 'Please fill the form correctly.')
            return redirect('Login')

        user = User.objects.all().filter(email=email)
        if user.exists():
            user = user.first()
            if user.profile.is_verified:
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Successfully Logged In')
                    return redirect('Home')
                else:
                    messages.error(request, 'Invalid Credentials')
                    return redirect('Login')
            else:
                request.session['user_email'] = email

                messages.error(request, 'Please verify your email.')
                return redirect('VerifyEmail')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('Login')
    return render(request, 'home/login.html')

def handleLogout(request):
    logout(request)
    messages.success(request, 'Successfully Logged Out')
    return redirect('Login')

def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        print(name, email, password, password2)

        if len(name)<3 or len(email)<3 or len(password)<3 or len(password2)<3:
            messages.error(request, 'Please fill the form correctly.')
            return redirect('Signup')
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('Signup')

        user = User.objects.all().filter(email=email)
        if user.exists():
            messages.info(request, mark_safe('Email already exists. Please <a href="/login">login</a>.'))
            return redirect('Signup')
        else:
            user = User.objects.create_user(email=email, password=password, name=name)
            otp = generateOTP()
            print(otp)
            user.profile.otp = str(otp)
            user.profile.otp_sent_time = timezone.now()
            user.profile.otp_expiry_time = timezone.now() + timedelta(minutes=5)
            user.save()

            # create user session
            request.session['user_email'] = email
            print(request.session['user_email'], 'signup')

            # set session expiry to 20 minutes
            # request.session.set_expiry(1200)
            
            # # Send email
            subject = 'OTP Verification for Updatabox'
            message = 'Your OTP for Signup Verification of Secure Cloud Storage (Valid for 5 mins) is: '+str(otp)+'\nPlease do not share with anyone!'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            # send_mail( subject, message, email_from, recipient_list )

            messages.success(request, 'OTP sent to your email. Please verify your email.')
            return redirect('VerifyEmail')
    
    return render(request, 'home/signup.html')

@user_email_in_session
@user_email_not_verified
def verify_email(request):
    if request.method == 'POST':
        otpcode = request.POST.get('otpcode')
        print(otpcode)

        if otpcode == '':
            messages.error(request, 'OTP field is blank.')
            return redirect('VerifyEmail')

        user_email = request.session.get('user_email')
        print(user_email, 'verify email')

        if user_email == None or user_email == '' or user_email == 'None':
            messages.error(request, 'Please Signup first.')
            return redirect('Signup')
        else:
            user = User.objects.all().filter(email=user_email)
            print(user)
            if user.exists():
                user = user.first()
                print(user.profile.otp, otpcode)
                if user.profile.is_verified:
                    messages.info(request, 'Your email is already verified.')
                    return redirect('Login')
                if user.profile.otp == otpcode:
                    if timezone.now() > user.profile.otp_expiry_time:
                        messages.error(request, 'OTP has expired. Please generate a new OTP.')
                        return redirect('VerifyEmail')
                    else:
                        user.profile.is_verified = True
                        uid = user.id
                        uemail = user.email
                        getEmail = uemail.split('@')[0]
                        print(uid, uemail)
                        user.profile.bucket_name = 'id-' + str(uid) +'-'+ str(getEmail)
                        print(user.profile.bucket_name)
                        res = create_s3_bucket(user.profile.bucket_name)
                        if (res):
                            messages.success(request, 'Email verified successfully. Please choose a plan')
                        else:
                            messages.error(request, 'Error occurred. Please try again.')
                        user.save()
                        # messages.success(request, 'Email Verified. Please choose a plan.')
                        return redirect('PricingPlans')
                else:
                    messages.error(request, 'OTP does not match.')
                    return redirect('VerifyEmail')
            else:
                messages.error(request, 'Signup first.')
                return redirect('Signup')

    return render(request, 'home/email_verify.html')

def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        print(user)
        if(email == ''):
            messages.error(request,'Email field is left blank.')
            return redirect('ForgetPassword')
        if(user):
            otp = generateOTP()
            print(otp)
            user.profile.otp = str(otp)
            user.profile.otp_sent_time = timezone.now()
            user.profile.otp_expiry_time = timezone.now() + timedelta(minutes=5)
            user.save()

            # create user session
            request.session['user_email'] = email
            print(request.session['user_email'], 'fp')

            # set session expiry to 20 minutes
            # request.session.set_expiry(1200)
            
            # # Send email
            subject = 'OTP For Forgot Password'
            message = 'Your OTP for password forgot of Secure Cloud Storage (Valid for 5 mins) is: '+str(otp)+'\nPlease do not share with anyone!'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail( subject, message, email_from, recipient_list )

            messages.success(request, 'OTP sent to your email. Please verify your email.')
            return redirect('VerifyEmail2')
        else:
            messages.error(request, 'Please enter a correct email.')
            return redirect('ForgetPassword')
    return render(request, 'home/forget-password.html')

@user_email_in_session
def verifyemail(request):
    if request.method == 'POST':
        otpcode = request.POST.get('otpcode')
        print(otpcode)

        if otpcode == '':
            messages.error(request, 'OTP field is blank.')
            return redirect('VerifyEmail2')

        user_email = request.session.get('user_email')
        print(user_email, 'verify email')

        if user_email == None or user_email == '' or user_email == 'None':
            messages.error(request, 'Please Signup first.')
            return redirect('Signup')
        else:
            user = User.objects.all().filter(email=user_email)
            print(user)
            if user.exists():
                user = user.first()
                print(user.profile.otp, otpcode)
                if user.profile.is_verified:
                    if user.profile.otp == otpcode:
                        if timezone.now() > user.profile.otp_expiry_time:
                            messages.error(request, 'OTP has expired. Please generate a new OTP.')
                            return redirect('VerifyEmail2')
                        else:
                            messages.success(request, 'Email Verified. Please change password.')
                            return redirect('PasswordChange')
                    else:
                        messages.error(request, 'OTP does not match.')
                        return redirect('VerifyEmail2')
                else:
                    messages.info(request, 'Your email is not registered. Please signup first.')
                    return redirect('Signup')
            else:
                messages.error(request, 'Signup first.')
                return redirect('Signup')

    return render(request, 'home/verify_email.html')

def password_change(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('password_conf')
        print(password, confirm_password)
        if password == '' or confirm_password == '':
            messages.error(request, 'Password field is left blank.')
            return redirect('PasswordChange')
        if password != confirm_password:
            messages.error(request, 'Password and confirm password does not match.')
            return redirect('PasswordChange')
        else:
            user_email = request.session.get('user_email')
            print(user_email, 'verify email')

            if user_email == None or user_email == '' or user_email == 'None':
                messages.error(request, 'Please Signup first.')
                return redirect('Signup')
            else:
                user = User.objects.all().filter(email=user_email)
                print(user)
                if user.exists():
                    user = user.first()
                    user.set_password(password)
                    user.save()
                    messages.success(request, 'Password changed successfully.')
                    return redirect('Login')
                else:
                    messages.error(request, 'Signup first.')
                    return redirect('Signup')

    return render(request, 'home/password-change.html')

def resend_code(request):
    user_email = request.session.get('user_email')
    print(user_email, '3')

    user = User.objects.get(email=user_email)

    if user.profile.is_verified == False:
        otp = generateOTP()
        print(otp)
        user.profile.otp = otp
        user.profile.otp_sent_time = timezone.now()
        user.profile.otp_expiry_time = timezone.now() + timedelta(minutes=5)
        user.save()

        # Send email
        subject = 'OTP Verification for Updatabox'
        message = 'Your OTP for Signup Verification of Secure Cloud Storage (Valid for 5 mins) is: '+str(otp)+'\nPlease do not share with anyone!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ]
        send_mail( subject, message, email_from, recipient_list )

        messages.success(request, 'OTP sent to your email. Please verify your email.')
        return redirect('VerifyEmail')
    else:
        messages.error(request, 'Email already verified.')
        return redirect('VerifyEmail')


@user_email_in_session
@user_email_verified
def pricing_plans(request):
    if request.method == 'POST':
        user_email = request.session.get('user_email')
        print(user_email, 'pricing_plans')

        if user_email == None or user_email == '' or user_email == 'None':
            messages.error(request, 'Please Signup first.')
            return redirect('Signup')

        user = User.objects.get(email=user_email)
        if user.profile.is_verified == True:
            plan = request.POST.get('plan')
            print(plan)

            if plan == 'free':
                print('free plan')
                user.profile.plan = 'Free'
                user.profile.storage_limit = 5368709120
                user.profile.is_payment_done = True
                user.profile.save()
                # return redirect('Checkout')
                context = {
                    'user_verified': user.profile.is_verified,
                    'plan': user.profile.plan,
                    'benefits': ['5GB Storage', '1GB Single file upload', '24/7 Support'],
                    'price': '$0.00',
                    'name': user.name,
                    'email': user.email,
                }
                messages.success(request, 'Free plan selected. Please pay to continue.')
                return render(request, 'home/checkout.html', context)
            elif plan == 'basic':
                print('basic plan')
                user.profile.plan = 'Basic'
                user.profile.storage_limit = 16106127360
                user.profile.is_payment_done = False
                user.profile.save()
                # return redirect('Checkout')
                context = {
                    'user_verified': user.profile.is_verified,
                    'plan': user.profile.plan,
                    'benefits': ['15GB Storage', '2GB Single file upload', '24/7 Support'],
                    'price': '$9.99 / MONTH',
                    'name': user.name,
                    'email': user.email,
                }
                messages.success(request, 'Basic plan selected. Please pay to continue.')
                return render(request, 'home/checkout.html', context)
            elif plan == 'premium':
                print('premiun plan')
                user.profile.plan = 'Premium'
                user.profile.storage_limit = 53687091200
                user.profile.is_payment_done = False
                user.profile.save()
                # return redirect('Checkout')
                context = {
                    'user_verified': user.profile.is_verified,
                    'plan': user.profile.plan,
                    'benefits': ['50GB Storage', '5GB Single file upload', '24/7 Support'],
                    'price': '$19.99 / MONTH',
                    'name': user.name,
                    'email': user.email,
                }
                messages.success(request, 'Premium plan selected. Please pay to continue.')
                return render(request, 'home/checkout.html', context)
            else:
                messages.error(request, 'Please select a plan.')
                return redirect('PricingPlans')
        else:
            messages.info(request, 'Please verify your email and then choose a plan')
            return redirect('VerifyEmail')
    return render(request, 'home/plans.html')

@user_email_in_session
def checkout(request):
    if request.method == "POST":
        email = request.POST.get("email")
        plan = request.POST.get("userplan")

        user = User.objects.get(email=email)
        amount = 0
        if plan == 'Basic':
            amount = 750
            user.profile.plan_start_date = timezone.now()
            user.profile.plan_end_date = timezone.now() + timedelta(days=30)
            user.profile.is_payment_done = True
            user.save()
        elif plan == 'Premium':
            amount = 1500
            user.profile.plan_start_date = timezone.now()
            user.profile.plan_end_date = timezone.now() + timedelta(days=30)
            user.profile.is_payment_done = True
            user.save()
        elif plan == 'Free':
            amount = 0
            messages.success(request, 'Account created successfully.')
            return redirect('Login')

        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
        order = Order.objects.create(
            user=user, provider_order_id=razorpay_order["id"]
        )
        order.save()
        return render(
            request,
            "home/payment.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/callback",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
                "amount": amount,
            },
        )
    # return render(request, "home/payment.html")
    return render(request, 'home/checkout.html')

@payment_started
def payment(request):
    return render(request, "home/payment.html")

@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if not verify_signature(request.POST):
            order.status = 'SUCCESS'
            order.save()
            messages.success(request, 'Account created successfully.')
            return render(request, "home/callback.html", context={"status": order.status})
        else:
            order.status = 'FAILURE'
            order.save()
            messages.error(request, 'Payment failed.')
            return render(request, "home/callback.html", context={"status": order.status})
    else:
        payment_id = request.POST.get("error[metadata]")
        provider_order_id = request.POST.get("error[metadata]")
        if payment_id and provider_order_id is not None:
            payment_id = json.loads(payment_id).get("payment_id")
            provider_order_id = json.loads(provider_order_id).get("order_id")
            order = Order.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.status = 'FAILURE'
            order.save()
            messages.error(request, 'Payment failed.')
            return render(request, "home/callback.html", context={"status": order.status})
        else:
            return redirect("Home")