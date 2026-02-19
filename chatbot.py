import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCursor


# ── LOGIC ────────────────────────────────────────────────
def count_characters(name):
    name = name.strip()
    if not name:
        return "Please enter a name!"
    count = len(name)
    no_space = len(name.replace(" ", ""))
    if " " in name:
        return f'"{name}" has {count} characters (with spaces),\nor {no_space} characters without spaces.'
    return f'"{name}" has {count} character{"s" if count != 1 else ""}.'

def get_bot_response(user_text):
    text  = user_text.strip()
    lower = text.lower()
    if lower in ("hi", "hello", "hey", "hii"):
        return "Hello! 👋 I'm CharBot.\nType any name and I'll count its characters!"
    if lower in ("bye", "goodbye", "exit", "quit"):
        return "Goodbye! 👋 Have a great day!"
    if lower in ("help", "?"):
        return "Just type any name!\n\nExamples:\n• Raghu\n• my name is Raghu\n• how many characters in Raghavendra"
    for phrase in ("how many characters in ", "count ", "characters in "):
        if lower.startswith(phrase):
            return count_characters(text[len(phrase):])
    if lower.startswith("my name is "):
        return "Nice to meet you! " + count_characters(text[len("my name is "):])
    return count_characters(text)


# ── BUBBLE WIDGET ────────────────────────────────────────
class MessageBubble(QFrame):
    def __init__(self, sender, message, is_bot):
        super().__init__()
        self.setContentsMargins(8, 4, 8, 4)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        bubble = QFrame()
        bubble.setMaximumWidth(280)
        bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        if is_bot:
            bubble.setStyleSheet("""
                background-color: #3a3a5c;
                border-radius: 14px;
                padding: 2px;
            """)
        else:
            bubble.setStyleSheet("""
                background-color: #4a90e2;
                border-radius: 14px;
                padding: 2px;
            """)

        vbox = QVBoxLayout(bubble)
        vbox.setContentsMargins(12, 8, 12, 8)
        vbox.setSpacing(2)

        # Sender label
        sender_label = QLabel(sender)
        sender_label.setFont(QFont("Helvetica", 9, QFont.Bold))
        sender_label.setStyleSheet("color: #aaaacc; background: transparent;")
        vbox.addWidget(sender_label)

        # Message label
        msg_label = QLabel(message)
        msg_label.setFont(QFont("Helvetica", 13))
        msg_label.setStyleSheet("color: #ffffff; background: transparent;")
        msg_label.setWordWrap(True)
        vbox.addWidget(msg_label)

        if is_bot:
            outer.addWidget(bubble, alignment=Qt.AlignLeft)
            outer.addStretch()
        else:
            outer.addStretch()
            outer.addWidget(bubble, alignment=Qt.AlignRight)

        self.setStyleSheet("background: transparent; border: none;")


# ── MAIN WINDOW ──────────────────────────────────────────
class ChatbotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CharBot")
        self.setFixedSize(400, 620)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #1e1e2e;")
        self._build_ui()
        QTimer.singleShot(300, self._welcome)

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("background-color: #12121f;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(14, 0, 14, 0)

        title = QLabel("🤖  CharBot")
        title.setFont(QFont("Helvetica", 14, QFont.Bold))
        title.setStyleSheet("color: #ffffff; background: transparent;")

        badge = QLabel("● always on top")
        badge.setFont(QFont("Helvetica", 9))
        badge.setStyleSheet("color: #4aeb8a; background: transparent;")

        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(badge)
        main.addWidget(header)

        # ── Scroll area for messages ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { background: #1e1e2e; border: none; }
            QScrollBar:vertical { background: #2e2e3e; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #555577; border-radius: 3px; }
        """)

        self.msg_widget = QWidget()
        self.msg_widget.setStyleSheet("background: #1e1e2e;")
        self.msg_layout = QVBoxLayout(self.msg_widget)
        self.msg_layout.setContentsMargins(6, 10, 6, 10)
        self.msg_layout.setSpacing(6)
        self.msg_layout.addStretch()

        self.scroll.setWidget(self.msg_widget)
        main.addWidget(self.scroll)

        # ── Input area ──
        input_frame = QFrame()
        input_frame.setFixedHeight(64)
        input_frame.setStyleSheet("background-color: #12121f;")
        i_layout = QHBoxLayout(input_frame)
        i_layout.setContentsMargins(10, 10, 10, 10)
        i_layout.setSpacing(8)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type a name and press Enter...")
        self.entry.setFont(QFont("Helvetica", 13))
        self.entry.setFixedHeight(40)
        self.entry.setStyleSheet("""
            QLineEdit {
                background-color: #2e2e3e;
                color: #ffffff;
                border: 2px solid #444466;
                border-radius: 10px;
                padding: 0 12px;
            }
            QLineEdit:focus {
                border: 2px solid #4a90e2;
            }
        """)
        self.entry.returnPressed.connect(self._send)

        send_btn = QPushButton("Send ➤")
        send_btn.setFixedSize(90, 40)
        send_btn.setFont(QFont("Helvetica", 12, QFont.Bold))
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2a6099;
            }
        """)
        send_btn.clicked.connect(self._send)

        i_layout.addWidget(self.entry)
        i_layout.addWidget(send_btn)
        main.addWidget(input_frame)

        self.entry.setFocus()

    def _welcome(self):
        self._add_message("CharBot",
            "Hi! I'm CharBot 🤖\nType any name and I'll count its characters!\n\nExamples:\n• Raghu\n• my name is Raghu\n• hello",
            is_bot=True)

    def _send(self):
        text = self.entry.text().strip()
        if not text:
            return
        self.entry.clear()
        self._add_message("You", text, is_bot=False)
        QTimer.singleShot(300, lambda: self._add_message(
            "CharBot", get_bot_response(text), is_bot=True))

    def _add_message(self, sender, message, is_bot):
        bubble = MessageBubble(sender, message, is_bot)
        # Insert before the trailing stretch
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_bottom)

    def _scroll_bottom(self):
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )


# ── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ChatbotWindow()
    window.show()
    sys.exit(app.exec_())
