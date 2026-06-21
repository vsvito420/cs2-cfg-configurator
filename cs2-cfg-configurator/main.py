# main.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # App-Icon: Titelleiste UND Taskleiste
    icon_path = Path(__file__).parent / "app" / "assets" / "icon.png"
    if not icon_path.exists():
        icon_path = Path(__file__).parent.parent / "icon.png"
    if icon_path.exists():
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)   # Taskleiste (alle Fenster)

    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))  # explizit auch am Fenster
    window.show()
    sys.exit(app.exec())
