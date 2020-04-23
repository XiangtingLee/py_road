from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from user.models import User


@login_required()
def main(request):
    data = {}
    user = User.objects.get(id=request.user.id)
    data["nick_name"] = user.nick_name
    data["face_img"] = user.face_img if user.face_img else "/media/face_img/default.png"
    return render(request, 'lib/main.html', data)


@login_required()
def index(request):
    return render(request, 'pyroad/index.html')
