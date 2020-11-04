layui.define(function (exports) {
    layui.use(['table', 'form', 'upload'], function () {
        var table = layui.table
            , form = layui.form
            , $ = layui.jquery
            , upload = layui.upload;

        table.render({
            elem: '#proxy-data-form'
            , url: '/public/proxy/filter/'
            , method: 'GET'
            , cellMinWidth: 80
            , toolbar: '#proxy-toolbar'
            , title: '数据表'
            , cols: [[
                {type: 'checkbox', fixed: 'left'}
                , {field: 'id', title: 'ID', width: 80, fixed: 'left', sort: true}
                , {field: 'type__name', title: '代理类型', minWidth: 200}
                , {field: 'protocol__name', title: '代理协议', width: 90}
                , {field: 'address', title: '代理地址', width: 150}
                , {field: 'port', title: '端口号', width: 100}
                , {
                    field: 'add_time', title: '入库时间', minWidth: 180, sort: true, templet: function (d) {
                        return d.add_time.replace("T", "\t");
                    }
                }
                , {
                    field: 'update_time', title: '更新时间', minWidth: 180, sort: true, templet: function (d) {
                        return d.update_time.replace("T", "\t");
                    }
                }
                , {
                    field: 'is_available',
                    title: '是否有效',
                    width: 100,
                    templet: '#test-table-switchTpl',
                    unresize: true,
                    sort: true
                }
            ]]
            ,
            page: true
            , id: 'proxyForm'
        });

        table.on('toolbar(proxy-data-form)', function (obj) {
            var checkStatus = table.checkStatus(obj.config.id);
            switch (obj.event) {
                case 'verify':
                    var verifyData = checkStatus.data;
                    validityids = [];
                    /*
                    if (verifyData.length === 0) {
                        layer.msg('请选择需要验证的数据', {icon: 5, time: 2000});
                    } else {
                    */
                    for (var i = 0; i < verifyData.length; i++) {
                        validityids.push(verifyData[i].id);
                    }
                    layer.confirm('即将执行验证操作，是否继续？', function () {
                        layer.msg('正在验证', {icon: 16, time: 500}, function () {
                            verify(validityids, table);
                        });
                    });
                    //}
                    break;
            }
        });
        var initUpload = function () {
            $(".layui-btn-container").append('<button type="button" class="layui-btn layui-btn-sm" id="upload"><i class="layui-icon"></i>导入</button>');
            upload.render({ //允许上传的文件后缀
                elem: '#upload'
                , url: '/public/proxy/upload/'
                , accept: 'file' //普通文件
                , exts: 'csv' //只允许上传csv文件
                , data: {
                    'csrfmiddlewaretoken': function () {
                        //return $(":input:first").val();
                        return $("input[name='csrfmiddlewaretoken']").attr('value');
                    }
                }
                , done: function (res) {
                    if (res.status === 1) {
                        layer.msg('上传成功', {icon: 1}, function () {
                            table.reload('proxyForm', {
                                page: {
                                    curr: 1 //重新从第 1 页开始
                                }
                                , where: {key: {}}
                            }, 'data');
                            initUpload();
                        });
                    } else if (res.status === 0) {
                        layer.msg('上传失败，' + res.message, {icon: 2});
                    }
                }
            });
        };
        initUpload();

        //监听修改有效性操作
        form.on('switch(test-table-sexDemo)', function (obj) {
            var id = this.value;
            layui.use(['jquery', 'layer'], function () {
                var $ = layui.$
                    , layer = layui.layer;
                $.ajax({
                    url: "/public/proxy/change/",
                    method: 'POST',
                    data: {'id': id, 'is_available': obj.elem.checked},
                    success: function (res) {
                        if (res.status === 1) {
                            layer.tips('修改成功', obj.othis); //获取按钮状态 obj.elem.checked
                        } else {
                            layer.tips('修改失败，请重试', obj.othis);
                            obj.elem.checked = !obj.elem.checked;
                            form.render();
                        }
                    }
                });
            });
        });

        $('#filter').on('click', function () {
            table.reload('proxyForm', {
                url: "/public/proxy/filter?" + $('#filter-form').serialize()
                , page: {curr: 1}
                , method: "GET"
                , where: {}
            }, 'data');
            initUpload();
        });

    });
    exports('proxy_pool', {})
});

//验证
function verify(ids, dataEle) {
    layui.use(['jquery', 'layer'], function () {
        var $ = layui.$
            , layer = layui.layer;
        $.ajax({
            url: "/public/proxy/check/",
            method: 'POST',
            data: {'ids': ids},
            success: function (data) {
                layer.msg('验证完毕，共验证' +
                    data.result.count + '条代理，' +
                    '有效' + data.result.valid + '条，失效' + data.result.invalid + '条',
                    {icon: 1, time: 1000}, function () {
                        dataEle.reload('proxyForm', {
                            page: {
                                curr: 1 //重新从第 1 页开始
                            }
                            , where: {
                                key: {
                                    id: demoReload.val()
                                }
                            }
                        }, 'data');
                    });
            }
        });
    });
}