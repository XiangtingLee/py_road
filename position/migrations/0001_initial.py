# Generated by Django 2.0 on 2019-12-25 22:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('public', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='公司id')),
                ('tyc_id', models.CharField(blank=True, max_length=20, null=True, verbose_name='天眼查id')),
                ('name', models.CharField(max_length=100, verbose_name='公司名称')),
                ('short_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='公司简称')),
                ('introduce', models.CharField(blank=True, max_length=255, null=True, verbose_name='公司介绍')),
                ('certification', models.BooleanField(default=True, verbose_name='公司认证')),
                ('url', models.CharField(blank=True, max_length=255, null=True, verbose_name='公司官网')),
                ('logo', models.CharField(blank=True, max_length=255, null=True, verbose_name='公司logo')),
                ('business_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='工商-公司名称')),
                ('business_credit_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='工商-公司信用代码')),
                ('business_establish_time', models.DateField(blank=True, null=True, verbose_name='工商-成立时间')),
                ('business_reg_capital', models.CharField(blank=True, max_length=20, null=True, verbose_name='工商-注册资本')),
                ('business_reg_location', models.CharField(blank=True, max_length=255, null=True, verbose_name='工商-注册地点')),
                ('business_legal_person_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='工商-法人姓名')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
                ('warehouse_time', models.DateTimeField(verbose_name='入库时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '招聘公司',
                'verbose_name_plural': '招聘公司',
                'db_table': 'position_company',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CompanyFinancing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='阶段名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '公司融资阶段',
                'verbose_name_plural': '公司融资阶段',
                'db_table': 'position_company_financing',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CompanyIndustries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='行业名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '公司所属行业',
                'verbose_name_plural': '公司所属行业',
                'db_table': 'position_company_industries',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CompanyLabels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='标签名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '公司标签',
                'verbose_name_plural': '公司标签',
                'db_table': 'position_company_labels',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CompanyRegStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='状态名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '公司经营状态',
                'verbose_name_plural': '公司经营状态',
                'db_table': 'position_company_reg_status',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CompanyScale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='规模名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '公司规模',
                'verbose_name_plural': '公司规模',
                'db_table': 'position_company_size',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='职位id')),
                ('position_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='职位名称')),
                ('salary_lower', models.IntegerField(verbose_name='薪水下限')),
                ('salary_upper', models.IntegerField(verbose_name='薪水上限')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
                ('warehouse_time', models.DateTimeField(verbose_name='入库时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='position.Company', verbose_name='公司id')),
            ],
            options={
                'verbose_name': '招聘职位',
                'verbose_name_plural': '招聘职位',
                'db_table': 'position_position',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PositionEducation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='学历要求')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '学历要求',
                'verbose_name_plural': '学历要求',
                'db_table': 'position_position_education',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PositionExperience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='经验要求')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '经验要求',
                'verbose_name_plural': '经验要求',
                'db_table': 'position_position_experience',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PositionLabels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='标签名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '职位标签',
                'verbose_name_plural': '职位标签',
                'db_table': 'position_position_labels',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PositionNature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='类型名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '职位性质',
                'verbose_name_plural': '职位性质',
                'db_table': 'position_position_nature',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PositionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='类型名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '职位类型',
                'verbose_name_plural': '职位类型',
                'db_table': 'position_position_type',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PositionWelfares',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='福利名称')),
                ('add_time', models.DateTimeField(verbose_name='新增时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_effective', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '职位福利',
                'verbose_name_plural': '职位福利',
                'db_table': 'position_position_welfares',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='position',
            name='education',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='position.PositionEducation', verbose_name='学历要求'),
        ),
        migrations.AddField(
            model_name='position',
            name='experience',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='position.PositionExperience', verbose_name='工作经验'),
        ),
        migrations.AddField(
            model_name='position',
            name='label',
            field=models.ManyToManyField(to='position.PositionLabels', verbose_name='职位标签'),
        ),
        migrations.AddField(
            model_name='position',
            name='position_business_zones',
            field=models.ManyToManyField(to='public.CityBusinessZone', verbose_name='工作所在商圈'),
        ),
        migrations.AddField(
            model_name='position',
            name='position_city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='position_level1', to='public.AdministrativeDiv', verbose_name='工作所在城市'),
        ),
        migrations.AddField(
            model_name='position',
            name='position_district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='position_level2', to='public.AdministrativeDiv', verbose_name='工作所在区域'),
        ),
        migrations.AddField(
            model_name='position',
            name='position_nature',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='position.PositionNature', verbose_name='职位性质'),
        ),
        migrations.AddField(
            model_name='position',
            name='position_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='position.PositionType', verbose_name='职位类型'),
        ),
        migrations.AddField(
            model_name='position',
            name='welfare',
            field=models.ManyToManyField(to='position.PositionWelfares', verbose_name='福利待遇'),
        ),
        migrations.AddField(
            model_name='company',
            name='business_reg_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='position.CompanyRegStatus', verbose_name='工商-经营状态'),
        ),
        migrations.AddField(
            model_name='company',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='public.AdministrativeDiv', verbose_name='所在地区'),
        ),
        migrations.AddField(
            model_name='company',
            name='financing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='position.CompanyFinancing', verbose_name='融资阶段'),
        ),
        migrations.AddField(
            model_name='company',
            name='industry',
            field=models.ManyToManyField(to='position.CompanyIndustries', verbose_name='公司所属行业'),
        ),
        migrations.AddField(
            model_name='company',
            name='label',
            field=models.ManyToManyField(to='position.CompanyLabels', verbose_name='公司标签'),
        ),
        migrations.AddField(
            model_name='company',
            name='scale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='position.CompanyScale', verbose_name='公司规模'),
        ),
    ]
