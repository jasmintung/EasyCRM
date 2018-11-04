from django.shortcuts import render, HttpResponse

# Create your views here.


def main_pg(request):
    print('student')
    return HttpResponse("student")
