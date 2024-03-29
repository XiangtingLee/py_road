layui.define(['table', 'form', 'tree', 'slider', 'treeSelect', 'laydate'], function (exports) {
    var table = layui.table
        , $ = layui.jquery
        , form = layui.form
        , slider = layui.slider
        , treeSelect = layui.treeSelect
        , laydate = layui.laydate;

    form.render();

    // 加载日历组件
    lay('.date-range').each(function () {
        laydate.render({
            elem: this
            , type: 'datetime'
            , range: true
        });
    });

    slider.render({
        elem: '#salaryRange'
        , value: 100
        , range: true
        , setTips: function (val) {
            return val + 'K';
        }
        , change: function (val) {
            $('#filterSalary').val(val[0] + "," + val[1]);
        }
    });
    treeSelect.render({
        elem: '#filterLocation',
        data: '/position/display/node/data/',
        type: 'post',
        placeholder: '请选择所在城市',
        search: true,
        style: {
            folder: {
                enable: false
            },
            line: {
                enable: true
            }
        },
        click: function (d) {
            $('#filterLocation').val(d.current.name);
            $('#filterLocation').attr("name", d.current.type);
        }
    });

    //方法级渲染
    table.render({
        elem: '#dataTableWithToolBar'
        , url: '/position/display/filter/'
        , method: 'GET'
        , toolbar: true
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
            , {field: 'company__name', title: '公司全称', minWidth: 101, sort: true}
            , {field: 'company__short_name', title: '公司简称', minWidth: 101, sort: true}
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
                field: 'update_time', title: '最后更新', width: 155, sort: true, templet: function (d) {
                    return d.update_time.replace("T", "\t").split(".")[0];
                }
            }
            , {fixed: 'right', title: '操作', width: 80, align: 'center', toolbar: '#item-operation'}
        ]]
        , id: 'dataForm'
        , page: true
    });

    var $ = layui.$, active = {
        filter: function () {
            const filter = $('#filterData').serialize();
            table.reload('dataForm', {
                url: "/position/display/filter/?" + filter
                , page: {curr: 1}
                , method: "GET"
                , where: {}
            }, 'data');
        }
    };

    $('#filter').on('click', function () {
        const type = $(this).data('type');
        active[type] ? active[type].call(this) : '';
    });
    //监听行工具事件
    table.on('tool(list-filter)', function (obj) { //注：tool 是工具条事件名，test 是 table 原始容器的属性 lay-filter="对应的值"
        const data = obj.data //获得当前行数据
            , layEvent = obj.event; //获得 lay-event 对应的值
        if (layEvent === 'detail') {
            window.open("https://www.lagou.com/jobs/" + data.id + ".html");
            // var iframe = layer.open({
            //     type: 2,
            //     title: data.position_name,
            //     shade: false,
            //     maxmin: true,
            //     content: "https://www.lagou.com/jobs/" + data.id + ".html"
            // });
            // layer.full(iframe);

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
    exports('display', {});
});

