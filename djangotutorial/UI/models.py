from django.db import models
from django.contrib.auth.models import User
import uuid

class UploadedVideo(models.Model):
    """
    上传视频的模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    unique_filename = models.CharField(max_length=255, verbose_name='唯一文件名')
    file_path = models.CharField(max_length=500, verbose_name='文件路径')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    mime_type = models.CharField(max_length=100, verbose_name='MIME类型')
    
    # 视频元数据
    duration = models.FloatField(null=True, blank=True, verbose_name='视频时长(秒)')
    width = models.IntegerField(null=True, blank=True, verbose_name='视频宽度')
    height = models.IntegerField(null=True, blank=True, verbose_name='视频高度')
    frame_rate = models.FloatField(null=True, blank=True, verbose_name='帧率')
    
    # 处理状态
    PROCESSING_STATUS = [
        ('pending', '等待处理'),
        ('processing', '处理中'),
        ('completed', '处理完成'),
        ('failed', '处理失败'),
    ]
    processing_status = models.CharField(
        max_length=20, 
        choices=PROCESSING_STATUS, 
        default='pending',
        verbose_name='处理状态'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 可选：关联用户
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = '上传视频'
        verbose_name_plural = '上传视频'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_name} ({self.processing_status})"
    
    @property
    def file_size_mb(self):
        """返回文件大小（MB）"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def duration_formatted(self):
        """返回格式化的时长"""
        if self.duration:
            minutes = int(self.duration // 60)
            seconds = int(self.duration % 60)
            return f"{minutes}:{seconds:02d}"
        return "未知"

class ChatSession(models.Model):
    """
    聊天会话模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(UploadedVideo, on_delete=models.CASCADE, verbose_name='关联视频')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # 可选：关联用户
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session for {self.video.original_name}"

class ChatMessage(models.Model):
    """
    聊天消息模型
    """
    MESSAGE_TYPES = [
        ('user', '用户消息'),
        ('ai', 'AI回复'),
        ('system', '系统消息'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, verbose_name='所属会话')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # AI回复的额外信息
    processing_time = models.FloatField(null=True, blank=True, verbose_name='处理时间(秒)')
    model_version = models.CharField(max_length=100, null=True, blank=True, verbose_name='模型版本')
    
    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class VideoAnalysis(models.Model):
    """
    视频分析结果模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.OneToOneField(UploadedVideo, on_delete=models.CASCADE, verbose_name='关联视频')
    
    # 分析结果
    summary = models.TextField(null=True, blank=True, verbose_name='视频摘要')
    objects_detected = models.JSONField(null=True, blank=True, verbose_name='检测到的对象')
    scenes_detected = models.JSONField(null=True, blank=True, verbose_name='检测到的场景')
    text_detected = models.JSONField(null=True, blank=True, verbose_name='检测到的文本')
    audio_transcription = models.TextField(null=True, blank=True, verbose_name='音频转录')
    
    # 关键帧
    key_frames = models.JSONField(null=True, blank=True, verbose_name='关键帧信息')
    
    # 分析状态
    ANALYSIS_STATUS = [
        ('pending', '等待分析'),
        ('analyzing', '分析中'),
        ('completed', '分析完成'),
        ('failed', '分析失败'),
    ]
    analysis_status = models.CharField(
        max_length=20, 
        choices=ANALYSIS_STATUS, 
        default='pending',
        verbose_name='分析状态'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '视频分析'
        verbose_name_plural = '视频分析'
    
    def __str__(self):
        return f"Analysis for {self.video.original_name}"

# Create your models here.
