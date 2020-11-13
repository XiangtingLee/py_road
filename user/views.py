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
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods

from .models import User
from public.tools import ListProcess, ResponseStandard, get_opt_kwargs

import time
import datetime
from .forms import CaptchaForms
from captcha.models import CaptchaStore
from captcha.views import captcha_image_url


RESP = ResponseStandard()


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
            return JsonResponse(RESP.get_opt_response(msg="验证码错误", icon=2))
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get("next_url", '')
        keep_login = request.POST.get("keep_login", '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                login_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META["REMOTE_ADDR"])
                _u = User.objects.get(username=username)
                _u.last_login_ip = login_ip
                _u.save()
                request.session['user'] = username
                if keep_login:
                    request.session.set_expiry(datetime.timedelta(days=10))
                else:
                    request.session.set_expiry(0)
                if not _u.mobile:
                    return JsonResponse(RESP.get_opt_response(msg="请完善资料", next='/reg/guide/', icon=3))
                return JsonResponse(RESP.get_opt_response(msg="欢迎回来，" + username, next=next_url, icon=1))
            else:
                return JsonResponse(RESP.get_opt_response(msg="您的账号已经锁定，请联系管理员", icon=2))
        else:
            return JsonResponse(RESP.get_opt_response(msg="用户名或密码错误", icon=2))
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
        return JsonResponse(RESP.get_opt_response(msg="退出成功", icon=1))
    except TimeoutError:
        return JsonResponse(RESP.get_opt_response(msg="退出失败,请检查网络后重试", icon=2))


@require_http_methods(["GET", "POST"])
def reg_act(request):
    if request.method == "POST":
        if not settings.ALLOW_REG:
            username = request.POST.get('username')
            password = request.POST.get('password')
            mobile = request.POST.get('mobile', None)
            if User.objects.filter(username=username):
                return JsonResponse(RESP.get_opt_response(msg="用户名已被注册", icon=2))
            if User.objects.filter(mobile=mobile):
                return JsonResponse(RESP.get_opt_response(msg="手机号已被注册", icon=2))
            nick_name = "User%s" % int(time.time() * 1000)
            User.objects.create_user(username=username, password=password, mobile=mobile, nick_name=nick_name)
            return JsonResponse(RESP.get_opt_response(msg="注册成功", next='/login', icon=1))
        return JsonResponse(RESP.get_opt_response(msg="暂不提供注册服务，请联系管理员", icon=2))
    else:
        if not request.user.is_anonymous:
            return redirect(reverse('main'))
        return render(request, 'user/register.html')


@require_http_methods(["GET", "POST"])
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
                username = "User%s" % int(time.time() * 1000)
                User.objects.create_user(username=username, password=password, mobile=mobile)
            else:
                return JsonResponse(RESP.get_opt_response(msg="暂不提供注册服务，请联系管理员", icon=2))
        return JsonResponse(RESP.get_opt_response(msg="修改成功", icon=1, next='../login'))
    else:
        if not request.user.is_anonymous:
            return redirect(reverse('main'))
        return render(request, 'user/reset.html')


@require_http_methods(["GET"])
def profile_view(request):
    data = {"user": request.user}
    return render(request, 'user/profile.html', data)


def profile_update(request):
    user_id = request.user.id
    kwargs = get_opt_kwargs(request, "POST", exclude=["role"], pagination=False)
    User.objects.filter(id=user_id).update(**kwargs)
    messages.success(request, "修改成功")
    return redirect('user:profile_view')


@require_http_methods(["POST"])
def profile_upload(request):
    if request.FILES['file']:
        uid = request.user.id
        file = request.FILES['file']
        file_save_name = "face_img/face_" + str(uid) + "_" + str(int(time.time()*100)) + "." + file.name.split('.')[-1]
        fs = FileSystemStorage()
        filename = fs.save(file_save_name, file)
        uploaded_file_url = fs.url(filename)
        User.objects.filter(id=uid).update(face_img=uploaded_file_url)
        return JsonResponse(RESP.get_opt_response(msg="上传成功", src=uploaded_file_url))


@require_http_methods(["GET"])
def password_view(request):
    return render(request, 'user/forget.html')


@login_required()
@require_http_methods(["POST"])
def password_change(request):
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
@require_http_methods(["GET", "POST"])
def reg_guide(request):
    if request.method == "POST":
        kwargs = get_opt_kwargs(request, "POST", exclude=["agreement", "vercode"], pagination=False)
        user_id = request.user.id
        if User.objects.filter(nick_name=kwargs["nick_name"]):
            return JsonResponse(RESP.get_opt_response(msg="昵称已存在", icon=2))
        if User.objects.filter(mobile=kwargs["mobile"]):
            return JsonResponse(RESP.get_opt_response(msg="手机号已被注册", icon=2))
        User.objects.filter(id=user_id).update(**kwargs)
        return JsonResponse(RESP.get_opt_response(msg="保存成功", next="/", icon=1))
    else:
        if request.user.mobile:
            return redirect('main')
        data = {}
        user = UserSocialAuth.objects.get(user=request.user)
        data["username"] = user.provider + '_' + Hashids(salt=settings.SECRET_KEY, min_length=10).encode(user.id)
        gender_dict = {"男": 1, "女": 0}
        data["sex"] = gender_dict.get(user.extra_data["gender"], 2)
        return render(request, 'user/reg_guide.html', data)


@login_required
@require_http_methods(["GET"])
def manage_view(request):
    return render(request, 'user/manage.html')


@login_required
@require_http_methods(["GET"])
def manage_filter(request):
    page, limit, filter_kwargs = get_opt_kwargs(request, "GET")
    _data = list(
        User.objects.filter(**filter_kwargs).values("id", "username", "nick_name", "face_img", "mobile", "email", "sex",
                                                    "last_login_ip", "date_joined", "is_active").order_by('id')
    )
    totalCount, render_data = ListProcess().pagination(_data, page, limit)
    resp = RESP.get_data_response(0, None, render_data, totalCount=totalCount, page=page, limit=limit)
    return JsonResponse(resp, json_dumps_params={'ensure_ascii': False})


@login_required
@require_http_methods(["GET", "POST"])
def manage_profile(request, uid):
    if request.method == "POST":
        if not request.user.is_superuser:
            return JsonResponse(RESP.get_opt_response(10011))
        _u = User.objects.get(id=uid)
        _u.is_active = request.POST.get("is_active", 1)
        _u.save()
        return JsonResponse(RESP.get_opt_response(msg="操作成功"))
    else:
        data = {}
        if uid:
            data = model_to_dict(User.objects.get(id=uid))
        return render(request, 'user/manage_profile.html', data)
