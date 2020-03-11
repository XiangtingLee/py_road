from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from .models import User

import time


# Create your views here.
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
    return render(request, 'user/password.html')


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
            messages.success(request, "修改成功, 登录密码将于下次登录生效")
            return redirect('user:password_view')
        except RuntimeError:
            messages.warning(request, "修改失败，请检查网络环境后重试")
            return redirect('user:password_view')
