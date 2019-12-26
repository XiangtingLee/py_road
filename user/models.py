import time

from django.db import models
from django.contrib.auth.models import AbstractUser

def get_nick_name():
    return "User-%s" % int(time.time()) * 100

# class User(AbstractUser):
#     mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="手机号码")
#     nick_name = models.CharField(max_length=20, default=get_nick_name(), verbose_name="昵称")
#     real_name = models.CharField(null=True, blank=True, max_length=50, verbose_name="真实姓名")
#     portrait = models.ImageField(verbose_name="头像")
