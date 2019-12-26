from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, models
from django.contrib.auth.models import User

def main(request):
    return render(request, 'lib/main.html')

def index(request):
    return render(request, 'pyroad/index.html')

def login_view(request):
    return render(request, 'pyroad/login.html')

def reg_view(request):
    return render(request, 'pyroad/register.html')


def login_action(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        request.session['user'] = username
        return render(request, '', {'message': "login sucess"})
    else:
        return render(request, 'pyroad/login.html', {'message': {'text':"用户名或密码错误！",'color':'red'}})

def reg_action(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    User.objects.create_user(username=username, password=password, email=email)
    return render(request, 'pyroad/login.html', {'message': {'text':"注册成功！",'color':'yellow'}})