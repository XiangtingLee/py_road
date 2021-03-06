from django.shortcuts import render
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import *
from public.tools import *
# from .tasks import long_time_def
from django.core.cache import cache

import time
from redis.connection import ConnectionError as RedisConnectionError
import datetime
from lxml import etree
import pandas as pd
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.charts import Bar, Line, Pie, WordCloud, Scatter, Funnel, Map

PYECHARTS_INIT_OPTS = opts.InitOpts(width="100%", height="100%", theme=ThemeType.MACARONS)
PYECHARTS_MARKPOINT_MIN = opts.MarkPointItem(type_="min", value_index=1)
PYECHARTS_MARKPOINT_MAX = opts.MarkPointItem(type_="max", value_index=1)
PYECHARTS_LINEPOINT_AVG = opts.MarkLineItem(type_="average", value_index=1)
RESP = ResponseStandard()


def _get_pie_render_data(data: list):
    value_count = pd.value_counts(data).to_frame()
    df = pd.DataFrame(value_count).reset_index()
    df.columns = ['name', 'counts']
    render_data = [(item[0], item[1]) for item in df.values]
    return render_data


def _company_financing():
    """
    获取公司融资情况
    """
    all_financing = Company.objects.filter(is_effective=1).values_list("financing__name", flat=True)
    render_data = _get_pie_render_data(list(all_financing))
    pie = Pie(init_opts=PYECHARTS_INIT_OPTS)
    pie.add(series_name="公司融资情况", data_pair=render_data, rosetype="area")
    return pie.render_embed()


def _company_scale():
    """
    公司规模数据
    """
    all_scala = Company.objects.values_list("scale__name", flat=True)
    render_data = _get_pie_render_data(list(all_scala))
    pie = Pie(init_opts=PYECHARTS_INIT_OPTS)
    pie.add(series_name="公司融资情况", data_pair=render_data, radius=["40%", "50%"])
    return pie.render_embed()


def _education():
    """
    获取学历要求
    """
    all_edu = Position.objects.filter(is_effective=1).values_list("education__name", flat=True)
    render_data = _get_pie_render_data(list(all_edu))
    pie = Pie(init_opts=PYECHARTS_INIT_OPTS)
    pie.add(series_name="学历要求", data_pair=render_data, tooltip_opts=opts.TooltipOpts(formatter="{b}:{c}({d}%)"))
    return pie.render_embed()


def _word_cloud():
    """
    标签词云数据
    """
    temp = []
    all_label = PositionLabels.objects.all()
    for label in all_label:
        name = label.name
        count = label.position_set.filter(is_effective=1).__len__()
        temp.append((name, count))
    df = pd.DataFrame(temp)
    df.columns = ['name', 'count']
    df = df.sort_values(by="count", ascending=False)
    render_data = [(item[0], item[1]) for item in df.values][:100]
    word_cloud = WordCloud(init_opts=PYECHARTS_INIT_OPTS)
    word_cloud.add(series_name="词云统计", data_pair=render_data)
    return word_cloud.render_embed()


def _company_industry():
    """
    获取公司所属行业
    """
    temp = []
    all_industry = CompanyIndustries.objects.all()
    for industry in all_industry:
        name = industry.name
        count = industry.company_set.filter(is_effective=1).__len__()
        temp.append((name, count))
    df = pd.DataFrame(temp)
    df.columns = ['name', 'count']
    df = df.sort_values(by="count", ascending=False)[0:10]
    render_data = [(item[0], item[1]) for item in df.values]
    funnel = Funnel(init_opts=PYECHARTS_INIT_OPTS)
    funnel.add(series_name="公司行业", data_pair=render_data)
    return funnel.render_embed()


def _local_distribution():
    """
    获取地区分布
    """
    data = {}
    all_city = Position.objects.filter(is_effective=1).values_list("position_city__province__name", flat=True)
    value_count = pd.value_counts(list(all_city)).to_frame()
    df_value_counts = pd.DataFrame(value_count).reset_index()
    df_value_counts.columns = ['name', 'counts']
    df_value_counts["name"] = df_value_counts['name'].str.slice(0, 2)
    data["count"] = all_city.__len__()
    all_data = df_value_counts.values
    range_max = (df_value_counts["counts"].values[0] // 100 + 2) * 100
    render_data = [(item[0], item[1]) for item in all_data]
    maps = Map(init_opts=PYECHARTS_INIT_OPTS)
    maps.add(series_name="总览", data_pair=render_data, zoom=1.2, is_map_symbol_show=False,
             itemstyle_opts=opts.series_options.ItemStyleOpts(area_color="#ddd", border_color="#eee",
                                                              border_width=.5), ).set_global_opts(
        visualmap_opts=opts.VisualMapOpts(max_=int(range_max)))
    return maps.render_embed()


def _experience():
    """
    获取经验要求
    """
    xAxis = []
    all_data = Position.objects.filter(is_effective=1).values_list("position_type__name", "experience__name")
    df = pd.DataFrame(list(all_data))
    df.columns = ["type", "name"]
    gdf = df.sort_values(by='name', ascending=False).groupby(["type", "name"]).size().to_frame()
    gdf.columns = ["count"]
    render_data = {}
    for k, v in gdf.to_dict()["count"].items():
        xAxis.append(k[1]) if k[1] not in xAxis else None
        try:
            render_data[k[0]].append(v)
        except KeyError:
            render_data[k[0]] = []
            render_data[k[0]].append(v)
    bar = Bar(init_opts=PYECHARTS_INIT_OPTS)
    bar.add_xaxis(xAxis)
    bar.set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts={"rotate": 45}))
    for k, v in render_data.items():
        bar.add_yaxis(k, v, markpoint_opts=opts.MarkPointOpts([PYECHARTS_MARKPOINT_MIN, PYECHARTS_MARKPOINT_MAX]))
    return bar.render_embed()


