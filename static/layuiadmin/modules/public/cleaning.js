layui.define('form', function (exports) {
    layui.use(['table'], function () {
        var table = layui.table;

        table.render({
            elem: '#data-table'
            , url: '/position/cleaning/filter/'
            , method: 'GET'
            , toolbar: '#toolbar'
            , title: '用户数据表'
            , parseData: function (res) {
                return {
                    data: res.data,
                    msg: res.msg,
                    code: res.code,
                    count: res.extra.total
                }
            }
            , cols: [[
                {type: 'checkbox', fixed: 'left'}
                , {field: 'id', title: 'ID', width: 90, fixed: 'left', sort: true}
                , {field: 'name', title: '职位名称', minWidth: 150}
                , {field: 'type__name', title: '职位类型', width: 101, sort: true}
                , {field: 'company__short_name', title: '公司名称', minWidth: 101, sort: true}
                , {field: 'city__name', title: '所在城市', width: 101, sort: true}
                , {field: 'district__name', title: '所在地点', width: 91}
                , {field: 'education__name', title: '学历要求', width: 101, sort: true}
                , {field: 'experience__name', title: '经验要求', width: 101, sort: true}
                , {field: 'salary', title: '薪资', width: 80, sort: true}
                , {
                    field: 'status', title: '职位状态', width: 101, sort: true, templet: function (d) {
                        return ["已过期", "已下线", "有效", "待发布"][d.status + 1]
                    }
                }
                , {
                    field: 'update_time', title: '最后修改时间', width: 155, sort: true, templet: function (d) {
                        return d.update_time.replace("T", "\t").split(".")[0];
                    }
                }
                , {fixed: 'right', title: '操作', width: 80, align: 'center', toolbar: '#item-operation'}
            ]]
            , id: 'dataForm'
            , page: true
        });

        table.on('tool(data-table)', function (obj) {
            const data = obj.data //获得当前行数据
                , layEvent = obj.event; //获得 lay-event 对应的值
            if (layEvent === 'detail') {
                window.open("https://www.lagou.com/jobs/" + data.id + ".html")
            } else if (layEvent === 'del') {
                layer.confirm('真的删除行么', function (index) {
                    obj.del(); //删除对应行（tr）的DOM结构
                    layer.close(index);
                    //向服务端发送删除指令
                });
            } else if (layEvent === 'edit') {
                layer.msg('编辑操作');
            }
        });

        //头工具栏事件
        table.on('toolbar(data-table)', function (obj) {
                var checkStatus = table.checkStatus(obj.config.id);
                switch (obj.event) {
                    case 'reloadData':
                        reloadData(table);
                        break;
                    case 'duplicateCheck':
                        var duplicateData = checkStatus.data;
                        var duplicateIds = [];
                        if (duplicateData.length === 0) {
                            layer.msg('请选择需要去重的数据', {icon: 5, time: 2000});
                        } else {
                            for (var i = 0; i < duplicateData.length; i++) {
                                duplicateIds.push(duplicateData[i].id);
                            }
                            layer.confirm('即将执行去重操作，是否继续？', function () {
                                layer.msg('正在去重', {icon: 16, time: 500}, function () {
                                    deDuplication(duplicateIds, table);
                                });
                            });
                        }
                        break;
                    case 'duplicateAll':
                        layer.confirm('即将执行去重操作，是否继续？', function () {
                            layer.msg('正在去重', {icon: 16, time: 500}, function () {
                                deDuplication([], table);
                            });
                        });
                        break;
                    case 'validityCheck':
                        var validityData = checkStatus.data;
                        validityids = [];
                        if (validityData.length === 0) {
                            layer.msg('请选择需要检查的数据', {icon: 5});
                        } else {
                            for (var i = 0; i < validityData.length; i++) {
                                validityids.push(validityData[i].id);
                            }
                            layer.confirm('即将执行数据检查操作，是否继续？', function () {
                                layer.msg('正在检测', {icon: 16, time: 500}, function () {
                                    validityCheck(validityids, table);
                                });
                            });
                        }
                        break;
                    case 'validityCheckAll':
                        layer.confirm('即将执行数据检查操作，是否继续？', function () {
                            layer.msg('正在检测', {icon: 16, time: 500}, function () {
                                validityCheck([], table);
                            });
                        });
                        break;
                }
            });
    })
    //去重
    function deDuplication(ids, dataEle) {
        layui.use(['jquery', 'layer'], function () {
            var $ = layui.$
                , layer = layui.layer;
            $.ajax({
                url: "{% url 'datas:deDuplication' %}",
                url: "***************",
                method: 'POST',
                data: {'ids': ids},
                success: function (data) {
                    layer.msg('去重成功，' +
                        data.result.repeat_row + '条数据，共去重' + data.result.effect_row + '条',
                        {icon: 1, time: 1000}, function(){
                            window.location.reload();
                        });
                }
            });
        });
    }

    //有效性检测
    function validityCheck(ids, dataEle) {
        layui.use(['jquery', 'layer'], function () {
            var $ = layui.$ //重点处
                , layer = layui.layer;
            $.ajax({
                url: "{% url 'position:cleaning_check' %}",
                method: 'POST',
                data: {'ids': ids},
                success: function (data) {
                    layer.msg('检测成功，共检测' +
                        data.result.check_row + '条数据，失效' + data.result.effect_row + '条',
                        {icon: 1}, function(){
                            reloadData(dataEle);
                        });
                }
            });
        });
    }

    //数据重载
    function reloadData(dataEle) {
        dataEle.reload('dataForm', {
            page: {
                curr: 1 //重新从第 1 页开始
            }
            , where: {
                key: {
                    // {#id: demoReload.val()#}
                }
            }
        }, 'data');
}
    exports('display', {})
});