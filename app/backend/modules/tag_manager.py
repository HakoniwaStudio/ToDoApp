from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from backend.core.base_module import BaseModule
from backend.database.models import Tag, Task


class TagManagerModule(BaseModule):
    """タグ管理モジュール"""

    def __init__(self):
        super().__init__("tag_manager")
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
            "create": self._create_tag,
            "read": self._read_tag,
            "read_all": self._read_all_tags,
            "update": self._update_tag,
            "delete": self._delete_tag,
            "assign_to_task": self._assign_to_task,
            "unassign_from_task": self._unassign_from_task,
            "get_tasks": self._get_tasks_by_tag,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return actions[action](params)

    def _create_tag(self, params: Dict[str, Any]) -> Tag:
        """タグを作成"""
        tag = Tag(name=params.get("name"))

        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)

        return tag

    def _read_tag(self, params: Dict[str, Any]) -> Optional[Tag]:
        """タグを取得"""
        tag_id = params.get("tag_id")
        if not tag_id:
            raise ValueError("tag_id is required")

        return self.db.query(Tag).filter(Tag.id == tag_id).first()

    def _read_all_tags(self, params: Dict[str, Any]) -> List[Tag]:
        """すべてのタグを取得"""
        return self.db.query(Tag).all()

    def _update_tag(self, params: Dict[str, Any]) -> Optional[Tag]:
        """タグを更新"""
        tag_id = params.get("tag_id")
        if not tag_id:
            raise ValueError("tag_id is required")

        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return None

        # 更新可能なフィールド
        if "name" in params:
            tag.name = params["name"]

        self.db.commit()
        self.db.refresh(tag)

        return tag

    def _delete_tag(self, params: Dict[str, Any]) -> bool:
        """タグを削除"""
        tag_id = params.get("tag_id")
        if not tag_id:
            raise ValueError("tag_id is required")

        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return False

        self.db.delete(tag)
        self.db.commit()

        return True

    def _assign_to_task(self, params: Dict[str, Any]) -> bool:
        """タグをタスクに割り当て"""
        task_id = params.get("task_id")
        tag_id = params.get("tag_id")

        if not task_id or not tag_id:
            raise ValueError("task_id and tag_id are required")

        task = self.db.query(Task).filter(Task.id == task_id).first()
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()

        if not task or not tag:
            return False

        if tag not in task.tags:
            task.tags.append(tag)
            self.db.commit()

        return True

    def _unassign_from_task(self, params: Dict[str, Any]) -> bool:
        """タスクからタグを解除"""
        task_id = params.get("task_id")
        tag_id = params.get("tag_id")

        if not task_id or not tag_id:
            raise ValueError("task_id and tag_id are required")

        task = self.db.query(Task).filter(Task.id == task_id).first()
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()

        if not task or not tag:
            return False

        if tag in task.tags:
            task.tags.remove(tag)
            self.db.commit()

        return True

    def _get_tasks_by_tag(self, params: Dict[str, Any]) -> List[Task]:
        """タグに属するタスクを取得"""
        tag_id = params.get("tag_id")
        if not tag_id:
            raise ValueError("tag_id is required")

        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return []

        return tag.tasks
