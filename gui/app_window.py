import customtkinter as ctk
import tkinter as tk
from typing import Optional, List, Dict
import datetime
import os

try:
    import data.database as db
    from core.models import Task, Note
    from gui.components.task_item_widget import TaskItemWidget
except ImportError as e:
    print(f"Error importing modules in app_window: {e}")
    import sys
    sys.exit(1)

APP_THEME_COLORS = {
    "main_bg_color": ("#F9F9F9", "#242424"),
    "tab_fg_color": ("#FFFFFF", "#2B2B2B"),
    "input_frame_bg_color": ("#F0F0F0", "#202020"),
    "scroll_frame_label_text_color": ("#4A4A4A", "#D0D0D0"),
    "button_primary_fg_color": ("#007AFF", "#007AFF"), # Example blue
    "button_primary_hover_color": ("#0056B3", "#0056B3"),
    "tab_selected_color": ("#007AFF", "#007AFF"),
    "tab_unselected_hover_color": ("#D0D0D0", "#4A4A4A"),
    "card_fg_color": ("#FFFFFF", "#2E2E2E"),
    "card_border_color": ("#DCDCDC", "#404040"),
    "details_text_color": ("#505050", "#A0A0A0"),
    "description_text_color": ("#181818", "#E0E0E0"),
    "completed_desc_color": ("#707070", "#888888")
}


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.configure(fg_color=APP_THEME_COLORS["main_bg_color"])
        ctk.set_appearance_mode("Light") # Or "Dark" or "System"
        # ctk.set_default_color_theme("blue") # Keep or use a custom theme file later

        self.title("NexusTask AI v1.2.0 - Visual Refresh")
        self.geometry("1050x750")
        self.minsize(850, 650)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(
            self,
            corner_radius=8,
            fg_color=APP_THEME_COLORS["tab_fg_color"],
            segmented_button_selected_color=APP_THEME_COLORS["tab_selected_color"],
            segmented_button_unselected_hover_color=APP_THEME_COLORS["tab_unselected_hover_color"]
        )
        self.tab_view.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.tasks_tab = self.tab_view.add("Tasks")
        self.notes_tab = self.tab_view.add("Notes")
        self.tab_view.set("Tasks")
        
        for tab_name in ["Tasks", "Notes"]:
            tab = self.tab_view.tab(tab_name)
            if tab:
                tab.configure(fg_color=APP_THEME_COLORS["tab_fg_color"])


        self.task_item_widgets_list: List[TaskItemWidget] = []
        self.note_widgets: List[Dict[str, ctk.CTkBaseClass]] = []
        self.current_tasks_for_notes_dropdown: List[Task] = []
        self.selected_note_id: Optional[int] = None

        self._configure_tasks_tab(self.tasks_tab)
        self._configure_notes_tab(self.notes_tab)

        self._load_tasks()
        self._load_notes()

    def _configure_tasks_tab(self, tab: ctk.CTkFrame):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        input_frame = ctk.CTkFrame(tab, corner_radius=8, fg_color=APP_THEME_COLORS["input_frame_bg_color"])
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        self.task_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter new task description...")
        self.task_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.task_priority_var = tk.StringVar(value="Media")
        self.task_priority_menu = ctk.CTkOptionMenu(input_frame, values=["Baja", "Media", "Alta"], variable=self.task_priority_var)
        self.task_priority_menu.grid(row=0, column=1, padx=5, pady=10)

        self.task_add_button = ctk.CTkButton(
            input_frame, text="Add Task", width=100,
            fg_color=APP_THEME_COLORS["button_primary_fg_color"],
            hover_color=APP_THEME_COLORS["button_primary_hover_color"],
            command=self._add_task_event
        )
        self.task_add_button.grid(row=0, column=3, padx=(5, 10), pady=10)

        self.task_list_scroll_frame = ctk.CTkScrollableFrame(
            tab, label_text="Current Tasks",
            label_text_color=APP_THEME_COLORS["scroll_frame_label_text_color"],
            fg_color=APP_THEME_COLORS["main_bg_color"] # Match tab background or main_bg
        )
        self.task_list_scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.task_list_scroll_frame.grid_columnconfigure(0, weight=1)


    def _configure_notes_tab(self, tab: ctk.CTkFrame):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        note_input_controls_frame = ctk.CTkFrame(tab, fg_color=APP_THEME_COLORS["input_frame_bg_color"], corner_radius=8)
        note_input_controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        note_input_controls_frame.grid_columnconfigure(0, weight=1)

        self.note_task_link_var = tk.StringVar(value="General Note (No Task)")
        self.note_task_link_dropdown = ctk.CTkOptionMenu(note_input_controls_frame, variable=self.note_task_link_var, values=["General Note (No Task)"])
        self.note_task_link_dropdown.grid(row=0, column=0, padx=(10,5), pady=10, sticky="ew")

        self.note_save_button = ctk.CTkButton(
            note_input_controls_frame, text="Save Note",
            fg_color=APP_THEME_COLORS["button_primary_fg_color"],
            hover_color=APP_THEME_COLORS["button_primary_hover_color"],
            command=self._save_note_event
        )
        self.note_save_button.grid(row=0, column=1, padx=5, pady=10)
        
        self.note_clear_button = ctk.CTkButton(note_input_controls_frame, text="New/Clear", command=self._clear_note_editor_event)
        self.note_clear_button.grid(row=0, column=2, padx=(5,10), pady=10)

        self.note_content_textbox = ctk.CTkTextbox(tab, wrap=tk.WORD, height=150, border_width=1, corner_radius=8)
        self.note_content_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.note_list_scroll_frame = ctk.CTkScrollableFrame(
            tab, label_text="Saved Notes",
            label_text_color=APP_THEME_COLORS["scroll_frame_label_text_color"],
            fg_color=APP_THEME_COLORS["main_bg_color"]
        )
        self.note_list_scroll_frame.grid(row=2, column=0, padx=10, pady=(0,10), sticky="nsew")
        self.note_list_scroll_frame.grid_columnconfigure(0, weight=1)

    def _clear_task_list_display(self):
        for widget in self.task_item_widgets_list:
            widget.destroy()
        self.task_item_widgets_list.clear()

    def _load_tasks(self):
        self._clear_task_list_display()
        try:
            tasks: List[Task] = db.get_all_tasks()
            for i, task in enumerate(tasks):
                if task.id is not None:
                    task_widget = TaskItemWidget(
                        master=self.task_list_scroll_frame,
                        task=task,
                        toggle_command=self._toggle_task_completion_event,
                        delete_command=self._delete_task_event,
                        app_theme=APP_THEME_COLORS 
                    )
                    task_widget.grid(row=i, column=0, sticky="ew", padx=5, pady=6) # pady between cards
                    self.task_item_widgets_list.append(task_widget)
            self._populate_tasks_for_notes_dropdown()
        except Exception as e:
            print(f"Error loading tasks into GUI: {e}")

    def _add_task_event(self):
        description = self.task_entry.get()
        priority = self.task_priority_var.get()
        if not description: return
        try:
            new_task = db.add_task(description=description, priority=priority, due_date=None)
            if new_task:
                self._load_tasks()
                self.task_entry.delete(0, tk.END)
                self.task_priority_var.set("Media")
        except Exception as e: print(f"Error in add task event: {e}")

    def _toggle_task_completion_event(self, task_id: int, new_status: bool):
        try:
            if db.update_task_completion(task_id, new_status):
                # TaskItemWidget updates its own style, but if other logic depends on it:
                # self._load_tasks() # Or find and update specific widget if needed
                pass # Widget handles its own style update on toggle
            else: print(f"Failed to update task {task_id} completion status.")
        except Exception as e: print(f"Error toggling task completion: {e}")

    def _delete_task_event(self, task_id: int):
        try:
            if db.delete_task(task_id): self._load_tasks()
            else: print(f"Failed to delete task {task_id}.")
        except Exception as e: print(f"Error deleting task: {e}")

    def _populate_tasks_for_notes_dropdown(self):
        self.current_tasks_for_notes_dropdown = db.get_all_tasks()
        dropdown_values = ["General Note (No Task)"] + \
                          [f"Task {t.id}: {t.description[:30]}..." for t in self.current_tasks_for_notes_dropdown if t.id is not None]
        if hasattr(self, 'note_task_link_dropdown'):
            current_selection = self.note_task_link_var.get()
            self.note_task_link_dropdown.configure(values=dropdown_values)
            if current_selection in dropdown_values:
                self.note_task_link_var.set(current_selection)
            else:
                self.note_task_link_var.set("General Note (No Task)")
    
    def _clear_note_list_display(self):
        for widget_dict in self.note_widgets:
            widget_dict['frame'].destroy()
        self.note_widgets.clear()

    def _create_note_widget(self, note: Note) -> Dict[str, ctk.CTkBaseClass]:
        note_row_frame = ctk.CTkFrame(
            self.note_list_scroll_frame, 
            corner_radius=8, border_width=1,
            fg_color=APP_THEME_COLORS["card_fg_color"],
            border_color=APP_THEME_COLORS["card_border_color"]
        )
        note_row_frame.grid_columnconfigure(0, weight=1)

        content_preview = note.content.replace("\n", " ")[:70] + ("..." if len(note.content) > 70 else "")
        created_at_str = note.created_at.strftime('%Y-%m-%d %H:%M') if note.created_at else "No date"
        
        task_link_info = ""
        if note.task_id:
            linked_task = next((task for task in self.current_tasks_for_notes_dropdown if task.id == note.task_id), None)
            if linked_task: task_link_info = f" (Task: {linked_task.description[:20]}...)"
            else: task_link_info = f" (Task ID: {note.task_id})"

        full_text = f"{content_preview}"
        details_text = f"Created: {created_at_str}{task_link_info}"

        note_label_content = ctk.CTkLabel(note_row_frame, text=full_text, anchor="w", justify="left", text_color=APP_THEME_COLORS["description_text_color"])
        note_label_content.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        note_label_content.bind("<Button-1>", lambda event, n_id=note.id: self._load_note_into_editor(n_id) if n_id is not None else None)

        note_label_details = ctk.CTkLabel(note_row_frame, text=details_text, anchor="w", justify="left", font=ctk.CTkFont(size=10), text_color=APP_THEME_COLORS["details_text_color"])
        note_label_details.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        note_label_details.bind("<Button-1>", lambda event, n_id=note.id: self._load_note_into_editor(n_id) if n_id is not None else None)
        
        delete_button = ctk.CTkButton(note_row_frame, text="Del", width=40, height=28, command=lambda n_id=note.id: self._delete_note_event(n_id) if n_id is not None else None)
        delete_button.grid(row=0, column=1, rowspan=2, padx=(5,10), pady=10, sticky="ns")
        
        return {"frame": note_row_frame, "label_content": note_label_content, "label_details": note_label_details, "delete_button": delete_button}

    def _load_notes(self):
        self._clear_note_list_display()
        try:
            notes: List[Note] = db.get_all_notes()
            for i, note in enumerate(notes):
                 if note.id is not None:
                    widget_dict = self._create_note_widget(note)
                    widget_dict['frame'].grid(row=i, column=0, sticky="ew", padx=5, pady=6) # pady between cards
                    self.note_widgets.append(widget_dict)
            self._populate_tasks_for_notes_dropdown()
        except Exception as e: print(f"Error loading notes into GUI: {e}")

    def _load_note_into_editor(self, note_id: int):
        if note_id is None: return
        note = db.get_note_by_id(note_id)
        if note:
            self.note_content_textbox.delete("1.0", tk.END)
            self.note_content_textbox.insert("1.0", note.content)
            self.selected_note_id = note.id
            if note.task_id:
                linked_task_display_val = next((f"Task {t.id}: {t.description[:30]}..." for t in self.current_tasks_for_notes_dropdown if t.id == note.task_id), None)
                if linked_task_display_val: self.note_task_link_var.set(linked_task_display_val)
                else: self.note_task_link_var.set("General Note (No Task)") 
            else: self.note_task_link_var.set("General Note (No Task)")
            self.note_save_button.configure(text="Update Note")
        else: self._clear_note_editor_event()

    def _clear_note_editor_event(self):
        self.selected_note_id = None
        self.note_content_textbox.delete("1.0", tk.END)
        self.note_task_link_var.set("General Note (No Task)")
        self.note_save_button.configure(text="Save Note")
        self.note_content_textbox.focus()

    def _save_note_event(self):
        content = self.note_content_textbox.get("1.0", tk.END).strip()
        selected_link_value = self.note_task_link_var.get()
        task_id: Optional[int] = None
        if selected_link_value != "General Note (No Task)":
            try:
                task_id_str = selected_link_value.split(":")[0].replace("Task ", "")
                task_id = int(task_id_str)
            except ValueError: task_id = None
        if not content: return
        try:
            if self.selected_note_id is not None:
                if db.update_note(self.selected_note_id, content): print(f"Note {self.selected_note_id} updated.")
                else: print(f"Failed to update note {self.selected_note_id}.")
            else:
                new_note = db.add_note(content=content, task_id=task_id)
                if new_note: print(f"Note added via GUI: {new_note}")
                else: print("Failed to add note via GUI.")
            self._load_notes()
            self._clear_note_editor_event()
        except Exception as e: print(f"Error in save note event: {e}")

    def _delete_note_event(self, note_id: int):
        if note_id is None: return
        try:
            if db.delete_note(note_id):
                self._load_notes()
                if self.selected_note_id == note_id: self._clear_note_editor_event()
            else: print(f"Failed to delete note {note_id}.")
        except Exception as e: print(f"Error deleting note: {e}")

if __name__ == "__main__":
    if not os.path.exists(db.INIT_FLAG_FILE) or not os.path.exists(db.DATABASE_PATH) :
        if os.path.exists(db.INIT_FLAG_FILE): os.remove(db.INIT_FLAG_FILE)
        db.initialize_database()
        try:
            with open(db.INIT_FLAG_FILE, 'w') as f: f.write(datetime.datetime.now().isoformat())
        except IOError as e: print(f"Warning: Could not create initialization flag file: {e}")
    app = AppWindow()
    app.mainloop()