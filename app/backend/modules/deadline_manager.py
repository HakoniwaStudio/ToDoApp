from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.core.base_module import BaseModule
from backend.core.module_manager import module_manager
from backend.database.models import Task


class DeadlineManagerModule(BaseModule):
    """タスクの期限管理を行うモジュール"""
    
    def __init__(self):
        super().__init__("deadline_manager")
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
            "set_deadline": self._set_deadline,
            "get_deadline": self._get_deadline,
            "remove_deadline": self._remove_deadline,
            "is_overdue": self._is_overdue,
            "get_overdue_tasks": self._get_overdue_tasks,
            "get_upcoming_deadlines": self._get_upcoming_deadlines,
            "get_time_remaining": self._get_time_remaining,
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return actions[action](params)
    
    def _set_deadline(self, params: Dict[str, Any]) -> Any:
        """タスクの期限を設定"""
        task_id = params.get("task_id")
        due_date = params.get("due_date")
        
        if not task_id:
            raise ValueError("task_id is required")
        
        if not due_date:
            raise ValueError("due_date is required")
        
        # 文字列の場合はdatetimeに変換
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Invalid date format. Use ISO format (e.g., '2024-12-31T23:59:59')")
        
        # task_crudモジュールを呼び出してタスクを更新
        return module_manager.call_module(
            "task_crud",
            "update",
            {"task_id": task_id, "due_date": due_date}
        )
    
    def _get_deadline(self, params: Dict[str, Any]) -> Optional[datetime]:
        """タスクの期限を取得"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        task = module_manager.call_module(
            "task_crud",
            "read",
            {"task_id": task_id}
        )
        
        return task.due_date if task else None
    
    def _remove_deadline(self, params: Dict[str, Any]) -> Any:
        """タスクの期限を削除"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        return module_manager.call_module(
            "task_crud",
            "update",
            {"task_id": task_id, "due_date": None}
        )
    
    def _is_overdue(self, params: Dict[str, Any]) -> bool:
        """タスクが期限切れかどうかを確認"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        due_date = self._get_deadline({"task_id": task_id})
        
        if not due_date:
            return False
        
        return datetime.utcnow() > due_date
    
    def _get_overdue_tasks(self, params: Dict[str, Any]) -> List[Task]:
        """期限切れのタスクを取得"""
        all_tasks = module_manager.call_module(
            "task_crud",
            "read_all",
            {}
        )
        
        overdue_tasks = [
            task for task in all_tasks
            if task.due_date and datetime.utcnow() > task.due_date
            and task.status != "completed"
        ]
        
        return overdue_tasks
    
    def _get_upcoming_deadlines(self, params: Dict[str, Any]) -> List[Task]:
        """近日中の期限があるタスクを取得"""
        days = params.get("days", 7)  # デフォルトは7日以内
        
        all_tasks = module_manager.call_module(
            "task_crud",
            "read_all",
            {}
        )
        
        now = datetime.utcnow()
        upcoming_deadline = now + timedelta(days=days)
        
        upcoming_tasks = [
            task for task in all_tasks
            if task.due_date and now <= task.due_date <= upcoming_deadline
            and task.status != "completed"
        ]
        
        # 期限が近い順にソート
        upcoming_tasks.sort(key=lambda x: x.due_date)
        
        return upcoming_tasks
    
    def _get_time_remaining(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """タスクの残り時間を取得"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        due_date = self._get_deadline({"task_id": task_id})
        
        if not due_date:
            return None
        
        now = datetime.utcnow()
        remaining = due_date - now
        
        is_overdue = remaining.total_seconds() < 0
        
        if is_overdue:
            remaining = abs(remaining)
        
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        return {
            "is_overdue": is_overdue,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "total_seconds": abs((due_date - now).total_seconds())
        }
