from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, models
from django.urls import reverse
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from user.models import User

@login_required()
def main(request):
    data = {}
    user = request.user
    data["nick_name"] = user.nick_name
    return render(request, 'lib/main.html', data)

@login_required()
def index(request):
    return render(request, 'pyroad/index.html')

def login_act(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get("next_url", '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['user'] = username
                return redirect(reverse('main'))
            else:
                return render(request, "pyroad/login.html", {
                    "msg": {'text': "您的账号已经锁定,请联系管理员解锁！", 'color': 'red'},
                    'next_url': next_url,
                })
        else:
            return render(request, "pyroad/login.html", {
                "msg": {'text':"用户名或密码错误！",'color':'red'},
                'next_url': next_url,
            })
    else:
        if request.user.is_authenticated:
            return redirect(reverse('main'))
        else:
            next_url = request.GET.get("next", '')
            return render(request, "pyroad/login.html", {
                'next_url': next_url,
            })

def logout_act(request):
    try:
        logout(request)
        return JsonResponse({"code": 0, "msg": "退出成功", "data": {"icon": 1}})
    except:
        return JsonResponse({"code": 0, "msg": "退出失败,请检查网络后重试", "data": {"icon": 2}})

def reg_act(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        User.objects.create_user(username=username, password=password, email=email)
        return render(request, 'pyroad/login.html', {'message': {'text':"注册成功！",'color':'yellow'}})
    else:
        return render(request, 'pyroad/register.html')