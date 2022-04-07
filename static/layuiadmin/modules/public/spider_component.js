layui.define('form', function (exports) {
    layui.use(['table'], function () {
        var $ = layui.$
            , table = layui.table;

        table.render({
            elem: '#record-table'
            , url: '/public/spider/component/data/'
            , method: 'GET'
            , parseData: function (res) {
                return {
                    data: res.data,
                    msg: res.msg,
                    code: res.code,
                    count: res.extra.total
                }
            }
            , cols: [[
                {type: 'numbers', title: '序号', fixed: 'left'}
                , {field: 'name', minWidth: 120, title: '名称'}
                , {field: 'description', minWidth: 300, title: '描述'}
                , {
                    field: 'frame_available', width: 90, title: '框架可用',
                    templet: function (d) {
                        if (d.frame_available) return "是";
                        return "否";
                    }
                }
                , {
                    field: 'add_time', width: 160, title: '添加时间', sort: true,
                    templet: function (d) {
                        return d.add_time.replace("T", "\t").split(".")[0];
                    }
                }
                , {
                    field: 'update_time', width: 160, title: '修改时间', sort: true,
                    templet: function (d) {
                        return d.update_time.replace("T", "\t").split(".")[0];
                    }
                }
                , {width: 178, align: 'center', fixed: 'right', toolbar: '#table-operate', title: '操作'}
            ]]
            , page: true
            , id: 'record'
        });

        //监听工具条
        table.on('tool(record-table)', function (obj) {
            var data = obj.data;
            if (obj.event === 'detail') {
                var code_url = "/public/spider/component/show/0/";
                var index = layer.open({
                    type: 2,
                    title: data.name + ' - 组件信息',
                    shade: 0,
                    maxmin: true,
                    area: ['375px', '425px'],
                    content: code_url.replace("/0/", '/' + data.id + '/'),
                });
                layer.full(index);
            } else if (obj.event === 'del') {
                layer.confirm('真的删除行么？</br>此操作将从数据库中物理删除，无法恢复！', {
                    icon: 3,
                    title: '警告',
                    skin: "my-skin"
                }, function (index) {
                    layer.confirm('推荐在"编辑"功能中将记录标记为"已删除"。</br>您确定要删除吗？', {
                        icon: 3,
                        title: '警告',
                        skin: "my-skin"
                    }, function (index) {
                        obj.del();
                        layer.close(index);
                    });
                });
            } else if (obj.event === 'edit') {
                var content_url = "/public/spider/component/edit/0/";
                var window = layer.open({
                    type: 2,
                    title: '编辑组件信息',
                    shadeClose: true,
                    maxmin: true,
                    shade: 0.8,
                    area: ['800px', '600px'],
                    content: content_url.replace("/0/", '/' + data.id + '/'),
                });
                layer.full(window);
            }
        });

        var active = {
            add: function () {
                var window = layer.open({
                    type: 2,
                    title: '添加组件',
                    shadeClose: true,
                    shade: 0.8,
                    maxmin: true,
                    area: ['800px', '600px'],
                    content: '/public/spider/component/edit/0/'
                });
                layer.full(window);
            }
        };

        $('.record-table-btn .layui-btn').on('click', function () {
            var type = $(this).data('type');
            active[type] ? active[type].call(this) : '';
        });
    });
    exports('spider_component', {})
});