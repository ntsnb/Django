from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def index_2(request):
    return render(request, template_name="index.html")

def info(request):
    username = 'nts'
    book = {"name":"水浒", "author":"施耐庵"}
    books = [
        {"name":"水浒", "author":"施耐庵"},
        {"name":"三国", "author":"罗贯中"}
    ]
    class book1:
        def __init__(self, book):
            self.bookname = book
    return render(request,template_name="info.html", context={"username": username, 
                                                              "book": book,
                                                              "books": books,
                                                              "book1": book1("红楼")                                                              
                                                              })

def if_view(request):
    author = "施耐庵"
    return render(request,template_name="if.html",context={"author":author})

def url_views(request):
    return render(request, template_name="url.html")