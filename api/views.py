from django.shortcuts import render
from django.http import HttpResponse
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
