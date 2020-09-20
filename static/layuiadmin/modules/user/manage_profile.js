layui.define('form', function (exports) {
    layui.extend({
        croppers: '../lib/extend/cropper/croppers'
    }).use(['form', 'croppers'], function () {
        var $ = layui.$
                , index = parent.layer.getFrameIndex(window.name)
                , layer = layui.layer
                , form = layui.form
                , croppers = layui.croppers;

            croppers.render({
                elem: '#face_img'
                , saveW: 150     //保存宽度
                , saveH: 150
                , mark: 1 / 1    //选取比例
                , area: '400px'  //弹窗宽度
                , url: "/user/info/upload/"  //图片上传接口返回和（layui 的upload 模块）返回的JOSN一样
                , done: function (url) { //上传完毕回调
                    $("#inputimgurl").val(url);
                    $("#face_img").attr('src', url);
                }
            });

            form.render(null, 'component-form-group');

            /* 自定义验证规则 */
            form.verify({
                nickname: function (value) {
                    if (!value) {return '昵称不能为空';}
                    if (value.length > 50) {return '名称过长，请重新输入';}
                },
                username: function (value) {
                    if (!value) {return '用户名不能为空';}
                    if (value.length > 50) {return '名称过长，请重新输入';}
                },
                mobile: function (value) {
                    if(value&&!value.match(/^1[0-9]{10}$/)){return '手机号格式错误，请重新输入';}
                },
                email: function (value) {
                    if(value&&!value.match(/^[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?$/)){return '邮箱格式错误，请重新输入';}
                }
            });

            /* 监听提交 */
            form.on('submit(do-submit)', function (formData) {
                var send_url = "/user/manage/profile/";
                send_url = send_url + document.location.toString().split("/").slice(-2, -1)[0] + '/';
                $.ajax({
                    url: send_url,
                    type:'post',
                    data:formData.field,
                    beforeSend:function () {
                        this.layerIndex = layer.load(0, { shade: [0.5, '#393D49'] });
                    },
                    success:function(data){
                        if(data.status == 'error'){
                            layer.msg(data.msg,{icon: 5});
                            return false;
                        }else if(data.status == 'success'){
                            layer.msg(data.msg, {icon: 6, time: 1000}, function(){
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
            });
    });
    exports('administrative_div', {})
});