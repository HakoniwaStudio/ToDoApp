"""API Package"""

from backend.api.tasks import router as tasks_router
from backend.api.categories import router as categories_router
from backend.api.tags import router as tags_router
from backend.api.reminders import router as reminders_router
from backend.api.progress import router as progress_router

__all__ = [
    "tasks_router",
    "categories_router",
    "tags_router",
    "reminders_router",
    "progress_router"
]
