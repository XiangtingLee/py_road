layui.define(['form', 'layedit'], function (exports) {
        let $ = layui.$
            , index = parent.layer.getFrameIndex(window.name)
            , layer = layui.layer
            , form = layui.form
            , layedit = layui.layedit;


        let codeEditor = layedit.build("code-editor");
        layedit.setContent(codeEditor, code);

        form.render(null, 'component-form-group');

        /* 自定义验证规则 */
        form.verify({
            name: function (value) {
                if (!value) {
                    return '请填写爬虫名称';
                }
                if (value.length > 50) {
                    return '名称过长，请重新输入';
                }
            }
            , path: [/^([\\\/].*?\.py)$/, '输入的路径有误']
        });

        /* 监听提交 */
        form.on('submit(do-submit)', function (formData) {
            formData.field.code = layedit.getContent(codeEditor);
            var send_url = "/public/spider/component/edit/0/";
            send_url = send_url.replace("/0/", '/' + document.location.toString().split("/")[7] + '/');
            $.ajax({
                url: send_url,
                type: 'post',
                data: formData.field,
                beforeSend: function () {
                    this.layerIndex = layer.load(0, {shade: [0.5, '#393D49']});
                },
                success: function (data) {
                    if (data.code != 0) {
                        layer.msg(data.msg, {icon: 5});
                        return false;
                    } else {
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
        });

        $(".layui-icon-help").mouseover(function () {
            layer.tips('相对于项目所在的路径。例:/myapp/spider/myspider.py', this, {
                tips: [1, "#000"]
            });
        });
    exports('spider_component_edit', {});
});