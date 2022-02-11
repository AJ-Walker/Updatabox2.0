
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from home.models import Contact, User, Order
from django.utils import timezone

from datetime import timedelta
import os
import os.path
import struct
import string
import hashlib
import random

import json

import razorpay

from user.resources import get_bucket, get_bucket_v2, get_buckets_list, create_s3_bucket

from Crypto import Random
from Crypto.Cipher import AES

def decryption_file(key, filename, chunk_size=24*1024):
    output_filename = os.path.splitext(filename)[0]
    filesize = os.path.getsize(filename)
    print(filesize)
    with open(filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        with open(output_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunk_size)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(origsize)
 
 
def encryption_file(key, filename, target, chunk_size=64*1024):

    newfile = os.path.split(filename)[1]
    output_filename = os.path.join(target, newfile + '.enc')

    iv = Random.new().read(AES.block_size)
    print(iv)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(filename)

    with open(filename, 'rb') as inputfile:
        with open(output_filename, 'wb') as outputfile:
            outputfile.write(struct.pack('<Q', filesize))
            outputfile.write(iv)
            while True:
                chunk = inputfile.read(chunk_size)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)
                outputfile.write(encryptor.encrypt(chunk))


@login_required(login_url='Login')
def dashboard(request):
    user = request.user
    print(user.name)
    files = get_bucket_v2(request) 
    # files = [
    #     {'Key': 'file1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'Key': 'sdvdsv.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'Key': 'sdvdsd.pdf', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'Key': 'fidfsdfle1.excel', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'Key': 'fdsfile1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    # ]
    print(len(files))
    if len(files) == 0:
        return render(request, 'user/dashboard.html', {'files': files})
    else:
        return render(request, 'user/dashboard.html', {'files': files[:5]})

@login_required(login_url='Login')
def profile(request):
    return render(request, 'user/profile.html')

@login_required(login_url='Login')
def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        print(name, email, message)
        if len(name)<2 or len(email)<3 or len(message)<10:
            messages.error(request, 'Please fill the form correctly.')
            return redirect('user:Contact')
        else:
            contact = Contact(name=name, email=email, message=message)
            contact.save()
            messages.success(request, ('Thank you for contacting us. We will get back to you soon.'))
            return redirect('user:Contact')
    return render(request, 'user/contact.html')

@login_required(login_url='Login')
def files(request):
    my_bucket = get_bucket(request)
    summaries = my_bucket.objects.all()
    # summaries = [
    #     {'key': 'file1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'sdvdsv.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'sdvdsd.pdf', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'fidfsdfle1.excel', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'fdsfile1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'fidfle1.img', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'fidle1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'fisdle1.png', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'file1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'file1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'fidle1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    #     {'key': 'fifle1.txt', 'size': '1.2 MB', 'date': '12/12/2019'},
    # ]
    # total_count = 1
    total_count = 0
    for key in summaries:
        total_count += 1
        if total_count == 1:
            break
    print(total_count)
    return render(request, 'user/files.html', {'files': summaries, 'obj_count': total_count})


@login_required(login_url='Login')
def upload(request):
    current_user = request.user
    if request.method == "POST":
        file = request.FILES['file']
        print(file)
        print(file.name)
        print(current_user.profile.plan_end_date)
        print(timezone.now())
        if current_user.profile.plan_end_date < timezone.now():
            messages.error(request, 'Your plan has expired. Please renew your plan.')
            return redirect('user:Files')
        if(file.name==''):
            messages.error(request, 'Please select a file to upload.')
            redirect('user:Files')
        if(file):
            my_bucket = get_bucket(request)
            my_bucket.Object(file.name).put(Body=file)
            current_size = current_user.profile.storage_used
            current_user.profile.storage_used = current_size + file.size
            current_user.profile.save()
            print('uploaded')
            messages.success(request, 'File uploaded successfully.')
            return HttpResponse('File uploaded successfully.')
    else:
        return redirect('user:Files')

