from django.urls import path
from . import views

app_name = 'UI'

urlpatterns = [
    # 主页
    path('', views.index, name='index'),
    
    # 视频上传
    path('upload_video/', views.upload_video, name='upload_video'),
    
    # AI对话
    # path('chat/', views.chat_with_ai, name='chat_with_ai'),

    path('api/chat/', views.chat_with_ai, name='chat_with_ai'),
    
    # 获取视频信息
    path('video/<str:video_id>/', views.get_video_info, name='video_info'),
    
    # 删除视频（可选）
    path('video/<str:video_id>/delete/', views.delete_video, name='delete_video'),
]