from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from backend.core.base_module import BaseModule
from backend.database.models import Task, Category, Tag


class TaskCRUDModule(BaseModule):
    """タスクのCRUD操作を管理するモジュール"""
    
    def __init__(self):
        super().__init__("task_crud")
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
            "create": self._create_task,
            "read": self._read_task,
            "read_all": self._read_all_tasks,
            "update": self._update_task,
            "delete": self._delete_task,
            "add_subtask": self._add_subtask,
            "get_subtasks": self._get_subtasks,
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return actions[action](params)
    
    def _create_task(self, params: Dict[str, Any]) -> Task:
        """タスクを作成"""
        task = Task(
            title=params.get("title"),
            description=params.get("description"),
            priority=params.get("priority", 3),
            due_date=params.get("due_date"),
            status=params.get("status", "pending"),
            progress=params.get("progress", 0),
            parent_task_id=params.get("parent_task_id")
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def _read_task(self, params: Dict[str, Any]) -> Optional[Task]:
        """タスクを取得"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def _read_all_tasks(self, params: Dict[str, Any]) -> List[Task]:
        """すべてのタスクを取得（フィルタリングオプション付き）"""
        query = self.db.query(Task)
        
        # ステータスフィルタ
        if "status" in params:
            query = query.filter(Task.status == params["status"])
        
        # 優先度フィルタ
        if "priority" in params:
            query = query.filter(Task.priority == params["priority"])
        
        # 親タスクのみ（サブタスクを除外）
        if params.get("root_only", False):
            query = query.filter(Task.parent_task_id.is_(None))
        
        return query.all()
    
    def _update_task(self, params: Dict[str, Any]) -> Optional[Task]:
        """タスクを更新"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # 更新可能なフィールド
        updatable_fields = [
            "title", "description", "priority", "due_date", 
            "status", "progress", "parent_task_id"
        ]
        
        for field in updatable_fields:
            if field in params:
                setattr(task, field, params[field])
        
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def _delete_task(self, params: Dict[str, Any]) -> bool:
        """タスクを削除"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        
        self.db.delete(task)
        self.db.commit()
        
        return True
    
    def _add_subtask(self, params: Dict[str, Any]) -> Task:
        """サブタスクを追加"""
        parent_id = params.get("parent_task_id")
        if not parent_id:
            raise ValueError("parent_task_id is required")
        
        # 親タスクの存在確認
        parent = self.db.query(Task).filter(Task.id == parent_id).first()
        if not parent:
            raise ValueError(f"Parent task with id {parent_id} not found")
        
        params["parent_task_id"] = parent_id
        return self._create_task(params)
    
    def _get_subtasks(self, params: Dict[str, Any]) -> List[Task]:
        """特定タスクのサブタスクを取得"""
        parent_id = params.get("parent_task_id")
        if not parent_id:
            raise ValueError("parent_task_id is required")
        
        return self.db.query(Task).filter(Task.parent_task_id == parent_id).all()
