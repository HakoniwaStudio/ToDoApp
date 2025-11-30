from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.api.schemas import (
    TagCreate, TagUpdate, TagResponse,
    TaskResponse, MessageResponse
)
from backend.core.module_manager import module_manager
from backend.modules import TagManagerModule

router = APIRouter(prefix="/tags", tags=["tags"])

# モジュールの初期化
tag_manager = TagManagerModule()
module_manager.register_module(tag_manager)


def setup_modules(db: Session):
    """各モジュールにDBセッションを設定"""
    tag_manager.set_db(db)


@router.post("/", response_model=TagResponse, status_code=201)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """タグを作成"""
    setup_modules(db)

    try:
        created_tag = module_manager.call_module(
            "tag_manager",
            "create",
            tag.model_dump()
        )
        return created_tag
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TagResponse])
def get_all_tags(db: Session = Depends(get_db)):
    """すべてのタグを取得"""
    setup_modules(db)

    tags = module_manager.call_module("tag_manager", "read_all", {})
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """特定のタグを取得"""
    setup_modules(db)

    tag = module_manager.call_module(
        "tag_manager",
        "read",
        {"tag_id": tag_id}
    )
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db)
):
    """タグを更新"""
    setup_modules(db)

    params = {"tag_id": tag_id}
    params.update(tag_update.model_dump(exclude_unset=True))

    updated_tag = module_manager.call_module(
        "tag_manager",
        "update",
        params
    )
    if not updated_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return updated_tag


@router.delete("/{tag_id}", response_model=MessageResponse)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """タグを削除"""
    setup_modules(db)

    success = module_manager.call_module(
        "tag_manager",
        "delete",
        {"tag_id": tag_id}
    )
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return MessageResponse(message="Tag deleted successfully")


@router.post("/{tag_id}/tasks/{task_id}", response_model=MessageResponse)
def assign_tag_to_task(
    tag_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """タグをタスクに割り当て"""
    setup_modules(db)

    success = module_manager.call_module(
        "tag_manager",
        "assign_to_task",
        {"tag_id": tag_id, "task_id": task_id}
    )
    if not success:
        raise HTTPException(status_code=404, detail="Tag or Task not found")
    return MessageResponse(message="Tag assigned to task successfully")


@router.delete("/{tag_id}/tasks/{task_id}", response_model=MessageResponse)
def unassign_tag_from_task(
    tag_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """タスクからタグを解除"""
    setup_modules(db)

    success = module_manager.call_module(
        "tag_manager",
        "unassign_from_task",
        {"tag_id": tag_id, "task_id": task_id}
    )
    if not success:
        raise HTTPException(status_code=404, detail="Tag or Task not found")
    return MessageResponse(message="Tag unassigned from task successfully")


@router.get("/{tag_id}/tasks", response_model=List[TaskResponse])
def get_tasks_by_tag(tag_id: int, db: Session = Depends(get_db)):
    """タグに属するタスクを取得"""
    setup_modules(db)

    tasks = module_manager.call_module(
        "tag_manager",
        "get_tasks",
        {"tag_id": tag_id}
    )
    return tasks
