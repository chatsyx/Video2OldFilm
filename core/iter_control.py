import os
import shutil  # 替换 os.system(copy)，更安全处理带空格路径
from core.video_compress import video_compress, get_video_info
from core.audio_compress import audio_compress, merge_audio_video

def iter_compress(input_path, output_path, iter_times, progress_callback=None):
    """
    多轮迭代压缩（修复temp目录、特殊文件名、路径空格问题）
    iter_times: 迭代次数（转发次数），progress_callback: 进度回调函数
    """
    # 1. 提前创建temp目录（使用绝对路径，确保无歧义，优先创建）
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp")
    temp_dir = os.path.abspath(temp_dir)  # 规范化路径，消除../
    os.makedirs(temp_dir, exist_ok=True)  # 提前创建，避免后续文件写入失败
    
    # 2. 构建临时文件绝对路径（避免相对路径问题，处理特殊字符）
    temp_video = os.path.join(temp_dir, "temp_video.mp4")
    temp_audio = os.path.join(temp_dir, "temp_audio.mp3")
    
    # 3. 复制原文件到临时文件（用shutil.copy替换os.system，完美处理带空格/中文/特殊字符路径）
    try:
        shutil.copy(input_path, temp_video)
    except Exception as e:
        raise Exception(f"复制原视频到临时文件失败：{e}（请检查原视频是否被占用）")
    
    # 4. 获取初始视频信息
    curr_res, curr_fps = get_video_info(temp_video)
    
    # 5. 迭代压缩主逻辑（构建每轮临时文件绝对路径）
    for i in range(iter_times):
        # 构建本轮临时文件绝对路径，避免命名冲突
        curr_output = os.path.join(temp_dir, f"temp_{i}.mp4")
        
        # 视频单轮压缩
        curr_res, curr_fps = video_compress(temp_video, curr_output, curr_res, curr_fps)
        
        # 音频单轮压缩（传入绝对路径）
        audio_compress(curr_output, temp_audio)
        
        # 音视频合成（传入绝对路径）
        merge_audio_video(curr_output, temp_audio, temp_video)
        
        # 进度回调
        if progress_callback:
            progress_callback(i+1, iter_times, curr_res, curr_fps)
        
        # 删除本轮临时文件（容错处理，避免删除失败报错）
        if os.path.exists(curr_output):
            try:
                os.remove(curr_output)
            except Exception as e:
                print(f"清理本轮临时文件失败：{e}")
    
    # 6. 最终导出结果（用shutil.move替换os.rename，兼容不同磁盘路径）
    try:
        shutil.move(temp_video, output_path)
    except Exception as e:
        raise Exception(f"导出最终视频失败：{e}（请检查导出路径是否有权限）")
    
    # 7. 清理残留临时音频文件（容错处理）
    if os.path.exists(temp_audio):
        try:
            os.remove(temp_audio)
        except Exception as e:
            print(f"清理残留临时音频文件失败：{e}")
    
    return True