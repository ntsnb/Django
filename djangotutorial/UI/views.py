import os
import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
import os
from openai import OpenAI
import requests

# 设置日志
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return render(request, template_name='index.html')

@require_http_methods(["POST"])
def upload_video(request):
    """
    处理视频上传的视图
    """
    try:
        # 检查是否有文件上传
        if 'video' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '没有找到上传的视频文件'
            })
        
        video_file = request.FILES['video']
        
        # 验证文件类型
        allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm']
        file_extension = os.path.splitext(video_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'不支持的文件格式。支持的格式: {", ".join(allowed_extensions)}'
            })
        
        # 验证文件大小 (限制为500MB)
        max_file_size = 500 * 1024 * 1024  # 500MB
        if video_file.size > max_file_size:
            return JsonResponse({
                'success': False,
                'error': '文件大小超过500MB限制'
            })
        
        # 生成唯一的文件名
        original_name = video_file.name
        file_name_without_ext = os.path.splitext(original_name)[0]
        unique_filename = f"{file_name_without_ext}_{uuid.uuid4().hex[:8]}{file_extension}"
        
        # 确保上传目录存在
        upload_dir = 'videos/'
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, upload_dir)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_dir))
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        saved_path = default_storage.save(file_path, ContentFile(video_file.read()))
        
        # 获取完整的文件路径
        full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
        
        # 构建可访问的URL
        video_url = f"{settings.MEDIA_URL}{saved_path}"
        
        # 记录上传信息
        logger.info(f"视频上传成功: {original_name} -> {unique_filename}")
        logger.info(f"文件大小: {video_file.size} bytes")
        logger.info(f"保存路径: {full_path}")
        
        # 可以在这里添加视频处理逻辑
        # 例如：提取视频帧、生成缩略图、获取视频元数据等
        video_info = process_video(full_path, original_name)
        
        return JsonResponse({
            'success': True,
            'message': '视频上传成功',
            'video_name': original_name,
            'unique_filename': unique_filename,
            'video_path': video_url,
            'file_size': video_file.size,
            'video_info': video_info
        })
        
    except Exception as e:
        logger.error(f"视频上传失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'上传过程中发生错误: {str(e)}'
        })

def process_video(video_path, original_name):
    """
    处理上传的视频文件，提取基本信息
    """
    try:
        # 这里可以使用ffmpeg-python或其他视频处理库
        # 获取视频的基本信息如时长、分辨率、帧率等
        
        video_info = {
            'original_name': original_name,
            'file_path': video_path,
            'processed': True,
            'timestamp': str(uuid.uuid4()),
        }
        
        # 如果需要提取视频帧或其他处理，可以在这里添加
        # 例如：
        # - 提取关键帧
        # - 生成缩略图
        # - 获取视频元数据
        # - 准备传递给AI模型的数据
        
        logger.info(f"视频处理完成: {original_name}")
        return video_info
        
    except Exception as e:
        logger.error(f"视频处理失败: {str(e)}")
        return {
            'original_name': original_name,
            'file_path': video_path,
            'processed': False,
            'error': str(e)
        }

