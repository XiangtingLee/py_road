from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import hashlib

# Create your views here.

def wechat_verify(request):
    params = request.GET
    signature = params.get("signature")
    timestamp = params.get("timestamp")
    nonce = params.get("nonce")
    echostr = params.get("echostr")
    token = "513932815"
    list = [token, timestamp, nonce]
    list.sort()
    temp = ''.join(list)
    sha1 = hashlib.sha1(temp.encode('utf-8')) # 进行sha1加密
    hashcode = sha1.hexdigest()
    if hashcode == signature:
        return HttpResponse(echostr)
    else:
        return HttpResponse(params)


@csrf_exempt
def proxy_verify(request):
    data = {
        "method": request.method,
        "ip": request.META.get("REMOTE_ADDR"),
        "proxy": False,
        "proxy_ip": None,
        "ua": request.META.get('HTTP_USER_AGENT'),
        "REMOTE_ADDR": request.META.get("REMOTE_ADDR"),
        "HTTP_X_FORWARDED_FOR": request.META.get('HTTP_X_FORWARDED_FOR')
    }
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        data["proxy"] = True
        data["ip"] = request.META.get("HTTP_X_FORWARDED_FOR")
        data["proxy_ip"] = request.META.get("REMOTE_ADDR")
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, safe=False)

