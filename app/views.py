from django.shortcuts import render
from . import models

# Create your views here.
def index(request, group_name):
    group = models.Group.objects.filter(name=group_name).first()
    chats = []
    if not group:
        group = models.Group(name=group_name.lower())
        group.save()
    else:
        chats = models.Chat.objects.filter(group=group)
    return render(request, 'app/index.html', {'groupname': group_name, 'chats' : chats})