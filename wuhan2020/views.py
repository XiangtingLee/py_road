from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import json
import pandas as pd
import numpy as np


from wuhan2020.models import DXYData
from public.tools import *


def __get_pneumonia_sum():
    data = {"xAxis": [], "series":[], "legend":{"data": []}}
    temp = []
    row_data = DXYData.objects.values_list("statistics", flat=True).order_by('id')
    for one in row_data:
        row_json = json.loads(one)
        modify_time = datetime.datetime.fromtimestamp(row_json["modifyTime"] / 1000).strftime("%Y-%m-%d")
        confirmed = row_json["confirmedCount"]
        suspected = row_json["suspectedCount"]
        cured = row_json["curedCount"]
        dead = row_json["deadCount"]
        temp.append((confirmed, suspected, cured, dead, modify_time))
    df = pd.DataFrame(temp, columns=["confirmed", "suspected", "cured", "dead", "modify_time"])
    grouped_df = df.groupby("modify_time").apply(
        lambda i: i.sort_values(
            by=["confirmed", "suspected", "cured", "dead"]).iloc[-1] if len(i) > 1 else np.nan)
    data_dict = grouped_df.tail(20).to_dict()
    # 开始构造数据
    data["xAxis"] = [i for i in data_dict["modify_time"].keys()]
    del data_dict["modify_time"]
    for title, title_data in data_dict.items():
        type_num = []
        for _, date_data in title_data.items():
            type_num.append(date_data)
        data["series"].append({
            "name": title,
            "type": "line",
            "itemStyle": {"normal": {"areaStyle": {"type": "default"}}},
            "data": type_num
        })
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
            "pneumonia_sum": __get_pneumonia_sum,
        }
        for k, v in data_dict.items():
            threads.append(MyThread(func=v, name=k, args=()))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            data[thread.name] = thread.result
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False})
    else:
        return JsonResponse({"msg": "访问太频繁，请稍后再试！"}, json_dumps_params={'ensure_ascii':False})
