from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Rango is going on!<br/>"
                        "<a href='/rango/about'>About</a>")


def about(request):
    return HttpResponse("Rango's about page<br/>"
                        "<a href='/rango'>Index</a>")