/**

 @Name：layuiAdmin 用户管理 管理员管理 角色管理
 @Author：star1029
 @Site：http://www.layui.com/admin/
 @License：LPPL

 */


layui.define(['table', 'form'], function (exports) {
    var $ = layui.$
        , table = layui.table
        , form = layui.form;

    // 监听搜索
    $('#filter').on('click', function () {
        const filter = $('#filter-form').serialize();
        table.reload('user-list', {
            url: "/user/manage/filter/?" + filter
            , page: { curr: 1 }
            , method: "GET"
            , where: {}
        }, 'data');
    });

    //用户管理
    table.render({
        elem: '#user-list'
        , url: '/user/manage/filter/' //模拟接口
        , method: 'get'
        , cols: [[
            {type: 'checkbox', fixed: 'left'}
            , {field: 'id', width: 60, fixed: 'left', title: 'ID'}
            , {field: 'username', title: '用户名', minWidth: 100}
            , {field: 'nick_name', title: '昵称', minWidth: 100}
            , {
                field: 'face_img', title: '头像', width: 100, templet: function (d) {
                    if (!d.face_img) {
                        d.face_img = "/media/face_img/default.png"
                    }
                    return '<img style="display: inline-block; width: 50%; height: 100%;" src=' + d.face_img + '>'
                }
            }
            , {field: 'mobile', title: '手机'}
            , {field: 'email', title: '邮箱'}
            , {
                field: 'sex', width: 60, title: '性别', templet: function (d) {
                    var sex_d = {0: "女", 1: "男", 2: "未知"};
                    return sex_d[d.sex]
                }
            }
            , {field: 'last_login_ip', title: '上次登录IP'}
            , {field: 'date_joined', title: '注册时间', templet: function (d) {return d.date_joined.replace("T", " ")}}
            , {
                title: '操作', width: 150, align: 'center', fixed: 'right', templet: function (d) {
                    var options = '<a class="layui-btn layui-btn-normal layui-btn-xs" lay-event="edit"><i\n' +
                        '                        class="layui-icon layui-icon-edit"></i>编辑</a>\n';
                    if(d.is_active){
                        return options + '<a class="layui-btn layui-btn-danger layui-btn-xs" lay-event="ban"><i\n' +
                        '                        class="layui-icon layui-icon-face-cry"></i>封号</a>\n'}
                    else{return options + '<a class="layui-btn layui-btn-success layui-btn-xs" lay-event="deban"><i\n' +
                        '                        class="layui-icon layui-icon-face-smile"></i>解封</a>'}
                }
            }
        ]]
        , page: true
        , limit: 30
        , height: 'full-220'
        , text: {none: '无数据'}
    });

    //监听工具条
    table.on('tool(user-list)', function (obj) {
        var data = obj.data;
        if (obj.event === 'ban' || obj.event === 'deban' ) {
            var tips = '确认要封号？', form = {is_active: 0};
            if(obj.event === 'deban'){tips = '确认要解封？';form.is_active = 1}
            layer.confirm(tips, function (index) {
                $.ajax({
                    url: "/user/manage/profile/" + data.id + '/',
                    method: "post",
                    data: form,
                    success: function (data) {
                        if(data.status == 'error'){
                            layer.msg(data.msg,{icon: 5});
                            return false;
                        }else if(data.status == 'success'){
                            layer.msg(data.msg, {icon: 6, time: 1000}, function(){
                                table.reload('user-list');
                            });
                        }
                    }
                });
                layer.close(index);
            });
        } else if (obj.event === 'edit') {
            layer.open({
                type: 2
                , title: '编辑信息'
                , content: '/user/manage/profile/' + data.id + '/'
                , shadeClose: true
                , area: ['425px', '535px']
            });
        }
    });

    //管理员管理
    table.render({
        elem: '#LAY-user-back-manage'
        , url: layui.setter.base + 'json/useradmin/mangadmin.js' //模拟接口
        , cols: [[
            {type: 'checkbox', fixed: 'left'}
            , {field: 'id', width: 80, title: 'ID', sort: true}
            , {field: 'loginname', title: '登录名'}
            , {field: 'telphone', title: '手机'}
            , {field: 'email', title: '邮箱'}
            , {field: 'role', title: '角色'}
            , {field: 'jointime', title: '加入时间', sort: true}
            , {field: 'check', title: '审核状态', templet: '#buttonTpl', minWidth: 80, align: 'center'}
            , {title: '操作', width: 150, align: 'center', fixed: 'right', toolbar: '#table-useradmin-admin'}
        ]]
        , text: '对不起，加载出现异常！'
    });

    //监听工具条
    table.on('tool(LAY-user-back-manage)', function (obj) {
        var data = obj.data;
        if (obj.event === 'del') {
            layer.prompt({
                formType: 1
                , title: '敏感操作，请验证口令'
            }, function (value, index) {
                layer.close(index);
                layer.confirm('确定删除此管理员？', function (index) {
                    console.log(obj)
                    obj.del();
                    layer.close(index);
                });
            });
        } else if (obj.event === 'edit') {
            var tr = $(obj.tr);

            layer.open({
                type: 2
                , title: '编辑管理员'
                , content: '../../../user/administrators/adminform.html'
                , area: ['420px', '420px']
                , btn: ['确定', '取消']
                , yes: function (index, layero) {
                    var iframeWindow = window['layui-layer-iframe' + index]
                        , submitID = 'LAY-user-back-submit'
                        , submit = layero.find('iframe').contents().find('#' + submitID);

                    //监听提交
                    iframeWindow.layui.form.on('submit(' + submitID + ')', function (data) {
                        var field = data.field; //获取提交的字段

                        //提交 Ajax 成功后，静态更新表格中的数据
                        //$.ajax({});
                        table.reload('LAY-user-front-submit'); //数据刷新
                        layer.close(index); //关闭弹层
                    });

                    submit.trigger('click');
                }
                , success: function (layero, index) {

                }
            })
        }
    });

    //角色管理
    table.render({
        elem: '#LAY-user-back-role'
        , url: layui.setter.base + 'json/useradmin/role.js' //模拟接口
        , cols: [[
            {type: 'checkbox', fixed: 'left'}
            , {field: 'id', width: 80, title: 'ID', sort: true}
            , {field: 'rolename', title: '角色名'}
            , {field: 'limits', title: '拥有权限'}
            , {field: 'descr', title: '具体描述'}
            , {title: '操作', width: 150, align: 'center', fixed: 'right', toolbar: '#table-useradmin-admin'}
        ]]
        , text: '对不起，加载出现异常！'
    });

    //监听工具条
    table.on('tool(LAY-user-back-role)', function (obj) {
        var data = obj.data;
        if (obj.event === 'del') {
            layer.confirm('确定删除此角色？', function (index) {
                obj.del();
                layer.close(index);
            });
        } else if (obj.event === 'edit') {
            var tr = $(obj.tr);

            layer.open({
                type: 2
                , title: '编辑角色'
                , content: '../../../user/administrators/roleform.html'
                , area: ['500px', '480px']
                , btn: ['确定', '取消']
                , yes: function (index, layero) {
                    var iframeWindow = window['layui-layer-iframe' + index]
                        , submit = layero.find('iframe').contents().find("#LAY-user-role-submit");

                    //监听提交
                    iframeWindow.layui.form.on('submit(LAY-user-role-submit)', function (data) {
                        var field = data.field; //获取提交的字段

                        //提交 Ajax 成功后，静态更新表格中的数据
                        //$.ajax({});
                        table.reload('LAY-user-back-role'); //数据刷新
                        layer.close(index); //关闭弹层
                    });

                    submit.trigger('click');
                }
                , success: function (layero, index) {

                }
            })
        }
    });

    exports('user_admin', {})
});