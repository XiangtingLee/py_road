layui.define(function (exports) {

    //区块轮播切换
    layui.use(['flow'], function () {
        var $ = layui.$
            , element = layui.element
            , flow = layui.flow;

        element.render();

        flow.load({
            elem: '#test-flow-auto'
            , done: function (page, next) {
                $.post('/COVID19/timeline/data/', {page: page, limit: 10}, function (res) {
                    var lis = [];
                    layui.each(res.content.result, function (index, item) {
                        var str_start = '<li class="layui-timeline-item">\n' +
                            '    <i class="layui-icon layui-timeline-axis"></i>\n' +
                            '    <div class="layui-timeline-content layui-text">\n' +
                            '        <h3 class="layui-timeline-title">' + item.pub_time_diff + '<small style="color: #999999;">\n' +
                            '            ' + item.publish_time.replace("T", "\t") + '</small></h3>\n' +
                            '        <div onclick="lay_open(\'' + item.title + '\',\'' + item.source_url + '\')" style="text-decoration: none; cursor: pointer;">\n' +
                            '            <fieldset class="layui-elem-field">\n' +
                            '                <legend><b style="color: #000000;">'
                            , str_end = '                    ' + item.title + '</b></legend>\n' +
                            '                <div class="layui-field-box">\n' +
                            '                    <p style="color: #999999;">' + item.source_summary + '</p>\n' +
                            '                    <p style="text-align: right;color: #999999;">信息来源：' + item.source_info + '</p>\n' +
                            '                </div>\n' +
                            '            </fieldset>\n' +
                            '        </div>\n' +
                            '    </div>\n' +
                            '</li>'
                            , latest = '<span class="layui-badge">最新</span>\n'
                            , display;
                        if (item.latest) {
                            display = str_start + latest + str_end
                        } else {
                            display = str_start + str_end
                        }
                        lis.push(display)
                    });
                    next(lis.join(''), page < res.content.totalPage);
                });
            },
            end: '<li class="layui-timeline-item">\n' +
                '     <i class="layui-icon layui-timeline-axis"></i>\n' +
                '     <div class="layui-timeline-content layui-text">\n' +
                '         <div class="layui-timeline-title" style="text-align: left;">过去</div>\n' +
                '     </div>\n' +
                ' </li>'
        });

    });
    exports('timeline', {})
});

function lay_open(title, url) {
    layui.use(['jquery', 'layer'], function () {
        var $ = layui.$ //重点处
            , layer = layui.layer;
        layer.open({
            type: 2,
            title: title,
            shade: false,
            maxmin: true,
            area: ['90%', '90%'],
            content: url
        });
    });
}