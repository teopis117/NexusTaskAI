import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional

try:
    from core.models import Task
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from core.models import Task

class TaskItemWidget(ctk.CTkFrame):
    def __init__(self, master, task: Task,
                 toggle_command: Optional[Callable[[int, bool], None]] = None,
                 delete_command: Optional[Callable[[int], None]] = None,
                 app_theme: dict = None):
        
        self.theme = app_theme if app_theme else {
            "card_fg_color": ("#FFFFFF", "#2B2B2B"),
            "card_border_color": ("#E0E0E0", "#444444"),
            "details_text_color": ("#555555", "#AAAAAA"),
            "description_text_color": ("#101010", "#E5E5E5"),
            "completed_desc_color": ("#777777", "#999999")
        }

        super().__init__(master, corner_radius=8, border_width=1,
                         fg_color=self.theme["card_fg_color"],
                         border_color=self.theme["card_border_color"])

        self.task = task
        self.toggle_command = toggle_command
        self.delete_command = delete_command

        self.grid_columnconfigure(1, weight=1)

        self.checkbox_var = tk.BooleanVar(value=self.task.completed)
        self.task_checkbox = ctk.CTkCheckBox(
            self, text="", variable=self.checkbox_var, command=self._on_toggle, width=20
        )
        self.task_checkbox.grid(row=0, column=0, rowspan=2, padx=(12, 5), pady=12, sticky="ns")

        desc_text = self.task.description
        self.task_label_description = ctk.CTkLabel(self, text=desc_text, anchor="w", justify="left", text_color=self.theme["description_text_color"])
        self.task_label_description.grid(row=0, column=1, padx=5, pady=(10, 2), sticky="ew")
        
        prio_text = f"Priority: {self.task.priority}"
        date_text = f"Due: {self.task.due_date.strftime('%Y-%m-%d')}" if self.task.due_date else "No due date"
        details_text = f"{prio_text} | {date_text}"

        self.task_label_details = ctk.CTkLabel(
            self, text=details_text, anchor="w", justify="left",
            font=ctk.CTkFont(size=11), text_color=self.theme["details_text_color"]
        )
        self.task_label_details.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="ew")

        self.delete_button = ctk.CTkButton(
            self, text="Delete", width=60, height=28, command=self._on_delete
        )
        self.delete_button.grid(row=0, column=2, rowspan=2, padx=(5, 12), pady=12, sticky="ns")
        
        self.bind("<Configure>", self._on_frame_configure) # Trigger wraplength update on resize
        self._update_style() # Initial style and wraplength update

        self.bind_all_mouse_scroll(self.task_label_description)
        self.bind_all_mouse_scroll(self.task_label_details)
        self.bind_all_mouse_scroll(self)

    def bind_all_mouse_scroll(self, widget):
        widget.bind("<MouseWheel>", lambda event: self._on_mouse_wheel(event), add="+")
        widget.bind("<Button-4>", lambda event: self._on_mouse_wheel(event), add="+")
        widget.bind("<Button-5>", lambda event: self._on_mouse_wheel(event), add="+")

    def _on_mouse_wheel(self, event):
        if self.master and hasattr(self.master, "_parent_canvas"): 
            canvas = self.master._parent_canvas 
            if event.num == 5 or event.delta < 0:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
        return "break"

    def _on_frame_configure(self, event=None):
        # Schedule the wraplength update.
        # Using 'after_idle' can be more robust than a fixed 'after(x)' ms.
        self.after_idle(self._update_label_wraplengths)

    def _update_label_wraplengths(self):
        if not self.winfo_exists():
            return
            
        parent_width = self.winfo_width()
        
        cb_width = self.task_checkbox.winfo_width() if self.task_checkbox.winfo_exists() else 30
        del_btn_width = self.delete_button.winfo_width() if self.delete_button.winfo_exists() else 70

        # Paddings for elements not in the label's column (column 1)
        # Checkbox: padx=(12,5) -> 17 total horizontal space including its own assumed internal padding.
        # Delete button: padx=(5,12) -> 17 total horizontal space.
        # Label's own grid padding: padx=5 -> 5 on left, 5 on right = 10
        
        # Estimate column 0 width (checkbox + its L/R grid padding)
        col0_effective_width = cb_width + 12 + 5 
        # Estimate column 2 width (button + its L/R grid padding)
        col2_effective_width = del_btn_width + 5 + 12
        
        # Available width for column 1 (labels' column)
        available_for_col1_content = parent_width - (col0_effective_width + col2_effective_width)
        
        # Subtract the label's own grid padding (padx=5 means 5 on each side)
        label_grid_padx_total = 5 + 5 
        final_wraplength = available_for_col1_content - label_grid_padx_total

        if final_wraplength < 20: # Minimum sensible wraplength
            final_wraplength = 20 

        if self.task_label_description.winfo_exists():
            self.task_label_description.configure(wraplength=final_wraplength)
        if self.task_label_details.winfo_exists():
            self.task_label_details.configure(wraplength=final_wraplength)


    def _on_toggle(self):
        if self.toggle_command and self.task.id is not None:
            self.toggle_command(self.task.id, self.checkbox_var.get())
        self._update_style()

    def _on_delete(self):
        if self.delete_command and self.task.id is not None:
            self.delete_command(self.task.id)

    def _update_style(self):
        current_description_color = self.theme["description_text_color"]
        current_details_color = self.theme["details_text_color"]
        
        description_font_slant = "roman"
        description_font_underline = False
        details_font_slant = "roman"
        details_font_underline = False

        if self.checkbox_var.get():
            description_font_slant = "italic"
            description_font_underline = True
            details_font_slant = "italic"
            details_font_underline = True
            current_description_color = self.theme["completed_desc_color"]
            current_details_color = self.theme["completed_desc_color"]
            
        self.task_label_description.configure(
            font=ctk.CTkFont(slant=description_font_slant, underline=description_font_underline),
            text_color=current_description_color
        )
        self.task_label_details.configure(
            font=ctk.CTkFont(size=11, slant=details_font_slant, underline=details_font_underline),
            text_color=current_details_color
        )
        self.after_idle(self._update_label_wraplengths) # Ensure wraplength is updated after style changes too

    def update_task_data(self, task: Task):
        self.task = task
        self.checkbox_var.set(self.task.completed)

        desc_text = self.task.description
        self.task_label_description.configure(text=desc_text)
        
        prio_text = f"Priority: {self.task.priority}"
        date_text = f"Due: {self.task.due_date.strftime('%Y-%m-%d')}" if self.task.due_date else "No due date"
        details_text = f"{prio_text} | {date_text}"
        self.task_label_details.configure(text=details_text)
        
        self._update_style()