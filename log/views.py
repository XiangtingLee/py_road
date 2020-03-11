from django.http import JsonResponse
from .models import *
# Create your views here.


def log_spider(request):
    data = {'code': 0, 'count': 0, 'data': [], 'msg': ''}
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        limit = int(request.POST.get('limit', 10))
        select_data = request.POST.get('key[id]', None)
        _data = list(SpiderRunLog.objects.filter(id=select_data).values()) if select_data else list(
            SpiderRunLog.objects.values())
        total = data['count'] = _data.__len__()
        if total:
            last = (total - 1) // limit + 1
            _data = _data[(page - 1) * limit: page * limit]
            if 1 <= page <= last:
                data['data'] = _data
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
