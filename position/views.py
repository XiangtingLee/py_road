from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse


from .models import *


def visualization_view(requests):
    return render(requests, 'position/visualization.html', locals())

def tag_analysis(requests):
    '''
    标签词云数据
    '''
    all = PositionLabels.objects.get(id=1)
    print(all)
    return JsonResponse({})