from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from backend.core.base_module import BaseModule
from backend.database.models import Reminder, Task


class ReminderManagerModule(BaseModule):
    """リマインダー管理モジュール"""

    def __init__(self):
        super().__init__("reminder_manager")
        self.db: Optional[Session] = None

    def initialize(self) -> bool:
        """モジュールの初期化"""
        print(f"[{self.name}] Module initialized")
        return True

    def set_db(self, db: Session):
        """データベースセッションを設定"""
        self.db = db

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """アクションの実行"""
        if not self.db:
            raise RuntimeError("Database session not set")

        params = params or {}

        actions = {
            "create": self._create_reminder,
            "read": self._read_reminder,
            "read_all": self._read_all_reminders,
            "update": self._update_reminder,
            "delete": self._delete_reminder,
            "get_by_task": self._get_reminders_by_task,
            "get_pending": self._get_pending_reminders,
            "mark_notified": self._mark_as_notified,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return actions[action](params)

    def _create_reminder(self, params: Dict[str, Any]) -> Reminder:
        """リマインダーを作成"""
        task_id = params.get("task_id")
        remind_at = params.get("remind_at")

        if not task_id:
            raise ValueError("task_id is required")
        if not remind_at:
            raise ValueError("remind_at is required")

        # タスクの存在確認
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        reminder = Reminder(
            task_id=task_id,
            remind_at=remind_at,
            is_notified=False
        )

        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)

        return reminder

    def _read_reminder(self, params: Dict[str, Any]) -> Optional[Reminder]:
        """リマインダーを取得"""
        reminder_id = params.get("reminder_id")
        if not reminder_id:
            raise ValueError("reminder_id is required")

        return self.db.query(Reminder).filter(Reminder.id == reminder_id).first()

    def _read_all_reminders(self, params: Dict[str, Any]) -> List[Reminder]:
        """すべてのリマインダーを取得"""
        return self.db.query(Reminder).all()

    def _update_reminder(self, params: Dict[str, Any]) -> Optional[Reminder]:
        """リマインダーを更新"""
        reminder_id = params.get("reminder_id")
        if not reminder_id:
            raise ValueError("reminder_id is required")

        reminder = self.db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return None

        # 更新可能なフィールド
        if "remind_at" in params:
            reminder.remind_at = params["remind_at"]
        if "is_notified" in params:
            reminder.is_notified = params["is_notified"]

        self.db.commit()
        self.db.refresh(reminder)

        return reminder

    def _delete_reminder(self, params: Dict[str, Any]) -> bool:
        """リマインダーを削除"""
        reminder_id = params.get("reminder_id")
        if not reminder_id:
            raise ValueError("reminder_id is required")

        reminder = self.db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return False

        self.db.delete(reminder)
        self.db.commit()

        return True

    def _get_reminders_by_task(self, params: Dict[str, Any]) -> List[Reminder]:
        """特定タスクのリマインダーを取得"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")

        return self.db.query(Reminder).filter(Reminder.task_id == task_id).all()

    def _get_pending_reminders(self, params: Dict[str, Any]) -> List[Reminder]:
        """未通知のリマインダーを取得（現在時刻より前のもの）"""
        now = datetime.utcnow()
        return self.db.query(Reminder).filter(
            Reminder.is_notified == False,
            Reminder.remind_at <= now
        ).all()

    def _mark_as_notified(self, params: Dict[str, Any]) -> bool:
        """リマインダーを通知済みとしてマーク"""
        reminder_id = params.get("reminder_id")
        if not reminder_id:
            raise ValueError("reminder_id is required")

        reminder = self.db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return False

        reminder.is_notified = True
        self.db.commit()

        return True
