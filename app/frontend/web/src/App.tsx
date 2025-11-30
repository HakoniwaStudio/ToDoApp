import { useState, useEffect } from 'react';
import './App.css';
import {
  taskApi,
  categoryApi,
  tagApi,
  reminderApi,
  progressApi,
} from './api';
import type {
  Task,
  TaskCreate,
  Category,
  Tag,
  Reminder,
  ProgressStats,
} from './types';

type View = 'all' | 'pending' | 'in_progress' | 'completed' | 'overdue' | 'upcoming';

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [currentView, setCurrentView] = useState<View>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Load data
  useEffect(() => {
    loadData();
  }, [currentView]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [tasksData, categoriesData, tagsData, statsData] = await Promise.all([
        loadTasks(),
        categoryApi.getAll(),
        tagApi.getAll(),
        progressApi.getStats(),
      ]);

      setCategories(categoriesData);
      setTags(tagsData);
      setStats(statsData);
    } catch (err) {
      setError('データの読み込みに失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    let tasksData: Task[];

    switch (currentView) {
      case 'pending':
        tasksData = await taskApi.getAll({ status: 'pending' });
        break;
      case 'in_progress':
        tasksData = await taskApi.getAll({ status: 'in_progress' });
        break;
      case 'completed':
        tasksData = await taskApi.getAll({ status: 'completed' });
        break;
      case 'overdue':
        tasksData = await taskApi.getOverdue();
        break;
      case 'upcoming':
        tasksData = await taskApi.getUpcoming(7);
        break;
      default:
        tasksData = await taskApi.getAll({ root_only: true });
    }

    setTasks(tasksData);
    return tasksData;
  };

  const handleCreateTask = async (data: TaskCreate) => {
    try {
      await taskApi.create(data);
      setShowTaskModal(false);
      loadData();
    } catch (err) {
      setError('タスクの作成に失敗しました');
      console.error(err);
    }
  };

  const handleUpdateTask = async (id: number, data: Partial<TaskCreate>) => {
    try {
      await taskApi.update(id, data);
      setEditingTask(null);
      setShowTaskModal(false);
      loadData();
    } catch (err) {
      setError('タスクの更新に失敗しました');
      console.error(err);
    }
  };

  const handleDeleteTask = async (id: number) => {
    if (!confirm('このタスクを削除してもよろしいですか？')) return;

    try {
      await taskApi.delete(id);
      loadData();
    } catch (err) {
      setError('タスクの削除に失敗しました');
      console.error(err);
    }
  };

  const handleToggleStatus = async (task: Task) => {
    const newStatus =
      task.status === 'completed'
        ? 'pending'
        : task.status === 'pending'
        ? 'in_progress'
        : 'completed';

    try {
      await taskApi.update(task.id, { status: newStatus });
      loadData();
    } catch (err) {
      setError('ステータスの更新に失敗しました');
      console.error(err);
    }
  };

  const getPriorityLabel = (priority: number): string => {
    const labels = {
      1: '最高',
      2: '高',
      3: '中',
      4: '低',
      5: '最低',
    };
    return labels[priority as keyof typeof labels] || '中';
  };

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  return (
    <div className="app">
      <header className="header">
        <h1>ToDoApp - タスク管理</h1>
      </header>

      <div className="main-container">
        <aside className="sidebar">
          <h2>ビュー</h2>
          <nav>
            <button
              className={currentView === 'all' ? 'active' : ''}
              onClick={() => setCurrentView('all')}
            >
              すべてのタスク
            </button>
            <button
              className={currentView === 'pending' ? 'active' : ''}
              onClick={() => setCurrentView('pending')}
            >
              未着手
            </button>
            <button
              className={currentView === 'in_progress' ? 'active' : ''}
              onClick={() => setCurrentView('in_progress')}
            >
              進行中
            </button>
            <button
              className={currentView === 'completed' ? 'active' : ''}
              onClick={() => setCurrentView('completed')}
            >
              完了
            </button>
            <button
              className={currentView === 'overdue' ? 'active' : ''}
              onClick={() => setCurrentView('overdue')}
            >
              期限切れ
            </button>
            <button
              className={currentView === 'upcoming' ? 'active' : ''}
              onClick={() => setCurrentView('upcoming')}
            >
              近日期限
            </button>
          </nav>
        </aside>

        <main className="content">
          {error && <div className="error">{error}</div>}

          {stats && (
            <div className="stats-grid">
              <div className="stat-card">
                <h3>総タスク数</h3>
                <div className="stat-value">{stats.total_tasks}</div>
              </div>
              <div className="stat-card">
                <h3>完了</h3>
                <div className="stat-value">{stats.completed_tasks}</div>
              </div>
              <div className="stat-card">
                <h3>進行中</h3>
                <div className="stat-value">{stats.in_progress_tasks}</div>
              </div>
              <div className="stat-card">
                <h3>平均進捗</h3>
                <div className="stat-value">{Math.round(stats.average_progress)}%</div>
              </div>
            </div>
          )}

          <div className="tasks-section">
            <div className="section-header">
              <h2>タスク一覧</h2>
              <button className="btn btn-primary" onClick={() => setShowTaskModal(true)}>
                + 新規タスク
              </button>
            </div>

            {tasks.length === 0 ? (
              <div className="empty-state">
                <p>タスクがありません</p>
                <button className="btn btn-primary" onClick={() => setShowTaskModal(true)}>
                  最初のタスクを作成
                </button>
              </div>
            ) : (
              <div className="task-list">
                {tasks.map((task) => (
                  <div key={task.id} className="task-item">
                    <div className="task-header">
                      <div>
                        <h3 className="task-title">{task.title}</h3>
                        {task.description && (
                          <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.25rem' }}>
                            {task.description}
                          </p>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                          onClick={() => {
                            setEditingTask(task);
                            setShowTaskModal(true);
                          }}
                        >
                          編集
                        </button>
                        <button
                          className="btn btn-danger"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                          onClick={() => handleDeleteTask(task.id)}
                        >
                          削除
                        </button>
                      </div>
                    </div>

                    <div className="task-meta">
                      <span
                        className={`badge badge-priority-${task.priority}`}
                      >
                        優先度: {getPriorityLabel(task.priority)}
                      </span>
                      <span className="badge badge-status">
                        {task.status === 'pending'
                          ? '未着手'
                          : task.status === 'in_progress'
                          ? '進行中'
                          : '完了'}
                      </span>
                      {task.due_date && (
                        <span>期限: {new Date(task.due_date).toLocaleDateString('ja-JP')}</span>
                      )}
                    </div>

                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                      進捗: {task.progress}%
                    </div>

                    <div style={{ marginTop: '0.5rem' }}>
                      <button
                        className="btn btn-primary"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                        onClick={() => handleToggleStatus(task)}
                      >
                        {task.status === 'completed'
                          ? '未完了に戻す'
                          : task.status === 'pending'
                          ? '開始する'
                          : '完了にする'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>

      {showTaskModal && (
        <TaskModal
          task={editingTask}
          onSave={(data) => {
            if (editingTask) {
              handleUpdateTask(editingTask.id, data);
            } else {
              handleCreateTask(data);
            }
          }}
          onClose={() => {
            setShowTaskModal(false);
            setEditingTask(null);
          }}
        />
      )}
    </div>
  );
}

interface TaskModalProps {
  task: Task | null;
  onSave: (data: TaskCreate) => void;
  onClose: () => void;
}

function TaskModal({ task, onSave, onClose }: TaskModalProps) {
  const [formData, setFormData] = useState<TaskCreate>({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || 3,
    status: task?.status || 'pending',
    progress: task?.progress || 0,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{task ? 'タスク編集' : '新規タスク'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>タイトル *</label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label>説明</label>
            <textarea
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label>優先度</label>
            <select
              value={formData.priority}
              onChange={(e) =>
                setFormData({ ...formData, priority: Number(e.target.value) })
              }
            >
              <option value={1}>最高</option>
              <option value={2}>高</option>
              <option value={3}>中</option>
              <option value={4}>低</option>
              <option value={5}>最低</option>
            </select>
          </div>

          <div className="form-group">
            <label>ステータス</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            >
              <option value="pending">未着手</option>
              <option value="in_progress">進行中</option>
              <option value="completed">完了</option>
            </select>
          </div>

          <div className="form-group">
            <label>進捗 ({formData.progress}%)</label>
            <input
              type="range"
              min="0"
              max="100"
              value={formData.progress}
              onChange={(e) =>
                setFormData({ ...formData, progress: Number(e.target.value) })
              }
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              キャンセル
            </button>
            <button type="submit" className="btn btn-primary">
              {task ? '更新' : '作成'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
