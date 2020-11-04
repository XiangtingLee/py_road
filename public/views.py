# 外部模块导入
import requests
import datetime
import time
import os
import re
import json
# from uuid import uuid4
# from urllib.parse import quote
# from scrapyd_api import ScrapydAPI

# Django模块导入
from django.db.models import F
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST, require_http_methods

# 项目内引用
from .models import *
from .tasks import delay_spider
# from log.models import SpiderRunLog
from position.models import PositionType
from .tools import MyThread, verify_sign, update_sign, ListProcess
from django.conf import settings


# connect scrapyd service
# scrapyd = ScrapydAPI('http://localhost:6800')


# @csrf_exempt
# @require_http_methods(['POST', 'GET'])  # only get and post
# def crawl(request):
#     # Post requests are for new crawling tasks
#     if request.method == 'POST':
#         location = request.POST.get('location', None)
#         spiderName = request.POST.get('spiderName', None)
#         if not location or not spiderName:
#             return JsonResponse({'error': 'Missing  args'})
#         unique_id = str(uuid4())  # create a unique ID.
#
#         # This is the custom settings for scrapy spider.
#         # We can send anything we want to use it inside spiders and pipelines.
#         # I mean, anything
#         settings = {
#             'unique_id': unique_id,  # unique ID for each record for DB
#             'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
#         }
#
#         # Here we schedule a new crawling task from scrapyd.
#         # Notice that settings is a special argument name.
#         # But we can pass other arguments, though.
#         # This returns a ID which belongs and will be belong to this task
#         # We are goint to use that to check task's status.
#         # task = scrapyd.schedule('default', 'lgspider',
#         #                         settings=settings, url=url, domain=domain)
#         task = scrapyd.schedule('default', spiderName,
#                                 settings=settings, location=quote(location), unique_id=unique_id)
#         SpiderRunLog.objects.create(spider_name=spiderName, task_id=task, unique_id=unique_id)
# return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})
# return HttpResponseRedirect('/spider/crawlData')
#
# # Get requests are for getting result of a specific crawling task
# elif request.method == 'GET':
#     # We were passed these from past request above. Remember ?
#     # They were trying to survive in client side.
#     # Now they are here again, thankfully. <3
#     # We passed them back to here to check the status of crawling
#     # And if crawling is completed, we respond back with a crawled data.
#     task_id = request.GET.get('task_id', None)
#     unique_id = request.GET.get('unique_id', None)
#
#     if not task_id or not unique_id:
#         return JsonResponse({'error': 'Missing args'})
#
#     # Here we check status of crawling that just started a few seconds ago.
#     # If it is finished, we can query from database and get results
#     # If it is not finished we can return active status
#     # Possible results are -> pending, running, finished
#     status = scrapyd.job_status('default', task_id)
#     if status == 'finished':
#         pass
#         # try:
#             # this is the unique_id that we created even before crawling started.
#             # item = ScrapyItem.objects.get(unique_id=unique_id)
#             # return JsonResponse({'data': item.to_dict['data']})
#         # except Exception as e:
#         #     return JsonResponse({'error': str(e)})
#     else:
#         return JsonResponse({'status': status})


@login_required
@require_http_methods(["GET"])
def proxy_view(request):
    protocols = ProxyPoolProtocol.objects.order_by('id').all()
    types = ProxyPoolType.objects.order_by('id').all()
    resp = render(request, 'public/proxy_pool.html', {"protocols": protocols, "types": types})
    resp.set_signed_cookie(key="sign", value=int(time.time()), salt=settings.SECRET_KEY, path="/public/proxy/")
    return resp


@login_required
# @verify_sign("GET")
@require_http_methods(["GET"])
def proxy_filter(request):
    data = {'code': 0, 'count': 0, 'data': [], 'msg': ''}
    form = request.GET
    page = int(form.get('page', 1))
    limit = int(form.get('limit', 10))
    filter_kwargs = {key: form[key] for key in form if
                     key not in ["csrfmiddlewaretoken", "page", "limit"] and form[key]}
    _data = ProxyPool.objects.filter(is_delete=0, **filter_kwargs).values("id", "protocol__name", "type__name",
                                                                          "address", "port", "add_time", "update_time")
    data['count'], data['data'] = ListProcess().pagination(_data, page, limit)
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


