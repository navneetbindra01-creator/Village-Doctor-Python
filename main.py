import os
import sys
import logging
import threading

try:
    import customtkinter as ctk
    from tkinter import messagebox
except ImportError:
    print("Install: pip install customtkinter")
    sys.exit(1)

from llama_cpp import Llama

# Console suppression for .exe
if sys.platform.startswith('win'):
    import ctypes

    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
model_path = r"C:\Users\navne\PycharmProjects\villageDoctor\II-Medical-8B-1706.Q5_K_M.gguf"


class VillageDoctorApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("🩺 Village Doctor AI")
        self.root.geometry("1000x750")  # Larger default size
        self.root.resizable(True, True)  # Make resizable
        # REMOVED: self.root.attributes('-fullscreen', True)  # Now movable!

        self.model = None
        self.chat_history = []
        self.setup_ui()
        self.load_model_thread()  # Non-blocking model load

    def load_model_thread(self):
        def load():
            try:
                self.model = Llama(model_path, n_ctx=2048, n_threads=8, verbose=False)
                self.root.after(0, lambda: self.add_message("System", "🩺 Doctor ready! Ask health questions."))
            except Exception as e:
                self.root.after(0, lambda: self.add_message("System", f"Model error: {str(e)[:100]}"))

        threading.Thread(target=load, daemon=True).start()

    def setup_ui(self):
        # Title
        title = ctk.CTkLabel(self.root, text="🩺 Village Doctor AI 🩺",
                             font=ctk.CTkFont(size=36, weight="bold"))
        title.pack(pady=30)

        # Status
        self.status_label = ctk.CTkLabel(self.root, text="Loading doctor...",
                                         font=ctk.CTkFont(size=20))
        self.status_label.pack(pady=10)

        # Chat area
        self.chat_frame = ctk.CTkScrollableFrame(self.root, width=950, height=500)
        self.chat_frame.pack(pady=20, padx=30, fill="both", expand=True)

        # Input
        input_frame = ctk.CTkFrame(self.root)
        input_frame.pack(pady=20, padx=30, fill="x")

        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="Type your health question here...",
                                        height=60, font=ctk.CTkFont(size=22))
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(15, 15), pady=15)
        self.input_entry.bind("<Return>", self.send_message)

        send_btn = ctk.CTkButton(input_frame, text="💬 Ask Doctor", height=60,
                                 font=ctk.CTkFont(size=22, weight="bold"),
                                 command=self.send_message, fg_color="green")
        send_btn.pack(side="right", padx=(15, 15), pady=15)

        # Controls
        ctrl_frame = ctk.CTkFrame(self.root)
        ctrl_frame.pack(pady=10)

        ctk.CTkButton(ctrl_frame, text="Exit (Ctrl+Q)", width=150,
                      command=self.root.quit).pack(side="left", padx=20)

        self.status_label.configure(text="GUI ready! Loading model...")
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.after(200, lambda: self.input_entry.focus())

    def add_message(self, role, text):
        color = "#4ade80" if "Doctor" in role else "#60a5fa" if "You" in role else "#f59e0b"
        msg_frame = ctk.CTkFrame(self.chat_frame, fg_color=color, corner_radius=15)
        msg_frame.pack(pady=8, padx=15, fill="x")

        role_label = ctk.CTkLabel(msg_frame, text=role, font=ctk.CTkFont(size=16, weight="bold"))
        role_label.pack(pady=(10, 5))

        text_label = ctk.CTkLabel(msg_frame, text=text, font=ctk.CTkFont(size=20),
                                  anchor="w", justify="left", wraplength=900)
        text_label.pack(pady=5, padx=15)

        self.chat_frame._parent_canvas.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def send_message(self, event=None):
        if not self.model:
            self.add_message("System", "Doctor still loading... please wait.")
            return

        user_input = self.input_entry.get().strip()
        if not user_input:
            return

        self.input_entry.delete(0, "end")
        self.add_message("You", user_input)
        self.status_label.configure(text="Doctor thinking...")

        def generate():
            try:
                response = self.model(user_input, max_tokens=300, temperature=0.6,
                                      top_p=0.9, echo=False)['choices'][0]['text'].strip()
                self.root.after(0, lambda: self.add_message("Doctor", response))
                self.root.after(0, lambda: self.status_label.configure(text="Ready!"))
            except Exception as e:
                self.root.after(0, lambda: self.add_message("Doctor", f"Error: {str(e)}"))
                self.root.after(0, lambda: self.status_label.configure(text="Error, try again"))

        threading.Thread(target=generate, daemon=True).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = VillageDoctorApp()
    app.run()
