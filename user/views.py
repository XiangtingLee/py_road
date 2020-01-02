from django.shortcuts import render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

from .models import User

import time
# Create your views here.
def info_view(request):
    data = {}
    data["user"] = request.user
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
    print(kwargs)
    messages.success(request, "修改成功")
    return redirect('user:info_view')

def info_upload(request):
    if request.method == 'POST' and request.FILES['file']:
        uid = request.user.id
        file = request.FILES['file']
        file_save_name = "face_img/face_" + str(uid) + "_" + str(int(time.time() * 100)) + "." + file.name.split('.')[-1]
        fs = FileSystemStorage()
        filename = fs.save(file_save_name, file)
        uploaded_file_url = fs.url(filename)
        User.objects.filter(id=uid).update(face_img=uploaded_file_url)
        return JsonResponse({"code": 0, "msg": "上传成功", "data": {"src": uploaded_file_url}})