/**

 @Name：layuiAdmin Echarts集成
 @Author：star1029
 @Site：http://www.layui.com/admin/
 @License：GPL-2

 */

layui.define(function (exports) {

    //区块轮播切换
    layui.use(['admin', 'carousel'], function () {
        var $ = layui.$
            , admin = layui.admin
            , carousel = layui.carousel
            , element = layui.element
            , device = layui.device();

        //轮播切换
        $('.layadmin-carousel').each(function () {
            var othis = $(this);
            carousel.render({
                elem: this
                , width: '100%'
                , arrow: 'none'
                , interval: othis.data('interval')
                , autoplay: othis.data('autoplay') === true
                , trigger: (device.ios || device.android) ? 'click' : 'hover'
                , anim: othis.data('anim')
            });
        });

        element.render('progress');

    });


    layui.use(['carousel', 'echarts', 'treeTable'], function () {
        var $ = layui.$
            , carousel = layui.carousel
            , echarts = layui.echarts
            , treeTable = layui.treeTable
            ,
            node_list = ["DistributionCS", "DistributionCD", "pneumoniaCSIncr", "pneumoniaCSSum", "pneumoniaCDIncr", "pneumoniaCDSum"];
        for (var i = 0; i < node_list.length; i++) {
            var node_name = node_list[i]
                , node_obj = $("#" + node_name).children('div');
            if (node_obj[0]) {
                var echars_obj = echarts.init(node_obj[0], layui.echartsTheme);
                echars_obj.showLoading({text: '正在加载数据'});
            }
        }

        $.ajax({
            url: "/wuhan2020/visualization/data/",
            method: 'POST',
            success: function (data) {

                //字段求和格式化数据函数
                var sum_func = function (params) {
                    var res = params[0].name + '</br>';
                    for (var i = 0, l = params.length; i < l; i++) {
                        res += params[i]["seriesName"] + ' : ' + params[i]["data"] + '</br>'
                    }
                    for (var sum = 0, i = 0, l = params.length; i < l; i++) {
                        sum += params[i].data;
                    }
                    res += 'total : ' + sum;
                    return res;
                };

                //循环渲染节点
                var node_data = {
                    //地图
                    "DistributionCS": {
                        // title: {
                        //     text: data.title,
                        //     subtext: data.subtitle
                        // },
                        tooltip: {
                            trigger: 'item'

                        },
                        dataRange: {
                            splitList: [
                                {start: 10000,},
                                {start: 1000, end: 10000},
                                {start: 500, end: 999},
                                {start: 100, end: 499},
                                {start: 10, end: 99},
                                {start: 1, end: 9},
                            ],
                            color: ['#4f070d', '#811c24', '#cb2a2f', '#e55a4e', '#f59e83', '#fdebcf']
                        },
                        series: [
                            {
                                name: '确诊/疑似数量',
                                type: 'map',
                                mapType: 'china',
                                mapLocation: {
                                    x: 'center'
                                },
                                selectedMode: 'multiple',
                                itemStyle: {
                                    normal: {label: {show: true, textStyle: {color: '#333'}}, borderColor: '#999'},
                                    emphasis: {label: {show: true}, shadowBlur: 10,}
                                },
                                label: {
                                    normal: {
                                        show: false
                                    },
                                    emphasis: {
                                        show: false
                                    }
                                },
                                data: data.domestic_province.province_cs
                                // {name: '广东', value: 53210.28(, selected: true)}

                            }

                        ],

                    },
                    //地图
                    "DistributionCD": {
                        // title: {
                        //     text: data.title,
                        //     subtext: data.subtitle
                        // },
                        tooltip: {
                            trigger: 'item'
                        },
                        dataRange: {
                            splitList: [
                                {start: 10000,},
                                {start: 1000, end: 10000},
                                {start: 500, end: 999},
                                {start: 100, end: 499},
                                {start: 10, end: 99},
                                {start: 1, end: 9},
                            ],
                        },
                        series: [
                            {
                                name: '治愈/死亡数量',
                                type: 'map',
                                mapType: 'china',
                                mapLocation: {
                                    x: 'center'
                                },
                                selectedMode: 'multiple',
                                itemStyle: {
                                    normal: {label: {show: true}, borderColor: '#ffffff'},
                                    emphasis: {label: {show: true}, shadowBlur: 10,}
                                },
                                label: {
                                    normal: {
                                        show: false
                                    },
                                    emphasis: {
                                        show: false
                                    }
                                },
                                data: data.domestic_province.province_cd
                                // {name: '广东', value: 53210.28(, selected: true)}

                            }

                        ],

                    },
                    //确诊/疑似日增趋势
                    "pneumoniaCSIncr": {
                        timeline: 0,
                        tooltip: {trigger: "axis"},
                        legend: data.pneumonia_cs_incr.legend,
                        calculable: !0,
                        xAxis: [{
                            type: "category",
                            axisLabel: {rotate: 45},
                            boundaryGap: !1,
                            data: data.pneumonia_cs_incr.xAxis
                        }],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_cs_incr.series
                    },
                    //确诊/疑似总量趋势
                    "pneumoniaCSSum": {
                        tooltip: {trigger: "axis", formatter: sum_func},
                        legend: data.pneumonia_cs_sum.legend,
                        calculable: !0,
                        xAxis: [{
                            type: "category",
                            axisLabel: {rotate: 45},
                            boundaryGap: !1,
                            data: data.pneumonia_cs_sum.xAxis
                        }],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_cs_sum.series
                    },
                    //治愈/死亡日增趋势
                    "pneumoniaCDIncr": {
                        timeline: 0,
                        tooltip: {trigger: "axis"},
                        legend: data.pneumonia_cd_incr.legend,
                        calculable: !0,
                        xAxis: [{
                            type: "category",
                            axisLabel: {rotate: 45},
                            boundaryGap: !1,
                            data: data.pneumonia_cd_incr.xAxis
                        }],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_cd_incr.series
                    },
                    //治愈/死亡总量趋势
                    "pneumoniaCDSum": {
                        tooltip: {trigger: "axis"},
                        legend: data.pneumonia_cd_sum.legend,
                        calculable: !0,
                        xAxis: [{
                            type: "category",
                            axisLabel: {rotate: 45},
                            boundaryGap: !1,
                            data: data.pneumonia_cd_sum.xAxis
                        }],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_cd_sum.series
                    }
                };

                for (var i = 0; i < node_list.length; i++) {
                    var node_name = node_list[i]
                        , node_obj = $("#" + node_name).children('div');
                    if (node_obj[0]) {
                        var echars_obj = echarts.init(node_obj[0], layui.echartsTheme);
                        if (node_name.indexOf("Distribution") != -1) {
                            echars_obj.on("click", function (ev) {
                                renderProvinceData(this, ev.seriesName.trim(), ev.name);
                            })
                        }
                        echars_obj.setOption(node_data[node_name]);
                        window.onresize = echars_obj.resize;
                        echars_obj.hideLoading();
                    }
                }

                // 国内疫情
                treeTable.render({
                    elem: '#treeTableInternal',
                    data: data.tree_table.internal,
                    tree: {
                        iconIndex: 0,
                        getIcon: function (d) {  // 自定义图标
                            if (d.children && d.children.length > 0) {  // 判断是否有子集
                                return '<i class="layui-icon layui-icon-list"></i> ';
                            } else {
                                return '<i class="layui-icon layui-icon-location"></i> ';
                            }
                        }
                    },
                    totalRow: true,
                    cols: [
                        {field: 'id', title: '地区', width: 180},
                        {field: 'currentExistingCount', title: '现存确诊', align: "center", width: 83},
                        {field: 'confirmedCount', title: '累计确诊', align: "center", width: 83},
                        {field: 'deadCount', title: '死亡', align: "center", width: 83},
                        {field: 'curedCount', title: '治愈', align: "center", width: 83},
                    ],
                    style: 'margin-top:0; color: #fff;',
                    getThead: function () {
                        return '<tr>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color:"><b>地区</b></td>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color: #f3bab0;"><b>现存确诊</b></td>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color: #e69a8d;"><b>累计确诊</b></td>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color: #b4c0d5;"><b>死亡</b></td>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color: #6c9;"><b>治愈</b></td>' +
                            '</tr>';
                    }
                });

                // 国际疫情
                treeTable.render({
                    elem: '#treeTableForeign',
                    data: data.tree_table.foreign,
                    tree: {
                        iconIndex: 0,
                        getIcon: function (d) {  // 自定义图标
                            if (d.children && d.children.length > 0) {  // 判断是否有子集
                                return '<i class="layui-icon layui-icon-list"></i> ';
                            } else {
                                return '<i class="layui-icon layui-icon-location"></i> ';
                            }
                        }
                    },
                    cols: [
                        {field: 'id', title: '地区', width: 180},
                        {field: 'currentExistingCount', title: '现存确诊', align: "center", width: 83},
                        {field: 'confirmedCount', title: '累计确诊', align: "center", width: 83},
                        {field: 'deadCount', title: '死亡', align: "center", width: 83},
                        {field: 'curedCount', title: '治愈', align: "center", width: 83},
                    ],
                    style: 'margin-top:0; color: #fff;',
                    getThead: function () {
                        return '<tr>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color:"><b>地区</b></td>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color: #f3bab0;"><b>现存确诊</b></td>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color: #e69a8d;"><b>累计确诊</b></td>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color: #b4c0d5;"><b>死亡</b></td>' +
                            '<td style="padding: 9px 10px; text-align: center; background-color: #6c9;"><b>治愈</b></td>' +
                            '</tr>';
                    }
                });
            }
        });
    });

    function renderProvinceData(echars_obj, type_name, province_name) {
        layui.use(['carousel', 'treeTable'], function () {
            var $ = layui.$
                , render_arr = {"治愈/死亡数量": "DistributionCD", "确诊/疑似数量": "DistributionCS"};
            echars_obj.showLoading({text: '正在加载数据'});
            $.ajax({
                url: "/wuhan2020/visualization/conversion/data/",
                data: {t_n: render_arr[type_name], p_n: province_name},
                method: 'POST',
                success: function (data) {

                    var render_data = {
                        tooltip: {
                            trigger: 'item'
                        },
                        toolbox: {
                            show: true,
                            showTitle: true,
                            x: "left",
                            y: "top",
                            feature: {
                                myTool: {
                                    show: true,
                                    title: '返回',
                                    icon: 'image://../back.svg',
                                    onclick: function () {
                                        renderCountryData(echars_obj, type_name)
                                    }
                                }
                            }
                        },
                        dataRange: {
                            splitList: [
                                {start: 10000,},
                                {start: 1000, end: 10000},
                                {start: 500, end: 999},
                                {start: 100, end: 499},
                                {start: 10, end: 99},
                                {start: 1, end: 9},
                            ]
                        },
                        series: [
                            {
                                name: type_name,
                                type: 'map',
                                mapType: province_name,
                                mapLocation: {
                                    x: 'center'
                                },
                                selectedMode: 'multiple',
                                itemStyle: {
                                    normal: {label: {show: true}},
                                    emphasis: {label: {show: true}, shadowBlur: 10,}
                                },
                                label: {
                                    normal: {
                                        show: false
                                    },
                                    emphasis: {
                                        show: false
                                    }
                                },
                                data: data.result
                                // {name: '广东', value: 53210.28(, selected: true)}

                            }

                        ],

                    };
                    if(type_name === "确诊/疑似数量"){
                        render_data.dataRange.color = ['#4f070d', '#811c24', '#cb2a2f', '#e55a4e', '#f59e83', '#fdebcf'];
                        render_data.series[0].itemStyle.normal = {label: {show: true, textStyle: {color: '#333'}}, borderColor: '#999'}
                    }
                    if (data.result) {
                        echars_obj.setOption(render_data);
                        window.onresize = echars_obj.resize;
                    }
                }
            });
            echars_obj.hideLoading();

        });
    }
    function renderCountryData(echars_obj, type_name) {
        layui.use(['carousel', 'treeTable'], function () {
            var $ = layui.$
                , render_arr = {"治愈/死亡数量": "DistributionCD", "确诊/疑似数量": "DistributionCS"};
            echars_obj.showLoading({text: '正在加载数据'});
            $.ajax({
                url: "/wuhan2020/visualization/conversion/data/",
                data: {t_n: render_arr[type_name]},
                method: 'POST',
                success: function (data) {

                    var render_data = {
                        tooltip: {
                            trigger: 'item'
                        },
                        dataRange: {
                            splitList: [
                                {start: 10000,},
                                {start: 1000, end: 10000},
                                {start: 500, end: 999},
                                {start: 100, end: 499},
                                {start: 10, end: 99},
                                {start: 1, end: 9},
                            ]
                        },
                        toolbox: { show: false },
                        series: [
                            {
                                name: type_name,
                                type: 'map',
                                mapType: 'china',
                                mapLocation: {
                                    x: 'center'
                                },
                                selectedMode: 'multiple',
                                itemStyle: {
                                    normal: {label: {show: true}},
                                    emphasis: {label: {show: true}, shadowBlur: 10,}
                                },
                                label: {
                                    normal: {
                                        show: false
                                    },
                                    emphasis: {
                                        show: false
                                    }
                                },
                                data: data.result

                            }

                        ],

                    };
                    if(type_name === "确诊/疑似数量"){
                        render_data.dataRange.color = ['#4f070d', '#811c24', '#cb2a2f', '#e55a4e', '#f59e83', '#fdebcf'];
                        render_data.series[0].itemStyle.normal = {label: {show: true, textStyle: {color: '#333'}}, borderColor: '#999'}
                    }
                    if (data.result) {
                        echars_obj.setOption(render_data);
                        window.onresize = echars_obj.resize;
                    }
                }
            });
            echars_obj.hideLoading();

        });
    }

    exports('wuhan2020', {})
});