from pydub import AudioSegment
import os

def audio_compress(input_video_path, output_audio_path):
    """单轮音频压缩：立体声→单声道+码率50kbps+高频截断+加底噪（修复带空格路径）"""
    try:
        # 1. 提取视频中的音频（传入绝对路径，兼容特殊文件名）
        audio = AudioSegment.from_file(input_video_path, format="mp4")
        
        # 2. 立体声转单声道
        audio = audio.set_channels(1)
        
        # 3. 码率压缩到50kbps
        audio = audio.set_frame_rate(22050).set_sample_width(1)
        
        # 4. 截断2000Hz以上高频（模拟沉闷音质）
        audio = audio.low_pass_filter(2000)
        
        # 5. 叠加轻微底噪（模拟多次压缩噪声累积）
        noise = AudioSegment.silent(duration=len(audio)).apply_gain(-40)
        audio = audio.overlay(noise)
        
        # 6. 导出压缩音频（传入绝对路径，覆盖已有文件）
        audio.export(output_audio_path, format="mp3", bitrate="50k", parameters=["-y"])
        
        return output_audio_path
    except Exception as e:
        raise Exception(f"音频压缩失败：{e}（请检查ffmpeg是否正常配置）")

def merge_audio_video(video_path, audio_path, output_path):
    """压缩后音视频重新合成（修复带空格路径，补充容错）"""
    try:
        # 1. 读取音视频文件（绝对路径）
        video = AudioSegment.from_file(video_path, format="mp4")
        audio = AudioSegment.from_file(audio_path, format="mp3")
        
        # 2. 音视频时长对齐
        final_audio = audio[:len(video)] if len(audio) > len(video) else audio
        final_video = video.overlay(final_audio)
        
        # 3. 导出合成视频（覆盖已有文件，兼容特殊路径）
        final_video.export(output_path, format="mp4", parameters=["-y"])
        
        # 4. 删除临时音频文件（容错处理）
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return output_path
    except Exception as e:
        raise Exception(f"音视频合成失败：{e}（请检查临时音频文件是否存在）")