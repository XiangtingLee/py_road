layui.define('form', function (exports) {
    layui.use(['table'], function () {
        var $ = layui.$
            , table = layui.table;

        table.render({
            elem: '#record-table'
            , data: eval($("#file-data").data("file"))
            , cols: [[
                {checkbox: true}
                , {type: 'numbers', title: '序号'}
                , {field: 'name', width: 150, title: '名称', edit: 'text'}
                , {field: 'path', title: '路径'}
            ]]
            , page: {layout: ['prev', 'page', 'next', 'skip'], limit: 5}
        });

        var active = {
            add: function () {
                var checkStatus = table.checkStatus('record-table')
                    , data = checkStatus.data;
                if (!data.length) {
                    layer.msg("请选择要添加的项目", {icon: 5});
                    return false;
                }
                for (var i = 0; i < data.length; i++) {
                    if (!data[i].name) {
                        layer.msg("请检查名称是否都已填写", {icon: 5});
                        return false;
                    }
                }
                $.ajax({
                    url: "/public/spider/manage/edit/0/",
                    type: 'post',
                    data: {'data': JSON.stringify(data)},
                    beforeSend: function () {
                        this.layerIndex = layer.load(0, {shade: [0.5, '#393D49']});
                    },
                    success: function (data) {
                        if(data.code === 20008) {
                            layer.msg(data.msg, {icon: 5, time: 1000}, function () {
                                setTimeout('window.location.reload();', 1000);
                            });
                            return false;
                        }
                        if(data.code != 0){
                            layer.msg(data.msg, {icon: 5});
                            return false;
                        } else  {
                            layer.msg(data.msg, {icon: 6, time: 1000}, function () {
                                parent.location.reload();
                                parent.layer.close(index);
                            });
                        }
                    },
                    complete: function () {
                        layer.close(this.layerIndex);
                    },
                });
                return false;
            }
        };

        $('.record-table-btn .layui-btn').on('click', function () {
            var type = $(this).data('type');
            active[type] ? active[type].call(this) : '';
        });
    });
    exports('spider_manage_probe', {})
});