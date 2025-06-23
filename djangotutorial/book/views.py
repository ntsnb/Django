from django.shortcuts import render, HttpResponse
from django.db import connection

def index(request):
    cursor = connection.cursor()
    cursor.execute("select * from book")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
# Create your views here.
    return HttpResponse("查找成功")