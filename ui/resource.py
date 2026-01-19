# 资源文件：后续可添加界面图标、样式表等资源
# 修复函数导出问题，确保能被main.py正常导入

def get_style():
    """界面样式表（美化界面用，返回完整CSS样式字符串）"""
    return """
    QPushButton{background-color:#4CAF50;color:white;border:none;padding:5px 10px;border-radius:3px;}
    QPushButton:hover{background-color:#45a049;}
    QProgressBar{border:1px solid #ccc;border-radius:3px;text-align:center;}
    QProgressBar::chunk{background-color:#4CAF50;}
    QTextEdit{border:1px solid #ccc;border-radius:3px;}
    QLabel{font-size:14px;}
    QLineEdit{border:1px solid #ccc;border-radius:3px;padding:3px;}
    QComboBox{border:1px solid #ccc;border-radius:3px;padding:3px;}
    """