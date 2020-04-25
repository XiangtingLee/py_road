from hashids import Hashids
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.contrib import messages, auth
from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.backends import ModelBackend
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout

from .models import User

import time
import datetime
from .forms import CaptchaForms
from captcha.models import CaptchaStore
from captcha.views import captcha_image_url


class CustomBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            auth_user = User.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
            if auth_user.check_password(password):
                return auth_user
        except User.DoesNotExist:
            return None


def login_act(request):
    if request.method == "POST":
        cap = CaptchaForms(request.POST).is_valid()
        if not cap:
            return JsonResponse({"code": 0, "msg": "验证码错误", "icon": 2})
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get("next_url", '')
        keep_login = request.POST.get("keep_login", '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['user'] = username
                if keep_login:
                    request.session.set_expiry(datetime.timedelta(days=10))
                else:
                    request.session.set_expiry(0)
                return JsonResponse({"code": 0, "msg": "欢迎回来，" + username, "next": next_url, "icon": 1})
            else:
                return JsonResponse({"code": 0, "msg": "您的账号已经锁定，请联系管理员", "icon": 2})
        else:
            return JsonResponse({"code": 0, "msg": "用户名或密码错误", "icon": 2})
    else:
        if request.user.is_authenticated:
            return redirect(reverse('main'))
        else:
            hash_key = CaptchaStore.generate_key()
            img_url = captcha_image_url(hash_key)
            next_url = request.GET.get("next", '')
            return render(request, "user/login.html", {
                "next_url": next_url,
                "hash_key": hash_key,
                "img_url": img_url,
            })


def logout_act(request):
    try:
        logout(request)
        return JsonResponse({"code": 0, "msg": "退出成功", "data": {"icon": 1}})
    except TimeoutError:
        return JsonResponse({"code": 0, "msg": "退出失败,请检查网络后重试", "data": {"icon": 2}})


def reg_act(request):
    if request.method == "POST":
        if settings.ALLOW_REG:
            username = request.POST.get('username')
            password = request.POST.get('password')
            mobile = request.POST.get('mobile', None)
            if User.objects.filter(username=username):
                return JsonResponse({"code": 0, "msg": "用户名已被注册", "icon": 2})
            if User.objects.filter(mobile=mobile):
                return JsonResponse({"code": 0, "msg": "手机号已被注册", "icon": 2})
            User.objects.create_user(username=username, password=password, mobile=mobile)
            return JsonResponse({"code": 0, "msg": "注册成功", "next": '../login', "icon": 1})
        return JsonResponse({"code": 0, "msg": "暂不提供注册服务，请联系管理员", "icon": 2})
    else:
        return render(request, 'user/register.html')


def reset_act(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile', None)
        password = request.POST.get('password')
        try:
            user = User.objects.get(mobile=mobile)
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            if settings.ALLOW_REG:
                username = "User%s" % int(time.time()*1000)
                User.objects.create_user(username=username, password=password, mobile=mobile)
            else:
                return JsonResponse({"code": 0, "msg": "暂不提供注册服务，请联系管理员", "icon": 2})
        return JsonResponse({"code": 0, "msg": "修改成功", "icon": 1, 'next': '../login'})
    else:
        return render(request, 'user/reset.html')


def info_view(request):
    data = {"user": request.user}
    return render(request, 'user/info.html', data)


def info_change(request):
    kwargs = {}
    req_args = request.POST
    user_id = request.user.id
    for i in req_args:
        kwargs[i] = req_args[i]

    del kwargs["csrfmiddlewaretoken"]
    del kwargs["role"]
    User.objects.filter(id=user_id).update(**kwargs)
    messages.success(request, "修改成功")
    return redirect('user:info_view')


def info_upload(request):
    if request.method == 'POST' and request.FILES['file']:
        uid = request.user.id
        file = request.FILES['file']
        file_save_name = "face_img/face_" + str(uid) + "_" + str(int(time.time() * 100)) + "." + file.name.split('.')[
            -1]
        fs = FileSystemStorage()
        filename = fs.save(file_save_name, file)
        uploaded_file_url = fs.url(filename)
        User.objects.filter(id=uid).update(face_img=uploaded_file_url)
        return JsonResponse({"code": 0, "msg": "上传成功", "data": {"src": uploaded_file_url}})


def password_view(request):
    return render(request, 'user/forget.html')


@login_required()
def password_change(request):
    if request.method == "POST":
        username = request.user.username
        req_args = request.POST
        old_pwd = req_args["oldPassword"]
        new_pwd = req_args["password"]
        if old_pwd == new_pwd:
            messages.warning(request, "新密码不能与旧密码相同，请重新输入")
            return redirect('user:password_view')
        user = auth.authenticate(username=username, password=old_pwd)
        if not user:
            messages.error(request, "修改失败，原密码输入错误")
            return redirect('user:password_view')
        try:
            user.set_password(new_pwd)
            user.save()
            logout(request)
            messages.success(request, "修改成功, 请重新登录")
            jump_to_console = '''<html><body onLoad="window.top.location.href='./'" ></body></html>'''
            return HttpResponse(jump_to_console)
        except RuntimeError:
            messages.warning(request, "修改失败，请检查网络环境后重试")
            return redirect('user:password_view')


@login_required
def reg_guide(request):
    if request.method == "POST":
        # 头像接口分辨率分为40,100,140,160,240,640六种
        kwargs = {}
        req_args = request.POST
        user_id = request.user.id
        for i in req_args:
            kwargs[i] = req_args[i]
        del kwargs["csrfmiddlewaretoken"]
        del kwargs["agreement"]
        del kwargs["vercode"]
        if User.objects.filter(nick_name=kwargs["nick_name"]):
            return JsonResponse({"code": 0, "msg": "昵称已存在", "icon": 2})
        if User.objects.filter(mobile=kwargs["mobile"]):
            return JsonResponse({"code": 0, "msg": "手机号已被注册", "icon": 2})
        User.objects.filter(id=user_id).update(**kwargs)
        return JsonResponse({"code": 0, "msg": "保存成功", "next": '../', "icon": 1})
    else:
        if not request.user.mobile:
            data = {}
            user = UserSocialAuth.objects.get(user=request.user)
            data["username"] = user.provider + '_' + Hashids(salt=settings.SECRET_KEY, min_length=10).encode(user.id)
            gender_dict = {"男": 1, "女": 0}
            data["sex"] = gender_dict.get(user.extra_data["gender"], 2)
            return render(request, 'user/reg_guide.html', data)
        return redirect('main')
