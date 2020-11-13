import time
import sys
import math
import threading
import requests
import datetime
from copy import deepcopy
from functools import wraps

from django.http import JsonResponse

from django.conf import settings
from django.core.cache import cache

REQUEST_HEADERS = {
    # 'Cookie': COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/76.0.3809.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3 '
}


class ResponseStandard(object):

    def __init__(self):
        self.RESPONSE_BASE_BODY = {
            "msg": "成功",  # 返回携带的消息
            "code": 0,  # 业务自定义状态码
            "extra": {}  # 全局附加数据，字段、内容不定
        }

    @staticmethod
    def _get_code_msg(code):
        msgs = {
            10001: "暂不提供注册服务",
            10002: "暂不提供登录服务",
            10003: "强制下线",
            10004: "用户名已被注册",
            10005: "手机号已被注册",
            10006: "未登录",
            10007: "登录失败",
            10008: "用户信息错误",
            10009: "退出登录失败",
            10010: "帐号已封禁",
            10011: "权限不足",
            20001: "请求方式错误",
            20002: "服务器拒绝处理请求",
            20003: "非法参数",
            20004: "添加数据失败",
            20005: "删除数据失败",
            20006: "修改数据失败",
            20007: "查询数据失败",
            20008: "部分数据添加失败",
            20009: "部分数据删除失败",
            20010: "部分数据修改失败",
            20011: "部分数据查询失败",
            30001: "文件不存在",
            30002: "文件夹不存在",
            30003: "文件已存在",
            30004: "文件夹已存在",
            30005: "文件名不能为空",
            30006: "文件夹名不能为空",
            40001: "上传为空，请重试",
            40002: "上传文件为空",
            40003: "文件格式错误",
            40004: "文件大小超限",
            40005: "上传文件名为空",
            40006: "上传文件已存在",
            40007: "上传文件内容格式错误",
            40008: "上传文件非法",
        }
        return msgs.get(code, "")

    def _get_base_response(self, code=0, msg=None, **extra):
        resp_base_body = deepcopy(self.RESPONSE_BASE_BODY)
        resp_base_body["code"] = code
        resp_base_body["msg"] = msg if msg else self._get_code_msg(code)
        resp_base_body["extra"] = extra
        return resp_base_body

    def get_opt_response(self, code=0, msg=None, **extra):
        return self._get_base_response(code, msg, **extra)

    def get_data_response(self, code, msg, data, **extra):
        resp = self._get_base_response(code, msg, **extra)
        resp["data"] = data
        return resp


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

    def run_result(self):
        try:
            return self.result
        except RuntimeError:
            return None


def get_session_request(url):
    """
    获取带有cookie的request请求
    :param url:
    :return:
    """
    REQUEST_HEADERS['Referer'] = url
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    session.get(url)
    return session


def verify_sign(method, key="sign"):
    """
    验证渲染标识
    """

    def decorator(func):
        @wraps(func)
        def returned_wrapper(request, *args, **kwargs):
            if request.method == method:
                user_agent = request.META.get('HTTP_USER_AGENT', None)
                req_time = request.get_signed_cookie(key=key, salt=settings.SECRET_KEY, default="0")
                referer = request.META.get("HTTP_REFERER", None)
                if int(time.time()) - int(req_time) > 3 or not user_agent or not referer:
                    client = request.META.get("REMOTE_ADDR", None)
                    return JsonResponse({"msg": "非法访问！您的IP已被记录。", "client": client},
                                        json_dumps_params={'ensure_ascii': False})
            return func(request, *args, **kwargs)

        return returned_wrapper

    return decorator


def update_sign(resp, key="sign", salt=settings.SECRET_KEY, key_path='/'):
    resp.set_signed_cookie(key=key, value=int(time.time()), salt=salt, path=key_path)
    return resp


class DateProcess(object):
    """
    时间处理类
    """

    @staticmethod
    def get_day_range_str(num: int, out_format: str = "%Y-%m-%d", include_today: bool = True) -> list:
        """
        获取指定格式n天前日期的str
        """
        days = []
        range_date_end = datetime.date.today() if include_today else datetime.date.today() - datetime.timedelta(days=1)
        range_date_start = range_date_end - datetime.timedelta(days=num - 1 if include_today else num)
        while range_date_start <= range_date_end:
            date_str = range_date_start.strftime(out_format)
            days.append(date_str)
            range_date_start = range_date_start + datetime.timedelta(days=1)
        return days

    @staticmethod
    def get_month_range_str(num: int, out_format: str = "%Y-%m", include_this_month: bool = True) -> list:
        """
        获取指定格式n月前的str
        """
        months = []
        sign = 1 if not include_this_month else 0
        for i in range(num):
            new_date = datetime.date.today().replace(day=1) - datetime.timedelta(days=30 * i + sign)
            months.append(new_date.strftime(out_format))
        return months[::-1]

    @staticmethod
    def get_time_difference_str(time_obj: datetime.datetime):
        difference = datetime.datetime.now() - time_obj
        difference_day = difference.days
        difference_hou = difference.seconds // 3600
        difference_min = difference.seconds // 60
        difference_sec = difference.seconds % 60
        if abs(difference_day) <= 7:
            if difference_day > 0:
                out_start = "%s天" % abs(difference_day) if difference_day != 0 else ""
            else:
                if not difference_hou:
                    if not difference_min:
                        out_start = "%s秒" % difference_sec if difference_sec != 0 else ""
                    else:
                        out_start = "%s分钟" % difference_min if difference_min != 0 else ""
                else:
                    out_start = "%s小时" % difference_hou if difference_hou != 0 else ""
            out_end = "后" if difference_day < 0 else "前"
            return out_start + out_end
        else:
            return time_obj.strftime('%m{m}%d{d} %H:%M').format(m='月', d='日')


class ListProcess(object):
    """
    list处理类
    """

    @staticmethod
    def slice_n(item: list, count: int) -> list:
        """
        将item按照count切割成多个list
        """
        return [item[i:i + count] for i in range(0, len(item), count)]

    @staticmethod
    def pagination(data: list, page: int, limit: int) -> tuple:
        total = data.__len__()
        if total:
            last = (total - 1) // limit + 1
            data = data[(page - 1) * limit: page * limit]
            if 1 <= page <= last:
                return total, data
            return total, []
        return total, []


def get_opt_kwargs(request, method: str = "GET", exclude: list = None, pagination: bool = True):
    items = ["csrfmiddlewaretoken", "page", "limit"]
    if exclude is not None and isinstance(exclude, list):
        [items.append(one) for one in exclude]
    form = request.GET if method.lower() == "get" else request.POST if method.lower() == "post" else None
    if form:
        filter_kwargs = {key: form[key] for key in form if
                         key not in items and form[key]}
        if pagination:
            page = int(form.get('page', 1))
            limit = int(form.get('limit', 10))
            return page, limit, filter_kwargs
        else:
            return filter_kwargs
    return 0, 0, {}
