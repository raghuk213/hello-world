import tkinter as tk
import threading
import time

BOT_NAME = "CharBot"

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
        return f"Hello! I am {BOT_NAME}.\nType any name and I will count its characters!"
    if lower in ("bye", "goodbye", "exit", "quit"):
        return "Goodbye! Have a great day!"
    if lower in ("help", "?"):
        return "Just type any name!\nExample: Raghu\nOr type: my name is Raghu"
    for phrase in ("how many characters in ", "count ", "characters in "):
        if lower.startswith(phrase):
            return count_characters(text[len(phrase):])
    if lower.startswith("my name is "):
        return "Nice to meet you! " + count_characters(text[len("my name is "):])
    return count_characters(text)


class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title(BOT_NAME)
        self.root.geometry("400x580+100+100")
        self.root.resizable(True, True)
        self.root.configure(bg="#2b2b2b")
        self.root.attributes("-topmost", True)
        self._build_ui()
        self.root.after(400, self._welcome)

    def _build_ui(self):
        # ── Top bar ──
        top = tk.Frame(self.root, bg="#1a1a1a", height=40)
        top.pack(fill=tk.X, side=tk.TOP)
        top.pack_propagate(False)
        tk.Label(top, text="CharBot  |  always on top",
                 bg="#1a1a1a", fg="#ffffff",
                 font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        # ── Chat display ──
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.chat = tk.Text(
            frame,
            bg="#2b2b2b",
            fg="#ffffff",
            font=("Helvetica", 13),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=8,
            highlightthickness=0,
            spacing1=2,
            spacing2=2,
            spacing3=8,
        )
        sb = tk.Scrollbar(frame, command=self.chat.yview, bg="#2b2b2b")
        self.chat.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # tags
        self.chat.tag_configure("bot_label",
            foreground="#7eb8f7", font=("Helvetica", 10, "bold"))
        self.chat.tag_configure("bot_text",
            foreground="#e8e8e8", font=("Helvetica", 13),
            lmargin1=10, lmargin2=10)
        self.chat.tag_configure("user_label",
            foreground="#90ee90", font=("Helvetica", 10, "bold"),
            justify=tk.RIGHT)
        self.chat.tag_configure("user_text",
            foreground="#ffffff", font=("Helvetica", 13),
            justify=tk.RIGHT, rmargin=10)
        self.chat.tag_configure("divider",
            foreground="#555555", font=("Helvetica", 6))

        # ── Input area ──
        bottom = tk.Frame(self.root, bg="#1a1a1a", pady=8)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        self.entry = tk.Entry(
            bottom,
            bg="#3c3c3c", fg="#ffffff",
            font=("Helvetica", 13),
            insertbackground="#ffffff",
            relief=tk.FLAT, bd=6,
            highlightthickness=1,
            highlightcolor="#4a90e2",
            highlightbackground="#555555"
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 6), ipady=4)
        self.entry.bind("<Return>", self._send)
        self.entry.focus_set()

        send = tk.Button(
            bottom, text="Send",
            bg="#4a90e2", fg="#ffffff",
            font=("Helvetica", 12, "bold"),
            relief=tk.FLAT, padx=16, pady=4,
            cursor="hand2",
            activebackground="#357abd",
            activeforeground="#ffffff",
            bd=0,
            command=self._send
        )
        send.pack(side=tk.RIGHT, padx=(0, 10))

    def _welcome(self):
        self._add_bot("Hi! I am CharBot.\nType any name and I will count its characters!\n\nTry typing:\n  Raghu\n  my name is Raghu\n  hello")

    def _send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._add_user(text)
        threading.Thread(target=self._respond, args=(text,), daemon=True).start()

    def _respond(self, text):
        time.sleep(0.3)
        response = get_bot_response(text)
        self.root.after(0, lambda: self._add_bot(response))

    def _add_bot(self, message):
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, "CharBot\n", "bot_label")
        self.chat.insert(tk.END, message + "\n", "bot_text")
        self.chat.insert(tk.END, "\n", "divider")
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)
        self.root.update_idletasks()

    def _add_user(self, message):
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, "You\n", "user_label")
        self.chat.insert(tk.END, message + "\n", "user_text")
        self.chat.insert(tk.END, "\n", "divider")
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