@login_required(login_url='Login')
def enc_upload(request):
    if request.method == "POST":
        current_user = request.user
        if current_user.profile.plan_end_date < timezone.now():
            messages.error(request, 'Your plan has expired. Please renew your plan.')
            return redirect('user:Files')
        source = os.path.join(settings.MEDIA_ROOT,'uploads')
        if(not os.path.exists(source)):
            os.makedirs(source)
        target = os.path.join(settings.MEDIA_ROOT, 'encrypted')
        if(not os.path.exists(target)):
            os.makedirs(target)
        print(source, target)

        file = request.FILES['file']
        print(file.name)
        
        if(file.name==''):
            messages.error(request, 'Please select a file to upload.')
            return redirect('user:Files')
        if(file):
            current_size = current_user.profile.storage_used
            current_user.profile.storage_used = current_size + file.size
            current_user.profile.save()

            file_loc = os.path.join(source,file.name)
            print(file_loc)
            with open(file_loc, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 20))
            res1 = bytes(res, 'utf-8') 
            key = hashlib.sha256(res1).digest()

            encryption_file(key, file_loc, target) # encrypts file
            loc = os.path.join(target,file.name+".enc")
            print(loc)

            my_bucket = get_bucket(request)
            my_bucket.Object(file.name+".enc").put(Body=open(loc,'rb'))

            source1 = os.path.join(settings.MEDIA_ROOT, 'keys')
            if(not os.path.exists(source1)):
                os.makedirs(source1)

            source2 = os.path.join(source1, file.name+".enc key.txt")

            keydir = eval(current_user.profile.keydir)
            keydir[file.name+".enc"] = key
            current_user.profile.keydir = str(keydir)
            current_user.profile.save()

            with open(source2, "w") as file1:
                file1.write(res)

            file2 = open(source2, "rb")

            messages.success(request, 'File uploaded successfully.')
            response = HttpResponse(file2.read(), headers={'Content-Type': 'text/plain', 'Content-Disposition': f'attachment; filename={file.name}.enc key.txt'})
            file2.close()
            return response
    else:
        return redirect('user:Files')

@login_required(login_url='Login')
def download(request):
    if request.method == 'POST':
        current_user = request.user
        urlpath = request.path
        print(urlpath)
        filename = request.POST['file']
        print(filename)

        if('.enc' == filename[-4:]):
            return render(request, 'user/secretkey.html', {'filename': filename})
        elif('.enc' != filename[-4:]):
            my_bucket = get_bucket(request)
            file_obj = my_bucket.Object(filename).get()
            messages.success(request, 'File downloaded successfully.')
            response = HttpResponse(file_obj['Body'].read(), headers={'Content-Type': 'text/plain', 'Content-Disposition': f'attachment; filename={filename}'})
            return response
    else:
        return redirect('user:Files')

@login_required(login_url='Login')
def dec_download(request):
    if request.method == 'POST':
        current_user = request.user
        seckey = request.POST['seckey']
        filename = request.POST['filename']
        print(filename, seckey)

        if seckey == '':
            messages.error(request, 'Please enter the secret key.')
            return redirect('user:Files')

        if (filename):
            seckey = bytes(seckey, 'utf-8') 
            seckey = hashlib.sha256(seckey).digest()

            keydir = eval(current_user.profile.keydir)

            target = os.path.join(settings.MEDIA_ROOT, 'downloads')
            if(not os.path.exists(target)):
                os.makedirs(target)

            downloadfile  = os.path.join(target, filename)
            my_bucket = get_bucket(request)
            my_bucket.download_file(filename, downloadfile)
            
            loc = os.path.join(target, filename)
            decryption_file(seckey, loc) # decrypts file

            if(keydir[filename]==seckey):
                loc0 = os.path.join(target,filename[:-4])
                filename = filename[:-4]
                file1 = open(loc0, "rb")
                messages.success(request, 'File downloaded successfully.')
                response = HttpResponse(file1.read(), headers={'Content-Type': 'text/plain', 'Content-Disposition': f'attachment; filename={filename}'})
                file1.close()
                return response
            else:
                messages.error(request, 'Wrong secret key.')
                return redirect('user:DecDownload')
        else:
            messages.error(request, 'Please select a file to download.')
            return redirect('user:DecDownload')
    return render(request, 'user/secretkey.html')

@login_required(login_url='Login')
def forget_key(request, filename):
    if request.method == 'POST':
        password = request.POST.get('password')
        current_user = request.user

        if(password == ''):
            messages.error(request, 'Password field is left blank.')
            return redirect('user:ForgetKey', filename)
        user = User.objects.get(email=current_user.email)
        print(user.password, password)
        if check_password(password, user.password):
            keydir = eval(user.profile.keydir)
            print(keydir)
            if filename in keydir:
                val = keydir[filename]
                source = os.path.join(settings.MEDIA_ROOT,'keys')
                loc0 = os.path.join(source, filename + " key.txt")
                file2 = open(loc0, "rb")

                messages.success(request,'Key send Successfully')
                response = HttpResponse(file2.read(), headers={'Content-Type': 'text/plain', 'Content-Disposition': f'attachment; filename={filename} key.txt'})
                file2.close()
                return response
        else:
            messages.error(request,'Incorrect Password, enter again')
            return redirect('user:ForgetKey', filename)
    return render(request, 'user/forget-key.html', {'filename': filename})

@login_required(login_url='Login')
def delete(request):
    if request.method == "POST":
        current_user = request.user
        file = request.POST['file']
        print(file)
        my_bucket = get_bucket(request)
        filesz = my_bucket.Object(file).content_length
        print(filesz)
        my_bucket.Object(file).delete()

        current_size = current_user.profile.storage_used
        current_user.profile.storage_used = current_size - filesz
        current_user.profile.save()
        messages.success(request, 'File deleted successfully.')
        return redirect('user:Files')
    else:
        return redirect('user:Files')


