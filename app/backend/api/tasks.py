from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.api.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, MessageResponse,
    PriorityUpdate, PriorityResponse,
    DeadlineUpdate, DeadlineResponse
)
from backend.core.module_manager import module_manager
from backend.modules import TaskCRUDModule, PriorityManagerModule, DeadlineManagerModule

router = APIRouter(prefix="/tasks", tags=["tasks"])

# モジュールの初期化（起動時に一度だけ実行される）
task_crud = TaskCRUDModule()
priority_manager = PriorityManagerModule()
deadline_manager = DeadlineManagerModule()

module_manager.register_module(task_crud)
module_manager.register_module(priority_manager)
module_manager.register_module(deadline_manager)


def setup_modules(db: Session):
    """各モジュールにDBセッションを設定"""
    task_crud.set_db(db)
    priority_manager.set_db(db)
    deadline_manager.set_db(db)


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """タスクを作成"""
    setup_modules(db)
    
    try:
        created_task = module_manager.call_module(
            "task_crud",
            "create",
            task.model_dump()
        )
        return created_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TaskResponse])
def get_all_tasks(
    status: str = None,
    priority: int = None,
    root_only: bool = False,
    db: Session = Depends(get_db)
):
    """すべてのタスクを取得（フィルタリング可能）"""
    setup_modules(db)
    
    params = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if root_only:
        params["root_only"] = root_only
    
    tasks = module_manager.call_module("task_crud", "read_all", params)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """特定のタスクを取得"""
    setup_modules(db)
    
    task = module_manager.call_module("task_crud", "read", {"task_id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """タスクを更新"""
    setup_modules(db)
    
    params = {"task_id": task_id}
    params.update(task_update.model_dump(exclude_unset=True))
    
    updated_task = module_manager.call_module("task_crud", "update", params)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """タスクを削除"""
    setup_modules(db)
    
    success = module_manager.call_module("task_crud", "delete", {"task_id": task_id})
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return MessageResponse(message="Task deleted successfully")


# サブタスク関連エンドポイント
@router.post("/{task_id}/subtasks", response_model=TaskResponse, status_code=201)
def add_subtask(task_id: int, subtask: TaskCreate, db: Session = Depends(get_db)):
    """サブタスクを追加"""
    setup_modules(db)
    
    params = subtask.model_dump()
    params["parent_task_id"] = task_id
    
    try:
        created_subtask = module_manager.call_module("task_crud", "add_subtask", params)
        return created_subtask
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}/subtasks", response_model=List[TaskResponse])
def get_subtasks(task_id: int, db: Session = Depends(get_db)):
    """サブタスクを取得"""
    setup_modules(db)
    
    subtasks = module_manager.call_module("task_crud", "get_subtasks", {"parent_task_id": task_id})
    return subtasks


# 優先度関連エンドポイント
@router.put("/{task_id}/priority", response_model=TaskResponse)
def set_priority(task_id: int, priority_data: PriorityUpdate, db: Session = Depends(get_db)):
    """タスクの優先度を設定"""
    setup_modules(db)
    
    try:
        updated_task = module_manager.call_module(
            "priority_manager",
            "set_priority",
            {"task_id": task_id, "priority": priority_data.priority}
        )
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}/priority", response_model=PriorityResponse)
def get_priority(task_id: int, db: Session = Depends(get_db)):
    """タスクの優先度を取得"""
    setup_modules(db)
    
    priority = module_manager.call_module("priority_manager", "get_priority", {"task_id": task_id})
    if priority is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    label = module_manager.call_module("priority_manager", "get_priority_label", {"priority": priority})
    
    return PriorityResponse(priority=priority, label=label)


# 期限関連エンドポイント
@router.put("/{task_id}/deadline", response_model=TaskResponse)
def set_deadline(task_id: int, deadline_data: DeadlineUpdate, db: Session = Depends(get_db)):
    """タスクの期限を設定"""
    setup_modules(db)
    
    try:
        updated_task = module_manager.call_module(
            "deadline_manager",
            "set_deadline",
            {"task_id": task_id, "due_date": deadline_data.due_date}
        )
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{task_id}/deadline", response_model=MessageResponse)
def remove_deadline(task_id: int, db: Session = Depends(get_db)):
    """タスクの期限を削除"""
    setup_modules(db)
    
    module_manager.call_module("deadline_manager", "remove_deadline", {"task_id": task_id})
    return MessageResponse(message="Deadline removed successfully")


@router.get("/overdue/list", response_model=List[TaskResponse])
def get_overdue_tasks(db: Session = Depends(get_db)):
    """期限切れのタスクを取得"""
    setup_modules(db)
    
    overdue_tasks = module_manager.call_module("deadline_manager", "get_overdue_tasks", {})
    return overdue_tasks


@router.get("/upcoming/list", response_model=List[TaskResponse])
def get_upcoming_deadlines(days: int = 7, db: Session = Depends(get_db)):
    """近日中の期限があるタスクを取得"""
    setup_modules(db)
    
    upcoming_tasks = module_manager.call_module(
        "deadline_manager",
        "get_upcoming_deadlines",
        {"days": days}
    )
    return upcoming_tasks
