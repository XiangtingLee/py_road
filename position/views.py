from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse


from .models import *

import json
import datetime
import pandas as pd

def visualization_view(requests):
    return render(requests, 'position/visualization.html', locals())

def __word_cloud():
    '''
    标签词云数据
    '''
    temp = []
    data = []
    all_label = PositionLabels.objects.all()
    for label in all_label:
        name = label.name
        count = label.position_set.all().__len__()
        one = (name, count)
        temp.append(one)
    df = pd.DataFrame(temp)
    df.columns = ['name', 'count']
    df = df.sort_values(by="count", ascending=False)
    for one in df.values:
        data.append({"name": one[0], "value": one[1]})
    return {"values": data}
    # return data
def __local_distribution():
    '''
    获取地区分布
    '''
    data = {}
    values = []
    all_city = Position.objects.values_list("position_city__province__name", flat=True)
    value_count = pd.value_counts(list(all_city)).to_frame()
    df_value_counts = pd.DataFrame(value_count).reset_index()
    df_value_counts.columns = ['name', 'counts']
    df_value_counts["name"] = df_value_counts['name'].str.slice(0, 2)
    data["count"] = all_city.__len__()
    all_data = df_value_counts.values
    range_max = ( df_value_counts["counts"].values[0] // 100 + 2 ) * 100
    data["range_max"] = int(range_max)
    for one in all_data:
        values.append({"name": one[0], "value": one[1]})
    data["values"] = values
    return data

def visualization_data(request):
    if request.method == "POST":
        data = {}
        data["word_cloud_data"] = __word_cloud()
        data["local_data"] = __local_distribution()
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False})
    else:
        return JsonResponse({}, json_dumps_params={'ensure_ascii':False})