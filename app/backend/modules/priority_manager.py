from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from backend.core.base_module import BaseModule
from backend.core.module_manager import module_manager


class PriorityManagerModule(BaseModule):
    """タスクの優先度管理を行うモジュール"""
    
    PRIORITY_LEVELS = {
        1: "最高",
        2: "高",
        3: "中",
        4: "低",
        5: "最低"
    }
    
    def __init__(self):
        super().__init__("priority_manager")
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
            "set_priority": self._set_priority,
            "get_priority": self._get_priority,
            "get_priority_label": self._get_priority_label,
            "get_tasks_by_priority": self._get_tasks_by_priority,
            "validate_priority": self._validate_priority,
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return actions[action](params)
    
    def _validate_priority(self, params: Dict[str, Any]) -> bool:
        """優先度が有効な値かを検証"""
        priority = params.get("priority")
        return priority in self.PRIORITY_LEVELS
    
    def _set_priority(self, params: Dict[str, Any]) -> Any:
        """タスクの優先度を設定（task_crudモジュール経由）"""
        task_id = params.get("task_id")
        priority = params.get("priority")
        
        if not task_id:
            raise ValueError("task_id is required")
        
        if not self._validate_priority({"priority": priority}):
            raise ValueError(f"Invalid priority level. Must be between 1 and 5")
        
        # task_crudモジュールを呼び出してタスクを更新
        return module_manager.call_module(
            "task_crud",
            "update",
            {"task_id": task_id, "priority": priority}
        )
    
    def _get_priority(self, params: Dict[str, Any]) -> Optional[int]:
        """タスクの優先度を取得"""
        task_id = params.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # task_crudモジュールを呼び出してタスクを取得
        task = module_manager.call_module(
            "task_crud",
            "read",
            {"task_id": task_id}
        )
        
        return task.priority if task else None
    
    def _get_priority_label(self, params: Dict[str, Any]) -> Optional[str]:
        """優先度のラベルを取得"""
        priority = params.get("priority")
        
        if priority is None:
            task_id = params.get("task_id")
            if task_id:
                priority = self._get_priority({"task_id": task_id})
        
        return self.PRIORITY_LEVELS.get(priority)
    
    def _get_tasks_by_priority(self, params: Dict[str, Any]) -> List[Any]:
        """指定した優先度のタスクを取得"""
        priority = params.get("priority")
        
        if not self._validate_priority({"priority": priority}):
            raise ValueError(f"Invalid priority level. Must be between 1 and 5")
        
        # task_crudモジュールを呼び出してタスクを取得
        return module_manager.call_module(
            "task_crud",
            "read_all",
            {"priority": priority}
        )