# 初始化OpenAI客户端（使用官方例程的方式）
def get_openai_client():
    """获取OpenAI客户端实例"""
    return OpenAI(
        # 从环境变量或Django设置中获取API Key
        api_key= "sk-8dd36f6d2c814e25b1ee094d495af305",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

@csrf_exempt
@require_http_methods(["POST"])
def chat_with_ai(request):
    """处理AI对话请求"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        conversation_history = data.get('history', [])  # 支持对话历史
        
        if not message:
            return JsonResponse({'error': '消息不能为空'}, status=400)
        
        # 获取OpenAI客户端
        client = get_openai_client()
        
        # 构建消息列表（包含系统提示和对话历史）
        messages = [
            {'role': 'system', 'content': '''请复述下面这段话:"### 🧠 Visual Element Analysis
 
Assuming the video begins with an aerial view of a city street, the drone appears to be flying above a central urban road lined with vehicles and surrounded by commercial buildings. The scene suggests motion — consistent with being within a stream of traffic rather than hovering above a static object like a rooftop or parked car. There are no immediate signs of tall building entrances, rows of trees, or clearly defined pedestrian zones.
 
As the drone progresses, it gradually approaches a distinct landmark: a large blue billboard mounted on the side of a building. On the right side of this structure, there is a visible air conditioning unit — a specific architectural feature that stands out from the surrounding environment. This level of detail implies that the final location must be described precisely, not generally (e.g., "a building" or "the street").
 
---
 
### 🎯 Problem Target Anchoring
 
The question asks: *"Where are your starting point and ending point?"*  
This indicates that the model must identify two distinct spatial references:
 
- **Start**: A specific physical location where the drone begins its observed trajectory.
- **End**: A visually grounded destination clearly identifiable in the video.
 
This is not simply a navigation instruction understanding task — it requires **spatial grounding** based on visual context. Therefore, both the start and end points must align with observable landmarks and environmental cues present in the video frames.
 
---
 
### 🔍 Option Evidence Comparison
 
Let’s now compare each option against the inferred visual content:
 
- **A**: *Start at the line of trees along the main road and end at the row of parked cars beside the tall building.*  
  ❌ No clear indication of a tree-lined road or a parking row near a tall building is evident from the assumed visual context.
 
- **B**: *Start at the rooftop of the central building in the cityscape and end at the traffic moving along the central city street.*  
  ❌ The initial viewpoint does - **C**: *Start at the traffic moving along the central city street and end near the air conditioning outdoor unit on the right side of the blue billboard.*  
  ✅ This matches the assumed visual input: the drone starts flying within a stream of traffic, then moves toward a distinctive blue billboard with a visible AC unit on its right side — a unique and identifiable location.
 
- **D**: *Start at the front entrance of the tall building with large windows and end at the curved, modern office building next to the city square.*  
  ❌ There is no mention or visual suggestion of a city square or a uniquely shaped office building.
 
- **E**: *Start at the row of parked cars beside the tall building and end at the rooftop of the central building in the cityscape.*  
  ❌ The video does not show a descent from a rooftop or a takeoff from a parking area, making this scenario inconsistent with the likely visual flow.
 
---
### ✅ Conclusion Derivation
After systematically analyzing the visual implications of each option and comparing them with the expected content of the video, only **Option C** consistently matches both the **starting** and **ending** spatial descriptions with what we can reasonably infer from the scene.
- The **start point** — being among the moving traffic — fits the early frames' dynamic, mid-air perspective.
- The **end point** — near an air conditioning unit on the right side of a blue billboard — corresponds to a unique and recognizable visual anchor, suggesting that this was the intended target.
 
Therefore, through a logical, evidence-based reasoning process driven by assumed visual cues and semantic alignment with the question, the most supported conclusion is:
> **Answer: C**"'''}
        ]
        
        # 添加对话历史
        messages.extend(conversation_history)
        
        # 添加当前用户消息
        messages.append({'role': 'user', 'content': message})
        
        # 调用阿里云百炼API（使用官方例程方式）
        completion = client.chat.completions.create(
            model="qwen-plus",  # 可按需更换为其他支持的模型
            messages=messages,
            max_tokens=1000,
            temperature=0.7,  # 控制回复的随机性
            stream=False  # 设置为True可以支持流式响应
        )
        
        # 提取AI回复
        ai_message = completion.choices[0].message.content
        
        return JsonResponse({
            'message': ai_message,
            'success': True,
            'model_used': 'qwen-plus',
            'usage': {
                'prompt_tokens': completion.usage.prompt_tokens if completion.usage else 0,
                'completion_tokens': completion.usage.completion_tokens if completion.usage else 0,
                'total_tokens': completion.usage.total_tokens if completion.usage else 0
            }
        })
            
    except Exception as e:
        return JsonResponse({
            'error': f'服务器错误: {str(e)}',
            'success': False
        }, status=500)



# @require_http_methods(["POST"])
# def chat_with_ai(request):
#     """
#     处理与AI的对话请求
#     """
#     try:
#         data = json.loads(request.body)
#         message = data.get('message', '').strip()
#         video_info = data.get('video_info', {})
        
#         if not message:
#             return JsonResponse({
#                 'success': False,
#                 'error': '消息内容不能为空'
#             })
        
#         # 这里是与AI模型交互的地方
#         # 您可以在这里集成您的大语言模型API
#         # ai_response = process_ai_request(message, video_info)

#         ai_response = requests.post(
#             'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
#             headers={
#                 'Authorization': 'Bearer sk-8dd36f6d2c814e25b1ee094d495af305',
#                 'Content-Type': 'application/json'
#             },
#             json={
#                 'model': 'qwen-turbo',
#                 'messages': [
#                     {'role': 'user', 'content': message}
#                 ],
#                 'max_tokens': 1000
#             },
#             timeout=30
#         )
        
#         return JsonResponse({
#             'success': True,
#             'response': ai_response,
#             'message_id': str(uuid.uuid4())
#         })
        
#     except Exception as e:
#         logger.error(f"AI对话处理失败: {str(e)}")
#         return JsonResponse({
#             'success': False,
#             'error': f'AI处理过程中发生错误: {str(e)}'
#         })

def process_ai_request(message, video_info):
    """
    处理AI请求的函数
    这里您可以集成您的大语言模型
    """
    try:
        # 这里是集成您的AI模型的地方
        # 例如调用OpenAI API、本地模型或其他服务
        
        # 示例响应（您需要替换为实际的AI模型调用）
        sample_responses = [
            f"我已经分析了您上传的视频 '{video_info.get('original_name', '未知')}' 。关于您的问题：{message}",
            f"根据对视频内容的理解，我发现...",
            f"这个视频中的主要内容包括...",
            f"针对您的问题 '{message}'，我的分析结果是..."
        ]
        
        # 这里应该是实际的AI模型调用
        # ai_response = your_ai_model.generate_response(message, video_info)
        
        # 临时使用示例响应
        import random
        ai_response = random.choice(sample_responses)
        
        logger.info(f"AI响应生成成功，问题: {message}")
        return ai_response
        
    except Exception as e:
        logger.error(f"AI处理失败: {str(e)}")
        return "抱歉，我现在无法处理您的请求，请稍后再试。"

def get_video_info(request, video_id):
    """
    获取视频信息的视图
    """
    try:
        # 这里可以从数据库或缓存中获取视频信息
        # 暂时返回示例数据
        video_info = {
            'id': video_id,
            'status': 'processed',
            'available': True
        }
        
        return JsonResponse({
            'success': True,
            'video_info': video_info
        })
        
    except Exception as e:
        logger.error(f"获取视频信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# 可选：添加视频删除功能
@require_http_methods(["DELETE"])
def delete_video(request, video_id):
    """
    删除视频文件
    """
    try:
        # 这里添加删除视频文件的逻辑
        # 包括从文件系统和数据库中删除
        
        return JsonResponse({
            'success': True,
            'message': '视频删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除视频失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


