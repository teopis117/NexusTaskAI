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

class Note:
    def __init__(self, id: Optional[int], content: str,
                 created_at: Optional[datetime.datetime] = None,
                 task_id: Optional[int] = None):
        self.id = id
        self.content = content
        self.created_at = created_at if created_at else datetime.datetime.now()
        self.task_id = task_id

    def __str__(self) -> str:
        created_str = self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else "No date"
        task_link_str = f" (TaskID: {self.task_id})" if self.task_id else ""
        return f"(ID: {self.id}) {self.content[:50]}... - Created: {created_str}{task_link_str}"

    def __repr__(self) -> str:
        return (f"Note(id={self.id!r}, content={self.content!r}, "
                f"created_at={self.created_at!r}, task_id={self.task_id!r})")