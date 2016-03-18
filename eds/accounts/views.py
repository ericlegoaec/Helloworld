from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

# Create your views here.

@csrf_exempt
def register(request):
    uname = request.POST.get('uname', None)
    passwd = request.POST.get('passwd', None)
    repasswd = request.POST.get('repasswd', None)
    fname = request.POST.get('fname', None)
    lname = request.POST.get('lname', None)
    email = request.POST.get('email', None)

    if(uname == None or passwd == None or repasswd == None or 
        fname == None or lname == None or email == None):
        return render_to_response('accounts/register.html')

    if( passwd != repasswd ):
        return render_to_response('accounts/register.html',
            {'error_message': 'Two passwd are not equal!'})

    user = User.objects.filter(username__iexact=uname)
    if user:
        return render_to_response('accounts/register.html',
            {'error_message': 'This nick name has been registered by others!'})

    user = User.objects.create_user(uname, email, passwd)
    user.first_name = fname
    user.last_name = lname
    user.is_staff = False
    user.is_active = False
    user.save()
    return HttpResponseRedirect('/accounts/login')

@csrf_exempt
def login(request):
    uname = request.POST.get('uname', None)
    passwd = request.POST.get('passwd', None)

    if(uname == None or passwd == None):
        return render_to_response('accounts/login.html')

    user = authenticate(username=uname, password=passwd)

    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return HttpResponseRedirect('/')

        else:
            return render_to_response('accounts/login.html', 
            {'error_message': 'Your account is not active. Please wait for approval from the web administrator.'})
    else:
        return render_to_response('accounts/login.html', 
            {'error_message': 'Wrong Nickname or Password!'})

    

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')