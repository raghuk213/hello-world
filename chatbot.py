import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame,
    QCompleter, QTabWidget, QDateTimeEdit, QListWidget,
    QListWidgetItem, QMessageBox, QTextEdit, QSplitter, QStackedWidget
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor

# ── DATA ─────────────────────────────────────────────────
DATA = {
    "OMS/Promise/IMS":                               "Deepak Gupta, Rajvir Dubey",
    "Transportation":                                "Praveen Kadakal",
    "RUI":                                           "Mandar.Ovalekar@ril.com",
    "Counterpart for Nilesh in WMS, Transportation": "Sridhar Vaidyanathan, Mandar.Ovalekar@ril.com",
    "Warehouse Automation":                          "Anoop1 Nari",
    "Control Tower":                                 "Harishkumar Rp",
    "Rover":                                         "Harishkumar Rp",
    "Platforms Dev":                                 "Amit42 Tiwari",
    "Tops Team":                                     "kiran4.s@ril.com",
}
ALL_KEYS = list(DATA.keys())
ALL_POCS = list(set(poc.strip() for pocs in DATA.values() for poc in pocs.split(",")))
ALL_SUGGESTIONS = ALL_KEYS + ALL_POCS
TASKS_FILE = os.path.expanduser("~/Desktop/tasks.json")
NOTES_FILE = os.path.expanduser("~/Desktop/raghav_notes.json")

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE) as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f)

def load_notes():
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE) as f:
                text = f.read().strip()
            if not text:
                return []
            data = json.loads(text)
            return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)

def get_response(user_text):
    text  = user_text.strip()
    lower = text.lower()
    if lower in ("hi", "hello", "hey"):
        return "Hello! 👋 Type a service name or POC name to get details."
    if lower in ("bye", "goodbye"):
        return "Goodbye! 👋"
    if lower in ("help", "?"):
        return "Type any service name or POC name.\n\nAvailable services:\n" + "\n".join(f"• {k}" for k in ALL_KEYS)
    if lower in ("list", "show all", "all"):
        return "Available services:\n" + "\n".join(f"• {k}" for k in ALL_KEYS)

    results = []

    # Search by service name
    for key in ALL_KEYS:
        if lower == key.lower() or lower in key.lower() or key.lower() in lower:
            results.append(f"📌 Service: {key}\n👤 POC: {DATA[key]}")

    # Search by POC name/email
    for key, poc in DATA.items():
        if lower in poc.lower() or poc.lower() in lower:
            # Avoid duplicates
            entry = f"📌 Service: {key}\n👤 POC: {poc}"
            if entry not in results:
                results.append(entry)

    if results:
        return "\n\n".join(results)

    return f'Sorry, couldn\'t find "{text}".\nType "list" to see all services.'


POPUP_STYLE = """
    QMessageBox { background-color: #1a1a3e; }
    QLabel { color: #1a1a2e; font-size: 13px; font-family: Helvetica; }
    QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6a00ff,stop:1 #5aabff);
                  color: #ffffff; border-radius: 8px;
                  padding: 6px 20px; font-size: 13px; font-weight: bold; min-width: 70px; }
    QPushButton:hover { background: #5aabff; color: #000000; }
"""

def show_popup(parent, title, message, kind="info"):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet(POPUP_STYLE)
    if kind == "warn":
        msg.setIcon(QMessageBox.Warning)
    elif kind == "question":
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    else:
        msg.setIcon(QMessageBox.Information)
    return msg.exec_()


