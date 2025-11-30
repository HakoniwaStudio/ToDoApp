from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.database import Base


# タスク-カテゴリ関連テーブル
task_categories = Table(
    'task_categories',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

# タスク-タグ関連テーブル
task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Task(Base):
    """タスクモデル"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=3)  # 1(最高) - 5(最低)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    progress = Column(Integer, default=0)  # 0-100
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    categories = relationship("Category", secondary=task_categories, back_populates="tasks")
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")


class Category(Base):
    """カテゴリモデル"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default="#000000")  # HEXカラーコード
    
    # リレーションシップ
    tasks = relationship("Task", secondary=task_categories, back_populates="categories")


class Tag(Base):
    """タグモデル"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    # リレーションシップ
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")


class Reminder(Base):
    """リマインダーモデル"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    is_notified = Column(Boolean, default=False)
    
    # リレーションシップ
    task = relationship("Task", back_populates="reminders")
