from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from django.db.models import Avg, Max, Min, Count
from django.contrib.auth.decorators import login_required


from .models import *

import json
import datetime
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
    count = all_financing.__len__()
    return {"xAxis": xAxis, "values": values}



def visualization_view(requests):
    return render(requests, 'position/visualization.html', locals())

@login_required
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