import cv2
import ffmpeg
import os
import sys

def video_compress(input_path, output_path, curr_res, curr_fps):
    """
    单轮视频压缩：移除无效colorspace参数+兼容编码+中文路径支持
    curr_res: 当前分辨率（tuple），curr_fps: 当前帧率
    """
    # 1. 前置检查（验证输入文件是否存在，避免无意义调用）
    if not os.path.exists(input_path):
        raise Exception(f"输入视频文件不存在：{input_path}")
    
    # 2. 分辨率降级（按微信规则阶梯下降，兼容边界值）
    res_map = [(1920, 1080), (1280, 720), (854, 480), (640, 360), (426, 240)]
    curr_idx = res_map.index(curr_res) if curr_res in res_map else 0
    next_idx = curr_idx + 1 if curr_idx + 1 < len(res_map) else len(res_map) - 1
    target_res = res_map[next_idx]

    # 3. 帧率降级（60→30→24→18，兼容边界值）
    fps_map = [60, 30, 24, 18]
    curr_fps_idx = fps_map.index(curr_fps) if curr_fps in fps_map else 0
    next_fps_idx = curr_fps_idx + 1 if curr_fps_idx + 1 < len(fps_map) else len(fps_map) - 1
    target_fps = fps_map[next_fps_idx]

    # 4. ffmpeg 核心压缩（移除无效colorspace参数+兼容编码+详细报错）
    try:
        # 兼容 Windows 中文路径：强制使用绝对路径
        input_path_abs = os.path.abspath(input_path)
        output_path_abs = os.path.abspath(output_path)
        
        # 移除无效的colorspace='srgb'，替换为兼容的色彩参数模拟偏色
        # 保留核心压缩逻辑：libx264编码+1.5Mbps码率+分辨率+帧率+色彩深度
        (
            ffmpeg
            .input(input_path_abs)
            .output(
                output_path_abs,
                vcodec='libx264',
                crf=28,  # 控制码率≈1.5Mbps，模拟微信压缩的低码率
                s=f"{target_res[0]}x{target_res[1]}",  # 分辨率降级
                r=target_fps,  # 帧率降级
                pix_fmt='yuv420p',  # 降低色彩深度，模拟偏色（替代srgb，兼容所有环境）
                preset='ultrafast',  # 快速编码，提升压缩速度
                acodec='aac',  # 音频编码兼容，避免音视频不同步
                y=None  # 自动覆盖已有文件，无需手动确认
            )
            .overwrite_output()
            .run(quiet=False)  # 关闭安静模式，方便排查剩余问题
        )
        
        # 验证输出文件是否生成
        if not os.path.exists(output_path_abs):
            raise Exception(f"ffmpeg 未生成压缩视频文件，编码流程异常")
        
        return target_res, target_fps
    except Exception as e:
        error_msg = f"视频压缩报错：{str(e)}"
        # 补充 ffmpeg 环境提示
        if "No such file or directory" in str(e):
            error_msg += "（大概率是ffmpeg未安装或环境变量未配置生效）"
        raise Exception(error_msg)

def get_video_info(video_path):
    """获取视频基础信息：分辨率、帧率（修复中文路径兼容）"""
    if not os.path.exists(video_path):
        raise Exception(f"视频文件不存在：{video_path}")
    
    # 兼容 OpenCV 中文路径（Windows 下需转码）
    width, height, fps = 0, 0, 0
    if sys.platform == "win32":
        # 优先使用 ffmpeg.probe 获取信息，避免 OpenCV 中文路径问题
        try:
            probe = ffmpeg.probe(os.path.abspath(video_path))
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream:
                width = int(video_stream['width'])
                height = int(video_stream['height'])
                fps = eval(video_stream['r_frame_rate'])
                fps = int(round(fps))
            else:
                raise Exception("未提取到视频流信息")
        except Exception as e:
            raise Exception(f"获取视频信息失败（中文路径兼容问题）：{e}")
    else:
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()

    # 标准化分辨率和帧率到预设档位（适配微信压缩规则）
    res_map = [(1920, 1080), (1280, 720), (854, 480), (640, 360), (426, 240)]
    closest_res = min(res_map, key=lambda x: abs(x[0] - width) + abs(x[1] - height))
    fps_map = [60, 30, 24, 18]
    closest_fps = min(fps_map, key=lambda x: abs(x - fps))
    
    return closest_res, closest_fps