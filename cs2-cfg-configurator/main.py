# main.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # App-Icon setzen (assets/icon.png)
    icon_path = Path(__file__).parent / "app" / "assets" / "icon.png"
    if not icon_path.exists():
        # Fallback: icon.png im Repo-Root
        icon_path = Path(__file__).parent.parent / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
