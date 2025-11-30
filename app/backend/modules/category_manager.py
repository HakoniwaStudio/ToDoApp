from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from backend.core.base_module import BaseModule
from backend.database.models import Category, Task


class CategoryManagerModule(BaseModule):
    """カテゴリ管理モジュール"""

    def __init__(self):
        super().__init__("category_manager")
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
            "create": self._create_category,
            "read": self._read_category,
            "read_all": self._read_all_categories,
            "update": self._update_category,
            "delete": self._delete_category,
            "assign_to_task": self._assign_to_task,
            "unassign_from_task": self._unassign_from_task,
            "get_tasks": self._get_tasks_by_category,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return actions[action](params)

    def _create_category(self, params: Dict[str, Any]) -> Category:
        """カテゴリを作成"""
        category = Category(
            name=params.get("name"),
            color=params.get("color", "#000000")
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def _read_category(self, params: Dict[str, Any]) -> Optional[Category]:
        """カテゴリを取得"""
        category_id = params.get("category_id")
        if not category_id:
            raise ValueError("category_id is required")

        return self.db.query(Category).filter(Category.id == category_id).first()

    def _read_all_categories(self, params: Dict[str, Any]) -> List[Category]:
        """すべてのカテゴリを取得"""
        return self.db.query(Category).all()

    def _update_category(self, params: Dict[str, Any]) -> Optional[Category]:
        """カテゴリを更新"""
        category_id = params.get("category_id")
        if not category_id:
            raise ValueError("category_id is required")

        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None

        # 更新可能なフィールド
        if "name" in params:
            category.name = params["name"]
        if "color" in params:
            category.color = params["color"]

        self.db.commit()
        self.db.refresh(category)

        return category

    def _delete_category(self, params: Dict[str, Any]) -> bool:
        """カテゴリを削除"""
        category_id = params.get("category_id")
        if not category_id:
            raise ValueError("category_id is required")

        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False

        self.db.delete(category)
        self.db.commit()

        return True

    def _assign_to_task(self, params: Dict[str, Any]) -> bool:
        """カテゴリをタスクに割り当て"""
        task_id = params.get("task_id")
        category_id = params.get("category_id")

        if not task_id or not category_id:
            raise ValueError("task_id and category_id are required")

        task = self.db.query(Task).filter(Task.id == task_id).first()
        category = self.db.query(Category).filter(Category.id == category_id).first()

        if not task or not category:
            return False

        if category not in task.categories:
            task.categories.append(category)
            self.db.commit()

        return True

    def _unassign_from_task(self, params: Dict[str, Any]) -> bool:
        """タスクからカテゴリを解除"""
        task_id = params.get("task_id")
        category_id = params.get("category_id")

        if not task_id or not category_id:
            raise ValueError("task_id and category_id are required")

        task = self.db.query(Task).filter(Task.id == task_id).first()
        category = self.db.query(Category).filter(Category.id == category_id).first()

        if not task or not category:
            return False

        if category in task.categories:
            task.categories.remove(category)
            self.db.commit()

        return True

    def _get_tasks_by_category(self, params: Dict[str, Any]) -> List[Task]:
        """カテゴリに属するタスクを取得"""
        category_id = params.get("category_id")
        if not category_id:
            raise ValueError("category_id is required")

        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return []

        return category.tasks
