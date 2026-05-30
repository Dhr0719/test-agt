from django.shortcuts import render

from django.http import JsonResponse

def hello(request):
    return JsonResponse({
        "msg": "我是 Django 后端，Vue 你好！",
        "code": 200
    })