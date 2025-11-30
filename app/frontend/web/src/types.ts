// Task types
export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: number;
  due_date: string | null;
  status: 'pending' | 'in_progress' | 'completed';
  progress: number;
  parent_task_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: number;
  due_date?: string;
  status?: string;
  progress?: number;
  parent_task_id?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: number;
  due_date?: string;
  status?: string;
  progress?: number;
}

// Category types
export interface Category {
  id: number;
  name: string;
  color: string;
}

export interface CategoryCreate {
  name: string;
  color?: string;
}

// Tag types
export interface Tag {
  id: number;
  name: string;
}

export interface TagCreate {
  name: string;
}

// Reminder types
export interface Reminder {
  id: number;
  task_id: number;
  remind_at: string;
  is_notified: boolean;
}

export interface ReminderCreate {
  task_id: number;
  remind_at: string;
}

// Progress types
export interface ProgressStats {
  total_tasks: number;
  average_progress: number;
  completed_tasks: number;
  in_progress_tasks: number;
  pending_tasks: number;
}
