from django.shortcuts import render

from django.http import JsonResponse

def test_api(request):
    return JsonResponse({
        "code": 0,
        "msg": "后端连接成功"
    })