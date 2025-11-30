"""Modules Package"""

from backend.modules.task_crud import TaskCRUDModule
from backend.modules.priority_manager import PriorityManagerModule
from backend.modules.deadline_manager import DeadlineManagerModule
from backend.modules.category_manager import CategoryManagerModule
from backend.modules.tag_manager import TagManagerModule
from backend.modules.reminder_manager import ReminderManagerModule
from backend.modules.progress_manager import ProgressManagerModule

__all__ = [
    "TaskCRUDModule",
    "PriorityManagerModule",
    "DeadlineManagerModule",
    "CategoryManagerModule",
    "TagManagerModule",
    "ReminderManagerModule",
    "ProgressManagerModule"
]
