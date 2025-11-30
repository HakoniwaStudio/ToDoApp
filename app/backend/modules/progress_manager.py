from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from backend.core.base_module import BaseModule
from backend.database.models import Task


class ProgressManagerModule(BaseModule):
    """進捗管理モジュール"""

    def __init__(self):
        super().__init__("progress_manager")
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
            "set_progress": self._set_progress,
            "get_progress": self._get_progress,
            "increment_progress": self._increment_progress,
            "get_tasks_by_progress": self._get_tasks_by_progress,
            "calculate_overall_progress": self._calculate_overall_progress,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return actions[action](params)

    def _set_progress(self, params: Dict[str, Any]) -> Optional[Task]:
        """タスクの進捗を設定"""
        task_id = params.get("task_id")
        progress = params.get("progress")

        if not task_id:
            raise ValueError("task_id is required")
        if progress is None:
            raise ValueError("progress is required")

        # 進捗値のバリデーション（0-100）
        if not 0 <= progress <= 100:
            raise ValueError("progress must be between 0 and 100")

        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        task.progress = progress

        # 進捗が100%になった場合、ステータスを完了に変更
        if progress == 100 and task.status != "completed":
            task.status = "completed"
        # 進捗が0%より大きく100%未満の場合、ステータスを進行中に変更
        elif 0 < progress < 100 and task.status == "pending":
            task.status = "in_progress"

        self.db.commit()
        self.db.refresh(task)

        return task

    def _get_progress(self, params: Dict[str, Any]) -> Optional[int]:
        """タスクの進捗を取得"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")

        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        return task.progress

    def _increment_progress(self, params: Dict[str, Any]) -> Optional[Task]:
        """タスクの進捗を増加"""
        task_id = params.get("task_id")
        increment = params.get("increment", 10)

        if not task_id:
            raise ValueError("task_id is required")

        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        # 新しい進捗値を計算（最大100）
        new_progress = min(task.progress + increment, 100)

        return self._set_progress({"task_id": task_id, "progress": new_progress})

    def _get_tasks_by_progress(self, params: Dict[str, Any]) -> List[Task]:
        """進捗範囲でタスクを取得"""
        min_progress = params.get("min_progress", 0)
        max_progress = params.get("max_progress", 100)

        return self.db.query(Task).filter(
            Task.progress >= min_progress,
            Task.progress <= max_progress
        ).all()

    def _calculate_overall_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """全体的な進捗統計を計算"""
        # フィルタリング条件
        query = self.db.query(Task)

        if "status" in params:
            query = query.filter(Task.status == params["status"])

        tasks = query.all()

        if not tasks:
            return {
                "total_tasks": 0,
                "average_progress": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "pending_tasks": 0
            }

        total_progress = sum(task.progress for task in tasks)
        completed = sum(1 for task in tasks if task.status == "completed")
        in_progress = sum(1 for task in tasks if task.status == "in_progress")
        pending = sum(1 for task in tasks if task.status == "pending")

        return {
            "total_tasks": len(tasks),
            "average_progress": total_progress / len(tasks) if tasks else 0,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "pending_tasks": pending
        }
