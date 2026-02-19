import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame,
    QCompleter, QTabWidget, QDateTimeEdit, QListWidget,
    QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont

# ── DATA ─────────────────────────────────────────────────
DATA = {
    "OMS/Promise/IMS":                               "Deepak Gupta, Rajvir Dubey",
    "Transportation":                                "Praveen Kadakal",
    "RUI":                                           "Mandar.Ovalekar@ril.com",
    "Counterpart for Nilesh in WMS, Transportation": "Sridhar Vaidyanathan, Mandar.Ovalekar@ril.com",
    "Warehouse Automation":                          "Anoop1 Nari",
    "Control Tower":                                 "Harishkumar Rp",
    "Rover":                                         "Harishkumar Rp",
}
ALL_KEYS = list(DATA.keys())
TASKS_FILE = os.path.expanduser("~/Desktop/tasks.json")

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE) as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f)

def get_response(user_text):
    text  = user_text.strip()
    lower = text.lower()
    if lower in ("hi", "hello", "hey"):
        return "Hello! 👋 Type a service name to get POC details."
    if lower in ("bye", "goodbye"):
        return "Goodbye! 👋"
    if lower in ("help", "?"):
        return "Type any service name.\n\nAvailable:\n" + "\n".join(f"• {k}" for k in ALL_KEYS)
    if lower in ("list", "show all", "all"):
        return "Available services:\n" + "\n".join(f"• {k}" for k in ALL_KEYS)
    for key in ALL_KEYS:
        if lower == key.lower() or lower in key.lower() or key.lower() in lower:
            return f"📌 Service: {key}\n👤 POC: {DATA[key]}"
    return f'Sorry, couldn\'t find "{text}".\nType "list" to see all services.'


# ── BUBBLE ───────────────────────────────────────────────
class Bubble(QFrame):
    def __init__(self, sender, message, is_bot):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        box = QFrame()
        box.setMaximumWidth(280)
        color  = "#ffffff" if is_bot else "#1a73e8"
        border = "1px solid #c0d8f0" if is_bot else "none"
        box.setStyleSheet(f"background:{color}; border-radius:14px; border:{border};")
        inner = QVBoxLayout(box)
        inner.setContentsMargins(12, 8, 12, 8)
        inner.setSpacing(3)

        ls = QLabel(sender)
        ls.setFont(QFont("Helvetica", 9, QFont.Bold))
        ls.setStyleSheet(f"color:{'#1a73e8' if is_bot else '#cce4ff'}; background:transparent;")
        inner.addWidget(ls)

        lm = QLabel(message)
        lm.setFont(QFont("Helvetica", 13))
        # BLACK for bot messages, white for user messages
        lm.setStyleSheet(f"color:{'#000000' if is_bot else '#ffffff'}; background:transparent;")
        lm.setWordWrap(True)
        inner.addWidget(lm)

        if is_bot:
            layout.addWidget(box, alignment=Qt.AlignLeft)
            layout.addStretch()
        else:
            layout.addStretch()
            layout.addWidget(box, alignment=Qt.AlignRight)
        self.setStyleSheet("background:transparent; border:none;")


