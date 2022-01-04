from django.shortcuts import render


def index(request):
    return render(request, 'chat/index.html')


def room(request, pk):
    return render(request, 'chat/room.html', {'room_pk': pk})
