from django.urls import path

from . import views

urlpatterns = [
    path("nts/", views.index_2, name="nts/"),
    path("", views.index, name="index"),
    path('info/', views.info, name="info"),
    path('if', views.if_view, name='if'),
    path('url', views.url_views, name="url")
]