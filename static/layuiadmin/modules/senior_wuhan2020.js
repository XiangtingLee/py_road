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


    layui.use(['carousel', 'echarts'], function () {
        var $ = layui.$
            , carousel = layui.carousel
            , echarts = layui.echarts
            , node_list = ["DistributionCS", "DistributionCD", "pneumoniaCSIncr", "pneumoniaCSSum", "pneumoniaCDIncr", "pneumoniaCDSum"];
        for (var i = 0; i < node_list.length; i++) {
            var node_name = node_list[i]
                , node_obj = $("#" + node_name).children('div');
                if(node_obj[0]){
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
                    for (var sum = 0,i = 0, l = params.length; i < l; i++) {
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
                        visualMap: {
                            min: 0,
                            max: data.domestic_province.range_max.cs,
                            splitNumber: 5,
                            color: ['#d94e5d','#eac736','#50a3ba'],
                            textStyle: {
                                color: '#fff'
                            }
                        },
                        dataRange: {
                            orient: 'horizontal',
                            min: 0,
                            max: data.domestic_province.range_max.cs,
                            text: ['高', '低'],           // 文本，默认为数值文本
                            splitNumber: 0,
                            range: [0, data.domestic_province.range_max.cs],
                            inverse: false,
                            realtime: true,
                            calculable: true,
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
                        visualMap: {
                            min: 0,
                            max: data.domestic_province.range_max.cd,
                            splitNumber: 5,
                            color: ['#d94e5d','#eac736','#50a3ba'],
                            textStyle: {
                                color: '#fff'
                            }
                        },
                        dataRange: {
                            orient: 'horizontal',
                            min: 0,
                            max: data.domestic_province.range_max.cd,
                            text: ['高', '低'],           // 文本，默认为数值文本
                            splitNumber: 0,
                            range: [0, data.domestic_province.range_max.cd],
                            inverse: false,
                            realtime: true,
                            calculable: true,
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
                        timeline:0,
                        tooltip: {trigger: "axis"},
                        legend: data.pneumonia_cs_incr.legend,
                        calculable: !0,
                        xAxis: [{type: "category", axisLabel: {rotate: 45}, boundaryGap: !1, data: data.pneumonia_cs_incr.xAxis}],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_cs_incr.series
                    },
                    //确诊/疑似总量趋势
                    "pneumoniaCSSum": {
                        tooltip: {trigger: "axis", formatter: sum_func},
                        legend: data.pneumonia_cs_sum.legend,
                        calculable: !0,
                        xAxis: [{type: "category", axisLabel: {rotate: 45}, boundaryGap: !1, data: data.pneumonia_cs_sum.xAxis}],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_cs_sum.series
                    },
                    //治愈/死亡日增趋势
                    "pneumoniaCDIncr": {
                        timeline:0,
                        tooltip: {trigger: "axis"},
                        legend: data.pneumonia_cd_incr.legend,
                        calculable: !0,
                        xAxis: [{type: "category", axisLabel: {rotate: 45}, boundaryGap: !1, data: data.pneumonia_cd_incr.xAxis}],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_cd_incr.series
                    },
                    //治愈/死亡总量趋势
                    "pneumoniaCDSum": {
                        tooltip: {trigger: "axis"},
                        legend: data.pneumonia_cd_sum.legend,
                        calculable: !0,
                        xAxis: [{type: "category", axisLabel: {rotate: 45}, boundaryGap: !1, data: data.pneumonia_cd_sum.xAxis}],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_cd_sum.series
                    }
                };

                for (var i = 0; i < node_list.length; i++) {
                    var node_name = node_list[i]
                        , node_obj = $("#" + node_name).children('div');
                        if(node_obj[0]){
                            var echars_obj = echarts.init(node_obj[0], layui.echartsTheme);
                            echars_obj.setOption(node_data[node_name]);
                            window.onresize = echars_obj.resize;
                            echars_obj.hideLoading();
                        }
                }
            }
        });
    });
    exports('senior_wuhan2020', {})
});