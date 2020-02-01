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
            , node_list = ["pneumoniaSumCs", "pneumoniaSumCsStack", "pneumoniaSumCd"];
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
                    //新增趋势
                    "pneumoniaSumCs": {
                        tooltip: {trigger: "axis", formatter: sum_func},
                        legend: data.pneumonia_sum_cs.legend,
                        calculable: !0,
                        xAxis: [{type: "category", axisLabel: {rotate: 45}, boundaryGap: !1, data: data.pneumonia_sum_cs.xAxis}],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_sum_cs.series
                    },
                    //新增趋势
                    "pneumoniaSumCsStack": {
                        tooltip: {trigger: "axis", formatter: sum_func},
                        legend: data.pneumonia_sum_cs_stack.legend,
                        calculable: !0,
                        xAxis: [{type: "category", axisLabel: {rotate: 45}, boundaryGap: !1, data: data.pneumonia_sum_cs_stack.xAxis}],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_sum_cs_stack.series
                    },
                    //治愈/死亡趋势
                    "pneumoniaSumCd": {
                        tooltip: {trigger: "axis"},
                        legend: data.pneumonia_sum_cd.legend,
                        calculable: !0,
                        xAxis: [{type: "category", axisLabel: {rotate: 45}, boundaryGap: !1, data: data.pneumonia_sum_cd.xAxis}],
                        yAxis: [{type: "value"}],
                        series: data.pneumonia_sum_cd.series
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