@login_required
@require_http_methods(["POST"])
def proxy_upload(request):
    csv_file = request.FILES.get('file', None)
    if not csv_file:
        return JsonResponse({'status': 0, 'message': '上传失败，请重新选择！'}, json_dumps_params={'ensure_ascii': False})
    if csv_file.multiple_chunks():
        return JsonResponse({'status': 0, 'message': '文件过大，请重新选择！'}, json_dumps_params={'ensure_ascii': False})
    file_data = csv_file.read().decode("utf-8")
    file_name = csv_file.name.replace('.csv', '').replace('.CSV', '')
    type_field = ProxyPoolType.objects.get_or_create(name=file_name,
                                                     defaults={"name": file_name, "add_time": datetime.datetime.now()})
    lines = file_data.split("\n")
    ins_list = []
    for line in lines:
        fields = line.split(",")
        protocol_field = ProxyPoolProtocol.objects.get_or_create(name=fields[0], defaults={"name": fields[0],
                                                                                           "add_time": datetime.datetime.now()})
        ins_list.append(ProxyPool(type=type_field[0], protocol=protocol_field[0], address=fields[1],
                                  port=fields[2].replace('\n', '').replace('\r', ''), add_time=datetime.datetime.now()))
    if ins_list.__len__() > 7000:
        times = (len(lines) // 7000) + 1
        for one in range(0, times):
            if one == times - 1:
                ProxyPool.objects.bulk_create(ins_list[7000 * one: ins_list.__len__() - 1])
            else:
                ProxyPool.objects.bulk_create(ins_list[7000 * one: (7000 * one) + 7000])
    else:
        ProxyPool.objects.bulk_create(ins_list)
    return update_sign(JsonResponse({'status': 1}, json_dumps_params={'ensure_ascii': False}), key_path="/public/proxy/")


@login_required
@require_http_methods(["POST"])
def proxy_change(request):
    data = {'status': 0, 'message': ''}
    proxy_id = request.POST.get('id', '')
    is_available = True if request.POST.get('is_available', 'false') == 'true' else False
    if proxy_id:
        a = ProxyPool.objects.filter(id=proxy_id).update(is_available=is_available, update_time=datetime.datetime.now())
        print(a)
        data['status'] = 1
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


@login_required
@require_http_methods(["POST"])
def proxy_check(request):
    data = {'message': ''}
    threads = []
    ids = request.POST.getlist('ids[]', None)
    judge_result = {'valid': [], 'invalid': []}
    check_id = list(map(int, ids))
    kwargs = {"is_delete": False}
    if check_id:
        kwargs["id__in"] = check_id
    for record in ProxyPool.objects.filter(**kwargs).values('id', 'protocol__name', 'address', 'port'):
        address = record['address'] + ':' + record['port']
        thread = MyThread(func=__proxy_judge, args=(record['protocol__name'], address,))
        thread.setName(str(record['id']))
        threads.append(thread)
    check_row = threads.__len__()
    if check_row > 5000:
        times = (check_row // 5000) + 1
        for one in range(0, times):
            if one == times - 1:
                print('cheking %s-%s' % (5000 * one, check_row - 1))
                start_check_thread = threads[5000 * one: check_row - 1]
            else:
                print('cheking %s-%s' % (5000 * one, (5000 * one) + 5000))
                start_check_thread = threads[5000 * one: (5000 * one) + 5000]
            for thread in start_check_thread:
                thread.start()
            for thread in start_check_thread:
                thread.join()
            thread_result = [{'id': i.name, 'result': i.run_result()} for i in start_check_thread]
            for result in thread_result:
                judge_result['valid'].append(int(result['id'])) if result['result'] else judge_result[
                    'invalid'].append(int(result['id']))
    else:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        thread_result = [{"id": i.name, "result": i.run_result()} for i in threads]
        for result in thread_result:
            judge_result['valid'].append(int(result['id'])) if result['result'] else judge_result[
                'invalid'].append(int(result['id']))
    ProxyPool.objects.filter(id__in=judge_result['valid']).update(is_available=1,
                                                                  update_time=datetime.datetime.now())
    ProxyPool.objects.filter(id__in=judge_result['invalid']).update(is_available=0,
                                                                    update_time=datetime.datetime.now())
    data['result'] = {'count': check_id.__len__(), 'valid': judge_result['valid'].__len__(),
                      'invalid': judge_result['invalid'].__len__()}
    return update_sign(JsonResponse(data, json_dumps_params={'ensure_ascii': False}), key_path="/public/proxy/")


def __proxy_judge(protocol, address):
    http_url = 'http://icanhazip.com/'
    https_url = 'https://baidu.com/'
    url = http_url if protocol == 'http' else https_url
    proxy = {"%s" % protocol: "%s:%s" % (protocol, address)}
    try:
        resp = requests.get(url, proxies=proxy, timeout=3)
        if 200 <= resp.status_code < 300:
            return True
        else:
            return False
    except requests.exceptions.ConnectTimeout or requests.exceptions.ReadTimeout:
        return False


@login_required
@require_http_methods(["GET"])
def spider_manage_view(request):
    resp = render(request, 'public/spider_manage.html')
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY, path='/public/spider/manage/')
    return resp


@login_required
@require_http_methods(["GET"])
def spider_manage_show(request, spider_id):
    spider = Spider.objects.get(id=spider_id)
    path = spider.path
    name = spider.name
    full_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + path
    try:
        with open(full_path, 'r', encoding='UTF-8') as f:
            code = f.readlines()
    except Exception as e:
        code = [e]
    resp = render(request, 'public/spider_manage_show.html',
                  {'id': spider_id, 'name': name, 'path': full_path, 'code': code})
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY, path='/public/spider/manage/')
    return resp


