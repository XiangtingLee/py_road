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
            , node_list = ["Distribution", "companyScale", "cpyIndustry", "companyFinancing", "companyFinancing"];
        for (var i = 0; i < node_list.length; i++) {
            var node_name = node_list[i]
                , node_obj = $("#" + node_name).children('div');
                if(node_obj[0]){
                    var echars_obj = echarts.init(node_obj[0], layui.echartsTheme);
                    echars_obj.showLoading({text: '正在加载数据'});
                }
        }
        $.ajax({
            url: "/position/visualization/data/",
            method: 'POST',
            success: function (data) {

                //循环渲染节点
                var node_data = {
                    //地图
                    "Distribution": {
                        // title: {
                        //     text: data.content.title,
                        //     subtext: data.content.subtitle
                        // },
                        tooltip: {
                            trigger: 'item'
                        },
                        dataRange: {
                            orient: 'horizontal',
                            min: 0,
                            max: data.content.local.range_max,
                            text: ['高', '低'],           // 文本，默认为数值文本
                            splitNumber: 0,
                            range: [0, data.content.local.range_max],
                            inverse: false,
                            realtime: true,
                            calculable: true,
                        },
                        series: [
                            {
                                name: '职位数量',
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
                                data: data.content.local.values
                                // {name: '广东', value: 53210.28(, selected: true)}

                            }

                        ],

                    },
                    //公司规模
                    "companyScale": {
                        tooltip: {
                            // trigger: 'item',
                            formatter: "{a} <br/>{b} : {c}家公司"
                        },
                        series: [{
                            name: '公司规模',
                            type: 'treemap',
                            itemStyle: {
                                normal: {label: {show: true}, borderColor: '#ffffff'},
                                emphasis: {label: {show: true, textStyle: {color: '#fff'}}, shadowBlur: 10,}
                            },
                            data: data.content.company_scale.values
                        }]
                    },
                    //公司行业
                    "cpyIndustry": {
                        // title: {
                        //     text: '世界人口总量',
                        //     subtext: '数据来自网络'
                        // },
                        tooltip: {
                            trigger: 'item',
                            formatter: "{a} <br/>{b} : {c}家公司"
                        },
                        legend: {
                            data: ['全部公司']
                        },
                        grid: {
                            left: '3%',
                            right: '4%',
                            bottom: '3%',
                            containLabel: true
                        },
                        xAxis: {
                            type: 'value',
                            boundaryGap: [0, 0.01]
                        },
                        yAxis: {
                            type: 'category',
                            data: data.content.company_industry.xAxis
                        },
                        series: [
                            {
                                name: '全部公司',
                                type: 'bar',
                                data: data.content.company_industry.values
                            }
                        ]
                    },
                    //公司融资
                    "companyFinancing": {
                        // title: {
                        //     text: data.content.title,
                        //     subtext: data.content.subtitle
                        // },
                        tooltip: {
                            trigger: 'item',
                            formatter: "{a} <br/>{b} : {c}家公司 ({d}%)"
                        },
                        legend: {
                            // orient: 'vertical',
                            top: 100,
                            data: data.content.company_financing.xAxis
                        },
                        series: [
                            {
                                name: '公司融资情况',
                                type: 'pie',
                                radius: '55%',
                                center: ['50%', '60%'],
                                roseType: 'area',
                                data: data.content.company_financing.values,
                                itemStyle: {
                                    emphasis: {
                                        shadowBlur: 10,
                                        shadowOffsetX: 0,
                                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                                    }
                                }
                            }
                        ]
                    },
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
    exports('senior_position', {})
});