import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

def count_characters(name):
    name = name.strip()
    if not name:
        return "Please enter a name!"
    count = len(name)
    no_space = len(name.replace(" ", ""))
    if " " in name:
        return f'"{name}" has {count} characters (with spaces), or {no_space} without spaces.'
    return f'"{name}" has {count} character{"s" if count != 1 else ""}.'

def get_bot_response(user_text):
    text  = user_text.strip()
    lower = text.lower()
    if lower in ("hi", "hello", "hey", "hii"):
        return "Hello! I am CharBot.\nType any name and I will count its characters!"
    if lower in ("bye", "goodbye"):
        return "Goodbye! Have a great day!"
    if lower in ("help", "?"):
        return "Just type any name!\nExample: Raghu\nOr: my name is Raghu"
    for phrase in ("how many characters in ", "count ", "characters in "):
        if lower.startswith(phrase):
            return count_characters(text[len(phrase):])
    if lower.startswith("my name is "):
        return "Nice to meet you! " + count_characters(text[len("my name is "):])
    return count_characters(text)

class Bubble(QFrame):
    def __init__(self, sender, message, is_bot):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        box = QFrame()
        box.setMaximumWidth(260)
        color = "#3a3a5c" if is_bot else "#4a90e2"
        box.setStyleSheet(f"background:{color}; border-radius:14px;")

        inner = QVBoxLayout(box)
        inner.setContentsMargins(12, 8, 12, 8)
        inner.setSpacing(3)

        lbl_sender = QLabel(sender)
        lbl_sender.setFont(QFont("Helvetica", 9, QFont.Bold))
        lbl_sender.setStyleSheet("color:#aaaacc; background:transparent;")
        inner.addWidget(lbl_sender)

        lbl_msg = QLabel(message)
        lbl_msg.setFont(QFont("Helvetica", 13))
        lbl_msg.setStyleSheet("color:#ffffff; background:transparent;")
        lbl_msg.setWordWrap(True)
        inner.addWidget(lbl_msg)

        if is_bot:
            layout.addWidget(box, alignment=Qt.AlignLeft)
            layout.addStretch()
        else:
            layout.addStretch()
            layout.addWidget(box, alignment=Qt.AlignRight)

        self.setStyleSheet("background:transparent; border:none;")

class ChatBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CharBot")
        self.resize(400, 620)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background:#1e1e2e;")
        self._build()
        QTimer.singleShot(400, self._welcome)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setFixedHeight(52)
        hdr.setStyleSheet("background:#12121f;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(14,0,14,0)
        t = QLabel("🤖  CharBot")
        t.setFont(QFont("Helvetica", 14, QFont.Bold))
        t.setStyleSheet("color:#fff; background:transparent;")
        b = QLabel("● always on top")
        b.setFont(QFont("Helvetica", 9))
        b.setStyleSheet("color:#4aeb8a; background:transparent;")
        hl.addWidget(t)
        hl.addStretch()
        hl.addWidget(b)
        root.addWidget(hdr)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea{background:#1e1e2e; border:none;}
            QScrollBar:vertical{background:#2e2e3e; width:6px; border-radius:3px;}
            QScrollBar::handle:vertical{background:#555577; border-radius:3px;}
        """)
        self.msg_widget = QWidget()
        self.msg_widget.setStyleSheet("background:#1e1e2e;")
        self.msg_layout = QVBoxLayout(self.msg_widget)
        self.msg_layout.setContentsMargins(6,10,6,10)
        self.msg_layout.setSpacing(6)
        self.msg_layout.addStretch()
        self.scroll.setWidget(self.msg_widget)
        root.addWidget(self.scroll)

        # Input bar
        bar = QFrame()
        bar.setFixedHeight(66)
        bar.setStyleSheet("background:#12121f;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10,12,10,12)
        bl.setSpacing(8)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type a name...")
        self.entry.setFont(QFont("Helvetica", 13))
        self.entry.setFixedHeight(42)
        self.entry.setStyleSheet("""
            QLineEdit{background:#2e2e3e; color:#fff; border:2px solid #444466;
                      border-radius:10px; padding:0 12px;}
            QLineEdit:focus{border:2px solid #4a90e2;}
        """)
        self.entry.returnPressed.connect(self._send)

        btn = QPushButton("Send ➤")
        btn.setFixedSize(90, 42)
        btn.setFont(QFont("Helvetica", 12, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton{background:#4a90e2; color:#fff; border:none; border-radius:10px;}
            QPushButton:hover{background:#357abd;}
            QPushButton:pressed{background:#2a6099;}
        """)
        btn.clicked.connect(self._send)

        bl.addWidget(self.entry)
        bl.addWidget(btn)
        root.addWidget(bar)

        self.entry.setFocus()

    def _welcome(self):
        self._bot("Hi! I am CharBot.\nType any name and I will count its characters!\n\nExamples:\n  Raghu\n  my name is Raghu")

    def _send(self):
        text = self.entry.text().strip()
        if not text:
            return
        self.entry.clear()
        self._add("You", text, False)
        QTimer.singleShot(300, lambda: self._bot(get_bot_response(text)))

    def _bot(self, msg):
        self._add("CharBot", msg, True)

    def _add(self, sender, msg, is_bot):
        self.msg_layout.insertWidget(self.msg_layout.count()-1, Bubble(sender, msg, is_bot))
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = ChatBot()
    w.show()
    sys.exit(app.exec_())
