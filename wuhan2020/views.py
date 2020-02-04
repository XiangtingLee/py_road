from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import json
import pandas as pd
import numpy as np

from wuhan2020.models import DXYData
from public.tools import *

colors = {"dead": "#5D7092", "cured": "#28B7A3", "confirmed": "#F74C31", "suspected": "#F78207", "serious": "#A25A4E"}


def __get_pneumonia_sum(is_stack=False, is_accumulate=False, *field, **kwargs):
    if field:
        field = field[0]
    fields = {"confirmed": "confirmedCount", "suspected": "suspectedCount", "cured": "curedCount", "dead": "deadCount", "serious": "seriousCount"}
    data = {"xAxis": [], "series": [], "legend": {"data": []}}
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
        series["itemStyle"] = {"normal": {"color": colors[title], "lineStyle": {"color": colors[title]}}}
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


def __get_domestic_province():
    data = {"province_cs": [], "province_cd": []}
    all_province_data = DXYData.objects.filter(is_available=1).order_by('id').last().domestic_province
    all_province_data_json = json.loads(all_province_data)
    for one_province_data in all_province_data_json:
        province_name = one_province_data["provinceShortName"]
        province_cs = one_province_data["confirmedCount"] + one_province_data["suspectedCount"]
        province_cd = one_province_data["curedCount"] + one_province_data["deadCount"]
        if province_name != "待明确地区":
            data["province_cs"].insert(data["province_cs"].__len__(), {"name": province_name, "value": province_cs})
            data["province_cd"].insert(data["province_cd"].__len__(), {"name": province_name, "value": province_cd})
    province_cs_range_max = (max(
        [i["value"] if i["name"] != "待明确地区" and i["name"] != "湖北" else 0 for i in data["province_cs"]]) // 100 + 2) * 100
    province_cd_range_max = (max(
        [i["value"] if i["name"] != "待明确地区" and i["name"] != "湖北" else 0 for i in data["province_cd"]]) // 100 + 2) * 100
    data["range_max"] = {"cs": province_cs_range_max, "cd": province_cd_range_max}
    return data


@login_required
def visualization_view(requests):
    data = {"introduction": [], "counter": []}
    data["is_first_use"] = False
    if DXYData.objects.count() == 0:
        data["is_first_use"] = True
    last_record = DXYData.objects.order_by('id').last()
    last_record_json = json.loads(last_record.statistics)
    for key, value in {"virus": "病毒名称: ", "infectSource": "传染源: ", "passWay": "传播途径: ",
                       "remark1": "", "remark2": "", "remark3": "", "remark4": "", "remark5": ""}.items():
        if last_record_json[key]:
            data["introduction"].append(value + last_record_json[key])
    data["introduction"] = ListProcess().sliceN(data["introduction"], 5)
    data["update_time"] = last_record.modify_time.strftime("%Y-%m-%d %H:%M:%S")
    for key, name in {"confirmed": "确诊病例", "suspected": "疑似病例", "serious": "危重病例", "cured": "治愈人数",
                      "dead": "死亡人数"}.items():
        data["counter"].append({"name": name, "href":key, "color": colors[key], "count": last_record_json[key + "Count"],
                                "incr": last_record_json[key + "Incr"]})

    data["counter"] = ListProcess().sliceN(data["counter"], 4)
    resp = render(requests, 'wuhan2020/visualization.html', data)
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY,
                           path='/wuhan2020/visualization/')
    return resp


@login_required
@verify_sign("POST")
def visualization_data(request):
    if request.method == "POST":
        data = {}
        threads = []
        data_dict = {
            "pneumonia_sum_cs": {"obj": __get_pneumonia_sum, "args": (False, False, ("confirmed", "suspected"),)},
            "pneumonia_sum_cs_stack": {"obj": __get_pneumonia_sum, "args": (True, True, ("confirmed", "suspected"),)},
            "pneumonia_sum_cd": {"obj": __get_pneumonia_sum, "args": (False, True, ("cured", "dead"),)},
            # "pneumonia_sum": {"obj": __get_pneumonia_sum, "args": (False, ("cured","dead"),)},
            "domestic_province": __get_domestic_province,
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
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({"msg": "访问太频繁，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})
