import datetime
from typing import Optional

class Task:
    def __init__(self, id: Optional[int], description: str, priority: str = "Media",
                 due_date: Optional[datetime.date] = None, completed: bool = False):
        if priority not in ["Baja", "Media", "Alta"]:
            raise ValueError("Priority must be 'Baja', 'Media', or 'Alta'")
        self.id = id
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed

    def __str__(self) -> str:
        status = "[X]" if self.completed else "[ ]"
        date_str = self.due_date.strftime('%Y-%m-%d') if self.due_date else "No date"
        return f"{status} (ID: {self.id}) {self.description} - Prio: {self.priority} - Due: {date_str}"

    def __repr__(self) -> str:
        return (f"Task(id={self.id!r}, description={self.description!r}, "
                f"priority={self.priority!r}, due_date={self.due_date!r}, "
                f"completed={self.completed!r})")