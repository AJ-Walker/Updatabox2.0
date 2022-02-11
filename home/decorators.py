from django.shortcuts import redirect
from .models import User, Order

def user_email_verified(func):
    def wrapper(request, *args, **kwargs):
        if request.user.profile.is_verified:
            return func(request, *args, **kwargs)
        else:
            return redirect('VerifyEmail')
    return wrapper

def user_email_in_session(f):
    def wrap(request, *args, **kwargs):
        useremail = request.session.get('user_email')
        if useremail:
            return f(request, *args, **kwargs)
        else:
            return redirect("Signup")
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def user_email_not_verified(f):
    def wrap(request, *args, **kwargs):
        useremail = request.session.get('user_email')
        if useremail:
            user = User.objects.get(email=useremail)
            if user.profile.is_verified == False:
                return f(request, *args, **kwargs)
            else:
                return redirect('Signup')
        else:
            return redirect("Signup") 
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def user_email_verified(f):
    def wrap(request, *args, **kwargs):
        useremail = request.session.get('user_email')
        if useremail:
            user = User.objects.get(email=useremail)
            if user.profile.is_verified == True:
                return f(request, *args, **kwargs)
            else:
                return redirect('VerifyEmail')
        else:
            return redirect("Signup") 
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def payment_started(f):
    def wrap(request, *args, **kwargs):
        email = request.session.get('user_email')
        print(email)
        user = User.objects.get(email=email)
        if user.profile.is_payment_done == True:
            return f(request, *args, **kwargs)
        else:
            return redirect('Signup')
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def is_not_logged_in(f):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            return redirect('user:Dashboard')
        else:
            return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap
