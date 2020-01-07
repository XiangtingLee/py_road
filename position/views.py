from django.shortcuts import render
from django.http.response import JsonResponse
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from django.contrib.auth.decorators import login_required

from django.conf import settings
from .models import *
from public.tools import verify_sign, MyThread, ThreadLock, get_session_request

import time
import datetime
from lxml import etree
import pandas as pd

def __word_cloud():
    '''
    标签词云数据
    '''
    temp = []
    data = []
    all_label = PositionLabels.objects.all()
    for label in all_label:
        name = label.name
        count = label.position_set.filter(is_effective=1).__len__()
        temp.append((name, count))
    df = pd.DataFrame(temp)
    df.columns = ['name', 'count']
    df = df.sort_values(by="count", ascending=False)
    for one in df.values:
        data.append({"name": one[0], "value": one[1]})
    return {"values": data}

def __local_distribution():
    '''
    获取地区分布
    '''
    data = {}
    all_city = Position.objects.filter(is_effective=1).values_list("position_city__province__name", flat=True)
    value_count = pd.value_counts(list(all_city)).to_frame()
    df_value_counts = pd.DataFrame(value_count).reset_index()
    df_value_counts.columns = ['name', 'counts']
    df_value_counts["name"] = df_value_counts['name'].str.slice(0, 2)
    data["count"] = all_city.__len__()
    all_data = df_value_counts.values
    range_max = ( df_value_counts["counts"].values[0] // 100 + 2 ) * 100
    data["range_max"] = int(range_max)
    data["values"] = [{"name": one[0], "value": one[1]} for one in all_data]
    return data

def __education():
    '''
    获取学历要求
    '''
    data = {}
    all_edu = Position.objects.filter(is_effective=1).values_list("education__name", flat=True)
    value_count = pd.value_counts(list(all_edu)).to_frame()
    df = pd.DataFrame(value_count).reset_index()
    df.columns = ['name', 'counts']
    data['xAxis'] = df["name"].tolist()
    data['values'] = [{"name": one[0], "value": one[1]} for one in df.values]
    data['count'] = all_edu.__len__()
    return data

def __experience():
    '''
    获取经验要求
    '''
    data = {}
    # all_exp = Position.objects.filter(is_effective=1).values_list("position_type__name").annotate(
    #     Count("experience__name")).values_list("experience__name", flat=True)
    all_exp = Position.objects.filter(is_effective=1).values_list("experience__name", flat=True)
    value_count = pd.value_counts(list(all_exp)).to_frame()
    df_value_counts = pd.DataFrame(value_count).reset_index()
    df_value_counts.columns = ['name', 'counts']
    all_data = df_value_counts.values
    data['xAxis'] = df_value_counts["name"].tolist()
    data['values'] = [{"name": one[0], "value": one[1]} for one in all_data]
    data['count'] = all_exp.__len__()
    return data

def __company_scale():
    '''
    公司规模数据
    '''
    all_scala = Company.objects.values_list("scale__name", flat=True)
    value_count = pd.value_counts(list(all_scala)).to_frame()
    df_value_counts = pd.DataFrame(value_count).reset_index()
    df_value_counts.columns = ['name', 'counts']
    all_data = df_value_counts.values
    values = [{"name": one[0], "value": one[1]} for one in all_data]
    return {"values": values}

def __company_industry():
    '''
    获取公司所属行业
    '''
    temp = []
    all_industry = CompanyIndustries.objects.all()
    for industry in all_industry:
        name = industry.name
        count = industry.company_set.filter(is_effective=1).__len__()
        temp.append((name, count))
    df = pd.DataFrame(temp)
    df.columns = ['name', 'count']
    df = df.sort_values(by="count", ascending=False)[0:11].sort_values(by="count", ascending=True)
    xAxis = df["name"].tolist()
    values = df["count"].tolist()
    return {"xAxis": xAxis, "values": values}

def __company_financing():
    '''
    获取公司融资情况
    '''
    all_financing = Company.objects.filter(is_effective=1).values_list("financing__name", flat=True)
    value_count = pd.value_counts(list(all_financing)).to_frame()
    df = pd.DataFrame(value_count).reset_index()
    df.columns = ['name', 'count']
    xAxis = df["name"].tolist()
    values = [{"name": one[0], "value": one[1]} for one in df.values]
    return {"xAxis": xAxis, "values": values}

@login_required
def visualization_view(requests):
    resp = render(requests, 'position/visualization.html', locals())
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY, path='/position/visualization/')
    return resp

@login_required
@verify_sign("POST")
def visualization_data(request):
    if request.method == "POST":
        data = {}
        data["word_cloud"] = __word_cloud()
        data["local"] = __local_distribution()
        data["education"] = __education()
        data["experience"] = __experience()
        data["company_scale"] =__company_scale()
        data["company_industry"] =__company_industry()
        data["company_financing"] =__company_financing()
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False})
    else:
        return JsonResponse({"msg": "访问太频繁，请稍后再试！"}, json_dumps_params={'ensure_ascii':False})

def display_view(request):
    data = {"search_node": []}
    data["all_type"] = PositionType.objects.values_list("name", flat=True)
    place_data = Position.objects.filter(is_effective=1).values_list("position_city__province__name", "position_city__name", "position_district__name")
    df = pd.DataFrame(list(place_data))
    df.columns = ["province", "city", "district"]
    df["district"] = df["district"].fillna("其它地区")
    df = df.drop_duplicates(subset=["province", "city", "district"])
    # 按照province过滤
    province_node = [city for city in df.drop_duplicates(['province'])['province']]
    for province in province_node:
        # 按照city过滤
        city_node = df[df['province'].str.contains(province)].drop_duplicates(['city'])['city']
        all_city_data = [] # 一个city下所有的district
        for city in city_node:
            province_df = df[df['province'].str.contains(province)]
            district_node = [{"name": place, "type": "district"} for place in
                province_df[province_df["city"].str.contains(city)].drop_duplicates(['district'])['district']]
            # 构造city数据
            all_city_data.append({"name": city, "type": "city", "children": district_node})
        # 构造province数据
        data["search_node"].append({"name": province, "type": "province", "children": all_city_data})
    resp = render(request, 'position/display.html', data)
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY, path='/position/reveal/')
    return resp


@login_required
@verify_sign("GET")
def display_filter(request):
    filter_data = request.GET
    data = {'code': 0, 'count': 0, 'data': [], 'msg': ''}
    filter_item = {'is_effective': 1}
    for k in filter_data:
        v = filter_data.get(k, "")
        if v and k == 'salary':
            try:
                filter_item["salary_lower__gte"] = int(filter_data["salary"].split(',')[0])
                filter_item["salary_lower__lte"] = int(filter_data["salary"].split(',')[1])
            except:
                pass
        elif v:
            filter_item[k + "__contains" if k in ["company__name", "position_name"] else k] = v
    first = 1
    page = int(request.POST.get('page', 1))
    limit = int(request.POST.get('limit', 10))
    _data = list(
        Position.objects.filter(**filter_item).annotate(salary=Concat("salary_lower", V("-"), "salary_upper", V("k"),
                                                        output_field=CharField())).values(
            'id', 'company__name', 'position_type__name', 'position_name', 'position_city__name',
            'position_district__name', 'education__name', 'experience__name', 'update_time', "salary")
    )
    data['count'] = total = _data.__len__()
    if total:
        last = (total - 1) // limit + 1
        _data = _data[(page - 1) * limit: page * limit]
        if first <= page <= last:
            data['data'] = _data
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

def cleaning_view(request):
    resp = render(request, 'position/cleaning.html')
    return resp


def __checkPositionEffective(pid):
    '''
    职位有效性检测
    :param record:
    :return:
    '''
    post_url = 'https://www.lagou.com/jobs/%s.html' % pid
    session = get_session_request(post_url)
    resp = session.get(post_url)
    DOM_elements = etree.HTML(resp.text)
    is_outline = DOM_elements.xpath("//span[@class='outline_tag']")
    is_online = DOM_elements.xpath('''//a[@class="send-CV-btn s-send-btn fr"]''')
    is_delete = True if '\n\t\t\t亲，你来晚了，该信息已经被删除鸟~\n\t\t\t' in DOM_elements.xpath(
        '''//div[@class="content"]/text()[1]''') else False
    if is_outline or is_delete:
        ThreadLock.acquire()
        effect_row = Position.objects.filter(id=pid).update(is_effective=0, update_time=datetime.datetime.now())
        ThreadLock.release()
        if effect_row:
            return 1
        else:
            return 0
    elif is_online:
        return 2
    else:
        return -1

def validityCheck(request):
    '''
    多线程职位检测
    :param request:
    :return:
    '''
    data = {'message': ''}
    if request.method == "POST":
        ids = request.POST.getlist('ids[]', None)
        check_id = list(map(int, ids))
        if check_id:
            filter = {'id__in': check_id}
        else:
            filter = {'is_effective': 1}
        check_data = Position.objects.filter(**filter).exclude(position_id=0).values_list('id', flat=True)

        threads = []
        for pid in check_data:
            thread = MyThread(func=__checkPositionEffective, args=(pid, ))
            thread.setName(pid['id'])
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        thread_result = pd.DataFrame([i.get_result() for i in threads])[0].value_counts().to_dict()
        print(thread_result)
        data['status'] = 'ok'
        data['result'] = {'check_row': check_data.__len__(), 'effect_row': thread_result.get(1, 0), 'failed_count': thread_result.get(0, 0)}
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False})
    else:
        return JsonResponse({"status": "error", "maessage": "网络繁忙，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})