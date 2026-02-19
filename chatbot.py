import tkinter as tk
from tkinter import scrolledtext
import threading

# ── CONFIG ──────────────────────────────────────────────
BOT_NAME   = "CharBot"
WIN_WIDTH  = 360
WIN_HEIGHT = 520
BG_COLOR   = "#1e1e2e"
USER_BG    = "#4a90e2"
BOT_BG     = "#2e2e3e"
TEXT_COLOR = "#ffffff"
INPUT_BG   = "#2e2e3e"
BTN_COLOR  = "#4a90e2"
FONT       = ("Segoe UI", 11)
FONT_BOLD  = ("Segoe UI", 11, "bold")
# ────────────────────────────────────────────────────────

def count_characters(name: str) -> str:
    name = name.strip()
    if not name:
        return "Please enter a name! 😊"
    count = len(name)
    # count with and without spaces
    no_space = len(name.replace(" ", ""))
    if " " in name:
        return (f'"{name}" has {count} characters '
                f'(including spaces) or {no_space} characters (without spaces).')
    return f'"{name}" has {count} character{"s" if count != 1 else ""}.'


def get_bot_response(user_text: str) -> str:
    text = user_text.strip()
    lower = text.lower()

    # greetings
    if lower in ("hi", "hello", "hey", "hii", "helo"):
        return f"Hello! 👋 I'm {BOT_NAME}. Type any name and I'll count its characters!"

    # farewells
    if lower in ("bye", "goodbye", "exit", "quit"):
        return "Goodbye! 👋 Have a great day!"

    # help
    if lower in ("help", "?", "what can you do"):
        return ("I can count characters in any name!\n"
                "Just type a name like: Raghu\n"
                "Or ask: how many characters in Raghu?")

    # "how many characters in X"
    for phrase in ("how many characters in ", "count ", "characters in "):
        if lower.startswith(phrase):
            name = text[len(phrase):]
            return count_characters(name)

    # "my name is X"
    if lower.startswith("my name is "):
        name = text[len("my name is "):]
        return "Nice to meet you! " + count_characters(name)

    # default — treat the whole input as a name
    return count_characters(text)


class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title(BOT_NAME)
        self.root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}+50+50")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Always on top
        self.root.attributes("-topmost", True)

        self._build_ui()
        self._add_message(BOT_NAME, f"Hi! I'm {BOT_NAME} 🤖\nType any name and I'll count its characters!", is_bot=True)

    # ── UI ──────────────────────────────────────────────
    def _build_ui(self):
        # Title bar
        title_bar = tk.Frame(self.root, bg="#12121f", pady=8)
        title_bar.pack(fill=tk.X)
        tk.Label(title_bar, text=f"🤖  {BOT_NAME}", bg="#12121f",
                 fg=TEXT_COLOR, font=FONT_BOLD).pack(side=tk.LEFT, padx=12)
        tk.Label(title_bar, text="● always on top", bg="#12121f",
                 fg="#4aeb8a", font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=12)

        # Chat area
        self.chat_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.canvas = tk.Canvas(self.chat_frame, bg=BG_COLOR,
                                highlightthickness=0)
        scrollbar = tk.Scrollbar(self.chat_frame, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.msg_container = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.msg_container, anchor="nw")

        self.msg_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Input area
        input_frame = tk.Frame(self.root, bg="#12121f", pady=8)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.entry = tk.Entry(input_frame, bg=INPUT_BG, fg=TEXT_COLOR,
                              font=FONT, insertbackground=TEXT_COLOR,
                              relief=tk.FLAT, bd=6)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 4))
        self.entry.bind("<Return>", self._on_send)
        self.entry.focus()

        send_btn = tk.Button(input_frame, text="Send ➤", bg=BTN_COLOR,
                             fg=TEXT_COLOR, font=FONT_BOLD, relief=tk.FLAT,
                             padx=10, cursor="hand2", command=self._on_send)
        send_btn.pack(side=tk.RIGHT, padx=(0, 10))

    # ── MESSAGING ───────────────────────────────────────
    def _on_send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._add_message("You", text, is_bot=False)
        # Run bot response in thread to keep UI responsive
        threading.Thread(target=self._respond, args=(text,), daemon=True).start()

    def _respond(self, text):
        response = get_bot_response(text)
        self.root.after(300, lambda: self._add_message(BOT_NAME, response, is_bot=True))

    def _add_message(self, sender, message, is_bot):
        bubble_color = BOT_BG if is_bot else USER_BG
        anchor = "w" if is_bot else "e"
        padx = (4, 40) if is_bot else (40, 4)

        outer = tk.Frame(self.msg_container, bg=BG_COLOR)
        outer.pack(fill=tk.X, pady=3)

        bubble = tk.Frame(outer, bg=bubble_color, padx=10, pady=7)
        bubble.pack(anchor=anchor, padx=padx)

        tk.Label(bubble, text=sender, bg=bubble_color,
                 fg="#aaaacc" if is_bot else "#d0e8ff",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")

        tk.Label(bubble, text=message, bg=bubble_color, fg=TEXT_COLOR,
                 font=FONT, wraplength=220, justify=tk.LEFT).pack(anchor="w")

        self.root.after(50, self._scroll_bottom)

    # ── HELPERS ─────────────────────────────────────────
    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _scroll_bottom(self):
        self.canvas.yview_moveto(1.0)


# ── MAIN ────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