# ── BUBBLE ───────────────────────────────────────────────
class Bubble(QFrame):
    def __init__(self, sender, message, is_bot):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        box = QFrame()
        box.setMaximumWidth(300)
        if is_bot:
            box.setStyleSheet("""
                background: #ede9fe;
                border-radius: 18px;
                border: none;
            """)
        else:
            box.setStyleSheet("""
                background: #f0f0f0;
                border-radius: 18px;
                border: none;
            """)
        inner = QVBoxLayout(box)
        inner.setContentsMargins(14, 10, 14, 10)
        inner.setSpacing(2)
        lm = QLabel(message)
        lm.setFont(QFont("Helvetica", 13))
        lm.setStyleSheet("color:#1a1a2e; background:transparent;")
        lm.setWordWrap(True)
        inner.addWidget(lm)
        if is_bot:
            # Bot avatar circle
            av = QLabel("✦")
            av.setFixedSize(36, 36)
            av.setAlignment(Qt.AlignCenter)
            av.setFont(QFont("Helvetica", 14))
            av.setStyleSheet("""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #7c3aed, stop:1 #4f46e5);
                border-radius: 18px;
                color: white;
            """)
            row = QHBoxLayout()
            row.setContentsMargins(0,0,0,0)
            row.setSpacing(8)
            row.addWidget(av, alignment=Qt.AlignTop)
            row.addWidget(box, alignment=Qt.AlignLeft)
            row.addStretch()
            outer = QFrame()
            outer.setStyleSheet("background:transparent; border:none;")
            outer.setLayout(row)
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0,0,0,0)
            main_layout.addWidget(outer)
        else:
            # User avatar circle
            av = QLabel("R")
            av.setFixedSize(36, 36)
            av.setAlignment(Qt.AlignCenter)
            av.setFont(QFont("Helvetica", 13, QFont.Bold))
            av.setStyleSheet("""
                background: #e8a050;
                border-radius: 18px;
                color: white;
            """)
            row = QHBoxLayout()
            row.setContentsMargins(0,0,0,0)
            row.setSpacing(8)
            row.addStretch()
            row.addWidget(box, alignment=Qt.AlignRight)
            row.addWidget(av, alignment=Qt.AlignTop)
            outer = QFrame()
            outer.setStyleSheet("background:transparent; border:none;")
            outer.setLayout(row)
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0,0,0,0)
            main_layout.addWidget(outer)
        self.setStyleSheet("background:transparent; border:none;")

