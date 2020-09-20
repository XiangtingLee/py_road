layui.define(function (exports) {

    //区块轮播切换
    layui.use(['admin', 'carousel', 'treeTable'], function () {
        var $ = layui.$
            , admin = layui.admin
            , carousel = layui.carousel
            , element = layui.element
            , treeTable = layui.treeTable
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

        // 国内疫情
        treeTable.render({
            elem: '#treeTableInternal',
            data: eval($("#data-internal").data("internal")),
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
            data: eval($("#data-foreign").data("foreign")),
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

    });
    exports('visualization', {})
});