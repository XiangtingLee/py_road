from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import json
import pandas as pd

from wuhan2020.models import DXYData, DXYTimeLine
from public.tools import *

colors_dict = {"dead": "#5D7092", "cured": "#28B7A3", "confirmed": "#F74C31", "suspected": "#F78207",
               "serious": "#A25A4E"}
fields_dict = {"confirmed": "confirmedCount", "suspected": "suspectedCount", "cured": "curedCount", "dead": "deadCount",
               "serious": "seriousCount"}


def _get_sum_data(filter_fields: list or dict = None) -> dict:
    temp = []
    filter_fields = filter_fields if filter_fields else fields_dict.keys()
    row_data = DXYData.objects.values_list("statistics", flat=True).order_by('id')
    for one in row_data:
        row_json = json.loads(one)
        temp.append(tuple([row_json.get(fields_dict[item], 0) for item in filter_fields] + [
            datetime.datetime.fromtimestamp(row_json["modifyTime"] / 1000).strftime("%Y-%m-%d")]))
    df = pd.DataFrame(temp, columns=[i for i in filter_fields] + ["modify_time"])
    grouped_df = df.groupby("modify_time").apply(
        lambda i: i.sort_values(by=[i for i in filter_fields]).iloc[-1])
    data_dict = grouped_df.tail(20).to_dict()
    return data_dict


def _get_sum(sum_data, is_stack=False, is_accumulate=False, *fields, **kwargs):
    fields = fields[0] if fields else fields_dict.keys()
    # 开始构造数据
    data = {"xAxis": [i for i in sum_data["modify_time"].keys()], "series": [], "legend": {"data": []}}
    del sum_data["modify_time"]
    for field in fields:
        type_num = []
        for _, date_data in sum_data[field].items():
            type_num.append(date_data)
        series = {"name": field, "type": "line", "data": type_num,
                  "itemStyle": {"normal": {"color": colors_dict[field], "lineStyle": {"color": colors_dict[field]}}}}
        if is_accumulate:
            series["itemStyle"] = {"normal": {"areaStyle": {"type": "default"}, "color": colors_dict[field]}}
        if is_stack:
            series["stack"] = "总量"
        else:
            series["markPoint"] = {"data": [{"type": 'max', "name": '最大值'}, {"type": 'min', "name": '最小值'}]}
            series["markLine"] = {"data": [{"type": 'average', "name": '平均值'}]}
        data["series"].append(series)
        data["legend"]["data"].append(field)
    return data


def _get_incr(sum_data, *fields, **kwargs):
    fields = fields[0] if fields else fields_dict.keys()
    # 开始构造数据
    data = {"xAxis": [i for i in sum_data["modify_time"].keys()], "series": [], "legend": {"data": []}}
    del sum_data["modify_time"]
    for field in fields:
        if field != "suspected" and field != "serious":
            type_num = [values for values in sum_data[field].values()]
            incr = [type_num[i] if not i else type_num[i] - type_num[i - 1] for i in range(type_num.__len__())]
            del incr[0]
            series = {
                "name": field,
                "type": "line",
                "data": incr,
                "itemStyle": {"normal": {"color": colors_dict[field], "lineStyle": {"color": colors_dict[field]}}}
            }
            data["series"].append(series)
            data["legend"]["data"].append(field)
    del data["xAxis"][0]
    return data


def _get_domestic_province():
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
    return data


@login_required
def visualization_view(request):
    data = {"introduction": [], "counter": [], "is_first_use": False}
    if DXYData.objects.count() == 0:
        data["is_first_use"] = True
    last_record = DXYData.objects.order_by('id').last()
    last_record_json = json.loads(last_record.statistics)
    for key in ["note1", "note2", "note3", "remark1", "remark2", "remark3", "remark4", "remark5"]:
        if last_record_json[key]:
            data["introduction"].append(last_record_json[key])
    data["introduction"] = ListProcess().slice_n(data["introduction"], 5)
    data["update_time"] = last_record.modify_time.strftime("%Y-%m-%d %H:%M:%S")
    for key, name in {"confirmed": "确诊病例", "suspected": "疑似病例", "serious": "危重病例", "cured": "治愈人数",
                      "dead": "死亡人数"}.items():
        data["counter"].append(
            {"name": name, "href": key, "color": colors_dict[key], "count": last_record_json[fields_dict[key]],
             "incr": last_record_json.get(key + "Incr", "")})

    data["counter"] = ListProcess().slice_n(data["counter"], 4)
    resp = render(request, 'wuhan2020/visualization.html', data)
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY,
                           path='/wuhan2020/visualization/')
    return resp