def _get_daily_num():
    """
    每日入库数据量统计
    """
    xAxis = []
    day = 7
    range_date_end = datetime.date.today()
    range_date_start = range_date_end - datetime.timedelta(days=day - 1)
    all_type = PositionType.objects.filter(is_effective=1)
    render_data = {}
    while range_date_start <= range_date_end:
        end_date = range_date_start + datetime.timedelta(days=1)
        date_str = range_date_start.strftime("%m-%d")
        xAxis.append(date_str)
        for one_type in all_type:
            daily_count = Position.objects.filter(position_type=one_type, warehouse_time__gte=range_date_start,
                                                  warehouse_time__lt=end_date).count()
            try:
                render_data[one_type.name].append(daily_count)
            except KeyError:
                render_data[one_type.name] = []
                render_data[one_type.name].append(daily_count)
        range_date_start = range_date_start + datetime.timedelta(days=1)
    line = Scatter(init_opts=PYECHARTS_INIT_OPTS)
    line.add_xaxis(xAxis)
    for k, v in render_data.items():
        line.add_yaxis(k, v,
                       markpoint_opts=opts.MarkPointOpts([PYECHARTS_MARKPOINT_MIN, PYECHARTS_MARKPOINT_MAX]),
                       markline_opts=opts.MarkLineOpts(False, [PYECHARTS_LINEPOINT_AVG]))
    return line.render_embed()


def _get_position_type_salary():
    """
    获取行业薪资
    """
    xAxis = DateProcess().get_month_range_str(6, out_format="%Y.%m", include_this_month=True)
    all_type = list(PositionType.objects.filter(is_effective=1).values_list("name", flat=True))
    a = Position.objects.filter(is_effective=1).values_list("position_type__name", "salary_lower", "salary_upper",
                                                            "warehouse_time")
    df = pd.DataFrame(list(a), columns=["type", "salary_low", "salary_up", "date"])
    df["salary"] = (df["salary_low"] + df["salary_up"]) / 2
    df.drop(columns=["salary_low", "salary_up"], inplace=True)
    df["date"] = [datetime.datetime.strftime(i, "%Y.%m") for i in df["date"]]
    render_data = {}
    for one_type in all_type:
        for month in xAxis:
            date_df = df[(df["type"] == one_type) & (df["date"] == month)]
            if date_df.empty:
                date_df = pd.DataFrame([0], columns=["salary"])
            mean = date_df["salary"].mean()
            try:
                render_data[one_type].append(round(mean, 2))
            except KeyError:
                render_data[one_type] = []
                render_data[one_type].append(round(mean, 2))
    line = Line(init_opts=PYECHARTS_INIT_OPTS)
    line.add_xaxis(xAxis)
    for k, v in render_data.items():
        line.add_yaxis(k, v, is_smooth=True,
                       markline_opts=opts.MarkLineOpts(False, [PYECHARTS_LINEPOINT_AVG]),
                       areastyle_opts=opts.AreaStyleOpts(.5))
    return line.render_embed()


@login_required
@require_http_methods(["GET"])
def visualization_view(request):
    try:
        render_data = cache.get('visualization_data', None)
        if not render_data:
            update_position_visualization_cache("")
        render_data = cache.get('visualization_data', None)
    except RedisConnectionError:
        render_data = {
            "word_cloud": _word_cloud,
            "location": _local_distribution,
            "education": _education,
            "experience": _experience,
            "company_scale": _company_scale,
            "company_industry": _company_industry,
            "company_financing": _company_financing,
            "daily": _get_daily_num,
            "salary": _get_position_type_salary
        }
    data = {"is_first_use": False,
            "render": render_data}
    if Position.objects.count() == 0:
        data["is_first_use"] = True
    resp = render(request, 'position/visualization.html', data)
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY,
                           path='/position/visualization/')
    return resp


def update_position_visualization_cache(task_id):
    data = {}
    threads = []
    data_dict = {
        "word_cloud": _word_cloud,
        "location": _local_distribution,
        "education": _education,
        "experience": _experience,
        "company_scale": _company_scale,
        "company_industry": _company_industry,
        "company_financing": _company_financing,
        "daily": _get_daily_num,
        "salary": _get_position_type_salary
    }
    for k, v in data_dict.items():
        threads.append(MyThread(func=v, name=k, args=()))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
        data[thread.name] = thread.result
    cache.set("visualization_data", data, 3600)


