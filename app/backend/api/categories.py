from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.api.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    TaskResponse, MessageResponse
)
from backend.core.module_manager import module_manager
from backend.modules import CategoryManagerModule

router = APIRouter(prefix="/categories", tags=["categories"])

# モジュールの初期化
category_manager = CategoryManagerModule()
module_manager.register_module(category_manager)


def setup_modules(db: Session):
    """各モジュールにDBセッションを設定"""
    category_manager.set_db(db)


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """カテゴリを作成"""
    setup_modules(db)

    try:
        created_category = module_manager.call_module(
            "category_manager",
            "create",
            category.model_dump()
        )
        return created_category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    """すべてのカテゴリを取得"""
    setup_modules(db)

    categories = module_manager.call_module("category_manager", "read_all", {})
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """特定のカテゴリを取得"""
    setup_modules(db)

    category = module_manager.call_module(
        "category_manager",
        "read",
        {"category_id": category_id}
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """カテゴリを更新"""
    setup_modules(db)

    params = {"category_id": category_id}
    params.update(category_update.model_dump(exclude_unset=True))

    updated_category = module_manager.call_module(
        "category_manager",
        "update",
        params
    )
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category


@router.delete("/{category_id}", response_model=MessageResponse)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """カテゴリを削除"""
    setup_modules(db)

    success = module_manager.call_module(
        "category_manager",
        "delete",
        {"category_id": category_id}
    )
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return MessageResponse(message="Category deleted successfully")


@router.post("/{category_id}/tasks/{task_id}", response_model=MessageResponse)
def assign_category_to_task(
    category_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """カテゴリをタスクに割り当て"""
    setup_modules(db)

    success = module_manager.call_module(
        "category_manager",
        "assign_to_task",
        {"category_id": category_id, "task_id": task_id}
    )
    if not success:
        raise HTTPException(status_code=404, detail="Category or Task not found")
    return MessageResponse(message="Category assigned to task successfully")


@router.delete("/{category_id}/tasks/{task_id}", response_model=MessageResponse)
def unassign_category_from_task(
    category_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """タスクからカテゴリを解除"""
    setup_modules(db)

    success = module_manager.call_module(
        "category_manager",
        "unassign_from_task",
        {"category_id": category_id, "task_id": task_id}
    )
    if not success:
        raise HTTPException(status_code=404, detail="Category or Task not found")
    return MessageResponse(message="Category unassigned from task successfully")


@router.get("/{category_id}/tasks", response_model=List[TaskResponse])
def get_tasks_by_category(category_id: int, db: Session = Depends(get_db)):
    """カテゴリに属するタスクを取得"""
    setup_modules(db)

    tasks = module_manager.call_module(
        "category_manager",
        "get_tasks",
        {"category_id": category_id}
    )
    return tasks
