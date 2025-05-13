import customtkinter as ctk

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NexusTask AI v0.1")
        self.geometry("800x600")
        self.minsize(600, 400)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        label_provisional = ctk.CTkLabel(master=self,
                                         text="Welcome to NexusTask AI!",
                                         font=("Arial", 18))
        label_provisional.pack(pady=20, padx=20)

        # We will replace the label above with actual task management widgets
        # in the next step (Step 3: GUI Integration for Tasks)

if __name__ == "__main__":
    app = AppWindow()
    app.mainloop()