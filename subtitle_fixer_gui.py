"""Sub Fixer GUI - solid custom titlebar + winotch-style dark glass body.

The window is frameless with per-pixel alpha (WA_TranslucentBackground).
The visual language is borrowed from yappologistic/winotch, whose entire
"liquid glass" look is pure painting on a transparent window - no acrylic,
no DWM backdrop, no blur of the desktop:
  * near-black shell (#050505) with large rounded corners,
  * hairline stroke + specular gloss for the glassy read.
Here the body keeps a hint of see-through (GLASS_ALPHA) so the desktop
shows through as a dark haze; the titlebar stays fully opaque.
The drop zone keeps its 3px dashed red border, bold Segoe print and same
texts - in white, because black text is unreadable on the dark shell.
DWM is used for cosmetics only (dark tint, rounded-corner preference,
no 1px window border).
"""

import ctypes
from os import getenv

from PyQt5.QtCore import QPoint, QRectF, Qt
from PyQt5.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from subtitle_processor import main

BAR_HEIGHT = 36
RADIUS = 18  # winotch-style generous corner rounding

# winotch palette (App.xaml: NotchBlack #050505) with a translucent take
SHELL_RGB = (5, 5, 5)
GLASS_ALPHA = 205  # 255 = fully opaque like winotch; lower = more see-through
HAIRLINE_ALPHA = 18  # 1px stroke around the shell

# DWM cosmetics (values are stable across Win10/11)
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_BORDER_COLOR = 34
DWMWA_COLOR_NONE = 0xFFFFFFFE


def _apply_dwm_cosmetics(hwnd: int) -> None:
    dwm = ctypes.windll.dwmapi
    dark = ctypes.c_int(1)
    dwm.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(dark), ctypes.sizeof(dark))
    # NOTE: no DWMWA_WINDOW_CORNER_PREFERENCE here on purpose. DWM rounds the
    # window at ~8px, which leaves the sliver between DWM's arc and our 18px
    # painted arc visible-but-unpainted, and that sliver composites as WHITE.
    # Our painted rounded corners are the only rounding.
    border = ctypes.c_uint(DWMWA_COLOR_NONE)
    dwm.DwmSetWindowAttribute(hwnd, DWMWA_BORDER_COLOR, ctypes.byref(border), ctypes.sizeof(border))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(r"assets\comics-mask_97446.ico"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Sub Fixer")  # targetable even though the titlebar is custom
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(400, 110)
        self.resize(430, 118)  # original ~400x110 proportions
        self._dragging = False

        # dashed border inset from the shell edge: left/right = 7+5 (stylesheet
        # margin) = 12, bottom = 12, and spacing puts the top gap at 12 too
        layout = QVBoxLayout()
        layout.setContentsMargins(7, 0, 7, 12)
        layout.setSpacing(12)
        self.bar = MyBar(self)
        self.bar.setFixedHeight(BAR_HEIGHT)
        layout.addWidget(self.bar)
        layout.addWidget(NewLabel(self), 1)
        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, "_cosmetics_done"):
            self._cosmetics_done = True
            _apply_dwm_cosmetics(int(self.winId()))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        r = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        shape = QPainterPath()
        shape.addRoundedRect(r, RADIUS, RADIUS)
        shell = QColor(*SHELL_RGB)

        # -- smoked-glass body: the desktop shows through as a dark haze.
        #    Square top edge (under the titlebar), rounded bottom.
        cut = QRectF(r.left(), r.top() + BAR_HEIGHT - RADIUS, r.width(), r.height() - BAR_HEIGHT + RADIUS)
        cut_path = QPainterPath()
        cut_path.addRect(cut)
        body = shape.intersected(cut_path)

        glass = QColor(shell)
        glass.setAlpha(GLASS_ALPHA)
        p.fillPath(body, glass)

        # depth: slightly darker toward the bottom edge of the pane
        depth = QLinearGradient(r.topLeft(), r.bottomLeft())
        depth.setColorAt(0.75, QColor(0, 0, 0, 0))
        depth.setColorAt(1.00, QColor(0, 0, 0, 60))
        p.fillPath(body, depth)

        # specular gloss catching light right under the titlebar
        streak = QRectF(r.left() + 2, r.top() + BAR_HEIGHT, r.width() - 4, 10)
        glow = QLinearGradient(streak.topLeft(), streak.bottomLeft())
        glow.setColorAt(0.0, QColor(255, 255, 255, 28))
        glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        streak_path = QPainterPath()
        streak_path.addRoundedRect(streak, 10, 10)
        p.fillPath(body.intersected(streak_path), glow)

        # -- solid titlebar (winotch NotchBlack, fully opaque)
        top = QPainterPath()
        top.addRect(QRectF(r.left(), r.top(), r.width(), BAR_HEIGHT))
        p.fillPath(shape.intersected(top), shell)

        # hairline separating titlebar from the glass
        p.fillRect(QRectF(r.left(), r.top() + BAR_HEIGHT, r.width(), 1), QColor(255, 255, 255, 26))

        # -- hairline stroke around the shell (winotch-style edge definition)
        p.strokePath(shape, QPen(QColor(255, 255, 255, HAIRLINE_ALPHA), 1))


