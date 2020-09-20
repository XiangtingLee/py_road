layui.define('form', function (exports) {
    layui.extend({
        citypicker: '../lib/extend/city-picker/city-picker'
    }).use(['table', 'citypicker'], function () {
        var $ = layui.$
            , table = layui.table
            , cityPicker = layui.citypicker;

        table.render({
            elem: '#record-table'
            , url: '/public/administrativeDiv/filter/'
            , method: 'GET'
            , toolbar: 'default'
            , defaultToolbar: ["filter","exports"]
            , cols: [[
                {checkbox: true, fixed: 'left', rowspan: 2}
                , {field: 'id', width: 90, rowspan: 2, title: 'ID', hide: true}
                , {field: 'code', width: 90, rowspan: 2, title: '区划代码', edit: 'text'}
                , {field: 'name', width: 100, rowspan: 2, title: '名称', edit: 'text'}
                , {field: 'pinyin', width: 100, rowspan: 2, title: '全拼', edit: 'text'}
                , {field: 'short_name', width: 100, rowspan: 2, title: '简称', edit: 'text'}
                , {field: 'zip_code', width: 100, rowspan: 2, title: '邮政编码', edit: 'text'}
                , {align: 'center', colspan: 3, title: "三级区划", PARENT_COL: true,}
                , {field: "lng_lat", width: 180, rowspan: 2, title: "经纬度", edit: 'text'}
                , {
                    field: 'add_time', width: 170, rowspan: 2, title: '添加时间', sort: true,
                    templet: function (d) {
                        return d.add_time.replace("T", "\t");
                    }
                }
                , {
                    field: 'update_time', width: 170, rowspan: 2, title: '修改时间', sort: true,
                    templet: function (d) {
                        return d.update_time.replace("T", " ");
                    }
                }
            ], [
                {field: 'province_name', width: 100, title: '省级'}
                , {field: 'city_name', width: 100, title: '市级'}
                , {field: 'area_name', width: 100, title: '区县'}
            ]]
            , page: true
            , id: 'dataForm'
        });

        //监听单元格编辑
        table.on('edit(record-table)', function (obj) {
            $.ajax({
                url: '/public/administrativeDiv/edit/' + obj.data.id + '/'
                , method: 'get'
                , data: {k: obj.field, d: obj.value}
                , success: function (d) {
                    if (d.code !== 10000) {
                        table.reload('dataForm', {
                            where: {}
                        }, 'data');
                        layer.msg(d.msg, {icon: 5});
                    }
                }
            });
        });

        table.on('toolbar(record-table)', function (obj) {
            var checkStatus = table.checkStatus(obj.config.id);
            switch (obj.event) {
                case 'add':
                    layer.msg('添加');
                    break;
                case 'delete':
                    layer.msg('删除');
                    break;
                case 'update':
                    layer.msg('编辑');
                    break;
            }
        });

        $('#filter').on('click', function () {
            table.reload('dataForm', {
                url: "/public/administrativeDiv/filter/?" + $('#filter-form').serialize()
                , page: {curr: 1}
                , method: "GET"
                , where: {}
            }, 'data');
        });

        var currentPicker = new cityPicker("#city-picker", {
            provincename: "province__code",
            cityname: "city__code",
            districtname: "area__code",
            level: 'districtId',// 级别
        });
        //currentPicker.setValue("北京市/北京市/东城区");
    });
    exports('administrative_div', {})
});