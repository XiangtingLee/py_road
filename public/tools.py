import time
import threading
import requests
import datetime
from functools import wraps

from django.http import JsonResponse

from django.conf import settings

REQUEST_HEADERS = {
    # 'Cookie': COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/76.0.3809.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3 '
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