@login_required
@require_http_methods(["GET", "POST"])
def spider_manage_edit(request, spider_id):
    spider_id = int(spider_id)
    if request.method == "POST":
        args = request.POST
        add_list = json.loads(args.get("data", "[]"))
        if add_list:
            ready = []
            for one in add_list:
                file_name = one.get("name", None)
                if Spider.objects.filter(name=file_name).count():
                    ready.append(file_name)
            if ready:
                return JsonResponse(
                    {'status': 'error', 'success': True, 'msg': "以下名称已存在，请修改。</br>" + "</br>".join(ready)})
            else:
                for one in add_list:
                    file_name = one.get("name", None)
                    now = datetime.datetime.now()
                    kwargs = {"name": file_name, "path": one["path"], "is_available": True, "is_delete": False,
                              "add_time": now, "update_time": now}
                    result = Spider.objects.create(**kwargs)
                    if not result:
                        return JsonResponse({'status': 'error', 'success': False, 'msg': "%s添加失败，请重试" % file_name})
                return update_sign(JsonResponse({'status': 'success', 'success': True, 'msg': "添加成功"}),
                                   key_path='/public/spider/manage/')

        is_available = True if args.get("is_available", False) else False
        is_delete = True if args.get("is_delete", False) else False
        file_name = args.get("name", None)
        file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + args["path"]
        if not file_name:
            return JsonResponse({'status': 'error', 'success': False, 'msg': "名称不能为空"})
        if not args["path"] or not os.path.exists(file_path):
            return JsonResponse({'status': 'error', 'success': False, 'msg': "文件路径错误，请修改"})
        kwargs = {"name": file_name, "path": args["path"], "is_available": is_available, "is_delete": is_delete,
                  "remark": args.get("remark", None), "update_time": datetime.datetime.now()}
        if not spider_id:
            if Spider.objects.filter(name=file_name).count():
                return JsonResponse({'status': 'error', 'success': False, 'msg': "名称已存在，请修改"})
            kwargs["add_time"] = datetime.datetime.now()
            result = Spider.objects.create(**kwargs)
            if result:
                return update_sign(JsonResponse({'status': 'success', 'success': True, 'msg': "添加成功"}),
                                   key_path='/public/spider/manage/')
            return JsonResponse({'status': 'error', 'success': False, 'msg': "添加失败"})
        result = Spider.objects.filter(id=spider_id).update(**kwargs)
        if result:
            return update_sign(JsonResponse({'status': 'success', 'success': True, 'msg': "修改成功"}),
                               key_path='/public/spider/manage/')
        return update_sign(JsonResponse({'status': 'error', 'success': False, 'msg': "修改失败"}),
                           key_path='/public/spider/manage/')

    else:
        data = {}
        if spider_id:
            data = model_to_dict(Spider.objects.get(id=spider_id))
        return render(request, 'public/spider_manage_edit.html', data)