# ── CHAT TAB ─────────────────────────────────────────────
class ChatTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f7f7f8;")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Chat display using QTextEdit - most reliable on Mac
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("""
            QTextEdit {
                background: #f7f7f8;
                border: none;
                padding: 10px;
                font-size: 13px;
                color: #000000;
            }
            QScrollBar:vertical {
                background: #eeeeee;
                width: 4px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #c4b5fd;
                border-radius: 2px;
            }
        """)
        self.chat.setFont(QFont("Helvetica", 13))
        root.addWidget(self.chat)

        # Input bar
        bar = QFrame()
        bar.setFixedHeight(72)
        bar.setStyleSheet("background:#ffffff; border-top:1px solid #eeeeee;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(12, 12, 12, 12)
        bl.setSpacing(10)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type service or POC name...")
        self.entry.setFont(QFont("Helvetica", 13))
        self.entry.setFixedHeight(46)
        self.entry.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #d0d0d0;
                border-radius: 23px;
                padding: 0 20px;
            }
            QLineEdit:focus {
                background: #ffffff;
                color: #000000;
                border: 1px solid #7c3aed;
            }
        """)

        self.completer = QCompleter(ALL_SUGGESTIONS)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.popup().setStyleSheet("""
            QListView {
                background: #ffffff;
                color: #000000;
                font-size: 13px;
                border: 1px solid #e0d9ff;
                border-radius: 10px;
                padding: 4px;
            }
            QListView::item { padding: 8px 12px; color: #000000; }
            QListView::item:hover { background: #ede9fe; color: #4f46e5; }
            QListView::item:selected { background: #ddd6fe; color: #4f46e5; }
        """)
        self.entry.setCompleter(self.completer)
        self.entry.returnPressed.connect(self._send)

        btn = QPushButton("Send ➤")
        btn.setFixedSize(90, 46)
        btn.setFont(QFont("Helvetica", 12, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #7c3aed, stop:1 #4f46e5);
                color: #ffffff;
                border: none;
                border-radius: 23px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #6d28d9, stop:1 #4338ca);
            }
        """)
        btn.clicked.connect(self._send)
        bl.addWidget(self.entry)
        bl.addWidget(btn)
        root.addWidget(bar)

        self.entry.setFocus()
        QTimer.singleShot(400, self._welcome)

    def _welcome(self):
        self._bot("Hi! 👋 I am Raghav Bot.\nType a service name or POC name to get details.\n\nType 'list' to see all services.")

    def _send(self):
        text = self.entry.text().strip()
        if not text:
            return
        self.entry.clear()
        self._add_user(text)
        response = get_response(text)
        QTimer.singleShot(300, lambda r=response: self._bot(r))

    def _bot(self, msg):
        # Left aligned bot message using HTML
        safe_msg = msg.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
        html = f"""
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="70%" align="left">
              <div style="
                background:#ede9fe;
                border-radius:14px;
                padding:10px 14px;
                margin:4px 0;
                display:inline-block;
              ">
                <span style="color:#7c3aed; font-size:9pt; font-weight:bold;">Raghav Bot</span><br>
                <span style="color:#1a1a2e; font-size:13pt;">{safe_msg}</span>
              </div>
            </td>
            <td width="30%"></td>
          </tr>
        </table>
        """
        self.chat.append(html)
        self.chat.ensureCursorVisible()

    def _add_user(self, msg):
        # Right aligned user message using HTML
        safe_msg = msg.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
        html = f"""
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="30%"></td>
            <td width="70%" align="right">
              <div style="
                background:#ddd6fe;
                border-radius:14px;
                padding:10px 14px;
                margin:4px 0;
                display:inline-block;
              ">
                <span style="color:#4f46e5; font-size:9pt; font-weight:bold;">You</span><br>
                <span style="color:#1a1a2e; font-size:13pt;">{safe_msg}</span>
              </div>
            </td>
          </tr>
        </table>
        """
        self.chat.append(html)
        self.chat.ensureCursorVisible()

# ── TASK TAB ─────────────────────────────────────────────
class TaskTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f7f7f8;")
        self.tasks = load_tasks()

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("📝  Task Reminder")
        title.setFont(QFont("Helvetica", 15, QFont.Bold))
        title.setStyleSheet("color:#1a1a2e; background:transparent; font-size:15px;")
        root.addWidget(title)

        name_lbl = QLabel("Task Name:")
        name_lbl.setFont(QFont("Helvetica", 11, QFont.Bold))
        name_lbl.setStyleSheet("color:#555555; background:transparent;")
        root.addWidget(name_lbl)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task name...")
        self.task_input.setFont(QFont("Helvetica", 13))
        self.task_input.setFixedHeight(42)
        self.task_input.setStyleSheet("""
            QLineEdit{background:#ffffff; color:#1a1a2e; border:1px solid #e0d9ff; border-radius:10px; padding:0 12px;}
            QLineEdit:focus{border:1px solid #7c3aed; background:#faf8ff;}
        """)
        root.addWidget(self.task_input)

        dt_lbl = QLabel("Due Date & Time:")
        dt_lbl.setFont(QFont("Helvetica", 11, QFont.Bold))
        dt_lbl.setStyleSheet("color:#555555; background:transparent;")
        root.addWidget(dt_lbl)

        self.dt_picker = QDateTimeEdit()
        self.dt_picker.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.dt_picker.setDisplayFormat("dd-MM-yyyy  hh:mm AP")
        self.dt_picker.setCalendarPopup(True)
        self.dt_picker.setFixedHeight(42)
        self.dt_picker.setFont(QFont("Helvetica", 13))
        self.dt_picker.setStyleSheet("""
            QDateTimeEdit{background:#ffffff; color:#1a1a2e; border:1px solid #e0d9ff; border-radius:10px; padding:0 12px;}
            QDateTimeEdit:focus{border:1px solid #7c3aed;}
        """)
        root.addWidget(self.dt_picker)

        add_btn = QPushButton("➕  Add Task")
        add_btn.setFixedHeight(44)
        add_btn.setFont(QFont("Helvetica", 13, QFont.Bold))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6a00ff,stop:1 #5aabff);color:#ffffff;border:none;border-radius:10px;font-weight:bold;letter-spacing:1px;}
            QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5aabff,stop:1 #a0d8ff);color:#000000;}
        """)
        add_btn.clicked.connect(self._add_task)
        root.addWidget(add_btn)

        list_lbl = QLabel("Your Tasks:  (select a task then click action)")
        list_lbl.setFont(QFont("Helvetica", 11, QFont.Bold))
        list_lbl.setStyleSheet("color:#555555; background:transparent;")
        root.addWidget(list_lbl)

        self.task_list = QListWidget()
        self.task_list.setFont(QFont("Helvetica", 12))
        self.task_list.setStyleSheet("""
            QListWidget{background:#ffffff; color:#1a1a2e; border:1px solid #e0d9ff; border-radius:10px; padding:4px;}
            QListWidget::item{padding:8px; color:#1a1a2e; border-bottom:1px solid #f0f0f0;}
            QListWidget::item:selected{background:#ede9fe; color:#4f46e5;}
        """)
        root.addWidget(self.task_list)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        done_btn = QPushButton("✅  Mark as Done")
        done_btn.setFixedHeight(44)
        done_btn.setFont(QFont("Helvetica", 12, QFont.Bold))
        done_btn.setCursor(Qt.PointingHandCursor)
        done_btn.setStyleSheet("QPushButton{background:#2e7d32;color:#fff;border:none;border-radius:10px;}"
                               "QPushButton:hover{background:#1b5e20;}")
        done_btn.clicked.connect(self._mark_done)
        btn_row.addWidget(done_btn)

        del_btn = QPushButton("🗑️  Delete Task")
        del_btn.setFixedHeight(44)
        del_btn.setFont(QFont("Helvetica", 12, QFont.Bold))
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet("QPushButton{background:#e53935;color:#fff;border:none;border-radius:10px;}"
                              "QPushButton:hover{background:#b71c1c;}")
        del_btn.clicked.connect(self._delete_task)
        btn_row.addWidget(del_btn)
        root.addLayout(btn_row)

        self._refresh_list()
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self._check_reminders)
        self.reminder_timer.start(30000)

    def _add_task(self):
        name = self.task_input.text().strip()
        if not name:
            show_popup(self, "Empty Task", "Please enter a task name!", "warn")
            return
        due_dt = self.dt_picker.dateTime().toPyDateTime()
        if due_dt <= datetime.now():
            show_popup(self, "Invalid Time", "Please select a future date and time!", "warn")
            return
        task = {"name": name, "due": due_dt.strftime("%Y-%m-%d %H:%M"), "reminded": False, "done": False}
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.task_input.clear()
        self._refresh_list()
        show_popup(self, "Task Added ✅", f'"{name}" added!\n🔔 Reminder set 2 hours before due time.')

    def _mark_done(self):
        row = self.task_list.currentRow()
        if row < 0 or row >= len(self.tasks):
            show_popup(self, "No Selection", "Please select a task to mark as done!", "warn")
            return
        task_name = self.tasks[row]["name"]
        self.tasks[row]["done"] = True
        save_tasks(self.tasks)
        self._refresh_list()
        show_popup(self, "Task Done ✅", f'"{task_name}" marked as completed! 🎉')

    def _delete_task(self):
        row = self.task_list.currentRow()
        if row < 0 or row >= len(self.tasks):
            show_popup(self, "No Selection", "Please select a task to delete!", "warn")
            return
        task_name = self.tasks[row]["name"]
        result = show_popup(self, "Confirm Delete",
            f'Are you sure you want to delete:\n"{task_name}"?', "question")
        if result == QMessageBox.Yes:
            self.tasks.pop(row)
            save_tasks(self.tasks)
            self._refresh_list()
            show_popup(self, "Deleted ✅", f'"{task_name}" has been deleted.')

    def _refresh_list(self):
        self.task_list.clear()
        if not self.tasks:
            item = QListWidgetItem("  No tasks yet. Add one above!")
            item.setForeground(QColor("#1a1a2e"))
            self.task_list.addItem(item)
            return
        for t in self.tasks:
            due = datetime.strptime(t["due"], "%Y-%m-%d %H:%M")
            now = datetime.now()
            if t.get("done"):
                status = "✅ Done"
            elif due < now:
                status = "⌛ Overdue"
            else:
                status = "⏳ Pending"
            remind_time = due - timedelta(hours=2)
            text = (f'{status}  —  {t["name"]}\n'
                    f'     📅 Due: {due.strftime("%d %b %Y, %I:%M %p")}'
                    f'   🔔 Remind at: {remind_time.strftime("%I:%M %p")}')
            item = QListWidgetItem(text)
            item.setForeground(QColor("#1a1a2e"))
            self.task_list.addItem(item)

    def _check_reminders(self):
        now = datetime.now()
        changed = False
        for t in self.tasks:
            if t.get("reminded") or t.get("done"):
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
                msg.setStyleSheet(POPUP_STYLE)
                msg.setWindowFlags(Qt.WindowStaysOnTopHint)
                msg.exec_()
        if changed:
            save_tasks(self.tasks)
            self._refresh_list()


# ── NOTES TAB ────────────────────────────────────────────
class NotesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f7f7f8;")
        self.notes = load_notes()
        self.current_index = -1

        root = QHBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # ── Left panel: notes list ──
        left = QVBoxLayout()
        left.setSpacing(6)

        lbl = QLabel("🗒️  My Notes")
        lbl.setFont(QFont("Helvetica", 13, QFont.Bold))
        lbl.setStyleSheet("color:#000000; background:transparent;")
        left.addWidget(lbl)

        self.notes_list = QListWidget()
        self.notes_list.setFixedWidth(140)
        self.notes_list.setFont(QFont("Helvetica", 11))
        self.notes_list.setStyleSheet("""
            QListWidget{background:rgba(255,255,255,0.05); color:#1a1a2e; border:1px solid rgba(90,171,255,0.2); border-radius:10px; padding:4px;}
            QListWidget::item{padding:6px; color:#1a1a2e; border-bottom:1px solid rgba(255,255,255,0.05);}
            QListWidget::item:selected{background:rgba(90,171,255,0.15); color:#5aabff;}
        """)
        self.notes_list.currentRowChanged.connect(self._load_note)
        left.addWidget(self.notes_list)

        new_btn = QPushButton("➕ New Note")
        new_btn.setFixedHeight(38)
        new_btn.setFont(QFont("Helvetica", 11, QFont.Bold))
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet("QPushButton{background:#1a73e8;color:#fff;border:none;border-radius:8px;}"
                              "QPushButton:hover{background:#1558b0;}")
        new_btn.clicked.connect(self._new_note)
        left.addWidget(new_btn)

        del_btn = QPushButton("🗑️ Delete")
        del_btn.setFixedHeight(38)
        del_btn.setFont(QFont("Helvetica", 11, QFont.Bold))
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet("QPushButton{background:#e53935;color:#fff;border:none;border-radius:8px;}"
                              "QPushButton:hover{background:#b71c1c;}")
        del_btn.clicked.connect(self._delete_note)
        left.addWidget(del_btn)

        root.addLayout(left)

        # ── Right panel: editor ──
        right = QVBoxLayout()
        right.setSpacing(6)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Note title...")
        self.title_input.setFont(QFont("Helvetica", 13, QFont.Bold))
        self.title_input.setFixedHeight(40)
        self.title_input.setStyleSheet("""
            QLineEdit{background:rgba(255,255,255,0.07); color:#1a1a2e; border:1px solid rgba(90,171,255,0.25); border-radius:8px; padding:0 10px;}
            QLineEdit:focus{border:1px solid #5aabff; background:rgba(90,171,255,0.1);}
        """)
        self.title_input.textChanged.connect(self._auto_save)
        right.addWidget(self.title_input)

        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Start writing your note here...")
        self.text_editor.setFont(QFont("Helvetica", 13))
        self.text_editor.setStyleSheet("""
            QTextEdit{background:rgba(255,255,255,0.05); color:#1a1a2e; border:1px solid rgba(90,171,255,0.2); border-radius:8px; padding:8px;}
            QTextEdit:focus{border:1px solid #5aabff; background:rgba(0,212,255,0.08);}
        """)
        self.text_editor.textChanged.connect(self._auto_save)
        right.addWidget(self.text_editor)

        # Save indicator
        self.save_lbl = QLabel("💾 All notes saved automatically")
        self.save_lbl.setFont(QFont("Helvetica", 9))
        self.save_lbl.setStyleSheet("color:#7ddfb0; background:transparent;")
        right.addWidget(self.save_lbl)

        root.addLayout(right)

        self._refresh_list()
        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._save_current)

    def _refresh_list(self):
        self.notes_list.clear()
        for n in self.notes:
            title = n.get("title") or "Untitled"
            item = QListWidgetItem(title)
            item.setForeground(QColor("#1a1a2e"))
            self.notes_list.addItem(item)

    def _new_note(self):
        self.title_input.blockSignals(True)
        self.text_editor.blockSignals(True)
        if self.current_index >= 0 and self.current_index < len(self.notes):
            self.notes[self.current_index]["title"] = self.title_input.text() or "Untitled"
            self.notes[self.current_index]["content"] = self.text_editor.toPlainText()
            save_notes(self.notes)
        note = {"title": "New Note", "content": "", "created": datetime.now().strftime("%Y-%m-%d %H:%M")}
        self.notes.append(note)
        save_notes(self.notes)
        self.current_index = len(self.notes) - 1
        self._refresh_list()
        self.notes_list.setCurrentRow(self.current_index)
        self.title_input.setText("New Note")
        self.text_editor.setPlainText("")
        self.title_input.blockSignals(False)
        self.text_editor.blockSignals(False)
        self.title_input.setFocus()
        self.title_input.selectAll()

    def _load_note(self, row):
        if row < 0 or row >= len(self.notes):
            return
        if self.current_index >= 0 and self.current_index < len(self.notes) and self.current_index != row:
            self.notes[self.current_index]["title"] = self.title_input.text() or "Untitled"
            self.notes[self.current_index]["content"] = self.text_editor.toPlainText()
            save_notes(self.notes)
        self.current_index = row
        note = self.notes[row]
        self.title_input.blockSignals(True)
        self.text_editor.blockSignals(True)
        self.title_input.setText(note.get("title", ""))
        self.text_editor.setPlainText(note.get("content", ""))
        self.title_input.blockSignals(False)
        self.text_editor.blockSignals(False)

    def _auto_save(self):
        self.save_lbl.setText("✏️ Editing...")
        self.save_lbl.setStyleSheet("color:#d97706; background:transparent;")
        self.save_timer.start(800)

    def _save_current(self):
        if self.current_index < 0 or self.current_index >= len(self.notes):
            return
        self.notes[self.current_index]["title"] = self.title_input.text() or "Untitled"
        self.notes[self.current_index]["content"] = self.text_editor.toPlainText()
        save_notes(self.notes)
        self._refresh_list()
        self.notes_list.setCurrentRow(self.current_index)
        self.save_lbl.setText("💾 Saved!")
        self.save_lbl.setStyleSheet("color:#7ddfb0; background:transparent;")

    def _delete_note(self):
        row = self.notes_list.currentRow()
        if row < 0 or row >= len(self.notes):
            show_popup(self, "No Selection", "Please select a note to delete!", "warn")
            return
        title = self.notes[row].get("title", "Untitled")
        result = show_popup(self, "Confirm Delete",
            f'Delete note:\n"{title}"?', "question")
        if result == QMessageBox.Yes:
            self.notes.pop(row)
            save_notes(self.notes)
            self.current_index = -1
            self.title_input.clear()
            self.text_editor.clear()
            self._refresh_list()


# ── MAIN WINDOW ──────────────────────────────────────────
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raghav Chatbot")
        self.resize(460, 720)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background: #f7f7f8;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setFixedHeight(56)
        hdr.setStyleSheet("background:#1a73e8;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(14, 0, 14, 0)
        t = QLabel("🤖  Raghav Chatbot")
        t.setFont(QFont("Helvetica", 14, QFont.Bold))
        t.setStyleSheet("color:#1a1a2e; background:transparent;")
        b = QLabel("● always on top")
        b.setFont(QFont("Helvetica", 9))
        b.setStyleSheet("color:#a8d4ff; background:transparent;")
        hl.addWidget(t)
        hl.addStretch()
        hl.addWidget(b)
        root.addWidget(hdr)

        # Tabs
        # Floating pill buttons
        btn_bar = QFrame()
        btn_bar.setFixedHeight(56)
        btn_bar.setStyleSheet("background:#f7f7f8; border-bottom:1px solid #eeeeee;")
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(16,8,16,8)
        btn_layout.setSpacing(10)

        self.stack = QStackedWidget()
        self.stack.addWidget(ChatTab())
        self.stack.addWidget(TaskTab())
        self.stack.addWidget(NotesTab())

        ACTIVE = "QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7c3aed,stop:1 #4f46e5);color:#ffffff;border:none;border-radius:16px;padding:6px 18px;font-size:12px;font-weight:bold;}"
        INACTIVE = "QPushButton{background:#eeeeee;color:#666666;border:none;border-radius:16px;padding:6px 18px;font-size:12px;font-weight:bold;}QPushButton:hover{background:#e0d9ff;color:#4f46e5;}"

        self.b0 = QPushButton("💬  Chat")
        self.b1 = QPushButton("📝  Tasks")
        self.b2 = QPushButton("🗒️  Notes")

        for b in [self.b0, self.b1, self.b2]:
            b.setFixedHeight(34)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(INACTIVE)
        self.b0.setStyleSheet(ACTIVE)

        def switch(idx, A=ACTIVE, I=INACTIVE):
            self.stack.setCurrentIndex(idx)
            self.b0.setStyleSheet(A if idx==0 else I)
            self.b1.setStyleSheet(A if idx==1 else I)
            self.b2.setStyleSheet(A if idx==2 else I)

        self.b0.clicked.connect(lambda: switch(0))
        self.b1.clicked.connect(lambda: switch(1))
        self.b2.clicked.connect(lambda: switch(2))

        btn_layout.addStretch()
        btn_layout.addWidget(self.b0)
        btn_layout.addWidget(self.b1)
        btn_layout.addWidget(self.b2)
        btn_layout.addStretch()

        root.addWidget(btn_bar)
        root.addWidget(self.stack)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
