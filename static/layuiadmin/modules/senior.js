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
            , echarts = layui.echarts;

        //词云
        var echwdcloud = [],
            elemwdcloud = $('#wdcloud').children('div')
            , renderwdcloud = function (index) {
                echwdcloud[index] = echarts.init(elemwdcloud[index], layui.echartsTheme);
                echwdcloud[index].showLoading({text: '正在加载数据'});
                $.ajax({
                    url: "/api/tagAnalysis/",
                    method: 'POST',
                    success: function (data) {
                        var plat = [
                            {
                                title: {
                                    text: data.title,
                                    subtext: data.subtitle
                                },
                                tooltip: {
                                    trigger: 'item'
                                },
                                series: [
                                    {
                                        type: 'wordCloud',
                                        size: ['90%', '90%'],
                                        gridSize: 8,
                                        textPadding: 1,
                                        rotationRange: [-90, 90],
                                        shape: 'pentagon',
                                        autoSize: {
                                            enable: true,
                                            // minSize: 20
                                        },
                                        textStyle: {
                                            normal: {
                                                color: function () {
                                                    return 'rgb(' + [
                                                        Math.round(Math.random() * 255),
                                                        Math.round(Math.random() * 255),
                                                        Math.round(Math.random() * 255)
                                                    ].join(',') + ')';
                                                }
                                            },
                                            emphasis: {
                                                shadowBlur: 10,
                                                shadowColor: '#333'
                                            }
                                        },
                                        data: data.values
                                    }
                                ]

                            }
                        ];
                        echwdcloud[index].setOption(plat[index]);
                        window.onresize = echwdcloud[index].resize;
                        echwdcloud[index].hideLoading();
                    }
                });
            };
        if (!elemwdcloud[0]) return;
        renderwdcloud(0);

        //地图
        var echDistribution = [],
            elemDistribution = $('#Distribution').children('div')
            , renderDistribution = function (index) {
                echDistribution[index] = echarts.init(elemDistribution[index], layui.echartsTheme);
                echDistribution[index].showLoading({text: '正在加载数据'});
                $.ajax({
                    url: "/api/getPositionNumber/",
                    method: 'POST',
                    success: function (data) {
                        var plat = [
                            {
                                title: {
                                    text: data.title,
                                    subtext: data.subtitle
                                },
                                tooltip: {
                                    trigger: 'item'
                                },
                                dataRange: {
                                    orient: 'horizontal',
                                    min: 0,
                                    max: data.range_max,
                                    text: ['高', '低'],           // 文本，默认为数值文本
                                    splitNumber: 0,
                                    range: [0, data.range_max],
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
                                        data: data.values
                                        // {name: '广东', value: 53210.28(, selected: true)}

                                    }

                                ],

                            }
                        ];
                        echDistribution[index].setOption(plat[index]);
                        window.onresize = echDistribution[index].resize;
                        echDistribution[index].hideLoading();
                    }
                });
            };
        if (!elemDistribution[0]) return;
        renderDistribution(0);

        //职位学历要求
        var echEduNum = [],
            elemEduNum = $('#EduNum').children('div'),
            renderEduNum = function (index) {
                echEduNum[index] = echarts.init(elemEduNum[index], layui.echartsTheme);
                echEduNum[index].showLoading({text: '正在加载数据'});

                $.ajax({
                    url: "/api/getEduNumber/",
                    method: 'POST',
                    success: function (data) {
                        var EduNum = [
                            {
                                title: {
                                    text: data.title,
                                    subtext: data.subtitle
                                },
                                tooltip: {
                                    trigger: 'item',
                                    formatter: "{a} <br/>{b} : {c}家公司 ({d}%)"
                                },
                                legend: {
                                    data: data.xAxis
                                },
                                series: [
                                    {
                                        name: '职位学历要求',
                                        type: 'pie',
                                        radius: '55%',
                                        center: ['50%', '60%'],
                                        data: data.values,
                                        itemStyle: {
                                            emphasis: {
                                                shadowBlur: 10,
                                                shadowOffsetX: 0,
                                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                                            }
                                        }
                                    }
                                ]
                            }
                        ];
                        echEduNum[index].setOption(EduNum[index]);
                        window.onresize = echEduNum[index].resize;
                        echEduNum[index].hideLoading();
                    }
                });
            };
        if (!elemEduNum[0]) return;
        renderEduNum(0);

        //职位经验要求
        var echExpNum = [],
            elemExpNum = $('#ExpNum').children('div'),
            renderExpNum = function (index) {
                echExpNum[index] = echarts.init(elemExpNum[index], layui.echartsTheme);
                echExpNum[index].showLoading({text: '正在加载数据'});

                $.ajax({
                    url: "/api/getExpNumber/",
                    method: 'POST',
                    success: function (data) {
                        var ExpNum = [
                            {
                                title: {
                                    text: data.title,
                                    subtext: data.subtitle
                                },
                                tooltip: {
                                    trigger: 'item',
                                    formatter: "{a} <br/>{b} : {c}个职位"
                                },
                                legend: {
                                    data: ['python方向']
                                },
                                xAxis: [
                                    {
                                        type: 'category',
                                        data: data.xAxis
                                    }
                                ],
                                yAxis: [
                                    {
                                        type: 'value'
                                    }
                                ],
                                series: [
                                    {
                                        name: 'python方向',
                                        type: 'bar',
                                        data: data.values,
                                    }
                                ]
                            }
                        ];
                        echExpNum[index].setOption(ExpNum[index]);
                        window.onresize = echExpNum[index].resize;
                        echExpNum[index].hideLoading();
                    }
                });
            };
        if (!elemExpNum[0]) return;
        renderExpNum(0);

        //每日入库量
        var dailyNum = [],
            elemDailyNum = $('#dailyNum').children('div'),
            renderDailyNum = function (index) {
                dailyNum[index] = echarts.init(elemDailyNum[index], layui.echartsTheme);
                dailyNum[index].showLoading({text: '正在加载数据'});

                $.ajax({
                    url: "/api/getDailyNumber/",
                    method: 'POST',
                    success: function (data) {
                        heapline = [
                            {
                                tooltip: {
                                    trigger: 'axis'
                                },
                                // legend: {data: ['邮件营销', '联盟广告', '视频广告', '直接访问', '搜索引擎']},
                                legend: {data: ['python职位']},
                                calculable: true,
                                xAxis: [
                                    {
                                        type: 'category',
                                        boundaryGap: false,
                                        data: data.xAxis
                                    }
                                ],
                                yAxis: [
                                    {
                                        type: 'value'
                                    }
                                ],
                                series: [
                                    {
                                        name: 'python职位',
                                        type: 'line',
                                        stack: '总量',
                                        data: data.values,
                                        markPoint: {
                                            data: [{type: 'max', name: '最大值'}, {type: 'min', name: '最小值'}]
                                        },
                                        markLine: {
                                            data: [{type: 'average', name: '平均值'}]
                                        }
                                    }
                                ]
                            }
                        ];
                        dailyNum[index].setOption(heapline[index]);
                        window.onresize = dailyNum[index].resize;
                        dailyNum[index].hideLoading();
                    }
                });
            };
        if (!elemDailyNum[0]) return;
        renderDailyNum(0);

        //公司规模
        var echCompanyScale = [],
            elemCompanyScale = $('#companyScale').children('div'),
            renderCompanyScale = function (index) {
                echCompanyScale[index] = echarts.init(elemCompanyScale[index], layui.echartsTheme);
                echCompanyScale[index].showLoading({text: '正在加载数据'});

                $.ajax({
                    url: "/api/getCpyScale/",
                    method: 'POST',
                    success: function (data) {
                        var CompanyScale = [
                            option = {
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
                                    data: data.values
                                }]
                            }

                        ];
                        echCompanyScale[index].setOption(CompanyScale[index]);
                        window.onresize = echCompanyScale[index].resize;
                        echCompanyScale[index].hideLoading();
                    }
                });
            };
        if (!elemCompanyScale[0]) return;
        renderCompanyScale(0);

        //公司融资
        var echFinancing = [],
            elemFinancing = $('#companyFinancing').children('div'),
            renderFinancing = function (index) {
                echFinancing[index] = echarts.init(elemFinancing[index], layui.echartsTheme);
                echFinancing[index].showLoading({text: '正在加载数据'});

                $.ajax({
                    url: "/api/getCpyFinancing/",
                    method: 'POST',
                    success: function (data) {
                        var Financing = [
                            {
                                title: {
                                    text: data.title,
                                    subtext: data.subtitle
                                },
                                tooltip: {
                                    trigger: 'item',
                                    formatter: "{a} <br/>{b} : {c}家公司 ({d}%)"
                                },
                                legend: {
                                    // orient: 'vertical',
                                    top: 100,
                                    data: data.xAxis
                                },
                                series: [
                                    {
                                        name: '公司融资情况',
                                        type: 'pie',
                                        radius: '55%',
                                        center: ['50%', '60%'],
                                        roseType : 'area',
                                        data: data.values,
                                        itemStyle: {
                                            emphasis: {
                                                shadowBlur: 10,
                                                shadowOffsetX: 0,
                                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                                            }
                                        }
                                    }
                                ]
                            }
                        ];
                        echFinancing[index].setOption(Financing[index]);
                        window.onresize = echFinancing[index].resize;
                        echFinancing[index].hideLoading();
                    }
                });
            };
        if (!elemFinancing[0]) return;
        renderFinancing(0);

        //公司所属行业分布
        var echheaparea = [],
            elemheaparea = $('#cpyIndustry').children('div'),
            renderheaparea = function (index) {
                echheaparea[index] = echarts.init(elemheaparea[index], layui.echartsTheme);
                echheaparea[index].showLoading({text: '正在加载数据'});

                $.ajax({
                    url: "/api/getCpyIndustry/",
                    method: 'POST',
                    success: function (data) {
                        var heaparea = [{
                    // title: {
                    //     text: '世界人口总量',
                    //     subtext: '数据来自网络'
                    // },
                    tooltip: {
                        trigger: 'item',
                        formatter: "{a} <br/>{b} : {c}家公司"
                    },
                    legend: {
                        data: ['python方向']
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
                        data: data.xAxis
                    },
                    series: [
                        {
                            name: 'python方向',
                            type: 'bar',
                            data: data.values
                        }
                    ]
                }];
                        echheaparea[index].setOption(heaparea[index]);
                        window.onresize = echheaparea[index].resize;
                        echheaparea[index].hideLoading();
                    }
                });
        };
        if (!elemheaparea[0]) return;
        renderheaparea(0);

    });

    exports('senior', {})

});