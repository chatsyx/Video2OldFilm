import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
                             QFileDialog, QProgressBar, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import cv2
from core.iter_control import iter_compress

# 压缩线程（独立线程防UI卡顿，信号通信传状态）
class CompressThread(QThread):
    progress_signal = pyqtSignal(int, int, tuple, int)
    finish_signal = pyqtSignal(bool, str)

    def __init__(self, input_path, output_path, iter_times):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.iter_times = iter_times

    def run(self):
        try:
            def progress_cb(curr_iter, total_iter, res, fps):
                self.progress_signal.emit(curr_iter, total_iter, res, fps)
            iter_compress(self.input_path, self.output_path, self.iter_times, progress_cb)
            self.finish_signal.emit(True, f"压缩完成！保存路径：{self.output_path}")
        except Exception as e:
            self.finish_signal.emit(False, f"压缩失败：{str(e)}")

# 主界面窗口（全功能适配，PyQt6 API无兼容问题）
class Video2OldFilmWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video2OldFilm - 微信视频迭代压缩模拟工具")
        self.setFixedSize(900, 600)
        self.input_path = ""
        self.output_path = ""
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        total_layout = QVBoxLayout(central_widget)

        # 1. 菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("导入视频", self.import_video)
        file_menu.addAction("导出结果", self.export_video)
        setting_menu = menubar.addMenu("设置")
        setting_menu.addAction("重置参数", self.reset_params)
        help_menu = menubar.addMenu("帮助")
        help_menu.addAction("使用说明", self.show_help)

        # 2. 预览区（左右分栏）
        preview_layout = QHBoxLayout()
        self.origin_label = QLabel("原视频预览")
        self.origin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.origin_label.setStyleSheet("border:1px solid #ccc;")
        self.result_label = QLabel("压缩后预览")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("border:1px solid #ccc;")
        preview_splitter = QSplitter(Qt.Orientation.Horizontal)
        preview_splitter.addWidget(self.origin_label)
        preview_splitter.addWidget(self.result_label)
        preview_layout.addWidget(preview_splitter)
        total_layout.addLayout(preview_layout)

        # 3. 参数设置区
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("迭代次数（转发次数）："))
        self.iter_input = QLineEdit("10")
        self.iter_input.setFixedWidth(50)
        param_layout.addWidget(self.iter_input)
        param_layout.addWidget(QLabel("老片质感："))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["轻度(5次)", "中度(10次)", "重度(20次)"])
        self.quality_combo.currentTextChanged.connect(self.quality_change)
        param_layout.addStretch()
        total_layout.addLayout(param_layout)

        # 4. 操作控制区
        ctrl_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始压缩")
        self.start_btn.clicked.connect(self.start_compress)
        self.pause_btn = QPushButton("暂停压缩")
        self.stop_btn = QPushButton("停止压缩")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        ctrl_layout.addWidget(self.start_btn)
        ctrl_layout.addWidget(self.pause_btn)
        ctrl_layout.addWidget(self.stop_btn)
        ctrl_layout.addWidget(self.progress_bar)
        total_layout.addLayout(ctrl_layout)

        # 5. 日志输出区
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        total_layout.addWidget(self.log_edit)

    # 导入视频
    def import_video(self):
        path, _ = QFileDialog.getOpenFileName(parent=self, caption="选择要压缩的视频", filter="视频文件 (*.mp4)")
        if path:
            self.input_path = path
            self.log_edit.append(f"✅ 已导入视频：{os.path.basename(path)}")
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.origin_label.setPixmap(QPixmap.fromImage(q_img).scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio))
            cap.release()

    # 导出视频（PyQt6 完全兼容，无关键字报错）
    def export_video(self):
        if not self.input_path:
            self.log_edit.append("❌ 请先导入视频！")
            return
        origin_file = os.path.basename(self.input_path)
        origin_name = os.path.splitext(origin_file)[0]
        default_name = f"{origin_name}_老片.mp4"
        path, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="选择视频保存路径",
            directory=default_name,
            filter="视频文件 (*.mp4)"
        )
        if path:
            self.output_path = path
            self.log_edit.append(f"📌 导出路径已选：{os.path.basename(path)}")

    # 质感档位联动迭代次数
    def quality_change(self, text):
        iter_map = {"轻度(5次)":5, "中度(10次)":10, "重度(20次)":20}
        self.iter_input.setText(str(iter_map[text]))

    # 启动压缩
    def start_compress(self):
        if not self.input_path or not self.output_path:
            self.log_edit.append("❌ 请先导入视频并选择导出路径！")
            return
        try:
            iter_times = int(self.iter_input.text())
            if iter_times < 1 or iter_times > 50:
                self.log_edit.append("❌ 迭代次数请设置1-50之间！")
                return
        except ValueError:
            self.log_edit.append("❌ 迭代次数请输入数字！")
            return
        
        self.compress_thread = CompressThread(self.input_path, self.output_path, iter_times)
        self.compress_thread.progress_signal.connect(self.update_progress)
        self.compress_thread.finish_signal.connect(self.complete_compress)
        self.compress_thread.start()
        self.log_edit.append(f"▶️ 开始压缩，共{iter_times}轮迭代")

    # 更新压缩进度
    def update_progress(self, curr_iter, total_iter, res, fps):
        progress = int((curr_iter/total_iter)*100)
        self.progress_bar.setValue(progress)
        self.log_edit.append(f"🔄 第{curr_iter}轮压缩完成 | 分辨率：{res[0]}x{res[1]} | 帧率：{fps}fps")

    # 压缩完成回调
    def complete_compress(self, status, msg):
        self.log_edit.append(msg)
        self.progress_bar.setValue(100 if status else 0)
        if status and os.path.exists(self.output_path):
            cap = cv2.VideoCapture(self.output_path)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.result_label.setPixmap(QPixmap.fromImage(q_img).scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio))
            cap.release()

    # 重置参数
    def reset_params(self):
        self.iter_input.setText("10")
        self.quality_combo.setCurrentIndex(1)
        self.progress_bar.setValue(0)
        self.log_edit.append("🔧 参数已重置为默认值（中度老片，10次迭代）")

    # 使用说明
    def show_help(self):
        help_info = """
使用说明：
1.  【文件-导入视频】：仅支持mp4格式视频
2.  【文件-导出结果】：选定保存位置，默认带老片后缀
3.  质感档位：轻度5次/中度10次/重度20次，也可手动改次数
4.  点击开始压缩，日志会实时显示每轮进度
提示：次数越多老片感越强，大视频压缩耗时会久一点
        """
        self.log_edit.append(help_info)

# 测试入口（导入齐全，无未定义报错）
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Video2OldFilmWindow()
    window.show()
    sys.exit(app.exec())