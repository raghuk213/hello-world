import tkinter as tk
import threading

BOT_NAME   = "CharBot"
WIN_WIDTH  = 380
WIN_HEIGHT = 560
BG_COLOR   = "#1e1e2e"
TEXT_COLOR = "#ffffff"
INPUT_BG   = "#2e2e3e"
BTN_COLOR  = "#4a90e2"


def count_characters(name: str) -> str:
    name = name.strip()
    if not name:
        return "Please enter a name! 😊"
    count = len(name)
    no_space = len(name.replace(" ", ""))
    if " " in name:
        return (f'"{name}" has {count} characters '
                f'(including spaces)\nor {no_space} without spaces.')
    return f'"{name}" has {count} character{"s" if count != 1 else ""}.'


def get_bot_response(user_text: str) -> str:
    text  = user_text.strip()
    lower = text.lower()
    if lower in ("hi", "hello", "hey", "hii"):
        return f"Hello! I'm {BOT_NAME}.\nType any name and I'll count its characters!"
    if lower in ("bye", "goodbye", "exit", "quit"):
        return "Goodbye! Have a great day!"
    if lower in ("help", "?"):
        return "Just type any name!\nExample: Raghu\nOr: my name is Raghu"
    for phrase in ("how many characters in ", "count ", "characters in "):
        if lower.startswith(phrase):
            return count_characters(text[len(phrase):])
    if lower.startswith("my name is "):
        return "Nice to meet you! " + count_characters(text[len("my name is "):])
    return count_characters(text)


class ChatbotApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(BOT_NAME)
        self.root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}+80+80")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)
        self.root.attributes("-topmost", True)
        self._build_ui()
        self.root.after(300, lambda: self._add_message(
            BOT_NAME,
            "Hi! I'm CharBot\nType any name and I'll count its characters!\n\nExamples:\n  Raghu\n  my name is Raghu",
            is_bot=True
        ))

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#12121f", height=44)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text=f"  {BOT_NAME}",
                 bg="#12121f", fg="#ffffff",
                 font=("Helvetica", 13, "bold")).pack(side=tk.LEFT, padx=14)
        tk.Label(header, text="always on top  ",
                 bg="#12121f", fg="#4aeb8a",
                 font=("Helvetica", 9)).pack(side=tk.RIGHT, padx=14)

        # Chat area
        chat_outer = tk.Frame(self.root, bg=BG_COLOR)
        chat_outer.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(chat_outer)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_text = tk.Text(
            chat_outer,
            bg=BG_COLOR, fg=TEXT_COLOR,
            font=("Helvetica", 12),
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=12, pady=10,
            cursor="arrow",
            yscrollcommand=scrollbar.set
        )
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat_text.yview)

        self.chat_text.tag_configure("bot_name", foreground="#9a9abf",
            font=("Helvetica", 9, "bold"))
        self.chat_text.tag_configure("bot_msg", foreground="#e0e0ff",
            font=("Helvetica", 12), lmargin1=8, lmargin2=8)
        self.chat_text.tag_configure("user_name", foreground="#90c8ff",
            font=("Helvetica", 9, "bold"), justify="right")
        self.chat_text.tag_configure("user_msg", foreground="#ffffff",
            font=("Helvetica", 12), justify="right", rmargin=8)
        self.chat_text.tag_configure("gap", font=("Helvetica", 5))

        # Input area
        input_frame = tk.Frame(self.root, bg="#12121f", pady=10)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.entry = tk.Entry(input_frame, bg=INPUT_BG, fg=TEXT_COLOR,
                              font=("Helvetica", 13),
                              insertbackground=TEXT_COLOR,
                              relief=tk.FLAT, bd=8)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 6))
        self.entry.bind("<Return>", self._on_send)
        self.entry.focus()

        tk.Button(input_frame, text="Send", bg=BTN_COLOR, fg=TEXT_COLOR,
                  font=("Helvetica", 12, "bold"), relief=tk.FLAT,
                  padx=14, pady=4, cursor="hand2",
                  activebackground="#357abd", activeforeground="#ffffff",
                  command=self._on_send).pack(side=tk.RIGHT, padx=(0, 10))

    def _on_send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._add_message("You", text, is_bot=False)
        threading.Thread(target=self._respond, args=(text,), daemon=True).start()

    def _respond(self, text):
        response = get_bot_response(text)
        self.root.after(300, lambda: self._add_message(BOT_NAME, response, is_bot=True))

    def _add_message(self, sender, message, is_bot):
        self.chat_text.configure(state=tk.NORMAL)
        if is_bot:
            self.chat_text.insert(tk.END, f"{sender}\n", "bot_name")
            self.chat_text.insert(tk.END, f"{message}\n", "bot_msg")
        else:
            self.chat_text.insert(tk.END, f"{sender}\n", "user_name")
            self.chat_text.insert(tk.END, f"{message}\n", "user_msg")
        self.chat_text.insert(tk.END, "\n", "gap")
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
