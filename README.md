# Video2OldFilm
Python+PyQt6 实现微信视频迭代压缩模拟工具，复刻多次互传后的「清朝老片」质感，支持自定义迭代次数，可视化UI操作。

## 功能介绍
- 精准复刻微信视频压缩逻辑：分辨率阶梯降级+码率压低+帧率下降+色彩偏色
- 精准复刻微信音频压缩逻辑：立体声→单声道+高频截断+底噪累积
- 多轮迭代压缩：模拟多次互传的累积损失，迭代次数越多，老片质感越强
- 可视化UI：支持视频预览、进度监控、日志输出，无需命令行操作

## 环境要求
- Python 3.8+
- Windows系统（已适配ffmpeg一键安装）
- 依赖库：见requirements.txt

## 快速使用
1.  克隆项目到本地：`git clone https://github.com/chatsyx/Video2OldFilm.git`
2.  进入项目目录：`cd Video2OldFilm`
3.  安装依赖：`pip install -r requirements.txt`
4.  启动程序：`python main.py`
5.  操作流程：导入mp4视频 → 选择迭代次数 → 选择导出路径 → 点击开始压缩

## 核心参数说明
- 轻度老片：5次迭代（分辨率降至480P，帧率24fps）
- 中度老片：10次迭代（分辨率降至360P，帧率18fps，接近微信互传10次效果）
- 重度老片：20次迭代（分辨率降至240P，帧率18fps，完全复刻清朝老片质感）

## 项目结构
Video2OldFilm/
├── main.py # 项目入口
├── core/ # 核心压缩引擎
│ ├── video_compress.py # 视频压缩逻辑
│ ├── audio_compress.py # 音频压缩逻辑
│ └── iter_control.py # 迭代控制逻辑
├── ui/ # PyQt6 UI 界面
│ ├── main_window.py # 主界面布局
│ └── resource.py # 界面资源
├── temp/ # 临时文件目录（自动创建）
├── requirements.txt # 依赖清单
├── README.md # 使用说明
└── LICENSE # MIT 开源协议
plaintext

## 开源协议
本项目采用MIT协议，可自由使用、修改、分发。