def _get_tree_table():
    data = {"internal": [], "foreign": []}
    latest_data = DXYData.objects.filter(is_available=1).order_by('id').last()
    internal_data = latest_data.domestic_area
    foreign_data = latest_data.foreign
    try:
        internal_json = json.loads(internal_data)
        foreign_json = json.loads(foreign_data)
    except TypeError or AttributeError:
        return data
    for province in internal_json:
        province_data = {"id": province["provinceShortName"], "confirmedCount": province["confirmedCount"],
                         "deadCount": province["deadCount"], "curedCount": province["curedCount"], "children": []}
        for city in province.get("cities", []):
            city_data = {"id": city["cityName"], "confirmedCount": city["confirmedCount"],
                         "deadCount": city["deadCount"], "curedCount": city["curedCount"], "children": []}
            province_data["children"].append(city_data)
        data["internal"].append(province_data)
    foreign_temp = []
    columns = ["continents", "provinceName", "confirmedCount", "deadCount", "curedCount"]
    for country in foreign_json:
        continents = country["continents"]
        provinceName = country["provinceName"]
        confirmedCount = country["confirmedCount"]
        deadCount = country["deadCount"]
        curedCount = country["curedCount"]
        foreign_temp.append((continents, provinceName, confirmedCount, deadCount, curedCount))
    df = pd.DataFrame(foreign_temp, columns=columns)
    grouped_df = df.groupby("continents")
    grouped_sum = grouped_df.sum().sort_values(by=["confirmedCount"], ascending=False)
    for continents_row in grouped_sum.itertuples():
        continents_data = {"id": getattr(continents_row, "Index"),
                           "confirmedCount": getattr(continents_row, "confirmedCount"),
                           "deadCount": getattr(continents_row, "deadCount"),
                           "curedCount": getattr(continents_row, "curedCount"), "children": []}
        group_data_df = grouped_df.get_group(continents_row[0])
        # group_data_df.reset_index(group_data_df["provinceName"], inplace=True)
        for country_row in group_data_df.itertuples():
            country_data = {"id": getattr(country_row, "provinceName"),
                            "confirmedCount": getattr(country_row, "confirmedCount"),
                            "deadCount": getattr(country_row, "deadCount"),
                            "curedCount": getattr(country_row, "curedCount"), "children": []}
            continents_data["children"].append(country_data)
        data["foreign"].append(continents_data)

    return data


def _get_province_detail(province_name, type_name):
    data = []
    latest_data = DXYData.objects.filter(is_available=1).order_by('id').last()
    internal_data = latest_data.domestic_area
    try:
        internal_json = json.loads(internal_data)
    except TypeError or AttributeError:
        return data
    for province in internal_json:
        if province_name == province["provinceShortName"]:
            for area in province["cities"]:
                area_name = area["cityName"] + "市" if not area["cityName"].endswith(('洲', '区', '县')) else area[
                    "cityName"]
                area_value = area.get("confirmedCount", 0) + area.get("suspectedCount",
                                                                      0) if type_name == "DistributionCS" else area.get(
                    "curedCount", 0) + area.get("deadCount", 0)
                data.append({'name': area_name, "value": area_value})
            break
    return data


@login_required
# @verify_sign("POST")
def visualization_data_province(request):
    if request.method == "POST":
        data = {}
        kwargs = request.POST
        data_type = kwargs.get("t_n", "")
        data_province = kwargs.get("p_n", "")
        data["result"] = _get_province_detail(data_province, data_type)
        print(data_type, data_province)
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({"msg": "访问太频繁，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})


@login_required
@verify_sign("POST")
def visualization_data(request):
    if request.method == "POST":
        data = {}
        threads = []
        sum_data = _get_sum_data()
        data_dict = {
            "pneumonia_cs_incr": {"obj": _get_incr, "args": (sum_data.copy(), ("confirmed",),)},
            "pneumonia_cd_incr": {"obj": _get_incr, "args": (sum_data.copy(), ("cured", "dead",),)},
            "pneumonia_cs_sum": {"obj": _get_sum, "args": (sum_data.copy(), True, True, ("confirmed", "suspected",),)},
            "pneumonia_cd_sum": {"obj": _get_sum, "args": (sum_data.copy(), False, True, ("cured", "dead",),)},
            "domestic_province": _get_domestic_province,
            "tree_table": _get_tree_table,
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


@login_required
def timeline_data(request):
    if request.method == "POST":
        query_dict = request.POST
        page = int(query_dict.get("page", 0))
        limit = int(query_dict.get("limit", 10))
        data = {"status": "success", "success": True, "content": {}}
        data["content"]["resultSize"] = limit
        _data = list(DXYTimeLine.objects.filter(is_available=1).order_by("-publish_time").values("title", "source_url",
                                                                                                 "publish_time",
                                                                                                 "source_summary",
                                                                                                 "source_info", ))

        data['count'] = total = _data.__len__()
        _data[0]["latest"] = 1
        if total:
            last = (total - 1) // limit + 1
            _data = _data[(page - 1) * limit: page * limit]
            for i in _data:
                i["pub_time_diff"] = DateProcess().get_time_difference_str(i["publish_time"])
            if 1 <= page <= last:
                data["content"]['result'] = _data
        data["content"]["totalPage"] = total // limit + 1

        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({"msg": "访问太频繁，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})


def timeline_view(request):
    resp = render(request, 'wuhan2020/timeline.html')
    # resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY,
    #                        path='/wuhan2020/timeline/')
    return resp
