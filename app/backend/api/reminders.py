from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.api.schemas import (
    ReminderCreate, ReminderUpdate, ReminderResponse,
    MessageResponse
)
from backend.core.module_manager import module_manager
from backend.modules import ReminderManagerModule

router = APIRouter(prefix="/reminders", tags=["reminders"])

# モジュールの初期化
reminder_manager = ReminderManagerModule()
module_manager.register_module(reminder_manager)


def setup_modules(db: Session):
    """各モジュールにDBセッションを設定"""
    reminder_manager.set_db(db)


@router.post("/", response_model=ReminderResponse, status_code=201)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    """リマインダーを作成"""
    setup_modules(db)

    try:
        created_reminder = module_manager.call_module(
            "reminder_manager",
            "create",
            reminder.model_dump()
        )
        return created_reminder
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ReminderResponse])
def get_all_reminders(db: Session = Depends(get_db)):
    """すべてのリマインダーを取得"""
    setup_modules(db)

    reminders = module_manager.call_module("reminder_manager", "read_all", {})
    return reminders


@router.get("/pending", response_model=List[ReminderResponse])
def get_pending_reminders(db: Session = Depends(get_db)):
    """未通知のリマインダーを取得"""
    setup_modules(db)

    reminders = module_manager.call_module("reminder_manager", "get_pending", {})
    return reminders


@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """特定のリマインダーを取得"""
    setup_modules(db)

    reminder = module_manager.call_module(
        "reminder_manager",
        "read",
        {"reminder_id": reminder_id}
    )
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    db: Session = Depends(get_db)
):
    """リマインダーを更新"""
    setup_modules(db)

    params = {"reminder_id": reminder_id}
    params.update(reminder_update.model_dump(exclude_unset=True))

    updated_reminder = module_manager.call_module(
        "reminder_manager",
        "update",
        params
    )
    if not updated_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return updated_reminder


@router.delete("/{reminder_id}", response_model=MessageResponse)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """リマインダーを削除"""
    setup_modules(db)

    success = module_manager.call_module(
        "reminder_manager",
        "delete",
        {"reminder_id": reminder_id}
    )
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return MessageResponse(message="Reminder deleted successfully")


@router.post("/{reminder_id}/notify", response_model=MessageResponse)
def mark_reminder_as_notified(reminder_id: int, db: Session = Depends(get_db)):
    """リマインダーを通知済みとしてマーク"""
    setup_modules(db)

    success = module_manager.call_module(
        "reminder_manager",
        "mark_notified",
        {"reminder_id": reminder_id}
    )
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return MessageResponse(message="Reminder marked as notified")


@router.get("/task/{task_id}", response_model=List[ReminderResponse])
def get_reminders_by_task(task_id: int, db: Session = Depends(get_db)):
    """特定タスクのリマインダーを取得"""
    setup_modules(db)

    reminders = module_manager.call_module(
        "reminder_manager",
        "get_by_task",
        {"task_id": task_id}
    )
    return reminders