@login_required
@require_http_methods(["GET"])
def display_view(request):
    data = {"all_type": PositionType.objects.values_list("name", flat=True)}
    resp = render(request, 'position/display.html', data)
    resp.set_signed_cookie(key='sign', value=int(time.time()), salt=settings.SECRET_KEY, path='/position/display/')
    return resp


@login_required
@verify_sign("POST")
@require_http_methods(["POST"])
def node_data(request):
    data = {"search_node": []}
    place_data = Position.objects.filter(is_effective=1).values_list("position_city__province__name",
                                                                     "position_city__name",
                                                                     "position_district__name")
    df = pd.DataFrame(list(place_data)).fillna("其它地区")
    df.columns = ["province", "city", "district"]
    df["district"] = df["district"].fillna("其它地区")
    df = df.drop_duplicates(subset=["province", "city", "district"])
    # 按照province过滤
    province_node = [city for city in df.drop_duplicates(['province'])['province']]
    for province in province_node:
        # 按照city过滤
        city_node = df[df['province'].str.contains(province)].drop_duplicates(['city'])['city']
        all_city_data = []  # 一个city下所有的district
        for city in city_node:
            province_df = df[df['province'].str.contains(province)]
            district_node = [{"name": place, "type": "position_district__name"} for place in
                             province_df[province_df["city"].str.contains(city)].drop_duplicates(['district'])[
                                 'district']]
            # 构造city数据
            all_city_data.append({"name": city, "type": "position_city__name", "children": district_node})
        # 构造province数据
        data["search_node"].append(
            {"name": province, "type": "position_city__province__name", "children": all_city_data})
    return JsonResponse(data["search_node"], json_dumps_params={'ensure_ascii': False}, safe=False)


@login_required
# @verify_sign("GET")
@require_http_methods(["GET"])
def display_filter(request):
    page, limit, filter_kwargs = get_opt_kwargs(request, "GET")
    filter_kwargs["is_effective"] = 1
    if 'salary' in filter_kwargs.keys():
        try:
            filter_kwargs["salary_lower__gte"] = int(filter_kwargs["salary"].split(',')[0])
            filter_kwargs["salary_upper__lte"] = int(filter_kwargs["salary"].split(',')[1])
            del filter_kwargs["salary"]
        except IndexError or TypeError:
            del filter_kwargs["salary"]
    if filter_kwargs.__contains__("position_city__province__name"):
        filter_kwargs["position_city__province__name"] = None if filter_kwargs[
                                                                     "position_city__province__name"] == "其它地区" else \
        filter_kwargs["position_city__province__name"]
    if filter_kwargs.__contains__("position_city__name"):
        filter_kwargs["position_city__name"] = None if filter_kwargs["position_city__name"] == "其它地区" else \
        filter_kwargs["position_city__name"]
    if filter_kwargs.__contains__("position_district__name"):
        filter_kwargs["position_district__name"] = None if filter_kwargs["position_district__name"] == "其它地区" else \
        filter_kwargs["position_district__name"]
    _data = list(
        Position.objects.filter(**filter_kwargs).annotate(salary=Concat("salary_lower", V("-"), "salary_upper", V("k"),
                                                                        output_field=CharField())).values(
            'id', 'company__name', 'position_type__name', 'position_name', 'position_city__name',
            'position_district__name', 'education__name', 'experience__name', 'update_time', "salary").order_by('id')
    )
    totalCount, render_data = ListProcess().pagination(_data, page, limit)
    resp = RESP.get_data_response(0, None, render_data, totalCount=totalCount, page=page, limit=limit)
    return JsonResponse(resp, json_dumps_params={'ensure_ascii': False})


@login_required
@require_http_methods(["GET"])
def cleaning_view(request):
    resp = render(request, 'position/cleaning.html')
    return resp


def _check_position_effective(pid):
    """
    职位有效性检测
    """
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


@login_required
def cleaning_check(request):
    """
    多线程职位检测
    """
    data = {'message': ''}
    if request.method == "POST":
        ids = request.POST.getlist('ids[]', None)
        check_id = list(map(int, ids))
        if check_id:
            filter_kwargs = {'id__in': check_id}
        else:
            filter_kwargs = {'is_effective': 1}
        check_data = Position.objects.filter(**filter_kwargs).values_list('id', flat=True)
        threads = []
        for pid in check_data:
            thread = MyThread(func=_check_position_effective, args=(pid,))
            thread.setName(pid)
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        thread_result = pd.DataFrame([i.result for i in threads])[0].value_counts().to_dict()
        data['status'] = 'ok'
        data['result'] = {'check_row': check_data.__len__(), 'effect_row': thread_result.get(1, 0),
                          'failed_count': thread_result.get(0, 0)}
        # messages.success(request, '检测成功，共检测%s条数据，失效%s条'%(check_data.__len__(), thread_result.get(1, 0)))
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({"status": "error", "maessage": "网络繁忙，请稍后再试！"}, json_dumps_params={'ensure_ascii': False})
