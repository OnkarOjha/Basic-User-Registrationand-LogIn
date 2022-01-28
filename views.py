from django.shortcuts import redirect,render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from simple_user_registration import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes , force_text
from . tokens import generate_token
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
# Create your views here.
def home(request):
    return render(request,"authentication/index.html")

def signup(request):

    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

#validation of user details
        if User.objects.filter(username=username):
            messages.error(request,"username already exist , please try some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request,"email already registered")
            return redirect('home')

        if len(username)>10:
            messages.error(request,"username must be undser 10 cahracters")

        if pass1 != pass2:
            messages.error(request,"passwords didn't match")

        if not username.isalnum():
            messages.error(request,"username must be alpha numeric")
            return redirect('home')


        myuser = User.objects.create_user(username, email , pass1)
        myuser.first_name=  fname
        myuser.last_name=  lname
        myuser.is_active = False
        myuser.save()

        messages.success(request,"your account has been successfully created , We have send you a confirmation email, PLease Confirm your email In order to activate your account")
#sending emails to user

        subject = "Welcome to Tech Geek's Project"
        message = "Hello! " + myuser.first_name + "!!  \n" + "Welcome to Tech Geek's project!!  \n Thank you for visiting our website \n We have also sent you a confirmation EMail , Please confirm your EMail ddress in order to acitvate your account. \n\n Thank You!!\n Onkar Ojha"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject , message , from_email , to_list , fail_silently = True)

        #email address conformation email
        current_site = get_current_site(request)
        email_subject = "COnfirm your email @ TEchgeek Django Login!"
        message2 = render_to_string('email_confirmation.html',{'name': myuser.first_name,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
        'token': generate_token.make_token(myuser),
        
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],

        )
        email.fail_silently  =True
        email.send()


        return redirect('signin')


    return render(request,"authentication/signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username , password = pass1)

        if user is not None:
            login(request,user)
            fname = user.first_name
            return render(request,"authentication/index.html", {'fname': fname})

        else:
            messages.error(request, "bad credentials")
            return redirect('home')


    return render(request,"authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged out Successfully")
    return redirect('home')

def activate(request , uidb64 , token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError , ValueError ,OverflowError , User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser , token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,"activation_failed.html")

