layui.define(['jquery', 'admin', 'form', 'supersized'], function (exports) {
    var $ = layui.$
        , admin = layui.admin
        , form = layui.form;
    var obj = {
        bg: function () {
            $.supersized({
                // 功能
                slide_interval: 4000,    // 转换之间的长度
                transition: 1,    // 0 - 无，1 - 淡入淡出，2 - 滑动顶，3 - 滑动向右，4 - 滑底，5 - 滑块向左，6 - 旋转木马右键，7 - 左旋转木马
                transition_speed: 1000,    // 转型速度
                performance: 1,    // 0 - 正常，1 - 混合速度/质量，2 - 更优的图像质量，三优的转换速度//（仅适用于火狐/ IE浏览器，而不是Webkit的）

                // 大小和位置
                min_width: 0,    // 最小允许宽度（以像素为单位）
                min_height: 0,    // 最小允许高度（以像素为单位）
                vertical_center: 1,    // 垂直居中背景
                horizontal_center: 1,    // 水平中心的背景
                fit_always: 0,    // 图像绝不会超过浏览器的宽度或高度（忽略分钟。尺寸）
                fit_portrait: 1,    // 纵向图像将不超过浏览器高度
                fit_landscape: 0,    // 景观的图像将不超过宽度的浏览器

                // 组件
                slide_links: 'blank',    // 个别环节为每张幻灯片（选项：假的，'民'，'名'，'空'）
                slides: [    // 幻灯片影像
                    {image: '../../static/layuiadmin/style/res/bg1.jpg'},
                    {image: '../../static/layuiadmin/style/res/bg2.jpg'},
                    {image: '../../static/layuiadmin/style/res/bg3.jpg'}
                ]

            });

        },
        reg: function (act_url) {
            verify();
            act(act_url, "注册");
        },
        reg_guide: function (act_url) {
            verify();
            act(act_url, "继续");
        },
        login: function (act_url) {
            act(act_url, "", true);
        },
        reset: function (act_url) {
            verify();
            act(act_url, "修改");
        },
        ref_cap: function (dom_id) {
            $(document).on('click', "#" + dom_id, function () {
                ref_cap(dom_id);
            })
        }
    };

    function verify() {
        form.verify({
            username: [/^[a-zA-Z0-9_-]{4,16}$/, "用户名需为4到16位（可包括：字母，数字，下划线，减号）"]
            , pass: [/^.*(?=.{6,12})(?=.*\d)(?=.*[a-z])(?=.*[\.,;:"'!@#$%^&*?\/\\\|\[\]\{\}]).*$/,
                '密码为6-12位，包括至少1个小写字母，1个数字，1个特殊字符']
            , repass: function (value) {
                if ($("#pass").val() !== $("#repass").val()) {
                    return '两次密码输入不一致';
                }
            }
            , vercode: [/(\d+){6}$/, '验证码为6位数字']
        });
    }

    function act(url, agree = '', has_cap=false) {
        form.on('submit(act-form)', function (obj) {
            const field = obj.field;
            if (agree !== '' && !field.agreement) {
                return layer.msg('你必须同意用户协议才能' + agree);
            }
            admin.req({
                url: url
                , data: obj.field
                , method: 'POST'
                , done: function (res) {
                    layer.msg(res.msg, {
                        offset: '15px'
                        , icon: res.icon
                        , time: 1000
                    }, function () {
                        if (res.icon === 1) {
                            location.href = res.next;
                        }
                        if(has_cap){
                            ref_cap();
                        }
                    });

                }
            });
            return false;
        });
    }

    function ref_cap(){
        $.getJSON("/captcha/refresh", function (data) {
            $("#cap_key").attr("value", data.key);
            $("#cap_img").attr("src", data.image_url);
        })
    }

    exports('reg_login', obj);
});