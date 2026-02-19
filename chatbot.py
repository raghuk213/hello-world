import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame,
    QCompleter, QTabWidget, QDateTimeEdit, QListWidget,
    QListWidgetItem, QMessageBox, QTextEdit, QSplitter
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
}
ALL_KEYS = list(DATA.keys())
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
        with open(NOTES_FILE) as f:
            return json.load(f)
    return []

def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)

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

POPUP_STYLE = """
    QMessageBox { background-color: #ddeeff; }
    QLabel { color: #000000; font-size: 13px; font-family: Helvetica; }
    QPushButton { background-color: #1a73e8; color: #ffffff; border-radius: 6px;
                  padding: 6px 20px; font-size: 13px; font-weight: bold; min-width: 70px; }
    QPushButton:hover { background-color: #1558b0; }
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
        root.setSpacing(8)

        title = QLabel("📝  Task Reminder")
        title.setFont(QFont("Helvetica", 15, QFont.Bold))
        title.setStyleSheet("color:#000000; background:transparent;")
        root.addWidget(title)

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

        add_btn = QPushButton("➕  Add Task")
        add_btn.setFixedHeight(44)
        add_btn.setFont(QFont("Helvetica", 13, QFont.Bold))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("QPushButton{background:#1a73e8;color:#fff;border:none;border-radius:10px;}"
                              "QPushButton:hover{background:#1558b0;}")
        add_btn.clicked.connect(self._add_task)
        root.addWidget(add_btn)

        list_lbl = QLabel("Your Tasks:  (select a task then click action)")
        list_lbl.setFont(QFont("Helvetica", 11, QFont.Bold))
        list_lbl.setStyleSheet("color:#000000; background:transparent;")
        root.addWidget(list_lbl)

        self.task_list = QListWidget()
        self.task_list.setFont(QFont("Helvetica", 12))
        self.task_list.setStyleSheet("""
            QListWidget{background:#fff; color:#000000; border:2px solid #90c0e8; border-radius:10px; padding:4px;}
            QListWidget::item{padding:8px; color:#000000; border-bottom:1px solid #ddeeff;}
            QListWidget::item:selected{background:#ddeeff; color:#000000;}
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
            item.setForeground(QColor("#000000"))
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
            item.setForeground(QColor("#000000"))
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
        self.setStyleSheet("background:#ddeeff;")
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
            QListWidget{background:#fff; color:#000000; border:2px solid #90c0e8; border-radius:10px; padding:4px;}
            QListWidget::item{padding:6px; color:#000000; border-bottom:1px solid #ddeeff;}
            QListWidget::item:selected{background:#1a73e8; color:#ffffff;}
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
            QLineEdit{background:#fff; color:#000000; border:2px solid #90c0e8; border-radius:8px; padding:0 10px;}
            QLineEdit:focus{border:2px solid #1a73e8;}
        """)
        self.title_input.textChanged.connect(self._auto_save)
        right.addWidget(self.title_input)

        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Start writing your note here...")
        self.text_editor.setFont(QFont("Helvetica", 13))
        self.text_editor.setStyleSheet("""
            QTextEdit{background:#ffffff; color:#000000; border:2px solid #90c0e8; border-radius:8px; padding:8px;}
            QTextEdit:focus{border:2px solid #1a73e8;}
        """)
        self.text_editor.textChanged.connect(self._auto_save)
        right.addWidget(self.text_editor)

        # Save indicator
        self.save_lbl = QLabel("💾 All notes saved automatically")
        self.save_lbl.setFont(QFont("Helvetica", 9))
        self.save_lbl.setStyleSheet("color:#2e7d32; background:transparent;")
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
            item.setForeground(QColor("#000000"))
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
        self.save_lbl.setStyleSheet("color:#e65100; background:transparent;")
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
        self.save_lbl.setStyleSheet("color:#2e7d32; background:transparent;")

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
        t = QLabel("🤖  Raghav Chatbot")
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
            QTabBar::tab{background:#b8d8f0; color:#000000; padding:10px 18px;
                         font-size:12px; border-top-left-radius:8px; border-top-right-radius:8px;}
            QTabBar::tab:selected{background:#1a73e8; color:#ffffff; font-weight:bold;}
            QTabBar::tab:hover{background:#90c0e8;}
        """)
        self.tabs.addTab(ChatTab(),  "💬  Chat")
        self.tabs.addTab(TaskTab(),  "📝  Tasks")
        self.tabs.addTab(NotesTab(), "🗒️  Notes")
        root.addWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
