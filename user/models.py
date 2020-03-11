import time

from django.db import models
from django.contrib.auth.models import AbstractUser


def get_nick_name():
    return "User%s" % int(time.time()*1000)


class Menu(models.Model):
    caption = models.CharField(max_length=32, verbose_name="菜单")

    class Meta:
        verbose_name = "菜单表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.caption


class Group(models.Model):
    title = models.CharField(max_length=32, verbose_name="组名称")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name="组内菜单", blank=True)  # 一个组下有多个菜单

    class Meta:
        verbose_name = "权限组"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Permission(models.Model):
    title = models.CharField(max_length=32, verbose_name="权限名")
    url = models.CharField(max_length=32, verbose_name="带正则的url")
    codes = models.CharField(max_length=32, verbose_name="代码")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="所属组", blank=True)  # 组和权限是一对多的关系，一个组有多个权限
    menu_gp = models.ForeignKey('self', on_delete=models.CASCADE, related_name='aaa', null=True, blank=True,
                                verbose_name="组内菜单")

    class Meta:
        verbose_name = "权限表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Role(models.Model):
    title = models.CharField(max_length=32, verbose_name="角色")
    permissions = models.ManyToManyField(Permission, verbose_name="拥有权限的角色", blank=True)  # 权限和角色是多对多的关系

    class Meta:
        verbose_name = '角色表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class User(AbstractUser):
    nick_name = models.CharField(null=True, blank=True, max_length=20, verbose_name="真实姓名", default=get_nick_name())
    face_img = models.ImageField(upload_to="face_img/", verbose_name="头像")
    qq = models.CharField(null=True, blank=True, max_length=11, verbose_name="qq号码")
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="手机号码")
    real_name = models.CharField(null=True, blank=True, max_length=50, verbose_name="真实姓名")
    sex = models.IntegerField(default=2, choices=((0, "女"), (1, "男"), (2, "保密")), verbose_name="性别")
    birthday = models.DateField(null=True, blank=True, verbose_name="生日")
    id_card = models.CharField(null=True, blank=True, max_length=18, verbose_name='身份证号')
    last_login_ip = models.CharField(null=True, blank=True, max_length=255, verbose_name="最后登录IP")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户权限")

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.username
