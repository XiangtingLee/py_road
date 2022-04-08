import datetime

from django.http import JsonResponse

from log.models.spider_run import SpiderRunLog
from public.tools import ListProcess, ResponseStandard, get_opt_kwargs

RESP = ResponseStandard()


def spider_filter(request):
    if request.method == 'GET':
        page, limit, filter_kwargs = get_opt_kwargs(request, "GET")
        for key in ["start_time", "end_time"]:
            if key in filter_kwargs.keys():
                filter_kwargs[key + "__range"] = (
                    datetime.datetime.strptime(filter_kwargs[key].split(" - ")[0], "%Y-%m-%d %H:%M:%S"),
                    datetime.datetime.strptime(filter_kwargs[key].split(" - ")[1], "%Y-%m-%d %H:%M:%S")
                )
                del filter_kwargs[key]
        _data = list(SpiderRunLog.objects.filter(**filter_kwargs).values())
        total, render_data = ListProcess().pagination(_data, page, limit)
        resp = RESP.get_data_response(0, None, render_data, total=total, page=page, limit=limit)
        return JsonResponse(resp, json_dumps_params={'ensure_ascii': False})
