# 外部模块导入
import requests
import datetime
import time
import os
from uuid import uuid4
from urllib.parse import quote
from scrapyd_api import ScrapydAPI

# Django模块导入
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

# 项目内引用
from .models import *
from log.models import *
from .tasks import run_shell
# from log.models import SpiderRunLog
from .tools import MyThread, verify_sign, update_sign
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


def proxy_view(requests):
    resp = render(requests, 'public/proxyPool.html')
    resp.set_signed_cookie(key="sign", value=int(time.time()), salt=settings.SECRET_KEY, path="/public/proxy/")
    return resp


@verify_sign("POST")
def proxy_data(request):
    if request.method == "POST":
        data = {'code': 0, 'count': 0, 'data': [], 'msg': ''}
        if request.method == 'POST':
            page = int(request.POST.get('page', 1))
            limit = int(request.POST.get('limit', 10))
            _data = list(ProxyPool.objects.filter(is_delete=0).values())
            total = data['count'] = _data.__len__()
            if total:
                last = (total - 1) // limit + 1
                _data = _data[(page - 1) * limit: page * limit]
                if 1 <= page <= last:
                    data['data'] = _data
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({"msg": "访问太频繁，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})


def proxy_upload(request):
    csv_file = request.FILES.get('file', None)
    if not csv_file:
        return JsonResponse({'status': 0, 'message': '上传失败，请重新选择！'}, json_dumps_params={'ensure_ascii': False})
    if csv_file.multiple_chunks():
        return JsonResponse({'status': 0, 'message': '文件过大，请重新选择！'}, json_dumps_params={'ensure_ascii': False})
    file_data = csv_file.read().decode("utf-8")
    file_name = csv_file.name.replace('.csv', '').replace('.CSV', '')
    lines = file_data.split("\n")
    insList = []
    for line in lines:
        fields = line.split(",")
        insList.append(ProxyPool(type=file_name, protocol=fields[0], address=fields[1],
                                 port=fields[2].replace('\n', '').replace('\r', '')))
    if insList.__len__() > 7000:
        times = (len(lines) // 7000) + 1
        for time in range(0, times):
            if time == times - 1:
                ProxyPool.objects.bulk_create(insList[7000 * time: insList.__len__() - 1])
            else:
                ProxyPool.objects.bulk_create(insList[7000 * time: (7000 * time) + 7000])
    else:
        ProxyPool.objects.bulk_create(insList)
    return JsonResponse({'status': 1}, json_dumps_params={'ensure_ascii': False})


def proxy_change(request):
    data = {'status': 0, 'message': ''}
    if request.method == 'POST':
        id = request.POST.get('id', '')
        is_available = True if request.POST.get('is_available', 'false') == 'true' else False
        if id:
            ProxyPool.objects.filter(id=id).update(is_available=is_available, updatetime=datetime.datetime.now())
            data['status'] = 1
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def proxy_check(request):
    data = {'message': ''}
    if request.method == "POST":
        threads = []
        ids = request.POST.getlist('ids[]', None)
        judge_result = {'valid': [], 'invalid': []}
        check_id = list(map(int, ids))
        if not check_id:
            for record in ProxyPool.objects.values('id', 'protocol', 'address', 'port'):
                id = record['id']
                protocol = record['protocol']
                address = record['address'] + ':' + record['port']
                thread = MyThread(func=__proxy_judge, args=(protocol, address,))
                thread.setName(str(id))
                threads.append(thread)
        else:
            for id in check_id:
                thread = MyThread(func=__proxy_judge, args=(id,))
                thread.setName(str(id))
                threads.append(thread)
        check_row = threads.__len__()
        if check_row > 5000:
            times = (check_row // 5000) + 1
            for time in range(0, times):
                if time == times - 1:
                    print('cheking %s-%s' % (5000 * time, check_row - 1))
                    start_check_thread = threads[5000 * time: check_row - 1]
                else:
                    print('cheking %s-%s' % (5000 * time, (5000 * time) + 5000))
                    start_check_thread = threads[5000 * time: (5000 * time) + 5000]
                for thread in start_check_thread:
                    thread.start()
                for thread in start_check_thread:
                    thread.join()
                thread_result = [{'id': i.name, 'result': i.get_result()} for i in start_check_thread]
                for result in thread_result:
                    judge_result['valid'].append(int(result['id'])) if result['result'] else judge_result[
                        'invalid'].append(int(result['id']))
        ProxyPool.objects.filter(id__in=judge_result['valid']).update(is_available=1,
                                                                      updatetime=datetime.datetime.now())
        ProxyPool.objects.filter(id__in=judge_result['invalid']).update(is_available=0,
                                                                        updatetime=datetime.datetime.now())
        data['result'] = {'count': check_id.__len__(), 'valid': judge_result['valid'].__len__(),
                          'invalid': judge_result['invalid'].__len__()}
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({"status": "error", "maessage": "网络繁忙，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})


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
    except Exception as e:
        return False


@login_required
def spider_manage_view(request):
    resp = render(request, 'public/spider_manage.html')
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY, path='/public/spider/manage/')
    return resp

@login_required
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
    resp = render(request, 'public/spider_manage_show.html', {'id': spider_id, 'name': name, 'path': full_path, 'code': code})
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY, path='/public/spider/manage/')
    return resp

import json
@login_required
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
                return JsonResponse({'status': 'error', 'success': True, 'msg': "以下名称已存在，请修改。</br>" + "</br>".join(ready)})
            else:
                for one in add_list:
                    file_name = one.get("name", None)
                    now = datetime.datetime.now()
                    kwargs = {"name": file_name, "path": one["path"], "is_available": True, "is_delete": False,
                          "add_time": now, "update_time": now}
                    result = Spider.objects.create(**kwargs)
                    if not result:
                        return JsonResponse({'status': 'error', 'success': False, 'msg': "%s添加失败，请重试"%file_name})
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

import re
@login_required
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
                            if not Spider.objects.filter(path=ret_path).exists():
                                record.append({'path': ret_path})
        return render(request, 'public/spider_manage_probe.html', {"data": record})





@login_required
@verify_sign("POST")
def spider_manage_data(request):
    if request.method == "POST":
        data = {"code": 0, "msg": "", "count": 1000, "data": []}
        spiders = Spider.objects.all().order_by('id')
        data["data"] = [model_to_dict(spider) for spider in spiders]
        data["count"] = spiders.count()
        return JsonResponse(data)
    else:
        return JsonResponse({"status": "error", "maessage": "网络繁忙，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})


@login_required
def spider_operate_view(request):
    spiders = Spider.objects.filter(is_available=1, is_delete=0).values("name", "remark").order_by('id')
    data = {"spiders": [i for i in spiders]}
    resp = render(request, 'public/spider_operate.html', data)
    return resp


def spider_operate_run(request):
    if request.method == "POST":
        location = request.POST.get('location', None)
        language = request.POST.get('language', None)
        spider_name = request.POST.get('spider', None)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spider_path = Spider.objects.get(name=spider_name).path
        param = " -" + location + " -" + language
        command = "python3 " + base_dir + spider_path + param
        sync_task = run_shell.delay(command)
        SpiderRunLog.objects.create(spider_name=spider_name, task_id=sync_task.id, param=param)
        return HttpResponseRedirect('/public/spider/view/')
    else:
        return JsonResponse({"status": "error", "maessage": "网络繁忙，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})
