import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame,
    QCompleter
)
from PyQt5.QtCore import Qt, QTimer, QStringListModel
from PyQt5.QtGui import QFont, QColor

# ── DATA TABLE ───────────────────────────────────────────
DATA = {
    "OMS/Promise/IMS":              "Deepak Gupta, Rajvir Dubey",
    "Transportation":               "Praveen Kadakal",
    "RUI":                          "Mandar.Ovalekar@ril.com",
    "Counterpart for Nilesh in WMS, Transportation": "Sridhar Vaidyanathan, Mandar.Ovalekar@ril.com",
    "Warehouse Automation":         "Anoop1 Nari",
    "Control Tower":                "Harishkumar Rp",
    "Rover":                        "Harishkumar Rp",
}

ALL_KEYS = list(DATA.keys())

def get_response(user_text):
    text = user_text.strip()
    lower = text.lower()

    if lower in ("hi", "hello", "hey"):
        return "Hello! 👋 How can I help you?\nType a service name to get the POC details."
    if lower in ("bye", "goodbye"):
        return "Goodbye! Have a great day! 👋"
    if lower in ("help", "?"):
        return "Type any service name to get POC details.\n\nAvailable services:\n" + "\n".join(f"• {k}" for k in ALL_KEYS)
    if lower in ("list", "show all", "all services"):
        return "Available services:\n" + "\n".join(f"• {k}" for k in ALL_KEYS)

    # Search for matching key
    for key in ALL_KEYS:
        if lower == key.lower() or lower in key.lower() or key.lower() in lower:
            return f"📌 Service: {key}\n👤 POC: {DATA[key]}"

    return f'Sorry, I couldn\'t find "{text}".\nType "list" to see all services.'


# ── BUBBLE ───────────────────────────────────────────────
class Bubble(QFrame):
    def __init__(self, sender, message, is_bot):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        box = QFrame()
        box.setMaximumWidth(280)
        color = "#ffffff" if is_bot else "#1a73e8"
        border = "1px solid #c0d8f0" if is_bot else "none"
        box.setStyleSheet(f"""
            background: {color};
            border-radius: 14px;
            border: {border};
        """)

        inner = QVBoxLayout(box)
        inner.setContentsMargins(12, 8, 12, 8)
        inner.setSpacing(3)

        lbl_sender = QLabel(sender)
        lbl_sender.setFont(QFont("Helvetica", 9, QFont.Bold))
        sender_color = "#1a73e8" if is_bot else "#cce4ff"
        lbl_sender.setStyleSheet(f"color:{sender_color}; background:transparent;")
        inner.addWidget(lbl_sender)

        lbl_msg = QLabel(message)
        lbl_msg.setFont(QFont("Helvetica", 13))
        msg_color = "#222222" if is_bot else "#ffffff"
        lbl_msg.setStyleSheet(f"color:{msg_color}; background:transparent;")
        lbl_msg.setWordWrap(True)
        inner.addWidget(lbl_msg)

        if is_bot:
            layout.addWidget(box, alignment=Qt.AlignLeft)
            layout.addStretch()
        else:
            layout.addStretch()
            layout.addWidget(box, alignment=Qt.AlignRight)

        self.setStyleSheet("background:transparent; border:none;")


# ── MAIN WINDOW ──────────────────────────────────────────
class ChatBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Service POC Bot")
        self.resize(420, 640)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background:#ddeeff;")
        self._build()
        QTimer.singleShot(400, self._welcome)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        hdr = QFrame()
        hdr.setFixedHeight(56)
        hdr.setStyleSheet("background:#1a73e8; border-bottom: 2px solid #1558b0;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(14, 0, 14, 0)

        t = QLabel("💬  Service POC Bot")
        t.setFont(QFont("Helvetica", 14, QFont.Bold))
        t.setStyleSheet("color:#ffffff; background:transparent;")

        b = QLabel("● always on top")
        b.setFont(QFont("Helvetica", 9))
        b.setStyleSheet("color:#a8d4ff; background:transparent;")

        hl.addWidget(t)
        hl.addStretch()
        hl.addWidget(b)
        root.addWidget(hdr)

        # ── Scroll area ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { background: #ddeeff; border: none; }
            QScrollBar:vertical { background: #c0d8f0; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #1a73e8; border-radius: 3px; }
        """)

        self.msg_widget = QWidget()
        self.msg_widget.setStyleSheet("background:#ddeeff;")
        self.msg_layout = QVBoxLayout(self.msg_widget)
        self.msg_layout.setContentsMargins(6, 10, 6, 10)
        self.msg_layout.setSpacing(6)
        self.msg_layout.addStretch()
        self.scroll.setWidget(self.msg_widget)
        root.addWidget(self.scroll)

        # ── Input bar ──
        bar = QFrame()
        bar.setFixedHeight(68)
        bar.setStyleSheet("background:#b8d8f0; border-top: 1px solid #90c0e8;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10, 12, 10, 12)
        bl.setSpacing(8)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type a service name...")
        self.entry.setFont(QFont("Helvetica", 13))
        self.entry.setFixedHeight(44)
        self.entry.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                color: #222222;
                border: 2px solid #90c0e8;
                border-radius: 22px;
                padding: 0 16px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)

        # ── Autocomplete ──
        self.completer = QCompleter(ALL_KEYS)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.popup().setStyleSheet("""
            QListView {
                background: #ffffff;
                color: #222222;
                font-size: 13px;
                border: 1px solid #90c0e8;
                border-radius: 8px;
                padding: 4px;
            }
            QListView::item:hover {
                background: #ddeeff;
            }
            QListView::item:selected {
                background: #1a73e8;
                color: white;
            }
        """)
        self.entry.setCompleter(self.completer)
        self.entry.returnPressed.connect(self._send)

        btn = QPushButton("Send ➤")
        btn.setFixedSize(90, 44)
        btn.setFont(QFont("Helvetica", 12, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton { background:#1a73e8; color:#fff; border:none; border-radius:22px; }
            QPushButton:hover { background:#1558b0; }
            QPushButton:pressed { background:#0d3d80; }
        """)
        btn.clicked.connect(self._send)

        bl.addWidget(self.entry)
        bl.addWidget(btn)
        root.addWidget(bar)

        self.entry.setFocus()

    def _welcome(self):
        self._bot("Hi! 👋 I'm your Service POC Bot.\nType a service name to get POC details.\n\nAvailable services:\n• OMS/Promise/IMS\n• Transportation\n• RUI\n• Warehouse Automation\n• Control Tower\n• Rover\n\nOr type 'list' to see all.")

    def _send(self):
        text = self.entry.text().strip()
        if not text:
            return
        self.entry.clear()
        self._add("You", text, False)
        QTimer.singleShot(300, lambda: self._bot(get_response(text)))

    def _bot(self, msg):
        self._add("POC Bot", msg, True)

    def _add(self, sender, msg, is_bot):
        self.msg_layout.insertWidget(
            self.msg_layout.count() - 1, Bubble(sender, msg, is_bot))
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = ChatBot()
    w.show()
    sys.exit(app.exec_())
