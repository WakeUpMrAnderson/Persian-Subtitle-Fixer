"""Sub Fixer GUI - solid custom titlebar + glassmorphism body.

The window is frameless with per-pixel alpha (WA_TranslucentBackground).
The body is classic glassmorphism (Apple liquid glass / glassmorphism
cards): a light translucent white tint over the desktop, bright rim
border glowing top-left, faint inner second edge, specular gloss under
the titlebar and generous corner rounding. No acrylic, no DWM backdrop,
no blur of the desktop - pure painting on a per-pixel-alpha window;
the titlebar stays solid #050505. The drop zone keeps its 3px dashed
red border, bold Segoe print and same texts (white for readability on
glass). DWM is used for cosmetics only (dark tint, no 1px window
border); corner rounding is ours, never DWM's.
"""

import ctypes
from os import getenv

from PyQt6.QtCore import QPoint, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFontMetrics,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from subtitle_processor import main

BAR_HEIGHT = 36
RADIUS = 18  # glassmorphism-card corner rounding

# titlebar: solid opaque black (kept solid on purpose)
SHELL_RGB = (5, 5, 5)

# glassmorphism body knobs (white tint - the desktop shows through hazed;
# alpha values are 0-255, higher = more frosted/opaque)
GLASS_TINT_TOP = 90
GLASS_TINT_MID = 60
GLASS_TINT_BOTTOM = 50
GLOSS_ALPHA = 50  # specular streak right under the titlebar
RIM_TOP = 170  # outer border: bright top-left ...
RIM_MID = 60
RIM_BOTTOM = 120  # ... dimmer bottom-right
INNER_EDGE_ALPHA = 55  # faint second edge just inside the rim

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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Sub Fixer")  # targetable even though the titlebar is custom
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
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
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        shape = QPainterPath()
        shape.addRoundedRect(r, RADIUS, RADIUS)
        shell = QColor(*SHELL_RGB)

        # -- glassmorphism body: translucent white tint; the desktop shows
        #    through hazed. Square top edge (under the titlebar), rounded bottom.
        cut = QRectF(r.left(), r.top() + BAR_HEIGHT - RADIUS, r.width(), r.height() - BAR_HEIGHT + RADIUS)
        cut_path = QPainterPath()
        cut_path.addRect(cut)
        body = shape.intersected(cut_path)

        tint = QLinearGradient(r.topLeft(), r.bottomLeft())
        tint.setColorAt(0.00, QColor(255, 255, 255, GLASS_TINT_TOP))
        tint.setColorAt(0.35, QColor(255, 255, 255, GLASS_TINT_MID))
        tint.setColorAt(1.00, QColor(255, 255, 255, GLASS_TINT_BOTTOM))
        p.fillPath(body, tint)

        # depth: slightly darker toward the bottom edge of the pane
        depth = QLinearGradient(r.topLeft(), r.bottomLeft())
        depth.setColorAt(0.70, QColor(0, 0, 0, 0))
        depth.setColorAt(1.00, QColor(0, 0, 0, 40))
        p.fillPath(body, depth)

        # specular gloss catching light right under the titlebar
        streak = QRectF(r.left() + 2, r.top() + BAR_HEIGHT, r.width() - 4, 10)
        glow = QLinearGradient(streak.topLeft(), streak.bottomLeft())
        glow.setColorAt(0.0, QColor(255, 255, 255, GLOSS_ALPHA))
        glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        streak_path = QPainterPath()
        streak_path.addRoundedRect(streak, 10, 10)
        p.fillPath(body.intersected(streak_path), glow)

        # -- solid titlebar (kept solid on purpose)
        top = QPainterPath()
        top.addRect(QRectF(r.left(), r.top(), r.width(), BAR_HEIGHT))
        p.fillPath(shape.intersected(top), shell)

        # hairline separating titlebar from the glass
        p.fillRect(QRectF(r.left(), r.top() + BAR_HEIGHT, r.width(), 1), QColor(255, 255, 255, 26))

        # -- glass border: bright top-left, dimmer bottom-right
        rim = QLinearGradient(r.topLeft(), r.bottomRight())
        rim.setColorAt(0.00, QColor(255, 255, 255, RIM_TOP))
        rim.setColorAt(0.45, QColor(255, 255, 255, RIM_MID))
        rim.setColorAt(1.00, QColor(255, 255, 255, RIM_BOTTOM))
        p.strokePath(shape, QPen(QBrush(rim), 1.2))

        # faint inner edge just inside the rim (glassmorphism double edge)
        inner = QPainterPath()
        inner.addRoundedRect(r.adjusted(2.0, 2.0, -2.0, -2.0), RADIUS - 2, RADIUS - 2)
        p.strokePath(inner, QPen(QColor(255, 255, 255, INNER_EDGE_ALPHA), 1))


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
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
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
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            # remember where on the window the grab happened
            self._drag_offset = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.parent.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def btn_close_clicked(self):
        self.parent.close()

    def btn_min_clicked(self):
        self.parent.showMinimized()


class NewLabel(QLabel):
    """Drop zone, custom-painted: dashed red border + text drawn as
    QPainterPath with a dark stroke, so the white glyphs keep a visible
    contour and stay readable even over white windows."""

    BORDER_INSET = 6  # dashed border inset from the label edge
    PAD = 6  # text padding inside the border
    STROKE_WIDTH = 4.5  # dark outline around the glyphs

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.stat = False
        self.setAcceptDrops(True)
        self.setText("Drag & Drop your Subtitle here.\nEnjoy ;)")

        font = self.font()
        font.setFamily("Segoe print")
        font.setBold(True)
        self.setFont(font)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(6)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # dashed red border, same look as the old stylesheet border
        box = self.rect().adjusted(
            self.BORDER_INSET, self.BORDER_INSET, -(self.BORDER_INSET + 1), -(self.BORDER_INSET + 1)
        )
        p.setPen(QPen(QColor("red"), 3, Qt.PenStyle.DashLine))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(box)

        text = self.text()
        if not text:
            return

        # text as paths: dark stroke first, white fill on top - the glyphs
        # keep a dark contour that reads on any background
        fm = QFontMetrics(self.font())
        area = self.rect().adjusted(
            self.BORDER_INSET + self.PAD,
            self.BORDER_INSET + self.PAD,
            -(self.BORDER_INSET + self.PAD),
            -(self.BORDER_INSET + self.PAD),
        )
        lines = text.split("\n")
        line_h = fm.lineSpacing()
        y = area.top() + (area.height() - len(lines) * line_h) / 2 + fm.ascent()
        path = QPainterPath()
        for line in lines:
            x = area.left() + (area.width() - fm.horizontalAdvance(line)) / 2
            path.addText(QPointF(x, y), self.font(), line)
            y += line_h

        p.setPen(
            QPen(
                QColor(15, 15, 15, 235),
                self.STROKE_WIDTH,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("white"))
        p.drawPath(path)

    def reset(self):
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
            event.setDropAction(Qt.DropAction.CopyAction)
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
