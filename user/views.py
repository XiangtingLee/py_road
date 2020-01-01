from django.shortcuts import render

# Create your views here.
def info_view(request):
    data = {}
    data["user"] = request.user
    return render(request, 'user/info.html', data)