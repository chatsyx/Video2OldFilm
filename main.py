import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import Video2OldFilmWindow
from ui.resource import get_style

# 添加项目根目录到环境变量（解决模块导入问题）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Video2OldFilmWindow()
    window.setStyleSheet(get_style())  # 应用样式表
    window.show()
    sys.exit(app.exec())