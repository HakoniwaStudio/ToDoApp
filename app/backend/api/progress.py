from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.api.schemas import (
    ProgressUpdate, ProgressResponse, ProgressStatsResponse,
    TaskResponse
)
from backend.core.module_manager import module_manager
from backend.modules import ProgressManagerModule

router = APIRouter(prefix="/progress", tags=["progress"])

# モジュールの初期化
progress_manager = ProgressManagerModule()
module_manager.register_module(progress_manager)


def setup_modules(db: Session):
    """各モジュールにDBセッションを設定"""
    progress_manager.set_db(db)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def set_task_progress(
    task_id: int,
    progress_data: ProgressUpdate,
    db: Session = Depends(get_db)
):
    """タスクの進捗を設定"""
    setup_modules(db)

    try:
        updated_task = module_manager.call_module(
            "progress_manager",
            "set_progress",
            {"task_id": task_id, "progress": progress_data.progress}
        )
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}", response_model=ProgressResponse)
def get_task_progress(task_id: int, db: Session = Depends(get_db)):
    """タスクの進捗を取得"""
    setup_modules(db)

    progress = module_manager.call_module(
        "progress_manager",
        "get_progress",
        {"task_id": task_id}
    )
    if progress is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return ProgressResponse(progress=progress)


@router.post("/tasks/{task_id}/increment", response_model=TaskResponse)
def increment_task_progress(
    task_id: int,
    increment: int = 10,
    db: Session = Depends(get_db)
):
    """タスクの進捗を増加"""
    setup_modules(db)

    updated_task = module_manager.call_module(
        "progress_manager",
        "increment_progress",
        {"task_id": task_id, "increment": increment}
    )
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return updated_task


@router.get("/tasks/range/list", response_model=List[TaskResponse])
def get_tasks_by_progress_range(
    min_progress: int = 0,
    max_progress: int = 100,
    db: Session = Depends(get_db)
):
    """進捗範囲でタスクを取得"""
    setup_modules(db)

    tasks = module_manager.call_module(
        "progress_manager",
        "get_tasks_by_progress",
        {"min_progress": min_progress, "max_progress": max_progress}
    )
    return tasks


@router.get("/stats", response_model=ProgressStatsResponse)
def get_overall_progress_stats(
    status: str = None,
    db: Session = Depends(get_db)
):
    """全体的な進捗統計を取得"""
    setup_modules(db)

    params = {}
    if status:
        params["status"] = status

    stats = module_manager.call_module(
        "progress_manager",
        "calculate_overall_progress",
        params
    )
    return stats
