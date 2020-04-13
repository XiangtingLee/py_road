from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from user.models import User


@login_required()
def main(request):
    data = {}
    user = User.objects.get(id=request.user.id)
    data["nick_name"] = user.nick_name
    return render(request, 'lib/main.html', data)


@login_required()
def index(request):
    return render(request, 'pyroad/index.html')
