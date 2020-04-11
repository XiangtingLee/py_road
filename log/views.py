import datetime

from django.http import JsonResponse
from .models import *
from public.tools import ListProcess


# Create your views here.


def spider_filter(request):
    data = {'code': 0, 'count': 0, 'data': [], 'msg': ''}
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        form = request.GET.dict()
        filter_kwargs = {key: form[key] for key in form if
                              key not in ["csrfmiddlewaretoken", "page", "limit"] and form[key]}
        for key in ["start_time", "end_time"]:
            if key in filter_kwargs.keys():
                filter_kwargs[key + "__range"] = \
                    (
                        datetime.datetime.strptime(filter_kwargs[key].split(" - ")[0], "%Y-%m-%d %H:%M:%S"),
                        datetime.datetime.strptime(filter_kwargs[key].split(" - ")[1], "%Y-%m-%d %H:%M:%S")
                    )
                del filter_kwargs[key]
        _data = list(SpiderRunLog.objects.filter(**filter_kwargs).values())
        data['count'], data['data'] = ListProcess().pagination(_data, page, limit)
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
