# Generated by Django 2.0 on 2019-12-25 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpiderRunLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spider_name', models.CharField(max_length=255, verbose_name='爬虫名称')),
                ('status', models.BooleanField(default=False, verbose_name='运行状态')),
                ('unique_id', models.CharField(blank=True, max_length=100, verbose_name='标识id')),
                ('task_id', models.CharField(blank=True, max_length=100, verbose_name='任务id')),
                ('start_time', models.DateTimeField(auto_now=True, verbose_name='运行开始时间')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='运行结束时间')),
            ],
            options={
                'verbose_name': 'spider运行日志',
                'verbose_name_plural': 'spider运行日志',
                'db_table': 'log_spider',
                'ordering': ['-id'],
                'managed': True,
            },
        ),
    ]
