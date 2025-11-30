import axios from 'axios';
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  Category,
  CategoryCreate,
  Tag,
  TagCreate,
  Reminder,
  ReminderCreate,
  ProgressStats,
} from './types';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Task API
export const taskApi = {
  getAll: async (params?: {
    status?: string;
    priority?: number;
    root_only?: boolean;
  }): Promise<Task[]> => {
    const response = await api.get('/tasks/', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Task> => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },

  create: async (data: TaskCreate): Promise<Task> => {
    const response = await api.post('/tasks/', data);
    return response.data;
  },

  update: async (id: number, data: TaskUpdate): Promise<Task> => {
    const response = await api.put(`/tasks/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  getSubtasks: async (parentId: number): Promise<Task[]> => {
    const response = await api.get(`/tasks/${parentId}/subtasks`);
    return response.data;
  },

  addSubtask: async (parentId: number, data: TaskCreate): Promise<Task> => {
    const response = await api.post(`/tasks/${parentId}/subtasks`, data);
    return response.data;
  },

  setPriority: async (id: number, priority: number): Promise<Task> => {
    const response = await api.put(`/tasks/${id}/priority`, { priority });
    return response.data;
  },

  setDeadline: async (id: number, due_date: string): Promise<Task> => {
    const response = await api.put(`/tasks/${id}/deadline`, { due_date });
    return response.data;
  },

  removeDeadline: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}/deadline`);
  },

  getOverdue: async (): Promise<Task[]> => {
    const response = await api.get('/tasks/overdue/list');
    return response.data;
  },

  getUpcoming: async (days: number = 7): Promise<Task[]> => {
    const response = await api.get('/tasks/upcoming/list', { params: { days } });
    return response.data;
  },
};

// Category API
export const categoryApi = {
  getAll: async (): Promise<Category[]> => {
    const response = await api.get('/categories/');
    return response.data;
  },

  getById: async (id: number): Promise<Category> => {
    const response = await api.get(`/categories/${id}`);
    return response.data;
  },

  create: async (data: CategoryCreate): Promise<Category> => {
    const response = await api.post('/categories/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<CategoryCreate>): Promise<Category> => {
    const response = await api.put(`/categories/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/categories/${id}`);
  },

  assignToTask: async (categoryId: number, taskId: number): Promise<void> => {
    await api.post(`/categories/${categoryId}/tasks/${taskId}`);
  },

  unassignFromTask: async (categoryId: number, taskId: number): Promise<void> => {
    await api.delete(`/categories/${categoryId}/tasks/${taskId}`);
  },

  getTasks: async (categoryId: number): Promise<Task[]> => {
    const response = await api.get(`/categories/${categoryId}/tasks`);
    return response.data;
  },
};

// Tag API
export const tagApi = {
  getAll: async (): Promise<Tag[]> => {
    const response = await api.get('/tags/');
    return response.data;
  },

  getById: async (id: number): Promise<Tag> => {
    const response = await api.get(`/tags/${id}`);
    return response.data;
  },

  create: async (data: TagCreate): Promise<Tag> => {
    const response = await api.post('/tags/', data);
    return response.data;
  },

  update: async (id: number, data: TagCreate): Promise<Tag> => {
    const response = await api.put(`/tags/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/tags/${id}`);
  },

  assignToTask: async (tagId: number, taskId: number): Promise<void> => {
    await api.post(`/tags/${tagId}/tasks/${taskId}`);
  },

  unassignFromTask: async (tagId: number, taskId: number): Promise<void> => {
    await api.delete(`/tags/${tagId}/tasks/${taskId}`);
  },

  getTasks: async (tagId: number): Promise<Task[]> => {
    const response = await api.get(`/tags/${tagId}/tasks`);
    return response.data;
  },
};

// Reminder API
export const reminderApi = {
  getAll: async (): Promise<Reminder[]> => {
    const response = await api.get('/reminders/');
    return response.data;
  },

  getById: async (id: number): Promise<Reminder> => {
    const response = await api.get(`/reminders/${id}`);
    return response.data;
  },

  create: async (data: ReminderCreate): Promise<Reminder> => {
    const response = await api.post('/reminders/', data);
    return response.data;
  },

  update: async (
    id: number,
    data: { remind_at?: string; is_notified?: boolean }
  ): Promise<Reminder> => {
    const response = await api.put(`/reminders/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/reminders/${id}`);
  },

  getPending: async (): Promise<Reminder[]> => {
    const response = await api.get('/reminders/pending');
    return response.data;
  },

  markAsNotified: async (id: number): Promise<void> => {
    await api.post(`/reminders/${id}/notify`);
  },

  getByTask: async (taskId: number): Promise<Reminder[]> => {
    const response = await api.get(`/reminders/task/${taskId}`);
    return response.data;
  },
};

// Progress API
export const progressApi = {
  setProgress: async (taskId: number, progress: number): Promise<Task> => {
    const response = await api.put(`/progress/tasks/${taskId}`, { progress });
    return response.data;
  },

  getProgress: async (taskId: number): Promise<number> => {
    const response = await api.get(`/progress/tasks/${taskId}`);
    return response.data.progress;
  },

  incrementProgress: async (taskId: number, increment: number = 10): Promise<Task> => {
    const response = await api.post(`/progress/tasks/${taskId}/increment`, null, {
      params: { increment },
    });
    return response.data;
  },

  getTasksByRange: async (minProgress: number = 0, maxProgress: number = 100): Promise<Task[]> => {
    const response = await api.get('/progress/tasks/range/list', {
      params: { min_progress: minProgress, max_progress: maxProgress },
    });
    return response.data;
  },

  getStats: async (status?: string): Promise<ProgressStats> => {
    const response = await api.get('/progress/stats', {
      params: status ? { status } : undefined,
    });
    return response.data;
  },
};

export default api;
