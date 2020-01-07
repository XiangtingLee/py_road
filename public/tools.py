import time
import threading
import requests
from functools import wraps

from django.http import JsonResponse, HttpResponseRedirect


from django.conf import settings

REQUEST_HEADERS = {
    # 'Cookie': COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
}

ThreadLock = threading.Lock()
class MyThread(threading.Thread):
    def __init__(self, func, args, name='', get_result=True):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.get_result = get_result
        # self.result = self.func(*self.args)

    def run(self):
        if self.get_result:
            self.result = self.func(*self.args)
        else:
            self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def get_session_request(url):
    '''
    获取带有cookie的request请求
    :param url:
    :return:
    '''
    REQUEST_HEADERS['Referer'] = url
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    session.get(url)
    return session

def verify_sign(method):
    '''
    验证渲染标识
    '''
    def decorator(func):
        @wraps(func)
        def returned_wrapper(request, *args, **kwargs):
            if request.method == method:
                user_agent = request.META.get('HTTP_USER_AGENT', None)
                req_time = request.get_signed_cookie(key="sign", salt=settings.SECRET_KEY, default="0")
                referer = request.META.get("HTTP_REFERER", None)
                if int(time.time()) - int(req_time) > 3 or not user_agent or not referer:
                    client = request.META.get("REMOTE_ADDR", None)
                    return JsonResponse({"msg": "非法访问！您的IP已被记录。", "client": client},
                                        json_dumps_params={'ensure_ascii': False})
            return func(request, *args, **kwargs)
        return returned_wrapper
    return decorator