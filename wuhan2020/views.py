from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import json
import pandas as pd
import numpy as np


from wuhan2020.models import DXYData
from public.tools import *


def __get_pneumonia_sum(is_stack=False, is_accumulate=False, *field, **kwargs):
    if field:
        field = field[0]
    # print(field, type(field), [i for i in field])
    fields = {"confirmed": "confirmedCount", "suspected": "suspectedCount", "cured": "curedCount", "dead": "deadCount"}
    colors = {"dead": "#2F4554", "cured": "#00FF7F", "confirmed": "#FF2400", "suspected": "#CFB53B"}
    data = {"xAxis": [], "series":[], "legend":{"data": []}}
    temp = []
    row_data = DXYData.objects.values_list("statistics", flat=True).order_by('id')
    for one in row_data:
        row_json = json.loads(one)
        temp.append(tuple([row_json[fields[one]] for one in field] + [
            datetime.datetime.fromtimestamp(row_json["modifyTime"] / 1000).strftime("%Y-%m-%d")]))
    df = pd.DataFrame(temp, columns=[i for i in field] + ["modify_time"])
    grouped_df = df.groupby("modify_time").apply(
        lambda i: i.sort_values(
            by=[i for i in field]).iloc[-1] if len(i) > 1 else np.nan)
    data_dict = grouped_df.tail(20).to_dict()
    # 开始构造数据
    data["xAxis"] = [i for i in data_dict["modify_time"].keys()]
    del data_dict["modify_time"]
    for title, title_data in data_dict.items():
        type_num = []
        for _, date_data in title_data.items():
            type_num.append(date_data)
        series = {
            "name": title,
            "type": "line",
            "data": type_num
        }
        series["itemStyle"] = {"color": colors[title]}
        if is_accumulate:
            series["itemStyle"] = {"normal": {"areaStyle": {"type": "default"}, "color": colors[title]}}
        if is_stack:
            series["stack"] = "总量"
        else:
            series["markPoint"] = {"data": [{"type": 'max', "name": '最大值'}, {"type": 'min', "name": '最小值'}]}
            series["markLine"] = {"data": [{"type": 'average', "name": '平均值'}]}
        data["series"].append(series)
        data["legend"]["data"].append(title)
    return data

@login_required
def visualization_view(requests):
    data = {}
    data["is_first_use"] = False
    if DXYData.objects.count() == 0:
        data["is_first_use"] = True
    resp = render(requests, 'wuhan2020/visualization.html', data)
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY, path='/wuhan2020/visualization/')
    return resp

@login_required
@verify_sign("POST")
def visualization_data(request):
    if request.method == "POST":
        data = {}
        threads = []
        data_dict = {
            "pneumonia_sum_cs": {"obj": __get_pneumonia_sum, "args": (False, False, ("confirmed","suspected"),)},
            "pneumonia_sum_cs_stack": {"obj": __get_pneumonia_sum, "args": (True, True, ("confirmed","suspected"),)},
            "pneumonia_sum_cd": {"obj": __get_pneumonia_sum, "args": (False, True, ("cured","dead"),)},
            # "pneumonia_sum": {"obj": __get_pneumonia_sum, "args": (False, ("cured","dead"),)},
        }
        for k, v in data_dict.items():
            if isinstance(v, dict):
                threads.append(MyThread(func=v["obj"], name=k, args=v["args"]))
            else:
                threads.append(MyThread(func=v, name=k, args=()))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            data[thread.name] = thread.result
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False})
    else:
        return JsonResponse({"msg": "访问太频繁，请稍后再试！"}, json_dumps_params={'ensure_ascii':False})