# ── CHAT TAB ─────────────────────────────────────────────
class ChatTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#ddeeff;")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{background:#ddeeff;border:none;}"
            "QScrollBar:vertical{background:#c0d8f0;width:6px;border-radius:3px;}"
            "QScrollBar::handle:vertical{background:#1a73e8;border-radius:3px;}")
        self.msg_widget = QWidget()
        self.msg_widget.setStyleSheet("background:#ddeeff;")
        self.msg_layout = QVBoxLayout(self.msg_widget)
        self.msg_layout.setContentsMargins(6, 10, 6, 10)
        self.msg_layout.setSpacing(6)
        self.msg_layout.addStretch()
        self.scroll.setWidget(self.msg_widget)
        root.addWidget(self.scroll)

        bar = QFrame()
        bar.setFixedHeight(68)
        bar.setStyleSheet("background:#b8d8f0; border-top:1px solid #90c0e8;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10, 12, 10, 12)
        bl.setSpacing(8)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type a service name...")
        self.entry.setFont(QFont("Helvetica", 13))
        self.entry.setFixedHeight(44)
        self.entry.setStyleSheet("""
            QLineEdit{background:#fff; color:#000000; border:2px solid #90c0e8; border-radius:22px; padding:0 16px;}
            QLineEdit:focus{border:2px solid #1a73e8;}
        """)
        self.completer = QCompleter(ALL_KEYS)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.popup().setStyleSheet("""
            QListView{background:#fff; color:#000000; font-size:13px; border:1px solid #90c0e8; border-radius:8px; padding:4px;}
            QListView::item:hover{background:#ddeeff;}
            QListView::item:selected{background:#1a73e8; color:white;}
        """)
        self.entry.setCompleter(self.completer)
        self.entry.returnPressed.connect(self._send)

        btn = QPushButton("Send ➤")
        btn.setFixedSize(90, 44)
        btn.setFont(QFont("Helvetica", 12, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("QPushButton{background:#1a73e8;color:#fff;border:none;border-radius:22px;}"
                          "QPushButton:hover{background:#1558b0;}")
        btn.clicked.connect(self._send)
        bl.addWidget(self.entry)
        bl.addWidget(btn)
        root.addWidget(bar)
        self.entry.setFocus()
        QTimer.singleShot(400, self._welcome)

    def _welcome(self):
        self._bot("Hi! 👋 I'm your Service POC Bot.\nType a service name to get POC details.\n\nType 'list' to see all services.")

    def _send(self):
        text = self.entry.text().strip()
        if not text: return
        self.entry.clear()
        self._add("You", text, False)
        QTimer.singleShot(300, lambda: self._bot(get_response(text)))

    def _bot(self, msg):
        self._add("POC Bot", msg, True)

    def _add(self, sender, msg, is_bot):
        self.msg_layout.insertWidget(self.msg_layout.count()-1, Bubble(sender, msg, is_bot))
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))


# ── TASK TAB ─────────────────────────────────────────────
class TaskTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#ddeeff;")
        self.tasks = load_tasks()

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QLabel("📝  Task Reminder")
        title.setFont(QFont("Helvetica", 15, QFont.Bold))
        title.setStyleSheet("color:#000000; background:transparent;")
        root.addWidget(title)

        # Task name
        name_lbl = QLabel("Task Name:")
        name_lbl.setFont(QFont("Helvetica", 11, QFont.Bold))
        name_lbl.setStyleSheet("color:#000000; background:transparent;")
        root.addWidget(name_lbl)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task name...")
        self.task_input.setFont(QFont("Helvetica", 13))
        self.task_input.setFixedHeight(42)
        self.task_input.setStyleSheet("""
            QLineEdit{background:#fff; color:#000000; border:2px solid #90c0e8; border-radius:10px; padding:0 12px;}
            QLineEdit:focus{border:2px solid #1a73e8;}
        """)
        root.addWidget(self.task_input)

        # Date/time
        dt_lbl = QLabel("Due Date & Time:")
        dt_lbl.setFont(QFont("Helvetica", 11, QFont.Bold))
        dt_lbl.setStyleSheet("color:#000000; background:transparent;")
        root.addWidget(dt_lbl)

        self.dt_picker = QDateTimeEdit()
        self.dt_picker.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.dt_picker.setDisplayFormat("dd-MM-yyyy  hh:mm AP")
        self.dt_picker.setCalendarPopup(True)
        self.dt_picker.setFixedHeight(42)
        self.dt_picker.setFont(QFont("Helvetica", 13))
        self.dt_picker.setStyleSheet("""
            QDateTimeEdit{background:#fff; color:#000000; border:2px solid #90c0e8; border-radius:10px; padding:0 12px;}
            QDateTimeEdit:focus{border:2px solid #1a73e8;}
        """)
        root.addWidget(self.dt_picker)

        # Add button
        add_btn = QPushButton("➕  Add Task")
        add_btn.setFixedHeight(44)
        add_btn.setFont(QFont("Helvetica", 13, QFont.Bold))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton{background:#1a73e8; color:#fff; border:none; border-radius:10px;}
            QPushButton:hover{background:#1558b0;}
        """)
        add_btn.clicked.connect(self._add_task)
        root.addWidget(add_btn)

        # Task list label
        list_lbl = QLabel("Your Tasks:  (select a task to delete)")
        list_lbl.setFont(QFont("Helvetica", 11, QFont.Bold))
        list_lbl.setStyleSheet("color:#000000; background:transparent;")
        root.addWidget(list_lbl)

        # Task list
        self.task_list = QListWidget()
        self.task_list.setFont(QFont("Helvetica", 12))
        self.task_list.setStyleSheet("""
            QListWidget{background:#fff; color:#000000; border:2px solid #90c0e8; border-radius:10px; padding:4px;}
            QListWidget::item{padding:8px; color:#000000; border-bottom:1px solid #ddeeff;}
            QListWidget::item:selected{background:#ddeeff; color:#000000;}
        """)
        root.addWidget(self.task_list)

        # Delete button
        del_btn = QPushButton("🗑️  Delete Selected Task")
        del_btn.setFixedHeight(44)
        del_btn.setFont(QFont("Helvetica", 13, QFont.Bold))
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet("""
            QPushButton{background:#e53935; color:#fff; border:none; border-radius:10px;}
            QPushButton:hover{background:#b71c1c;}
        """)
        del_btn.clicked.connect(self._delete_task)
        root.addWidget(del_btn)

        self._refresh_list()

        # Check reminders every 30 seconds
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self._check_reminders)
        self.reminder_timer.start(30000)

    def _add_task(self):
        name = self.task_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Empty Task", "Please enter a task name!")
            return
        due_dt = self.dt_picker.dateTime().toPyDateTime()
        if due_dt <= datetime.now():
            QMessageBox.warning(self, "Invalid Time", "Please select a future date and time!")
            return
        task = {"name": name, "due": due_dt.strftime("%Y-%m-%d %H:%M"), "reminded": False}
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.task_input.clear()
        self._refresh_list()
        QMessageBox.information(self, "Task Added ✅",
            f'"{name}" added!\n🔔 Reminder set 2 hours before due time.')

    def _delete_task(self):
        row = self.task_list.currentRow()
        if row < 0 or row >= len(self.tasks):
            QMessageBox.warning(self, "No Selection", "Please select a task from the list to delete!")
            return
        task_name = self.tasks[row]["name"]
        confirm = QMessageBox.question(self, "Confirm Delete",
            f'Are you sure you want to delete:\n"{task_name}"?',
            QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.tasks.pop(row)
            save_tasks(self.tasks)
            self._refresh_list()
            QMessageBox.information(self, "Deleted ✅", f'"{task_name}" has been deleted.')

    def _refresh_list(self):
        self.task_list.clear()
        if not self.tasks:
            item = QListWidgetItem("  No tasks yet. Add one above!")
            item.setForeground(QColor("#000000"))
            self.task_list.addItem(item)
            return
        for t in self.tasks:
            due = datetime.strptime(t["due"], "%Y-%m-%d %H:%M")
            now = datetime.now()
            status = "✅ Done" if due < now else "⏳ Pending"
            remind_time = due - timedelta(hours=2)
            text = (f'{status}  —  {t["name"]}\n'
                    f'     📅 Due: {due.strftime("%d %b %Y, %I:%M %p")}'
                    f'   🔔 Remind at: {remind_time.strftime("%I:%M %p")}')
            item = QListWidgetItem(text)
            item.setForeground(QColor("#000000"))
            self.task_list.addItem(item)

    def _check_reminders(self):
        now = datetime.now()
        changed = False
        for t in self.tasks:
            if t.get("reminded"):
                continue
            due = datetime.strptime(t["due"], "%Y-%m-%d %H:%M")
            remind_at = due - timedelta(hours=2)
            if now >= remind_at and now < due:
                t["reminded"] = True
                changed = True
                msg = QMessageBox()
                msg.setWindowTitle("⏰ Task Reminder!")
                msg.setText(f'🔔 Reminder!\n\n"{t["name"]}"\nis due at {due.strftime("%I:%M %p")} today!\n\n⏳ Only 2 hours left!')
                msg.setIcon(QMessageBox.Information)
                msg.setWindowFlags(Qt.WindowStaysOnTopHint)
                msg.exec_()
        if changed:
            save_tasks(self.tasks)
            self._refresh_list()


# ── MAIN WINDOW ──────────────────────────────────────────
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Service POC Bot")
        self.resize(420, 680)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background:#ddeeff;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setFixedHeight(56)
        hdr.setStyleSheet("background:#1a73e8;")
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

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Helvetica", 12))
        self.tabs.setStyleSheet("""
            QTabWidget::pane{border:none; background:#ddeeff;}
            QTabBar::tab{background:#b8d8f0; color:#000000; padding:10px 24px;
                         font-size:13px; border-top-left-radius:8px; border-top-right-radius:8px;}
            QTabBar::tab:selected{background:#1a73e8; color:#ffffff; font-weight:bold;}
            QTabBar::tab:hover{background:#90c0e8;}
        """)
        self.tabs.addTab(ChatTab(), "💬  Chat")
        self.tabs.addTab(TaskTab(), "📝  Tasks")
        root.addWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
