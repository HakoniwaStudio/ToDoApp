from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# タスク関連スキーマ
class TaskBase(BaseModel):
    """タスクの基本情報"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)
    due_date: Optional[datetime] = None
    status: str = Field(default="pending")
    progress: int = Field(default=0, ge=0, le=100)
    parent_task_id: Optional[int] = None


class TaskCreate(TaskBase):
    """タスク作成用スキーマ"""
    pass


class TaskUpdate(BaseModel):
    """タスク更新用スキーマ"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    parent_task_id: Optional[int] = None


class TaskResponse(TaskBase):
    """タスクレスポンス用スキーマ"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 優先度関連スキーマ
class PriorityUpdate(BaseModel):
    """優先度更新用スキーマ"""
    priority: int = Field(..., ge=1, le=5)


class PriorityResponse(BaseModel):
    """優先度レスポンス用スキーマ"""
    priority: int
    label: str


# 期限関連スキーマ
class DeadlineUpdate(BaseModel):
    """期限更新用スキーマ"""
    due_date: datetime


class DeadlineResponse(BaseModel):
    """期限レスポンス用スキーマ"""
    due_date: Optional[datetime]
    is_overdue: bool
    time_remaining: Optional[dict]


# カテゴリ関連スキーマ
class CategoryBase(BaseModel):
    """カテゴリの基本情報"""
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryCreate(CategoryBase):
    """カテゴリ作成用スキーマ"""
    pass


class CategoryResponse(CategoryBase):
    """カテゴリレスポンス用スキーマ"""
    id: int
    
    class Config:
        from_attributes = True


# タグ関連スキーマ
class TagBase(BaseModel):
    """タグの基本情報"""
    name: str = Field(..., min_length=1, max_length=50)


class TagCreate(TagBase):
    """タグ作成用スキーマ"""
    pass


class TagResponse(TagBase):
    """タグレスポンス用スキーマ"""
    id: int
    
    class Config:
        from_attributes = True


# 汎用レスポンス
class MessageResponse(BaseModel):
    """メッセージレスポンス"""
    message: str
    success: bool = True