class MyBar(QWidget):
    __version__ = getenv("APP_VERSION", "0.0.0")

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._dragging = False
        self._drag_offset = QPoint(0, 0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 5, 0)
        layout.setSpacing(4)

        self.title = QLabel("Sub Fixer " + self.__version__)
        self.title.setFixedHeight(35)
        self.title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title.setStyleSheet("""
            padding-top: 8px;
            padding-left: 4px;
            color: white;
            font: bold;
            font-family: Segoe print;
        """)

        self.btn_close = QPushButton("x")
        self.btn_close.clicked.connect(self.btn_close_clicked)
        self.btn_close.setFixedSize(26, 16)
        self.btn_close.setStyleSheet(
            "QPushButton{color:white; font:bold; border-radius:3px;"
            " padding-bottom:3px; background:transparent;}"
            " QPushButton:hover{background-color:red;}"
        )

        self.btn_min = QPushButton("_")
        self.btn_min.clicked.connect(self.btn_min_clicked)
        self.btn_min.setFixedSize(26, 16)
        self.btn_min.setStyleSheet(
            "QPushButton{color:white; font:bold; border-radius:3px;"
            " padding-bottom:3px; background:transparent;}"
            " QPushButton:hover{background-color:#2a2a2a;}"
        )

        self.btn_help = QPushButton("?")
        self.btn_help.setFixedSize(14, 14)
        self.btn_help.setStyleSheet(
            "QPushButton{color:red; border:1px solid red; border-radius:7px;"
            " padding-left:1px; padding-bottom:1px; background:transparent;}"
            " QToolTip{font-size:11px; font:bold; color:black;"
            " font-family: Segoe print; border:1px solid black; border-radius:0px;}"
        )
        self.btn_help.setToolTip("Supported Formats: srt, SRT, ass\n PS: Use Files with utf8 or ansi Encoding")

        layout.addWidget(self.title, 1)
        layout.addWidget(self.btn_help)
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            # remember where on the window the grab happened
            self._drag_offset = event.globalPos() - self.parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & Qt.LeftButton:
            self.parent.move(event.globalPos() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def btn_close_clicked(self):
        self.parent.close()

    def btn_min_clicked(self):
        self.parent.showMinimized()


class NewLabel(QLabel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.stat = False
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drag & Drop your Subtitle here.\nEnjoy ;)")
        self.setStyleSheet("""
                     border: 3px dashed red;
                     margin-left:5px;
                     margin-right:5px;
                     padding:5px;
                     color: White;
                     font: bold;
                     font-family: Segoe print;

                 """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(6)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

    def reset(self):
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drag & Drop your Subtitle here.\nEnjoy ;)")
        self.stat = False

    def mousePressEvent(self, event):
        if self.stat:
            self.reset()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                # else:       # for next version catch sub from url
                #     links.append(str(url.toString()))
            num = main(links)
            self.change_label(num)

        else:
            event.ignore()

    def change_label(self, count="0"):
        self.stat = True
        self.setText(f"Done! {count} Files were not supported Files\nClick for Fixing more. ")
        self.setAcceptDrops(False)