@login_required(login_url='Login')
def plan(request):
    current_user = request.user
    return render(request, 'user/plan.html', {'user': current_user})


@login_required(login_url='Login')
def checkout(request, plan):
    user = request.user
    if request.method == "POST":
        amount = 0
        if plan == 'basic':
            amount = 750

        elif plan == 'premium':
            amount = 1500

        elif plan == 'free':
            amount = 0
            user.profile.storage_limit = 5368709120 # In bytes
            user.profile.plan = 'Free'
            user.profile.save()
            messages.success(request, 'Plan successfully changed.')
            return redirect('user:Dashboard')

        
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
            "user/payment.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/u/callback/" + plan,
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
                "amount": amount,
            },
        )
    else:
        if plan == 'free':
            print('free plan')
            user.profile.is_payment_done = True
            user.profile.save()
            context = {
                'user_verified': user.profile.is_verified,
                'plan': plan,
                'benefits': ['5GB Storage', '1GB Single file upload', '24/7 Support'],
                'price': '$0.00',
                'name': user.name,
                'email': user.email,
            }
            messages.success(request, 'Free plan selected. Please pay to continue.')
            return render(request, 'user/checkout.html', context)
        elif plan == 'basic':
            print('basic plan')
            user.profile.is_payment_done = False
            user.profile.save()
            context = {
                'user_verified': user.profile.is_verified,
                'plan': plan,
                'benefits': ['15GB Storage', '2GB Single file upload', '24/7 Support'],
                'price': '$9.99 / MONTH',
                'name': user.name,
                'email': user.email,
            }
            messages.success(request, 'Basic plan selected. Please pay to continue.')
            return render(request, 'user/checkout.html', context)
        elif plan == 'premium':
            print('premiun plan')
            user.profile.is_payment_done = False
            user.profile.save()
            context = {
                'user_verified': user.profile.is_verified,
                'plan': plan,
                'benefits': ['50GB Storage', '5GB Single file upload', '24/7 Support'],
                'price': '$19.99 / MONTH',
                'name': user.name,
                'email': user.email,
            }
            messages.success(request, 'Premium plan selected. Please pay to continue.')
            return render(request, 'user/checkout.html', context)

    
@login_required(login_url='Login')
def payment(request):
    return render(request, "user/payment.html")

# @login_required(login_url='Login')
@csrf_exempt
def callback(request, plan):
    plan = plan
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
        user = order.user.email
        print(user)

        user = User.objects.get(email=user)
        order.save()
        if not verify_signature(request.POST):
            order.status = 'SUCCESS'
            order.save()

            if plan == 'basic':
                user.profile.storage_limit = 16106127360
                user.profile.plan = 'Basic'
                user.profile.plan_start_date = timezone.now()
                user.profile.plan_end_date = timezone.now() + timedelta(days=30)
                user.profile.is_payment_done = True
                user.save()
            elif plan == 'premium':
                user.profile.storage_limit = 53687091200
                user.profile.plan = 'Premium'
                user.profile.plan_start_date = timezone.now()
                user.profile.plan_end_date = timezone.now() + timedelta(days=30)
                user.profile.is_payment_done = True
                user.save()

            messages.success(request, 'Plan changed successfully.')
            return render(request, "user/callback.html", context={"status": order.status})
        else:
            order.status = 'FAILURE'
            order.save()
            messages.error(request, 'Payment failed.')
            return render(request, "user/callback.html", context={"status": order.status})
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
            return render(request, "user/callback.html", context={"status": order.status})
        else:
            return redirect("user:Dashboard")

@login_required(login_url='Login')
def change_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        newpass = request.POST.get('newpass')
        confirm_password = request.POST.get('renewpass')

        if password == '' or newpass == '' or confirm_password == '':
            messages.error(request, 'Please fill all the fields.')
            return redirect('user:Profile')
        else:
            user = request.user
            if user.check_password(password):
                if newpass == confirm_password:
                    user.set_password(newpass)
                    user.save()
                    messages.success(request, 'Password changed successfully.')
                    return redirect('user:Profile')
                else:
                    messages.error(request, 'New password and confirm password does not match.')
                    return redirect('user:Profile')
            else:
                messages.error(request, 'Old password does not match.')
                return redirect('user:Profile')
    else:
        return redirect('user:Profile')


@login_required(login_url='Login')
def edit_profile(request):
    if request.method == 'POST':
        name = request.POST.get('fullname')
        print(name)
        if name == '':
            messages.error(request, 'Please fill all the fields.')
            return redirect('user:EditProfile')
        else :
            user = request.user
            user.name = name
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user:Profile')
    else:
        return redirect('user:Profile')