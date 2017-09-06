from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    context = {'boldmessage': 'Rango is going on!'}
    return render(request, 'rango/index.html', context=context)


def about(request):
    context = {'creator': 'wangfp'}
    return render(request, 'rango/about.html', context=context)