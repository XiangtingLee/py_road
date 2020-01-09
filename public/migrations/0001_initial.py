# Generated by Django 2.0 on 2020-01-08 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrativeDiv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(verbose_name='地区编码')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='地区名称')),
                ('pinyin', models.CharField(blank=True, max_length=100, null=True, verbose_name='拼音名')),
                ('short_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='简称')),
                ('zip_code', models.IntegerField(blank=True, null=True, verbose_name='邮政编码')),
                ('lng_lat', models.CharField(blank=True, max_length=100, null=True, verbose_name='经纬度')),
                ('add_time', models.DateTimeField(verbose_name='添加时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='level3', to='public.AdministrativeDiv', verbose_name='区')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='level2', to='public.AdministrativeDiv', verbose_name='市')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='level1', to='public.AdministrativeDiv', verbose_name='省')),
            ],
            options={
                'verbose_name': '全国行政区划',
                'verbose_name_plural': '全国行政区划',
                'db_table': 'public_administrative_div',
                'ordering': ['-id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CityBusinessZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='商圈名称')),
                ('add_time', models.DateTimeField(verbose_name='添加时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_level3', to='public.AdministrativeDiv')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_level2', to='public.AdministrativeDiv')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_level1', to='public.AdministrativeDiv')),
            ],
            options={
                'verbose_name': '全国城市商圈',
                'verbose_name_plural': '全国城市商圈',
                'db_table': 'public_city_business_zone',
                'ordering': ['-id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ProxyPool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol', models.CharField(max_length=6, verbose_name='代理协议')),
                ('address', models.CharField(max_length=15, verbose_name='代理地址')),
                ('port', models.CharField(max_length=10, verbose_name='代理端口号')),
                ('type', models.CharField(max_length=255, verbose_name='代理类型')),
                ('add_time', models.DateTimeField(verbose_name='添加时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_available', models.BooleanField(default=False, verbose_name='是否可用')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
            ],
            options={
                'verbose_name': '代理池',
                'verbose_name_plural': '代理池',
                'db_table': 'public_proxy_pool',
                'ordering': ['-id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Spider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='爬虫名称')),
                ('path', models.CharField(max_length=255, verbose_name='爬虫路径')),
                ('add_time', models.DateTimeField(verbose_name='添加时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_available', models.BooleanField(default=False, verbose_name='是否可用')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('remark', models.TextField(verbose_name='备注')),
            ],
            options={
                'verbose_name': '已有爬虫',
                'verbose_name_plural': '已有爬虫',
                'db_table': 'public_spider',
                'ordering': ['-id'],
                'managed': True,
            },
        ),
    ]