@login_required
# @require_http_methods(["POST"])
def spider_manage_probe(request):
    if request.method == "POST":
        print(request.POST)
    else:
        record = []
        apps = settings.INSTALLED_APPS[6:]
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        apps_path = [os.path.join(project_path, app) for app in apps]
        for app_path in apps_path:
            spider_path = os.path.join(app_path, "spider")
            if os.path.exists(spider_path):
                for root, dirs, files in os.walk(spider_path, topdown=False):
                    for name in files:
                        if name.endswith('.py'):
                            file_path = os.path.join(root, name)
                            ret_path = re.sub('(.*?road).*?', '', file_path)
                            if not Spider.objects.filter(path__in=[ret_path.replace("/", "\\"), ret_path.replace("\\", "/")]).exists():
                                record.append({'path': ret_path})
        return render(request, 'public/spider_manage_probe.html', {"file": record})


@login_required
@require_http_methods(["GET"])
@verify_sign("GET")
def spider_manage_data(request):
    data = {"code": 0, "msg": "", "data": []}
    spiders = Spider.objects.all().order_by('id')
    data["data"] = [model_to_dict(spider) for spider in spiders]
    data["count"] = spiders.count()
    return JsonResponse(data)


@login_required
def spider_operate_view(request):
    spiders = Spider.objects.filter(is_available=1, is_delete=0).values("name", "remark").order_by('id')
    position_types = PositionType.objects.filter(is_effective=1).values_list("name", flat=True).order_by('id')
    data = {"spiders": [i for i in spiders], "position_types": position_types}
    resp = render(request, 'public/spider_operate.html', data)
    return resp


def spider_operate_run(request):
    if request.method == "POST":
        args = request.POST.getlist("args", None)
        spider_name = request.POST.get('spider', None)
        kwargs = request.POST.dict()
        del kwargs["csrfmiddlewaretoken"]
        del kwargs["spider"]
        if "args" in kwargs.keys():
            del kwargs["args"]
        delay_spider(spider_name, *tuple(args), **kwargs)
        return HttpResponseRedirect('/public/spider/operate/view/')
    else:
        return JsonResponse({"status": "error", "maessage": "网络繁忙，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})


@login_required
def administrative_div_view(request):
    now = int(time.time())
    resp = render(request, 'public/administrative_div.html')
    resp.set_signed_cookie(key='sign', value=now, salt=settings.SECRET_KEY, path='/public/administrativeDiv/')
    return resp


@login_required
def administrative_div_filter(request):
    if request.method == "GET":
        data = {"code": 0, "msg": "", "data": []}
        form = request.GET
        page = int(form.get('page', 1))
        limit = int(form.get('limit', 10))
        filter_kwargs = {key: form[key] for key in form if
                         key not in ["city-picker", "csrfmiddlewaretoken", "page", "limit"] and form[key]}
        _data = AdministrativeDiv.objects.filter(**filter_kwargs).annotate(province_name=F("province__name"),
                                                                           city_name=F("city__name"),
                                                                           area_name=F("area__name")).values(
            "id", "code", "name", "pinyin", "short_name", "zip_code", "province_name", "city_name", "area_name",
            "lng_lat",
            "add_time", "update_time").order_by('id')
        data['count'], data['data'] = ListProcess().pagination(_data, page, limit)
        return JsonResponse(data)
    else:
        return JsonResponse({"status": "error", "maessage": "网络繁忙，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})


@login_required
def administrative_div_edit(request, div_id):
    if request.method == "POST":
        kwargs = {request.POST["k"]: None if not request.POST["d"] else request.POST["d"]}
        kwargs["update_time"] = datetime.datetime.now()
        try:
            update_count = AdministrativeDiv.objects.filter(id=div_id).update(**kwargs)
            return JsonResponse({'code': 10000, "count": update_count, "msg": "修改成功"})
        except:
            return JsonResponse({'code': 10003, "count": 0, "msg": "修改失败"})
    else:
        return JsonResponse({"code": 10004, "msg": "网络繁忙，请稍后再试"}, json_dumps_params={'ensure_ascii': False})
